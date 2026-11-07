"""
Google Gemini LLM Provider.
Implements BaseLLMProvider using Google Gemini API with fallback to heuristic NLP synthesis.
"""
import json
from typing import Any, Dict, List, Optional
import google.generativeai as genai

from app.core.config import get_settings
from app.core.logging import logger
from app.rag.providers.base import BaseLLMProvider
from app.rag.providers.common import (
    build_answer_generation_system_prompt,
    build_query_rewrite_system_prompt,
    format_retrieved_context,
    heuristic_rewrite,
    synthesize_grounded_fallback,
)

settings = get_settings()


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini Provider for Query Rewriting and Grounded Answer Generation.
    Falls back gracefully to heuristic/extractive methods when API key is missing or calls fail.
    """

    def __init__(self, model_name: Optional[str] = None):
        self._model_name = model_name or settings.GEMINI_MODEL
        self._client_configured = False
        self._init_client()

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def _init_client(self, custom_api_key: Optional[str] = None) -> None:
        key = custom_api_key or settings.GEMINI_API_KEY
        if key and key.strip():
            try:
                genai.configure(api_key=key.strip())
                self._client_configured = True
                logger.info(f"GeminiProvider initialized with model: {self._model_name}")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini client: {e}")
                self._client_configured = False
        else:
            self._client_configured = False
            logger.info("No GEMINI_API_KEY provided; GeminiProvider will use heuristic fallback mode.")

    def rewrite_query(
        self,
        customer_question: str,
        product_name: str = "NexaDesk",
        product_version: str = "v3.0"
    ) -> Dict[str, Any]:
        """
        Rewrite conversational customer questions into technical queries via Gemini.
        Falls back to heuristic rewriter if unavailable or on error.
        """
        clean_q = customer_question.strip()
        if not clean_q:
            return {
                "original_query": "",
                "rewritten_query": "",
                "search_keywords": [],
                "intent": "general_inquiry",
                "rewriter_used": "none",
                "reasoning": "Empty query"
            }

        if self._client_configured:
            try:
                system_prompt = build_query_rewrite_system_prompt(product_name, product_version)
                model = genai.GenerativeModel(
                    model_name=self._model_name,
                    generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
                )
                user_content = f"Customer Question: \"{clean_q}\"\nTarget Version: {product_version}"
                response = model.generate_content([system_prompt, user_content])
                response_text = response.text.strip()

                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                data = json.loads(response_text)
                return {
                    "original_query": clean_q,
                    "rewritten_query": data.get("rewritten_query", clean_q),
                    "search_keywords": data.get("search_keywords", []),
                    "intent": data.get("intent", "product_inquiry"),
                    "rewriter_used": self._model_name,
                    "reasoning": data.get("reasoning", "Rewritten via Gemini API")
                }
            except Exception as e:
                logger.warning(f"Gemini query rewriting error: {e}. Falling back to heuristic rewriter.")

        return heuristic_rewrite(clean_q, product_name, product_version, provider_note="heuristic_fallback")

    def generate_answer(
        self,
        question: str,
        product_version: str,
        product_name: str,
        chunks: List[Dict[str, Any]],
        history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1,
        custom_api_key: Optional[str] = None
    ) -> str:
        """
        Synthesize grounded support answer via Gemini API with strict citations.
        Falls back to extractive synthesis if Gemini is unconfigured or fails.
        """
        if custom_api_key:
            self._init_client(custom_api_key)

        if self._client_configured and chunks:
            try:
                system_prompt = build_answer_generation_system_prompt(product_name, product_version)
                context_block = format_retrieved_context(chunks)

                history_lines = []
                if history:
                    for h in history[-4:]:
                        role = "Customer" if h.get("role") == "user" else "Assistant"
                        content = h.get("content", "").strip()
                        history_lines.append(f"{role}: {content}")
                history_text = "\n".join(history_lines) if history_lines else "None (New conversation)"

                prompt = (
                    f"{system_prompt}\n\n"
                    f"================ RECENT CONVERSATION HISTORY ================\n"
                    f"{history_text}\n\n"
                    f"================ RETRIEVED DOCUMENTATION CONTEXT ================\n"
                    f"{context_block}\n\n"
                    f"================ CURRENT CUSTOMER QUESTION ================\n"
                    f"Question: {question.strip()}\n\n"
                    f"Official Grounded Support Answer:"
                )

                model = genai.GenerativeModel(
                    model_name=self._model_name,
                    generation_config={"temperature": temperature}
                )
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini answer generation error: {e}. Falling back to grounded fallback engine.")

        return synthesize_grounded_fallback(question, product_version, product_name, chunks)

    def check_health(self) -> Dict[str, Any]:
        """Health diagnostics for Gemini provider."""
        has_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "configured": has_key,
            "client_ready": self._client_configured,
            "status": "ready" if self._client_configured else "fallback_mode",
            "message": "Gemini API active" if self._client_configured else "Gemini API key not configured, operating in heuristic fallback mode."
        }
