"""
Phase 5: Grounded Answer Generator with Citations and Version Safety.
Integrates Query Rewriting, Hybrid Retrieval, and Google Gemini API (with deterministic fallback).
Enforces strict multi-version isolation, hallucination abstention, and verifiable source citations.
"""
import json
import re
import sqlite3
import uuid
from typing import Any, Dict, List, Optional, Tuple
import google.generativeai as genai

from app.core.config import get_settings
from app.core.logging import logger
from app.database.connection import get_sqlite_path
from app.models.schemas import CitationItem

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
      - Google Gemini API integration with offline extractive fallback synthesizer.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.GEMINI_MODEL
        self.db_path = get_sqlite_path()
        self._init_gemini()

    def _init_gemini(self) -> None:
        """Initialize Google Gemini client if API key is present."""
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY.strip())
                self._gemini_available = True
                logger.info(f"Gemini Answer Generator initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Could not configure Gemini client: {e}")
                self._gemini_available = False
        else:
            self._gemini_available = False
            logger.info("No GEMINI_API_KEY configured; Generator will use grounded extractive fallback engine.")

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
            return False, f"Retrieved documentation evidence falls below confidence threshold."

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
            # Clean snippet for citation
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

        # Step 3: Check for Gemini API availability (global or custom)
        api_key_to_use = custom_api_key or settings.GEMINI_API_KEY
        if api_key_to_use and api_key_to_use.strip():
            try:
                genai.configure(api_key=api_key_to_use.strip())
                answer_text = self._generate_with_gemini(
                    question=question,
                    product_version=product_version,
                    product_name=product_name,
                    chunks=retrieved_chunks,
                    history=conversation_history,
                    temperature=temperature
                )
                return {
                    "answer": answer_text,
                    "citations": citations,
                    "abstained": False,
                    "model_used": self.model_name
                }
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Utilizing deterministic grounded fallback synthesizer.")

        # Step 4: Deterministic Grounded Fallback Synthesizer
        fallback_answer = self._synthesize_grounded_fallback(
            question=question,
            product_version=product_version,
            product_name=product_name,
            chunks=retrieved_chunks
        )
        return {
            "answer": fallback_answer,
            "citations": citations,
            "abstained": False,
            "model_used": "extractive-grounded-fallback"
        }

    # --------------------------------------------------------------------------
    # Gemini LLM Generation Engine
    # --------------------------------------------------------------------------
    def _generate_with_gemini(
        self,
        question: str,
        product_version: str,
        product_name: str,
        chunks: List[Dict[str, Any]],
        history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> str:
        """Call Gemini API with strict system instructions and context grounding."""
        # Format context with explicit source markers
        context_blocks = []
        for idx, c in enumerate(chunks, start=1):
            block = (
                f"[Source {idx}]\n"
                f"Document: {c['document_name']} ({c['document_type'].upper()})\n"
                f"Version: {c['product_version']}\n"
                f"Section: {c['section_title']}\n"
                f"Page: {c['page_number']}\n"
                f"Content:\n{c['text_content'].strip()}\n"
            )
            context_blocks.append(block)
        formatted_context = "\n----------------------------------------\n".join(context_blocks)

        system_instruction = (
            f"You are the official customer support assistant for {product_name} (Target Product Version: {product_version}).\n\n"
            "STRICT GROUNDING & ANSWERING RULES:\n"
            f"1. Answer the customer's question using ONLY the retrieved {product_version} documentation context provided below.\n"
            f"2. Strict Version Boundaries: The user has selected {product_name} {product_version}. Never assume or borrow features, pricing, or settings from other versions (e.g. do not discuss v2.0 scheduled exports or v3.0 AI Copilot when answering for v1.0).\n"
            "3. Tone: Clear, friendly, simple, and helpful. Avoid unnecessary jargon.\n"
            "4. Use step-by-step numbered steps where explaining procedures.\n"
            "5. In-Text Citations: At the end of relevant points or instructions, include citation references matching the source, e.g. [Doc: <doc_name>, Section: <section>, Page: <page>].\n"
            "6. Hallucination Refusal: If the provided documentation context does not contain enough information to answer the question, state: "
            f"\"I cannot find verified information regarding this in the available NexaDesk {product_version} documentation. Please contact our support team for assistance.\"\n"
            "7. Do NOT answer questions using external knowledge outside the provided context."
        )

        user_prompt = f"DOCUMENTATION CONTEXT:\n{formatted_context}\n\nCUSTOMER QUESTION:\n{question}\n\nSUPPORT ANSWER:"

        # Include prior conversation context if present
        messages_payload = [system_instruction]
        if history:
            history_summary = "\n".join([f"{m.get('role', 'user').capitalize()}: {m.get('content', '')}" for m in history[-4:]])
            messages_payload.append(f"PREVIOUS CONVERSATION HISTORY:\n{history_summary}\n")

        messages_payload.append(user_prompt)

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"temperature": temperature}
        )
        response = model.generate_content(messages_payload)
        return response.text.strip()

    # --------------------------------------------------------------------------
    # Deterministic Grounded Fallback Synthesizer
    # --------------------------------------------------------------------------
    def _synthesize_grounded_fallback(
        self,
        question: str,
        product_version: str,
        product_name: str,
        chunks: List[Dict[str, Any]]
    ) -> str:
        """
        High-quality extractive response synthesizer for offline environments.
        Synthesizes a customer-friendly, step-by-step or explanatory response
        directly from the actual top retrieved document chunks with verifiable citations.
        """
        if not chunks:
            return ABSTENTION_MESSAGE_TEMPLATE.format(product_version=product_version)

        top_chunk = chunks[0]
        doc_name = top_chunk["document_name"]
        section = top_chunk["section_title"]
        page = top_chunk["page_number"]
        content = top_chunk["text_content"].strip()
        citation_tag = f"[Doc: {doc_name}, Section: {section}, Page: {page}]"

        # Split content into logical points
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        response_lines = [
            f"According to the **{product_name} {product_version}** documentation regarding *{section}*:\n"
        ]

        # Extract factual statements directly from chunk content
        extracted_points = []
        for p in paragraphs:
            # Clean Markdown heading markers if any
            clean_p = re.sub(r"^#+\s*", "", p)
            if clean_p.lower().startswith("nexadesk") or "support" in clean_p.lower() or "tier" in clean_p.lower() or "feature" in clean_p.lower():
                extracted_points.append(clean_p)
            elif any(clean_p.startswith(prefix) for prefix in ["1.", "2.", "3.", "-", "*"]):
                extracted_points.append(clean_p)

        if not extracted_points:
            extracted_points = paragraphs[:2]

        for pt in extracted_points[:3]:
            response_lines.append(f"{pt}\n")

        # Append source citation
        response_lines.append(f"\n*Source Reference:* {citation_tag}")

        return "\n".join(response_lines).strip()

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
