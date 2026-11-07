"""
Phase 4: Query Rewriter Module.
Transforms informal customer questions into precise, documentation-oriented search queries.
Uses Google Gemini API with robust graceful fallback to heuristic technical query synthesis.
"""
import json
import re
from typing import Any, Dict, List, Optional
import google.generativeai as genai

from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

# Common English stop words & conversational fillers to remove during heuristic analysis
CONVERSATIONAL_FILLERS = [
    r"\bwhy\s+can't\s+i\b",
    r"\bwhy\s+cant\s+i\b",
    r"\bhow\s+do\s+i\b",
    r"\bhow\s+can\s+i\b",
    r"\bhow\s+to\b",
    r"\bwhere\s+do\s+i\s+find\b",
    r"\bwhere\s+is\s+the\b",
    r"\bwhere\s+can\s+i\s+see\b",
    r"\bcan\s+i\b",
    r"\bcan\s+we\b",
    r"\bis\s+it\s+possible\s+to\b",
    r"\bwhat\s+is\s+the\s+deal\s+with\b",
    r"\bi\s+am\s+trying\s+to\b",
    r"\bi'm\s+trying\s+to\b",
    r"\bi\s+want\s+to\b",
    r"\bi\s+need\s+to\b",
    r"\bplease\s+help\s+me\s+with\b",
    r"\bcan\s+someone\s+explain\b",
    r"\btell\s+me\s+about\b",
    r"\blike\s+before\b",
    r"\bin\s+my\s+account\b",
    r"\bdoesn't\s+work\b",
    r"\bdoesnt\s+work\b",
    r"\bnot\s+working\b",
]

# Vocabulary mappings from colloquial terms to official documentation terminology
CONCEPT_SYNONYM_MAP = {
    "schedule": "scheduled configuration",
    "scheduling": "scheduled recurring",
    "export": "export functionality",
    "exporting": "export configuration",
    "reports": "report exports",
    "report": "reporting and metrics",
    "price": "pricing plans",
    "pricing": "subscription pricing plans",
    "cost": "billing and pricing",
    "how much": "subscription fees and quotas",
    "discount": "annual billing discount",
    "quota": "ticket quotas and limits",
    "limits": "quota limits",
    "sla": "SLA policy and breach targets",
    "deadline": "first response SLA targets",
    "breach": "SLA breach rules",
    "ticket": "ticket management",
    "tickets": "ticket management and lifecycle",
    "assign": "ticket assignment rules",
    "routing": "automated ticket routing",
    "round robin": "round-robin distribution",
    "roles": "user roles and permissions",
    "role": "role-based access control",
    "permissions": "permission matrix and RBAC",
    "admin": "administrator role capabilities",
    "agent": "support agent permissions",
    "slack": "Slack integration and webhooks",
    "teams": "Microsoft Teams webhook notifications",
    "webhook": "webhook configuration",
    "ai": "AI Copilot capabilities",
    "copilot": "AI Copilot and smart assistance",
    "nexaflow": "NexaFlow Workflow Studio",
    "automation": "automation rules and triggers",
    "sso": "Enterprise SAML SSO authentication",
}


class GeminiQueryRewriter:
    """
    Transforms conversational customer questions into technical search queries
    optimized for documentation vector and lexical retrieval.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.GEMINI_MODEL
        self._gemini_client_configured = False
        self._init_gemini()

    def _init_gemini(self) -> None:
        """Configure Gemini client if API key is present."""
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY.strip())
                self._gemini_client_configured = True
                logger.info(f"Gemini API configured with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini client: {e}")
                self._gemini_client_configured = False
        else:
            logger.info("No GEMINI_API_KEY found; query rewriter will use technical heuristic fallback mode.")
            self._gemini_client_configured = False

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
          - rewriter_used ('gemini-1.5-flash' or 'heuristic_fallback')
          - reasoning
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

        # Try Gemini API if configured
        if self._gemini_client_configured:
            try:
                return self._gemini_rewrite(clean_q, product_name, product_version)
            except Exception as e:
                logger.warning(f"Gemini API query rewriting failed: {e}. Falling back to heuristic rewriter.")

        # Fallback to intelligent technical heuristic rewriter
        return self._heuristic_rewrite(clean_q, product_name, product_version)

    def _gemini_rewrite(
        self,
        question: str,
        product_name: str,
        product_version: str
    ) -> Dict[str, Any]:
        """Execute query rewriting via Gemini API with structured JSON output."""
        system_prompt = (
            f"You are a technical documentation query specialist for '{product_name}' (Target Version: {product_version}). "
            "Your task is to transform informal, colloquial, confused, or conversational customer support inquiries "
            "into formal, documentation-oriented search queries suitable for dense vector and BM25 search.\n\n"
            "STRICT RULES:\n"
            "1. Preserve the user's core intent faithfully.\n"
            "2. Convert conversational phrasing ('Why can't I schedule my reports like before?') into official documentation terms ('Scheduled report export functionality, configuration and availability').\n"
            "3. Extract key technical keywords and entities.\n"
            "4. NEVER invent or hallucinate product features not implied by the question.\n"
            "5. Return ONLY a valid JSON object with the following schema, and no extra prose:\n"
            "{\n"
            '  "rewritten_query": "string",\n'
            '  "search_keywords": ["keyword1", "keyword2", "keyword3"],\n'
            '  "intent": "string",\n'
            '  "reasoning": "string"\n'
            "}"
        )

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
        )

        user_content = f"Customer Question: \"{question}\"\nTarget Version: {product_version}"
        response = model.generate_content([system_prompt, user_content])
        response_text = response.text.strip()

        # Clean potential markdown wrapping
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        data = json.loads(response_text)
        return {
            "original_query": question,
            "rewritten_query": data.get("rewritten_query", question),
            "search_keywords": data.get("search_keywords", []),
            "intent": data.get("intent", "product_inquiry"),
            "rewriter_used": self.model_name,
            "reasoning": data.get("reasoning", "Rewritten via Gemini API")
        }

    def _heuristic_rewrite(
        self,
        question: str,
        product_name: str,
        product_version: str
    ) -> Dict[str, Any]:
        """
        High-quality heuristic technical query rewriter.
        Strips conversational filler, canonicalizes synonyms to documentation vocabulary,
        and constructs high-precision documentation search terms.
        """
        text = question.strip()

        # 1. Strip conversational fillers
        clean_text = text
        for pattern in CONVERSATIONAL_FILLERS:
            clean_text = re.sub(pattern, "", clean_text, flags=re.IGNORECASE).strip()

        # Remove trailing question marks and punctuation
        clean_text = re.sub(r"[?!.,;]+$", "", clean_text).strip()

        # 2. Extract words and map concept synonyms
        words = re.findall(r"\b[a-zA-Z0-9_\-]+\b", clean_text.lower())
        mapped_terms: List[str] = []
        keywords: List[str] = []

        seen_terms = set()
        for w in words:
            if w in CONCEPT_SYNONYM_MAP:
                term = CONCEPT_SYNONYM_MAP[w]
                if term not in seen_terms:
                    mapped_terms.append(term)
                    seen_terms.add(term)
            elif len(w) > 3 and w not in ["with", "that", "this", "from", "have", "been", "will", "would"]:
                if w not in seen_terms:
                    mapped_terms.append(w)
                    seen_terms.add(w)

        # 3. Determine primary domain intent
        intent = "general_documentation_query"
        lower_q = question.lower()
        if "export" in lower_q or "report" in lower_q or "schedule" in lower_q:
            intent = "reporting_and_exports"
        elif "price" in lower_q or "plan" in lower_q or "cost" in lower_q or "quota" in lower_q or "tier" in lower_q:
            intent = "pricing_and_plans"
        elif "role" in lower_q or "permission" in lower_q or "admin" in lower_q or "agent" in lower_q or "rbac" in lower_q:
            intent = "user_roles_and_permissions"
        elif "sla" in lower_q or "breach" in lower_q or "policy" in lower_q:
            intent = "sla_and_policies"
        elif "routing" in lower_q or "round robin" in lower_q or "assign" in lower_q:
            intent = "ticket_routing_rules"
        elif "ai" in lower_q or "copilot" in lower_q or "nexaflow" in lower_q:
            intent = "ai_and_automation"

        # 4. Synthesize rewritten documentation-style query
        if mapped_terms:
            rewritten_query = " ".join(mapped_terms).capitalize() + f" in {product_name} {product_version}"
        else:
            rewritten_query = clean_text.capitalize() + f" documentation {product_version}"

        # 5. Extract distinctive keywords
        for term in mapped_terms:
            for token in re.findall(r"\b[a-zA-Z0-9_\-]+\b", term):
                if len(token) > 2 and token.lower() not in keywords:
                    keywords.append(token.lower())

        return {
            "original_query": question,
            "rewritten_query": rewritten_query,
            "search_keywords": keywords[:8],
            "intent": intent,
            "rewriter_used": "heuristic_fallback",
            "reasoning": f"Heuristic NLP rewriter applied: conversational syntax normalized to formal {intent} documentation terms."
        }


# Global instance
query_rewriter = GeminiQueryRewriter()

