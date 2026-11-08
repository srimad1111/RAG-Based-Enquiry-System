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
        raw_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        # Normalize localhost to 127.0.0.1 to avoid IPv6 resolution failures on Windows
        if "localhost" in raw_url:
            raw_url = raw_url.replace("localhost", "127.0.0.1")
        self._base_url = raw_url
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
        product_version: str = "v3.0",
        allow_fallback: bool = False
    ) -> Dict[str, Any]:
        """
        Rewrite customer question using local Ollama model (Qwen 3.5 4B) with structured JSON formatting.
        If allow_fallback is False, raises clear RuntimeError on connection error, timeout, or missing model.
        """
        clean_q = customer_question.strip()
        if not clean_q:
            return {
                "original_query": "",
                "rewritten_query": "",
                "search_keywords": [],
                "intent": "general_inquiry",
                "rewriter_used": f"ollama/{self._model_name}",
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
            "think": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 128
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

                try:
                    parsed = json.loads(msg_content)
                except json.JSONDecodeError:
                    import re
                    rq_match = re.search(r'"rewritten_query"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', msg_content)
                    rewritten_val = rq_match.group(1) if rq_match else clean_q
                    kw_match = re.findall(r'"([^"\\]+)"', msg_content)
                    parsed = {
                        "rewritten_query": rewritten_val,
                        "search_keywords": [k for k in kw_match if k not in ("rewritten_query", "search_keywords", "intent", "reasoning")][:5],
                        "intent": "product_inquiry",
                        "reasoning": "Extracted from structured JSON output"
                    }

                logger.info(f"Qwen ({self._model_name}) rewrote query successfully: '{clean_q}' -> '{parsed.get('rewritten_query')}'")
                return {
                    "original_query": clean_q,
                    "rewritten_query": parsed.get("rewritten_query", clean_q),
                    "search_keywords": parsed.get("search_keywords", []),
                    "intent": parsed.get("intent", "product_inquiry"),
                    "rewriter_used": f"ollama/{self._model_name}",
                    "reasoning": parsed.get("reasoning", f"Rewritten via local Ollama ({self._model_name})")
                }
            elif response.status_code == 404:
                err_msg = f"Ollama model '{self._model_name}' not found at {self._base_url}. Please run: ollama pull {self._model_name}"
                logger.error(err_msg)
                if not allow_fallback:
                    raise RuntimeError(err_msg)
            else:
                err_msg = f"Ollama API returned HTTP {response.status_code}: {response.text[:200]}"
                logger.error(err_msg)
                if not allow_fallback:
                    raise RuntimeError(err_msg)
        except requests.exceptions.ConnectionError as e:
            err_msg = f"Ollama daemon is offline at {self._base_url}. Start it via `ollama serve` to enable local inference."
            logger.error(err_msg)
            if not allow_fallback:
                raise RuntimeError(err_msg) from e
        except requests.exceptions.Timeout as e:
            err_msg = f"Ollama request timed out after {self._timeout}s on model '{self._model_name}' at {self._base_url}."
            logger.error(err_msg)
            if not allow_fallback:
                raise RuntimeError(err_msg) from e
        except Exception as e:
            logger.error(f"Ollama query rewrite error: {e}")
            if not allow_fallback:
                raise RuntimeError(f"Ollama query rewrite failed on model '{self._model_name}': {e}") from e

        if not allow_fallback:
            raise RuntimeError(f"Ollama query rewriting failed and fallback is disabled.")

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
        custom_api_key: Optional[str] = None,
        allow_fallback: bool = False
    ) -> str:
        """
        Generate grounded answer using local Ollama model (Qwen 3.5 4B) with context injection.
        If allow_fallback is False, raises clear RuntimeError on connection error, timeout, or missing model.
        """
        if not chunks:
            if not allow_fallback:
                raise RuntimeError("No documentation chunks provided for answer generation.")
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
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": 512
            }
        }

        try:
            url = f"{self._base_url}/api/chat"
            response = requests.post(url, json=payload, timeout=self._timeout)
            if response.status_code == 200:
                res_data = response.json()
                content = res_data.get("message", {}).get("content", "").strip()
                if content:
                    logger.info(f"Qwen ({self._model_name}) generated grounded answer ({len(content)} chars)")
                    return content
            elif response.status_code == 404:
                err_msg = f"Ollama model '{self._model_name}' not found at {self._base_url}. Please run: ollama pull {self._model_name}"
                logger.error(err_msg)
                if not allow_fallback:
                    raise RuntimeError(err_msg)
            else:
                err_msg = f"Ollama API returned HTTP {response.status_code}: {response.text[:200]}"
                logger.error(err_msg)
                if not allow_fallback:
                    raise RuntimeError(err_msg)
        except requests.exceptions.ConnectionError as e:
            err_msg = f"Ollama daemon is offline at {self._base_url}. Start it via `ollama serve` to enable local inference."
            logger.error(err_msg)
            if not allow_fallback:
                raise RuntimeError(err_msg) from e
        except requests.exceptions.Timeout as e:
            err_msg = f"Ollama answer generation timed out after {self._timeout}s on model '{self._model_name}' at {self._base_url}."
            logger.error(err_msg)
            if not allow_fallback:
                raise RuntimeError(err_msg) from e
        except Exception as e:
            logger.error(f"Ollama answer generation error: {e}")
            if not allow_fallback:
                raise RuntimeError(f"Ollama answer generation failed on model '{self._model_name}': {e}") from e

        if not allow_fallback:
            raise RuntimeError(f"Ollama answer generation failed and fallback is disabled.")

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

