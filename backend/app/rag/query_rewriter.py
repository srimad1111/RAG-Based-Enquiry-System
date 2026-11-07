"""
Phase 4: Query Rewriter Module.
Transforms informal customer questions into precise, documentation-oriented search queries.
Supports interchangeable LLM providers (Google Gemini, Local Ollama) with intelligent fallback.
"""
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.logging import logger
from app.rag.providers.common import (
    CONCEPT_SYNONYM_MAP,
    CONVERSATIONAL_FILLERS,
    heuristic_rewrite,
)
from app.rag.providers.factory import get_llm_provider

settings = get_settings()


class QueryRewriter:
    """
    Transforms conversational customer questions into technical search queries
    optimized for documentation vector and lexical retrieval.
    Delegates to the configured LLM provider (Gemini or Ollama) with graceful fallback.
    """

    def __init__(self, provider_name: Optional[str] = None, model_name: Optional[str] = None):
        self.provider_name = provider_name or settings.LLM_PROVIDER
        self.model_name = model_name or (
            settings.OLLAMA_MODEL if self.provider_name == "ollama" else settings.GEMINI_MODEL
        )
        self.provider = get_llm_provider(self.provider_name)

    def rewrite(
        self,
        customer_question: str,
        product_name: str = "NexaDesk",
        product_version: str = "v3.0"
    ) -> Dict[str, Any]:
        """
        Rewrite an informal customer question into a documentation-oriented query.
        Returns a structured dictionary with:
          - original_query
          - rewritten_query
          - search_keywords
          - intent
          - rewriter_used
          - reasoning
        """
        return self.provider.rewrite_query(
            customer_question=customer_question,
            product_name=product_name,
            product_version=product_version
        )

    def _heuristic_rewrite(
        self,
        question: str,
        product_name: str,
        product_version: str
    ) -> Dict[str, Any]:
        """Backward-compatible helper for deterministic heuristic rewriting."""
        return heuristic_rewrite(
            question,
            product_name,
            product_version,
            provider_note="heuristic_fallback"
        )


# Backward-compatible alias for existing imports
GeminiQueryRewriter = QueryRewriter

# Global singleton instance
query_rewriter = QueryRewriter()
