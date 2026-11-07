import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure offline operation for local sentence-transformers
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.logging import logger
from app.models.schemas import ChunkDetail
from app.utils.helpers import ensure_directory_exists

settings = get_settings()


class LocalSentenceTransformerEmbeddingFunction(EmbeddingFunction[Documents]):
    """
    Offline SentenceTransformer embedding generator using 'all-MiniLM-L6-v2'.
    Generates 384-dimensional dense vectors locally.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @classmethod
    def name(cls) -> str:
        return "sentence-transformers-all-MiniLM-L6-v2"

    def get_config(self) -> Dict[str, Any]:
        return {"model_name": self.model_name}

    @classmethod
    def build_from_config(cls, config: Dict[str, Any]) -> "LocalSentenceTransformerEmbeddingFunction":
        return cls(model_name=config.get("model_name", "all-MiniLM-L6-v2"))

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading local SentenceTransformer model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name, local_files_only=True)
        return self._model

    def __call__(self, input: Documents) -> Embeddings:
        """Embed a list of document strings."""
        if not input:
            return []
        vectors = self.model.encode(list(input), convert_to_numpy=True)
        return vectors.tolist()


class ChromaVectorStore:
    """
    Persistent ChromaDB vector store with version-aware partitioning and metadata filtering.
    Enforces strict isolation across product versions (v1.0, v2.0, v3.0).
    """

    def __init__(self, persist_directory: Optional[Path] = None):
        self.persist_directory = persist_directory or settings.chroma_path
        ensure_directory_exists(self.persist_directory)

        # Initialize persistent client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.embedding_fn = LocalSentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
        self.collection_name = "nexadesk_versioned_embeddings"
        self._collection = None

    @property
    def collection(self):
        """Lazy access to persistent ChromaDB collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    def index_chunks(self, chunks: List[ChunkDetail]) -> int:
        """
        Upsert chunks into ChromaDB with stable IDs and complete metadata.
        Prevents duplicate embeddings through idempotent ID upsertion.
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
                "document_id": str(c.document_id),
                "document_name": str(c.metadata.document_name),
                "product_name": str(c.metadata.product_name),
                "product_version": str(c.metadata.product_version),
                "document_type": str(c.metadata.document_type),
                "category": str(c.metadata.category or "General"),
                "section_title": str(c.section_title or "General"),
                "page_number": int(c.page_number or 1),
                "chunk_id": str(c.id),
                "chunk_index": int(c.chunk_index),
                "char_count": int(c.char_count)
            })

        batch_size = 64
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

        logger.info(f"ChromaDB: Indexed {total_indexed} chunks into '{self.collection_name}'.")
        return total_indexed

    def search_vectors(
        self,
        query: str,
        product_version: Optional[str] = None,
        product_name: Optional[str] = None,
        document_type: Optional[str] = None,
        document_name: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query vector database with metadata filtering supporting:
        - Product name
        - Product version
        - Document type
        - Document name
        """
        query_clean = query.strip()
        if not query_clean:
            return []

        # Construct compound ChromaDB where filter
        filter_conditions = []
        if product_version:
            filter_conditions.append({"product_version": product_version.strip()})
        if product_name:
            filter_conditions.append({"product_name": product_name.strip()})
        if document_type:
            filter_conditions.append({"document_type": document_type.strip().lower().lstrip(".")})
        if document_name:
            filter_conditions.append({"document_name": document_name.strip()})

        where_filter = None
        if len(filter_conditions) == 1:
            where_filter = filter_conditions[0]
        elif len(filter_conditions) > 1:
            where_filter = {"$and": filter_conditions}

        results = self.collection.query(
            query_texts=[query_clean],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        output: List[Dict[str, Any]] = []
        if results and results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for rank, (c_id, text, meta, dist) in enumerate(zip(ids, docs, metas, distances), start=1):
                # Convert cosine distance (0 to 2) to cosine similarity (1.0 = identical)
                similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0 if dist > 1.0 else dist)))
                output.append({
                    "chunk_id": c_id,
                    "document_id": meta.get("document_id"),
                    "text_content": text,
                    "similarity_score": round(float(similarity), 4),
                    "cosine_distance": round(float(dist), 4),
                    "rank": rank,
                    "metadata": meta
                })

        return output

    def delete_by_document_id(self, document_id: str) -> None:
        """Delete all chunk embeddings belonging to a single document without affecting others."""
        try:
            self.collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted Chroma embeddings for document: {document_id}")
        except Exception as e:
            logger.warning(f"Error removing embeddings for document {document_id}: {e}")

    def reset_collection(self) -> None:
        """Clear the collection completely."""
        try:
            self.client.delete_collection(self.collection_name)
            self._collection = None
            logger.info(f"ChromaDB collection '{self.collection_name}' reset.")
        except Exception as e:
            logger.warning(f"Could not delete collection: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Return diagnostic health and statistics for vector storage."""
        count = 0
        by_version: Dict[str, int] = {}
        try:
            count = self.collection.count()
            for ver in settings.SUPPORTED_PRODUCT_VERSIONS:
                ver_res = self.collection.get(where={"product_version": ver})
                by_version[ver] = len(ver_res["ids"]) if ver_res and ver_res["ids"] else 0
        except Exception as e:
            logger.warning(f"Error reading collection count: {e}")

        directory_exists = self.persist_directory.exists()
        writable = os.access(self.persist_directory, os.W_OK) if directory_exists else False

        return {
            "status": "ready" if directory_exists and writable else "error",
            "directory_exists": directory_exists,
            "writable": writable,
            "persist_directory": str(self.persist_directory),
            "collection_name": self.collection_name,
            "total_chunks_indexed": count,
            "by_version": by_version,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "supported_versions": settings.SUPPORTED_PRODUCT_VERSIONS
        }


    def check_status(self) -> Dict[str, Any]:
        """Backward compatible check_status method for health service."""
        return self.get_status()


chroma_vector_store = ChromaVectorStore()
chroma_storage_manager = chroma_vector_store
ChromaStorageManager = ChromaVectorStore
