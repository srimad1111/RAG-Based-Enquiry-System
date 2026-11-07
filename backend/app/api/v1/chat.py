"""
Phase 5: Customer Enquiry Chat & Grounded Response Synthesis API.
Provides endpoints for version-grounded conversational enquiries, source citations,
and SQLite conversation thread history.
"""
import sqlite3
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.config import get_settings
from app.core.logging import logger
from app.database.connection import get_sqlite_path
from app.models.schemas import (
    CustomerEnquiryRequest,
    CustomerEnquiryResponse,
    EnquiryHistoryItem,
    EnquiryHistoryResponse,
)
from app.rag.generator import grounded_generator
from app.rag.pipeline import rag_pipeline

settings = get_settings()

router = APIRouter(prefix="/chat", tags=["Customer Enquiry Assistant"])


@router.post(
    "/enquiry",
    response_model=CustomerEnquiryResponse,
    summary="Submit Customer Support Enquiry (Phase 5 Grounded RAG)",
    description=(
        "Executes the full RAG sequence: Query Rewriting -> Version Filtering -> Hybrid Retrieval -> "
        "Grounded LLM Answer Generation with Verifiable Citations and Abstention Guard. "
        "Returns answer, citations, product_version, rewritten_query, retrieved_sources, abstained, conversation_id."
    )
)
def submit_customer_enquiry(payload: CustomerEnquiryRequest) -> CustomerEnquiryResponse:
    try:
        conv_id = payload.conversation_id or payload.session_id

        result = rag_pipeline.answer_customer_enquiry(
            question=payload.question,
            product_version=payload.product_version,
            product_name=payload.product_name,
            conversation_id=conv_id,
            retrieval_mode=payload.retrieval_mode,
            top_k=payload.top_k,
            enable_rewriting=payload.enable_rewriting,
            temperature=payload.temperature,
            api_key=payload.api_key
        )

        return CustomerEnquiryResponse(**result)
    except Exception as e:
        logger.error(f"Error processing customer enquiry '{payload.question}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enquiry processing failed: {str(e)}"
        )


@router.get(
    "/history/{conversation_id}",
    summary="Get Conversation Thread History",
    description="Fetches message history and citations for an ongoing customer conversation thread."
)
def get_conversation_thread(conversation_id: str, limit: int = Query(10, ge=1, le=50)) -> List[Dict[str, Any]]:
    try:
        return grounded_generator.get_conversation_history(conversation_id, limit=limit)
    except Exception as e:
        logger.error(f"Error fetching conversation history for {conversation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve conversation history: {str(e)}"
        )


@router.get(
    "/logs",
    response_model=EnquiryHistoryResponse,
    summary="Get Recent Enquiry Audit Logs",
    description="Fetches recent enquiries stored in SQLite enquiry_logs table for review and evaluation."
)
def get_recent_enquiry_logs(limit: int = Query(20, ge=1, le=100)) -> EnquiryHistoryResponse:
    try:
        db_path = get_sqlite_path()
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, session_id, user_query, product_version, response_text, sources, created_at
                FROM enquiry_logs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            logs: List[EnquiryHistoryItem] = []
            for r in rows:
                sources_count = 0
                if r["sources"]:
                    try:
                        import json
                        sources_list = json.loads(r["sources"])
                        sources_count = len(sources_list)
                    except Exception:
                        sources_count = 0
                logs.append(EnquiryHistoryItem(
                    id=r["id"],
                    session_id=r["session_id"],
                    user_query=r["user_query"],
                    product_version=r["product_version"],
                    response_text=r["response_text"],
                    sources_count=sources_count,
                    created_at=str(r["created_at"])
                ))
            return EnquiryHistoryResponse(total_logs=len(logs), history=logs)
    except Exception as e:
        logger.error(f"Error retrieving enquiry logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve enquiry logs: {str(e)}"
        )


@router.get(
    "/config",
    summary="Get Chat & LLM Engine Configuration",
    description="Returns current LLM model configuration, API key presence, and supported product versions."
)
def get_chat_configuration() -> Dict[str, Any]:
    return {
        "status": "ready",
        "llm_model": settings.GEMINI_MODEL,
        "api_key_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip()),
        "default_version": settings.DEFAULT_PRODUCT_VERSION,
        "supported_versions": settings.SUPPORTED_PRODUCT_VERSIONS,
        "supported_retrieval_modes": ["hybrid", "dense_only", "sparse_only"],
        "fallback_engine": "extractive-grounded-fallback"
    }

