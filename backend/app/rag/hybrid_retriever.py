"""
Phase 4: Hybrid Retriever Module with Reciprocal Rank Fusion (RRF).
Combines dense semantic vector retrieval (ChromaDB + all-MiniLM-L6-v2) and sparse
lexical retrieval (BM25Okapi) with strict version-aware isolation.
"""
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.rag.bm25_retriever import bm25_retriever, BM25Retriever
from app.rag.vector_store import chroma_vector_store, ChromaVectorStore


class HybridRetriever:
    """
    Orchestrates dense semantic search and sparse lexical search, merging candidates
    using Reciprocal Rank Fusion (RRF) with configurable weights and strict product version filtering.
    """

    def __init__(
        self,
        vector_store: Optional[ChromaVectorStore] = None,
        bm25: Optional[BM25Retriever] = None,
        rrf_k: int = 60
    ):
        self.vector_store = vector_store or chroma_vector_store
        self.bm25 = bm25 or bm25_retriever
        self.rrf_k = rrf_k  # Standard IR smoothing constant

    def retrieve(
        self,
        query: str,
        product_version: str,
        product_name: str = "NexaDesk",
        retrieval_mode: str = "hybrid",
        top_k: int = 4,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
        similarity_threshold: float = 0.0,
        document_type: Optional[str] = None,
        document_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute version-isolated retrieval according to the specified mode:
          - 'hybrid': Merges dense and sparse candidates via RRF
          - 'dense_only': ChromaDB vector similarity search only
          - 'sparse_only': BM25 keyword search only
        """
        clean_q = query.strip()
        if not clean_q:
            return []

        # Candidate pool size for fusion
        candidate_k = max(top_k * 3, 10)

        # 1. Dense Semantic Retrieval
        dense_results: List[Dict[str, Any]] = []
        if retrieval_mode in ("hybrid", "dense_only"):
            dense_results = self.vector_store.search_vectors(
                query=clean_q,
                product_version=product_version,
                product_name=product_name,
                document_type=document_type,
                document_name=document_name,
                top_k=candidate_k
            )

        # 2. Sparse Lexical Retrieval
        sparse_results: List[Dict[str, Any]] = []
        if retrieval_mode in ("hybrid", "sparse_only"):
            sparse_results = self.bm25.search(
                query=clean_q,
                product_version=product_version,
                top_k=candidate_k,
                document_type=document_type,
                document_name=document_name
            )

        # Handle single-mode bypasses
        if retrieval_mode == "dense_only":
            return self._format_dense_only(dense_results, top_k, similarity_threshold)
        elif retrieval_mode == "sparse_only":
            return self._format_sparse_only(sparse_results, top_k, similarity_threshold)

        # 3. Hybrid Fusion via Reciprocal Rank Fusion (RRF)
        return self._fuse_rrf(
            dense_results=dense_results,
            sparse_results=sparse_results,
            top_k=top_k,
            dense_weight=dense_weight,
            sparse_weight=sparse_weight,
            similarity_threshold=similarity_threshold
        )

    def _fuse_rrf(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        top_k: int,
        dense_weight: float,
        sparse_weight: float,
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Compute RRF score for all candidate chunks:
        RRF(d) = w_dense / (k + rank_dense(d)) + w_sparse / (k + rank_sparse(d))
        """
        chunk_map: Dict[str, Dict[str, Any]] = {}

        # Index dense candidates
        for item in dense_results:
            c_id = item["chunk_id"]
            chunk_map[c_id] = {
                "chunk_id": c_id,
                "document_id": item.get("document_id") or item["metadata"].get("document_id", ""),
                "document_name": item["metadata"].get("document_name", "Unknown"),
                "product_name": item["metadata"].get("product_name", "NexaDesk"),
                "product_version": item["metadata"].get("product_version", ""),
                "document_type": item["metadata"].get("document_type", ""),
                "section_title": item["metadata"].get("section_title", "General"),
                "page_number": int(item["metadata"].get("page_number", 1)),
                "text_content": item["text_content"],
                "dense_rank": item.get("rank", 999),
                "dense_score": item.get("similarity_score", 0.0),
                "sparse_rank": None,
                "sparse_score": None,
                "metadata": item["metadata"]
            }

        # Index sparse candidates
        for item in sparse_results:
            c_id = item["chunk_id"]
            if c_id in chunk_map:
                chunk_map[c_id]["sparse_rank"] = item["rank"]
                chunk_map[c_id]["sparse_score"] = item["sparse_score"]
            else:
                chunk_map[c_id] = {
                    "chunk_id": c_id,
                    "document_id": item.get("document_id") or item["metadata"].get("document_id", ""),
                    "document_name": item["metadata"].get("document_name", "Unknown"),
                    "product_name": item["metadata"].get("product_name", "NexaDesk"),
                    "product_version": item["metadata"].get("product_version", ""),
                    "document_type": item["metadata"].get("document_type", ""),
                    "section_title": item["metadata"].get("section_title", "General"),
                    "page_number": int(item["metadata"].get("page_number", 1)),
                    "text_content": item["text_content"],
                    "dense_rank": None,
                    "dense_score": None,
                    "sparse_rank": item["rank"],
                    "sparse_score": item["sparse_score"],
                    "metadata": item["metadata"]
                }

        if not chunk_map:
            return []

        # Calculate weighted RRF score for each unique chunk
        scored_chunks: List[Dict[str, Any]] = []
        for c_id, data in chunk_map.items():
            rrf_dense_term = (
                dense_weight / (self.rrf_k + data["dense_rank"])
                if data["dense_rank"] is not None
                else 0.0
            )
            rrf_sparse_term = (
                sparse_weight / (self.rrf_k + data["sparse_rank"])
                if data["sparse_rank"] is not None
                else 0.0
            )
            raw_rrf = rrf_dense_term + rrf_sparse_term

            scored_chunks.append({
                **data,
                "raw_rrf": raw_rrf
            })

        # Sort descending by raw RRF score
        scored_chunks.sort(key=lambda x: x["raw_rrf"], reverse=True)

        # Theoretical maximum RRF score when a document is rank 1 in both dense and sparse
        max_possible_rrf = (dense_weight / (self.rrf_k + 1)) + (sparse_weight / (self.rrf_k + 1))
        
        results: List[Dict[str, Any]] = []
        for rank, item in enumerate(scored_chunks, start=1):
            normalized_rrf = item["raw_rrf"] / max_possible_rrf if max_possible_rrf > 0 else 0.0
            score_final = round(float(normalized_rrf), 4)

            if score_final < similarity_threshold:
                continue

            results.append({
                "chunk_id": item["chunk_id"],
                "document_id": item["document_id"],
                "document_name": item["document_name"],
                "product_name": item["product_name"],
                "product_version": item["product_version"],
                "document_type": item["document_type"],
                "section_title": item["section_title"],
                "page_number": item["page_number"],
                "text_content": item["text_content"],
                "dense_score": item["dense_score"],
                "sparse_score": item["sparse_score"],
                "rrf_score": score_final,
                "rank": rank,
                "retrieval_method": "hybrid",
                "metadata": item["metadata"]
            })

            if len(results) >= top_k:
                break

        return results

    def _format_dense_only(
        self,
        dense_results: List[Dict[str, Any]],
        top_k: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Format dense-only retrieval results."""
        results: List[Dict[str, Any]] = []
        for rank, item in enumerate(dense_results[:top_k], start=1):
            score = item.get("similarity_score", 0.0)
            if score < threshold:
                continue
            meta = item["metadata"]
            results.append({
                "chunk_id": item["chunk_id"],
                "document_id": meta.get("document_id", ""),
                "document_name": meta.get("document_name", "Unknown"),
                "product_name": meta.get("product_name", "NexaDesk"),
                "product_version": meta.get("product_version", ""),
                "document_type": meta.get("document_type", ""),
                "section_title": meta.get("section_title", "General"),
                "page_number": int(meta.get("page_number", 1)),
                "text_content": item["text_content"],
                "dense_score": score,
                "sparse_score": None,
                "rrf_score": score,
                "rank": rank,
                "retrieval_method": "dense",
                "metadata": meta
            })
        return results

    def _format_sparse_only(
        self,
        sparse_results: List[Dict[str, Any]],
        top_k: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Format sparse-only retrieval results."""
        results: List[Dict[str, Any]] = []
        for rank, item in enumerate(sparse_results[:top_k], start=1):
            score = item.get("sparse_score", 0.0)
            if score < threshold:
                continue
            meta = item["metadata"]
            results.append({
                "chunk_id": item["chunk_id"],
                "document_id": meta.get("document_id", ""),
                "document_name": meta.get("document_name", "Unknown"),
                "product_name": meta.get("product_name", "NexaDesk"),
                "product_version": meta.get("product_version", ""),
                "document_type": meta.get("document_type", ""),
                "section_title": meta.get("section_title", "General"),
                "page_number": int(meta.get("page_number", 1)),
                "text_content": item["text_content"],
                "dense_score": None,
                "sparse_score": score,
                "rrf_score": score,
                "rank": rank,
                "retrieval_method": "bm25",
                "metadata": meta
            })
        return results


# Global instance
hybrid_retriever = HybridRetriever()

