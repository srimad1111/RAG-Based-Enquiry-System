"""
Local Ollama LLM Provider.
Implements BaseLLMProvider communicating with local Ollama daemon over HTTP REST API.
Includes robust error handling, connection timeout management, and deterministic fallback.
"""
import json
from typing import Any, Dict, List, Optional
import requests

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


class OllamaProvider(BaseLLMProvider):
    """
    Local Ollama Provider for Query Rewriting and Grounded Answer Generation.
    Communicates via Ollama's REST API (default http://localhost:11434).
    Falls back gracefully to heuristic/extractive synthesis if Ollama is offline or model is missing.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        self._model_name = model_name or settings.OLLAMA_MODEL
        self._base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._timeout = timeout or settings.OLLAMA_TIMEOUT

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def base_url(self) -> str:
        return self._base_url

    def rewrite_query(
        self,
        customer_question: str,
        product_name: str = "NexaDesk",
        product_version: str = "v3.0"
    ) -> Dict[str, Any]:
        """
        Rewrite customer question using local Ollama model with structured JSON formatting.
        Falls back to heuristic rewriter if Ollama is unreachable.
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

        system_prompt = build_query_rewrite_system_prompt(product_name, product_version)
        payload = {
            "model": self._model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Customer Question: \"{clean_q}\"\nTarget Version: {product_version}"}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }

        try:
            url = f"{self._base_url}/api/chat"
            response = requests.post(url, json=payload, timeout=self._timeout)
            if response.status_code == 200:
                res_data = response.json()
                msg_content = res_data.get("message", {}).get("content", "").strip()

                # Clean optional markdown ticks
                if msg_content.startswith("```json"):
                    msg_content = msg_content[7:]
                if msg_content.startswith("```"):
                    msg_content = msg_content[3:]
                if msg_content.endswith("```"):
                    msg_content = msg_content[:-3]
                msg_content = msg_content.strip()

                parsed = json.loads(msg_content)
                return {
                    "original_query": clean_q,
                    "rewritten_query": parsed.get("rewritten_query", clean_q),
                    "search_keywords": parsed.get("search_keywords", []),
                    "intent": parsed.get("intent", "product_inquiry"),
                    "rewriter_used": f"ollama/{self._model_name}",
                    "reasoning": parsed.get("reasoning", f"Rewritten via local Ollama ({self._model_name})")
                }
            else:
                logger.warning(
                    f"Ollama API returned HTTP {response.status_code}: {response.text[:200]}. "
                    "Falling back to heuristic rewriter."
                )
        except requests.exceptions.ConnectionError:
            logger.info(
                f"Ollama service offline at {self._base_url}. "
                "Using heuristic query rewriter."
            )
        except requests.exceptions.Timeout:
            logger.warning(
                f"Ollama request timed out after {self._timeout}s at {self._base_url}. "
                "Using heuristic query rewriter."
            )
        except Exception as e:
            logger.warning(f"Ollama query rewrite error: {e}. Using heuristic query rewriter.")

        return heuristic_rewrite(
            clean_q,
            product_name,
            product_version,
            provider_note=f"ollama_fallback_{self._model_name}"
        )

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
        Generate grounded answer using local Ollama model with context injection.
        Falls back to extractive synthesis if Ollama is unreachable.
        """
        if not chunks:
            return synthesize_grounded_fallback(question, product_version, product_name, chunks)

        system_prompt = build_answer_generation_system_prompt(product_name, product_version)
        context_block = format_retrieved_context(chunks)

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for h in history[-4:]:
                role = "user" if h.get("role") == "user" else "assistant"
                content = h.get("content", "").strip()
                if content:
                    messages.append({"role": role, "content": content})

        user_content = (
            f"DOCUMENTATION CONTEXT:\n{context_block}\n\n"
            f"CUSTOMER QUESTION:\n{question.strip()}\n\n"
            "Please provide a helpful, step-by-step response citing sources [Doc: ..., Section: ..., Page: ...]."
        )
        messages.append({"role": "user", "content": user_content})

        payload = {
            "model": self._model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        try:
            url = f"{self._base_url}/api/chat"
            response = requests.post(url, json=payload, timeout=self._timeout)
            if response.status_code == 200:
                res_data = response.json()
                content = res_data.get("message", {}).get("content", "").strip()
                if content:
                    return content
            else:
                logger.warning(
                    f"Ollama API returned HTTP {response.status_code}: {response.text[:200]}. "
                    "Using grounded fallback synthesis."
                )
        except requests.exceptions.ConnectionError:
            logger.info(
                f"Ollama service offline at {self._base_url}. "
                "Using grounded extractive fallback engine."
            )
        except requests.exceptions.Timeout:
            logger.warning(
                f"Ollama answer generation timed out after {self._timeout}s at {self._base_url}. "
                "Using grounded fallback synthesis."
            )
        except Exception as e:
            logger.warning(f"Ollama answer generation error: {e}. Using grounded fallback synthesis.")

        return synthesize_grounded_fallback(question, product_version, product_name, chunks)

    def check_health(self) -> Dict[str, Any]:
        """Probes local Ollama /api/tags endpoint to check daemon availability and available models."""
        try:
            url = f"{self._base_url}/api/tags"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name") for m in data.get("models", [])]
                has_model = any(self._model_name in m for m in models)
                return {
                    "provider": self.provider_name,
                    "model": self.model_name,
                    "base_url": self._base_url,
                    "status": "ready" if has_model else "model_missing",
                    "available": True,
                    "installed_models": models,
                    "message": f"Ollama daemon online. Model '{self._model_name}' {'is ready' if has_model else 'needs to be pulled (run: ollama pull ' + self._model_name + ')'}."
                }
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "base_url": self._base_url,
                "status": f"http_{response.status_code}",
                "available": False,
                "message": f"Ollama returned HTTP status {response.status_code}."
            }
        except requests.exceptions.ConnectionError:
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "base_url": self._base_url,
                "status": "offline",
                "available": False,
                "message": f"Ollama daemon is offline at {self._base_url}. Start it via `ollama serve` if you wish to use local models."
            }
        except Exception as e:
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "base_url": self._base_url,
                "status": "error",
                "available": False,
                "message": f"Ollama health check error: {str(e)}"
            }

