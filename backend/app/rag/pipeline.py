"""
Phase 4: Version-Aware Hybrid RAG Pipeline.
Orchestrates:
  1. Customer Query
  2. Query Rewriting (Gemini API with heuristic fallback)
  3. Product Version Filtering (strict isolation)
  4. Dense Semantic Retrieval (ChromaDB + all-MiniLM-L6-v2)
  5. Sparse Lexical Retrieval (BM25Okapi)
  6. Reciprocal Rank Fusion (RRF)
  7. Final Retrieved Context with Debugging & Transparency Diagnostics
"""
import json
import sqlite3
import time
import uuid
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.logging import logger
from app.database.connection import get_sqlite_path
from app.models.schemas import ChunkDetail, ChunkMetadata
from app.rag.bm25_retriever import bm25_retriever
from app.rag.generator import grounded_generator
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.query_rewriter import query_rewriter
from app.rag.vector_store import chroma_vector_store

settings = get_settings()


class VersionAwareRAGPipeline:
    """
    Core RAG Pipeline implementing Query Rewriting, Version-Aware Hybrid Retrieval,
    and Grounded Answer Generation with Citations (Phase 5).
    """

    def __init__(self):
        self.vector_store = chroma_vector_store
        self.bm25 = bm25_retriever
        self.rewriter = query_rewriter
        self.hybrid = hybrid_retriever
        self.generator = grounded_generator
        self.db_path = get_sqlite_path()
        self.bm25 = bm25_retriever
        self.rewriter = query_rewriter
        self.hybrid = hybrid_retriever
        self.db_path = get_sqlite_path()

    def sync_all_from_sqlite(self) -> Dict[str, Any]:
        """
        Scan all document chunks in SQLite and index them into ChromaDB and BM25.
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
        # Invalidate BM25 cache so it refreshes from updated SQLite data
        self.bm25.invalidate_cache()
        status_info = self.vector_store.get_status()

        logger.info(f"RAG Pipeline: Synced {indexed_count} chunks from SQLite into ChromaDB and reset BM25 cache.")
        return {
            "status": "success",
            "chunks_synced": indexed_count,
            "total_indexed_in_chroma": status_info["total_chunks_indexed"],
            "by_version": status_info["by_version"]
        }

    def execute_hybrid_retrieval(
        self,
        customer_question: str,
        product_version: str,
        product_name: str = "NexaDesk",
        enable_query_rewriting: bool = True,
        retrieval_mode: str = "hybrid",
        top_k: int = 4,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
        similarity_threshold: float = 0.0,
        document_type: Optional[str] = None,
        document_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the full Phase 4 retrieval sequence:
        1. Customer Query
        2. Query Rewriting (Gemini API with heuristic fallback)
        3. Product Version Filtering (strict isolation)
        4. Dense Semantic Retrieval (ChromaDB)
        5. Sparse Lexical Retrieval (BM25)
        6. Reciprocal Rank Fusion (RRF)
        7. Final Context & Diagnostics
        """
        start_time = time.time()
        clean_question = customer_question.strip()

        # Step B: Version-Aware Pre-Check
        # Check if version exists in database
        version_has_docs = False
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents WHERE product_version = ?", (product_version,))
            count = cursor.fetchone()[0]
            version_has_docs = (count > 0)

        if not version_has_docs:
            return {
                "original_query": clean_question,
                "rewritten_query": None,
                "search_keywords": [],
                "product_name": product_name,
                "product_version": product_version,
                "retrieval_mode": retrieval_mode,
                "total_retrieved": 0,
                "results": [],
                "status_message": f"No documentation exists for requested product version '{product_version}'. Strict version isolation prevented fallback to other versions.",
                "diagnostics": {
                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                    "version_found": False
                }
            }

        # Step A: Query Rewriting
        rewriting_data = {
            "rewritten_query": clean_question,
            "search_keywords": [],
            "intent": "raw_query",
            "rewriter_used": "none",
            "reasoning": "Query rewriting disabled"
        }

        search_query = clean_question
        if enable_query_rewriting:
            rewriting_data = self.rewriter.rewrite(
                customer_question=clean_question,
                product_name=product_name,
                product_version=product_version
            )
            search_query = rewriting_data.get("rewritten_query", clean_question)

        # Step C & D: Hybrid Retrieval with strict version filtering
        results = self.hybrid.retrieve(
            query=search_query,
            product_version=product_version,
            product_name=product_name,
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            dense_weight=dense_weight,
            sparse_weight=sparse_weight,
            similarity_threshold=similarity_threshold,
            document_type=document_type,
            document_name=document_name
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "original_query": clean_question,
            "rewritten_query": rewriting_data.get("rewritten_query"),
            "search_keywords": rewriting_data.get("search_keywords", []),
            "product_name": product_name,
            "product_version": product_version,
            "retrieval_mode": retrieval_mode,
            "total_retrieved": len(results),
            "results": results,
            "status_message": f"Successfully retrieved {len(results)} context chunks strictly isolated to {product_version}.",
            "diagnostics": {
                "latency_ms": elapsed_ms,
                "rewriter_used": rewriting_data.get("rewriter_used"),
                "intent_detected": rewriting_data.get("intent"),
                "fusion_weights": {"dense": dense_weight, "sparse": sparse_weight, "rrf_k": self.hybrid.rrf_k},
                "version_isolated": True,
                "top_document_names": list({r["document_name"] for r in results})
            }
        }

    def compare_retrieval_methods(
        self,
        customer_question: str,
        product_version: str,
        product_name: str = "NexaDesk",
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Executes a 3-way comparative evaluation on the exact same customer question:
          1. Raw Query + Dense Retrieval
          2. Rewritten Query + Dense Retrieval
          3. Rewritten Query + Hybrid Retrieval (RRF)
        Returns side-by-side retrieved chunks and summary analysis.
        """
        clean_q = customer_question.strip()

        # Step 1: Rewrite query
        rewritten_data = self.rewriter.rewrite(
            customer_question=clean_q,
            product_name=product_name,
            product_version=product_version
        )
        rewritten_q = rewritten_data.get("rewritten_query", clean_q)

        # 1. Raw Query + Dense Retrieval
        raw_dense = self.hybrid.retrieve(
            query=clean_q,
            product_version=product_version,
            product_name=product_name,
            retrieval_mode="dense_only",
            top_k=top_k
        )

        # 2. Rewritten Query + Dense Retrieval
        rewritten_dense = self.hybrid.retrieve(
            query=rewritten_q,
            product_version=product_version,
            product_name=product_name,
            retrieval_mode="dense_only",
            top_k=top_k
        )

        # 3. Rewritten Query + Hybrid Retrieval (RRF)
        rewritten_hybrid = self.hybrid.retrieve(
            query=rewritten_q,
            product_version=product_version,
            product_name=product_name,
            retrieval_mode="hybrid",
            top_k=top_k
        )

        # Extract top IDs and section names for comparison
        raw_ids = [r["chunk_id"] for r in raw_dense]
        rewritten_dense_ids = [r["chunk_id"] for r in rewritten_dense]
        hybrid_ids = [r["chunk_id"] for r in rewritten_hybrid]

        overlap_dense = len(set(raw_ids).intersection(set(rewritten_dense_ids)))
        overlap_hybrid = len(set(rewritten_dense_ids).intersection(set(hybrid_ids)))

        return {
            "original_query": clean_q,
            "rewritten_query": rewritten_q,
            "search_keywords": rewritten_data.get("search_keywords", []),
            "product_version": product_version,
            "raw_dense_results": raw_dense,
            "rewritten_dense_results": rewritten_dense,
            "rewritten_hybrid_results": rewritten_hybrid,
            "summary_analysis": {
                "raw_dense_top_section": raw_dense[0]["section_title"] if raw_dense else None,
                "rewritten_dense_top_section": rewritten_dense[0]["section_title"] if rewritten_dense else None,
                "rewritten_hybrid_top_section": rewritten_hybrid[0]["section_title"] if rewritten_hybrid else None,
                "raw_vs_rewritten_dense_overlap": overlap_dense,
                "dense_vs_hybrid_overlap": overlap_hybrid,
                "rewriter_used": rewritten_data.get("rewriter_used"),
                "intent": rewritten_data.get("intent")
            }
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
        """Backward-compatible search method for vector store."""
        return self.vector_store.search_vectors(
            query=query,
            product_version=product_version,
            product_name=product_name,
            document_type=document_type,
            document_name=document_name,
            top_k=top_k
        )

    def answer_customer_enquiry(
        self,
        question: str,
        product_version: str,
        product_name: str = "NexaDesk",
        conversation_id: Optional[str] = None,
        retrieval_mode: str = "hybrid",
        top_k: int = 4,
        enable_rewriting: bool = True,
        temperature: float = 0.1,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete Phase 5 grounded question answering workflow:
          1. Retrieve multi-turn conversation history for context continuity.
          2. Execute fresh query rewriting and version-isolated hybrid retrieval.
          3. Evaluate evidence sufficiency (abstention / refusal check).
          4. Generate customer-friendly grounded answer with verifiable source citations.
          5. Persist conversation turn and audit log in SQLite.
        """
        start_time = time.time()
        conv_id = conversation_id or f"conv_{uuid.uuid4().hex[:12]}"

        # 1. Fetch prior conversation history for conversational awareness
        history_records = self.generator.get_conversation_history(conv_id, limit=6)
        formatted_history = [
            {"role": h["role"], "content": h["content"]} for h in history_records
        ]

        # 2. Execute fresh query rewriting & hybrid retrieval for this turn
        retrieval_res = self.execute_hybrid_retrieval(
            customer_question=question,
            product_version=product_version,
            product_name=product_name,
            enable_query_rewriting=enable_rewriting,
            retrieval_mode=retrieval_mode,
            top_k=top_k
        )

        retrieved_chunks = retrieval_res.get("results", [])

        # 3. Generate grounded answer with citations
        gen_res = self.generator.generate_grounded_answer(
            question=question,
            product_version=product_version,
            retrieved_chunks=retrieved_chunks,
            conversation_history=formatted_history,
            product_name=product_name,
            temperature=temperature,
            custom_api_key=api_key
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # 4. Save conversation turns into SQLite
        try:
            self.generator.save_conversation_message(
                conversation_id=conv_id,
                role="user",
                content=question,
                product_version=product_version
            )
            self.generator.save_conversation_message(
                conversation_id=conv_id,
                role="assistant",
                content=gen_res["answer"],
                product_version=product_version,
                rewritten_query=retrieval_res.get("rewritten_query"),
                citations=gen_res.get("citations"),
                abstained=gen_res.get("abstained", False)
            )

            # 5. Audit log in enquiry_logs
            citations_data = [c.model_dump() for c in gen_res.get("citations", [])]
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO enquiry_logs (session_id, user_query, product_version, response_text, sources, latency_ms, retrieval_mode, abstained)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conv_id,
                        question,
                        product_version,
                        gen_res["answer"],
                        json.dumps(citations_data),
                        elapsed_ms,
                        retrieval_mode,
                        1 if gen_res.get("abstained", False) else 0
                    )
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Error persisting enquiry log to SQLite: {e}")

        return {
            "answer": gen_res["answer"],
            "citations": gen_res.get("citations", []),
            "product_version": product_version,
            "rewritten_query": retrieval_res.get("rewritten_query"),
            "retrieved_sources": retrieved_chunks,
            "abstained": gen_res.get("abstained", False),
            "conversation_id": conv_id,
            "product_name": product_name,
            "original_query": question,
            "model_used": gen_res.get("model_used", "gemini-1.5-flash"),
            "latency_ms": elapsed_ms
        }

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Provides status of the vector indexing and hybrid retrieval pipeline."""
        chroma_status = self.vector_store.get_status()

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
            "current_phase": "Phase 5: Grounded Answer Generation with Citations",
            "pipeline_state": "active",
            "embedding_model": chroma_status["embedding_model"],
            "sparse_model": "BM25Okapi",
            "llm_provider": self.generator.provider.provider_name,
            "generation_model": self.generator.model_name,
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
