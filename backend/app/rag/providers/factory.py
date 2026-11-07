"""
LLM Provider Factory.
Instantiates and manages interchangeable LLM providers (Gemini, Ollama).
Supports runtime provider resolution based on configuration or explicit request.
"""
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.core.logging import logger
from app.rag.providers.base import BaseLLMProvider
from app.rag.providers.gemini_provider import GeminiProvider
from app.rag.providers.ollama_provider import OllamaProvider

settings = get_settings()

_PROVIDER_INSTANCES: Dict[str, BaseLLMProvider] = {}


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """
    Retrieve or initialize the active LLM provider.
    Priority:
      1. Explicit provider_name argument ('gemini' or 'ollama')
      2. Environment variable settings.LLM_PROVIDER ('gemini' or 'ollama')
      3. Default fallback to 'gemini'
    """
    resolved_name = (provider_name or settings.LLM_PROVIDER or "gemini").lower().strip()

    if resolved_name == "ollama":
        if "ollama" not in _PROVIDER_INSTANCES:
            logger.info(f"Instantiating OllamaProvider (Model: {settings.OLLAMA_MODEL}, Base URL: {settings.OLLAMA_BASE_URL})")
            _PROVIDER_INSTANCES["ollama"] = OllamaProvider()
        return _PROVIDER_INSTANCES["ollama"]

    elif resolved_name == "gemini":
        if "gemini" not in _PROVIDER_INSTANCES:
            logger.info(f"Instantiating GeminiProvider (Model: {settings.GEMINI_MODEL})")
            _PROVIDER_INSTANCES["gemini"] = GeminiProvider()
        return _PROVIDER_INSTANCES["gemini"]

    else:
        logger.warning(f"Unknown LLM provider '{resolved_name}'. Falling back to 'gemini'.")
        if "gemini" not in _PROVIDER_INSTANCES:
            _PROVIDER_INSTANCES["gemini"] = GeminiProvider()
        return _PROVIDER_INSTANCES["gemini"]


def list_available_providers() -> Dict[str, Any]:
    """
    Returns diagnostic health and configuration status for all supported providers.
    """
    active_name = (settings.LLM_PROVIDER or "gemini").lower().strip()
    gemini_prov = GeminiProvider()
    ollama_prov = OllamaProvider()

    return {
        "active_provider": active_name,
        "providers": {
            "gemini": gemini_prov.check_health(),
            "ollama": ollama_prov.check_health()
        }
    }

