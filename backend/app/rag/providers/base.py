"""
Common LLM Provider Interface.
Defines the contract for interchangeable LLM providers (Gemini, Ollama, etc.)
supporting Query Rewriting and Grounded Answer Generation.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers in the NexaDesk RAG pipeline.
    Ensures identical response structures across both cloud (Gemini) and local (Ollama) providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'gemini', 'ollama')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Active model identifier (e.g. 'gemini-1.5-flash', 'llama3')."""
        pass

    @abstractmethod
    def rewrite_query(
        self,
        customer_question: str,
        product_name: str = "NexaDesk",
        product_version: str = "v3.0"
    ) -> Dict[str, Any]:
        """
        Transform an informal customer question into a documentation-oriented query.
        Returns a dictionary with:
          - original_query: str
          - rewritten_query: str
          - search_keywords: List[str]
          - intent: str
          - rewriter_used: str
          - reasoning: str
        """
        pass

    @abstractmethod
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
        Generate a strictly grounded customer support answer using retrieved documentation context.
        Must include verifiable source citations and adhere to strict version boundaries.
        Returns the synthesized answer text.
        """
        pass

    @abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """
        Verify connectivity and status of the LLM provider.
        Returns diagnostic information.
        """
        pass

