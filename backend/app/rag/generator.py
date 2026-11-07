"""
Phase 5: Grounded Answer Generator with Citations and Version Safety.
Integrates Query Rewriting, Hybrid Retrieval, and Interchangeable LLM Providers (Gemini / Ollama).
Enforces strict multi-version isolation, hallucination abstention, and verifiable source citations.
"""
import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import get_settings
from app.core.logging import logger
from app.database.connection import get_sqlite_path
from app.models.schemas import CitationItem
from app.rag.providers.common import synthesize_grounded_fallback
from app.rag.providers.factory import get_llm_provider

settings = get_settings()

ABSTENTION_MESSAGE_TEMPLATE = (
    "I cannot find verified information regarding this in the available NexaDesk {product_version} documentation. "
    "To ensure you receive accurate guidance, I recommend escalating this enquiry to our human support team "
    "or checking the official NexaDesk {product_version} documentation portal."
)


class GroundedAnswerGenerator:
    """
    Synthesizes customer-friendly, strictly grounded support answers using retrieved documentation.
    Features:
      - Strict version safety (never leaks or borrows features across v1.0, v2.0, v3.0).
      - Verifiable source citations linking directly to retrieved document chunks.
      - Retrieval sufficiency check with graceful abstention and human escalation offer.
      - Pluggable LLM Provider architecture (Gemini and Ollama) with offline fallback.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        provider_name: Optional[str] = None
    ):
        self.provider_name = (provider_name or settings.LLM_PROVIDER).lower()
        self.provider = get_llm_provider(self.provider_name)
        self.model_name = model_name or self.provider.model_name
        self.db_path = get_sqlite_path()
        logger.info(f"GroundedAnswerGenerator active provider: {self.provider.provider_name} ({self.provider.model_name})")

    # --------------------------------------------------------------------------
    # Retrieval Sufficiency & Abstention Check
    # --------------------------------------------------------------------------
    def evaluate_retrieval_sufficiency(
        self,
        retrieved_chunks: List[Dict[str, Any]],
        question: str = "",
        threshold: float = 0.35
    ) -> Tuple[bool, Optional[str]]:
        """
        Determines whether the retrieved documentation context contains sufficient evidence
        to reliably answer the customer question without hallucination.
        Returns: (is_sufficient: bool, reason: str)
        """
        if not retrieved_chunks:
            return False, "No relevant documentation chunks were retrieved for the target version."

        top_chunk = retrieved_chunks[0]
        dense_score = top_chunk.get("dense_score")
        sparse_score = top_chunk.get("sparse_score")

        # 1. Out-of-domain / unrelated check:
        # If BM25 matched zero keywords and dense cosine similarity is below 0.45,
        # the question cannot be verified from documentation (e.g. cookie recipes, unrelated trivia).
        if (sparse_score is None or sparse_score <= 0.0) and (dense_score is not None and dense_score < 0.45):
            return False, f"Zero lexical keyword match and low semantic similarity ({dense_score:.3f}). Question is unrecorded or out-of-domain."

        # 2. Direct query keyword overlap check:
        if question:
            from app.rag.bm25_retriever import tokenize_text
            q_tokens = set(tokenize_text(question))
            if q_tokens:
                chunk_tokens = set(tokenize_text(top_chunk["text_content"] + " " + top_chunk["section_title"]))
                overlap = q_tokens.intersection(chunk_tokens)
                if len(overlap) == 0 and (dense_score is None or dense_score < 0.50):
                    return False, "Zero topical keyword overlap found between inquiry and retrieved documentation."

        # 3. General low confidence check:
        if (dense_score is not None and dense_score < 0.30) and (sparse_score is None or sparse_score < 0.15):
            return False, "Retrieved documentation evidence falls below confidence threshold."

        return True, "Sufficient evidence found."

    # --------------------------------------------------------------------------
    # Main Generation Method
    # --------------------------------------------------------------------------
    def generate_grounded_answer(
        self,
        question: str,
        product_version: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        product_name: str = "NexaDesk",
        temperature: float = 0.1,
        custom_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a customer-friendly, grounded answer with citations.
        Returns dictionary containing:
          - answer: str
          - citations: List[CitationItem]
          - abstained: bool
          - model_used: str
        """
        # Step 1: Sufficiency check
        is_sufficient, reason = self.evaluate_retrieval_sufficiency(retrieved_chunks, question=question)

        if not is_sufficient:
            abstention_answer = ABSTENTION_MESSAGE_TEMPLATE.format(product_version=product_version)
            return {
                "answer": abstention_answer,
                "citations": [],
                "abstained": True,
                "model_used": "abstention-guard",
                "reason": reason
            }

        # Step 2: Build citations mapping
        citations: List[CitationItem] = []
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            snippet_text = chunk["text_content"]
            if len(snippet_text) > 250:
                snippet_text = snippet_text[:250].strip() + "..."

            citations.append(CitationItem(
                citation_id=idx,
                document_name=chunk["document_name"],
                document_type=chunk["document_type"],
                section_title=chunk["section_title"],
                page_number=chunk["page_number"],
                chunk_id=chunk["chunk_id"],
                snippet=snippet_text,
                relevance_score=chunk.get("rrf_score", 0.0)
            ))

        # Step 3: Delegate answer generation to the interchangeable LLM provider
        provider = get_llm_provider(self.provider_name)
        answer_text = provider.generate_answer(
            question=question,
            product_version=product_version,
            product_name=product_name,
            chunks=retrieved_chunks,
            history=conversation_history,
            temperature=temperature,
            custom_api_key=custom_api_key
        )

        return {
            "answer": answer_text,
            "citations": citations,
            "abstained": False,
            "model_used": f"{provider.provider_name}/{provider.model_name}"
        }

    def _synthesize_grounded_fallback(
        self,
        question: str,
        product_version: str,
        product_name: str,
        chunks: List[Dict[str, Any]]
    ) -> str:
        """Backward-compatible helper for deterministic extractive fallback synthesis."""
        return synthesize_grounded_fallback(question, product_version, product_name, chunks)

    # --------------------------------------------------------------------------
    # SQLite Conversation History Storage
    # --------------------------------------------------------------------------
    def save_conversation_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        product_version: str,
        rewritten_query: Optional[str] = None,
        citations: Optional[List[CitationItem]] = None,
        abstained: bool = False
    ) -> None:
        """Persist a message into the SQLite conversation_messages table."""
        try:
            citations_json = json.dumps([c.model_dump() for c in (citations or [])])
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO conversation_messages 
                    (conversation_id, role, content, product_version, rewritten_query, citations_json, abstained)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conversation_id,
                        role,
                        content,
                        product_version,
                        rewritten_query,
                        citations_json,
                        1 if abstained else 0
                    )
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Error saving conversation message to SQLite: {e}")

    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch recent message history for a conversation thread."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, conversation_id, role, content, product_version, rewritten_query,
                           citations_json, abstained, created_at
                    FROM conversation_messages
                    WHERE conversation_id = ?
                    ORDER BY id ASC
                    LIMIT ?
                    """,
                    (conversation_id, limit)
                )
                rows = cursor.fetchall()
                history = []
                for r in rows:
                    citations = []
                    if r["citations_json"]:
                        try:
                            citations = json.loads(r["citations_json"])
                        except Exception:
                            citations = []
                    history.append({
                        "id": r["id"],
                        "conversation_id": r["conversation_id"],
                        "role": r["role"],
                        "content": r["content"],
                        "product_version": r["product_version"],
                        "rewritten_query": r["rewritten_query"],
                        "citations": citations,
                        "abstained": bool(r["abstained"]),
                        "created_at": str(r["created_at"])
                    })
                return history
        except Exception as e:
            logger.warning(f"Error fetching conversation history for {conversation_id}: {e}")
            return []


# Global generator instance
grounded_generator = GroundedAnswerGenerator()
