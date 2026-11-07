from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from app.core.config import get_settings
from app.core.logging import logger
from app.models.schemas import ChunkDetail
from app.utils.helpers import ensure_directory_exists

settings = get_settings()


class ChromaVectorStore:
    """
    Manages persistent local ChromaDB vector store, collection indexing,
    and dense semantic vector queries filtered by product version.
    """

    def __init__(self, persist_directory: Optional[Path] = None):
        self.persist_directory = persist_directory or settings.chroma_path
        ensure_directory_exists(self.persist_directory)

        # Persistent Chroma client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Embedding function: Use all-MiniLM-L6-v2 via sentence-transformers
        # with fallback to DefaultEmbeddingFunction
        try:
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
            logger.info("ChromaVectorStore initialized with SentenceTransformerEmbeddingFunction ('all-MiniLM-L6-v2')")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer embedding function: {e}. Falling back to default.")
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            self.embedding_model_name = "default-onnx"

        # Collection name
        self.collection_name = "nexadesk_documentation"
        self._collection = None

    @property
    def collection(self):
        """Lazy get or create collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    def index_chunks(self, chunks: List[ChunkDetail]) -> int:
        """
        Add or update chunks into the persistent ChromaDB collection.
        Enforces strict metadata tagging for version-isolated filtering.
        """
        if not chunks:
            return 0

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for c in chunks:
            ids.append(c.id)
            documents.append(c.text_content)
            metadatas.append({
                "document_id": c.document_id,
                "document_name": c.metadata.document_name,
                "product_name": c.metadata.product_name,
                "product_version": c.metadata.product_version,
                "document_type": c.metadata.document_type,
                "section_title": c.section_title or "General",
                "page_number": c.page_number or 1,
                "category": c.metadata.category or "General",
                "chunk_index": c.chunk_index,
                "char_count": c.char_count
            })

        # Upsert into Chroma collection in batches of 100
        batch_size = 100
        total_indexed = 0
        for i in range(0, len(ids), batch_size):
            b_ids = ids[i:i + batch_size]
            b_docs = documents[i:i + batch_size]
            b_metas = metadatas[i:i + batch_size]
            self.collection.upsert(
                ids=b_ids,
                documents=b_docs,
                metadatas=b_metas
            )
            total_indexed += len(b_ids)

        logger.info(f"Indexed {total_indexed} chunks into ChromaDB collection '{self.collection_name}'.")
        return total_indexed

    def query_dense(
        self,
        query_text: str,
        version: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform dense semantic vector search strictly filtered by product version.
        Returns results with normalized similarity scores.
        """
        if not query_text.strip():
            return []

        # Enforce version isolation filter
        where_filter = {"product_version": version.strip()}

        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        dense_results: List[Dict[str, Any]] = []
        if results and results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for rank, (chunk_id, doc_text, meta, dist) in enumerate(zip(ids, docs, metas, distances), start=1):
                # Convert cosine distance to cosine similarity: sim = 1.0 - (dist / 2.0) or 1.0 - dist
                sim_score = max(0.0, min(1.0, 1.0 - (dist / 2.0 if dist > 1.0 else dist)))
                dense_results.append({
                    "chunk_id": chunk_id,
                    "document_id": meta.get("document_id"),
                    "text": doc_text,
                    "metadata": meta,
                    "dense_distance": float(dist),
                    "dense_similarity": float(sim_score),
                    "dense_rank": rank
                })

        return dense_results

    def delete_by_document_id(self, document_id: str) -> None:
        """Remove all chunks associated with a document ID from ChromaDB."""
        try:
            self.collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted chunks for document {document_id} from ChromaDB.")
        except Exception as e:
            logger.warning(f"Error removing chunks for {document_id} from Chroma: {e}")

    def reset_collection(self) -> None:
        """Clear and recreate the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self._collection = None
            logger.info(f"Reset ChromaDB collection '{self.collection_name}'.")
        except Exception as e:
            logger.warning(f"Collection reset warning: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Return diagnostic health and statistics for vector storage."""
        count = 0
        try:
            count = self.collection.count()
        except Exception:
            pass

        return {
            "status": "ready",
            "persist_directory": str(self.persist_directory),
            "collection_name": self.collection_name,
            "total_chunks_indexed": count,
            "embedding_model": self.embedding_model_name
        }


chroma_vector_store = ChromaVectorStore()
