"""
LLM Providers Package.
Exposes interchangeable LLM implementations for NexaDesk RAG.
"""
from app.rag.providers.base import BaseLLMProvider
from app.rag.providers.common import (
    build_answer_generation_system_prompt,
    build_query_rewrite_system_prompt,
    format_retrieved_context,
    heuristic_rewrite,
    synthesize_grounded_fallback,
)
from app.rag.providers.factory import get_llm_provider, list_available_providers
from app.rag.providers.gemini_provider import GeminiProvider
from app.rag.providers.ollama_provider import OllamaProvider

__all__ = [
    "BaseLLMProvider",
    "GeminiProvider",
    "OllamaProvider",
    "get_llm_provider",
    "list_available_providers",
    "build_query_rewrite_system_prompt",
    "build_answer_generation_system_prompt",
    "format_retrieved_context",
    "heuristic_rewrite",
    "synthesize_grounded_fallback",
]

