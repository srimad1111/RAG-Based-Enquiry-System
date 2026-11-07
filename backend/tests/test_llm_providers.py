"""
Tests for Interchangeable LLM Providers (Gemini & Ollama).
Validates:
  1. BaseLLMProvider contract adherence.
  2. GeminiProvider query rewriting and grounded answer generation (with fallback).
  3. OllamaProvider handling of offline daemon, timeouts, and mocked responses.
  4. Provider factory resolution via LLM_PROVIDER environment variable.
  5. Exact schema and response parity across providers.
  6. Health check diagnostics.
"""
import json
from unittest.mock import MagicMock, patch
import pytest

from app.core.config import get_settings
from app.rag.providers.base import BaseLLMProvider
from app.rag.providers.factory import get_llm_provider, list_available_providers
from app.rag.providers.gemini_provider import GeminiProvider
from app.rag.providers.ollama_provider import OllamaProvider
from app.rag.pipeline import rag_pipeline

settings = get_settings()

MOCK_CHUNKS = [
    {
        "document_name": "reporting_and_exports.md",
        "document_type": "markdown",
        "product_version": "v1.0",
        "section_title": "Manual Report Exports in v1.0",
        "page_number": 1,
        "chunk_id": "chunk_v1_001",
        "text_content": "NexaDesk v1.0 supports manual report exports to CSV and PDF formats from the Admin Analytics tab. Scheduled exports are not supported in v1.0.",
        "rrf_score": 0.85
    }
]


def test_gemini_provider_interface_and_properties():
    """Verify GeminiProvider adheres to BaseLLMProvider contract and returns proper properties."""
    provider = GeminiProvider()
    assert isinstance(provider, BaseLLMProvider)
    assert provider.provider_name == "gemini"
    assert provider.model_name == settings.GEMINI_MODEL

    health = provider.check_health()
    assert health["provider"] == "gemini"
    assert "status" in health
    assert "configured" in health


def test_gemini_provider_rewriting_and_generation_fallback():
    """Verify GeminiProvider handles query rewriting and answer generation with valid fallback."""
    provider = GeminiProvider()

    # Rewrite
    rewrite_res = provider.rewrite_query(
        customer_question="Why can't I schedule my reports like before?",
        product_name="NexaDesk",
        product_version="v1.0"
    )
    assert "original_query" in rewrite_res
    assert "rewritten_query" in rewrite_res
    assert "search_keywords" in rewrite_res
    assert "intent" in rewrite_res
    assert "rewriter_used" in rewrite_res
    assert "reasoning" in rewrite_res
    assert isinstance(rewrite_res["search_keywords"], list)

    # Generate answer
    answer = provider.generate_answer(
        question="How do I export reports in NexaDesk?",
        product_version="v1.0",
        product_name="NexaDesk",
        chunks=MOCK_CHUNKS
    )
    assert isinstance(answer, str)
    assert len(answer) > 20
    assert "[Doc: reporting_and_exports.md" in answer


def test_ollama_provider_interface_and_offline_resilience():
    """Verify OllamaProvider handles offline status gracefully without crashing."""
    provider = OllamaProvider(base_url="http://127.0.0.1:99999", timeout=1)  # invalid port
    assert isinstance(provider, BaseLLMProvider)
    assert provider.provider_name == "ollama"
    assert provider.model_name == settings.OLLAMA_MODEL

    # Health check on offline daemon
    health = provider.check_health()
    assert health["provider"] == "ollama"
    assert health["available"] is False
    assert health["status"] in ["offline", "error"]

    # Rewrite on offline daemon must fall back seamlessly
    rewrite_res = provider.rewrite_query(
        customer_question="How do I configure SLA breach policies?",
        product_name="NexaDesk",
        product_version="v2.0"
    )
    assert "rewritten_query" in rewrite_res
    assert "search_keywords" in rewrite_res
    assert "intent" in rewrite_res
    assert "ollama_fallback" in rewrite_res["rewriter_used"]

    # Generate answer on offline daemon must fall back seamlessly
    answer = provider.generate_answer(
        question="How do I export reports?",
        product_version="v1.0",
        product_name="NexaDesk",
        chunks=MOCK_CHUNKS
    )
    assert isinstance(answer, str)
    assert "Manual Report Exports in v1.0" in answer
    assert "[Doc: reporting_and_exports.md" in answer


def test_ollama_provider_mocked_success():
    """Verify OllamaProvider correctly parses Ollama REST JSON responses when daemon is online."""
    provider = OllamaProvider(base_url="http://localhost:11434")

    # Mock successful query rewrite chat response
    mock_rewrite_response = MagicMock()
    mock_rewrite_response.status_code = 200
    mock_rewrite_response.json.return_value = {
        "model": "llama3",
        "message": {
            "role": "assistant",
            "content": json.dumps({
                "rewritten_query": "Manual CSV and PDF export procedures in NexaDesk v1.0",
                "search_keywords": ["manual", "export", "csv", "pdf"],
                "intent": "reporting_and_exports",
                "reasoning": "Normalized question into formal documentation search query"
            })
        }
    }

    # Mock successful answer generation chat response
    mock_answer_response = MagicMock()
    mock_answer_response.status_code = 200
    mock_answer_response.json.return_value = {
        "model": "llama3",
        "message": {
            "role": "assistant",
            "content": "To export reports in NexaDesk v1.0, navigate to Admin Analytics and select CSV. [Doc: reporting_and_exports.md, Section: Manual Report Exports in v1.0, Page: 1]"
        }
    }

    with patch("requests.post") as mock_post:
        # Test rewrite
        mock_post.return_value = mock_rewrite_response
        rewrite_res = provider.rewrite_query("How to export reports?", "NexaDesk", "v1.0")
        assert rewrite_res["rewriter_used"] == f"ollama/{settings.OLLAMA_MODEL}"
        assert rewrite_res["rewritten_query"] == "Manual CSV and PDF export procedures in NexaDesk v1.0"
        assert "csv" in rewrite_res["search_keywords"]

        # Test answer generation
        mock_post.return_value = mock_answer_response
        answer = provider.generate_answer(
            question="How do I export reports?",
            product_version="v1.0",
            product_name="NexaDesk",
            chunks=MOCK_CHUNKS
        )
        assert "To export reports in NexaDesk v1.0" in answer
        assert "[Doc: reporting_and_exports.md" in answer


def test_provider_factory_resolution_and_parity():
    """Verify provider factory correctly instantiates providers and enforces response parity."""
    gemini = get_llm_provider("gemini")
    ollama = get_llm_provider("ollama")

    assert gemini.provider_name == "gemini"
    assert ollama.provider_name == "ollama"

    # Fallback for unknown provider
    unknown = get_llm_provider("unsupported_provider")
    assert unknown.provider_name == "gemini"

    # Verify response schema parity on query rewriting
    q = "Where can I view active SLA targets?"
    res_gemini = gemini.rewrite_query(q, "NexaDesk", "v2.0")
    res_ollama = ollama.rewrite_query(q, "NexaDesk", "v2.0")

    expected_keys = {"original_query", "rewritten_query", "search_keywords", "intent", "rewriter_used", "reasoning"}
    assert set(res_gemini.keys()) == expected_keys
    assert set(res_ollama.keys()) == expected_keys
    assert isinstance(res_gemini["search_keywords"], list)
    assert isinstance(res_ollama["search_keywords"], list)


def test_list_available_providers():
    """Verify list_available_providers returns diagnostic status for all supported providers."""
    info = list_available_providers()
    assert "active_provider" in info
    assert "providers" in info
    assert "gemini" in info["providers"]
    assert "ollama" in info["providers"]
    assert "status" in info["providers"]["gemini"]
    assert "status" in info["providers"]["ollama"]


def test_end_to_end_pipeline_with_switched_provider():
    """Verify the full RAG pipeline executes seamlessly regardless of active provider."""
    # Run full enquiry pipeline
    result = rag_pipeline.answer_customer_enquiry(
        question="How do report exports work in NexaDesk v1.0?",
        product_version="v1.0",
        top_k=2
    )

    assert "answer" in result
    assert "citations" in result
    assert result["product_version"] == "v1.0"
    assert len(result["citations"]) > 0
    assert result["abstained"] is False
    assert "model_used" in result

