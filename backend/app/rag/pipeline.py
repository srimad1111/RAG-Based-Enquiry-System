import sqlite3
from typing import Any, Dict, List, Optional
from app.core.config import get_settings
from app.core.logging import logger
from app.database.connection import get_sqlite_path
from app.models.schemas import ChunkDetail, ChunkMetadata
from app.rag.vector_store import chroma_vector_store

settings = get_settings()


class VersionAwareRAGPipeline:
    """
    RAG Pipeline Core (Phase 3: Version-Aware Vector Indexing).
    Orchestrates synchronization between SQLite chunk storage and ChromaDB,
    guaranteeing strict version isolation and rich metadata filtering.
    """

    def __init__(self):
        self.vector_store = chroma_vector_store
        self.db_path = get_sqlite_path()

    def sync_all_from_sqlite(self) -> Dict[str, Any]:
        """
        Scan all document chunks in SQLite and index them into ChromaDB.
        Idempotent: Uses chunk IDs to avoid duplicate embeddings.
        """
        all_chunks: List[ChunkDetail] = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, d.document_name, d.product_name, d.product_version,
                       d.category, d.document_type
                FROM document_chunks c
                JOIN documents d ON c.document_id = d.id
                ORDER BY c.document_id, c.chunk_index
            """)
            rows = cursor.fetchall()
            for r in rows:
                meta = ChunkMetadata(
                    document_id=r["document_id"],
                    document_name=r["document_name"],
                    product_name=r["product_name"],
                    product_version=r["product_version"],
                    document_type=r["document_type"],
                    section_title=r["section_title"],
                    page_number=r["page_number"],
                    upload_timestamp=str(r["created_at"]),
                    chunk_id=r["id"],
                    category=r["category"]
                )
                all_chunks.append(ChunkDetail(
                    id=r["id"],
                    document_id=r["document_id"],
                    chunk_index=r["chunk_index"],
                    text_content=r["text_content"],
                    char_count=r["char_count"],
                    section_title=r["section_title"],
                    page_number=r["page_number"],
                    metadata=meta
                ))

        indexed_count = self.vector_store.index_chunks(all_chunks)
        status_info = self.vector_store.get_status()

        logger.info(f"RAG Pipeline: Synced {indexed_count} chunks from SQLite into ChromaDB.")
        return {
            "status": "success",
            "chunks_synced": indexed_count,
            "total_indexed_in_chroma": status_info["total_chunks_indexed"],
            "by_version": status_info["by_version"]
        }

    def search(
        self,
        query: str,
        product_version: Optional[str] = None,
        product_name: Optional[str] = "NexaDesk",
        document_type: Optional[str] = None,
        document_name: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Version-isolated semantic vector retrieval.
        Never crosses boundaries between v1.0, v2.0, and v3.0 unless explicitly unconstrained.
        """
        return self.vector_store.search_vectors(
            query=query,
            product_version=product_version,
            product_name=product_name,
            document_type=document_type,
            document_name=document_name,
            top_k=top_k
        )

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Provides status of the vector indexing pipeline."""
        chroma_status = self.vector_store.get_status()

        # Count chunks in SQLite for sync verification
        sqlite_chunk_count = 0
        sqlite_doc_count = 0
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                sqlite_doc_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM document_chunks")
                sqlite_chunk_count = cursor.fetchone()[0]
        except Exception:
            pass

        return {
            "current_phase": "Phase 3: Version-Aware Vector Indexing",
            "pipeline_state": "active",
            "embedding_model": chroma_status["embedding_model"],
            "supported_versions": settings.SUPPORTED_PRODUCT_VERSIONS,
            "total_documents": sqlite_doc_count,
            "sqlite_chunks_count": sqlite_chunk_count,
            "chroma_chunks_indexed": chroma_status["total_chunks_indexed"],
            "is_synchronized": (sqlite_chunk_count == chroma_status["total_chunks_indexed"]),
            "by_version": chroma_status["by_version"],
            "persist_directory": chroma_status["persist_directory"]
        }


# Global pipeline instance
rag_pipeline = VersionAwareRAGPipeline()
rag_pipeline_stub = rag_pipeline
BaseRAGPipeline = VersionAwareRAGPipeline
