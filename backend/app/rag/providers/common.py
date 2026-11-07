"""
Shared Prompts, Fallback Synthesizers & Formatting Utilities.
Ensures zero code duplication between Gemini and Ollama providers.
"""
import re
from typing import Any, Dict, List, Optional

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


def build_query_rewrite_system_prompt(product_name: str, product_version: str) -> str:
    """Standardized system prompt for query rewriting."""
    return (
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


def build_answer_generation_system_prompt(product_name: str, product_version: str) -> str:
    """Standardized system prompt for version-grounded answer generation."""
    return (
        f"You are the official customer support assistant for {product_name} (Target Product Version: {product_version}).\n\n"
        "STRICT GROUNDING & ANSWERING RULES:\n"
        f"1. Answer the customer's question using ONLY the retrieved {product_version} documentation context provided below.\n"
        f"2. Strict Version Boundaries: The user has selected {product_name} {product_version}. Never assume or borrow features, pricing, or settings from other versions (e.g. do not discuss v2.0 scheduled exports or v3.0 AI Copilot when answering for v1.0).\n"
        "3. Tone: Clear, friendly, simple, and helpful. Avoid unnecessary jargon.\n"
        "4. Use step-by-step numbered steps where explaining procedures.\n"
        "5. In-Text Citations: At the end of relevant points or instructions, include citation references matching the source, e.g. [Doc: <doc_name>, Section: <section>, Page: <page>].\n"
        "6. Hallucination Refusal: If the provided documentation context does not contain enough information to answer the question, state: "
        f"\"I cannot find verified information regarding this in the available NexaDesk {product_version} documentation. Please contact our support team for assistance.\"\n"
        "7. Do NOT answer questions using external knowledge outside the provided context."
    )


def format_retrieved_context(chunks: List[Dict[str, Any]]) -> str:
    """Formats retrieved chunks with clear source boundaries for LLM ingestion."""
    blocks = []
    for idx, c in enumerate(chunks, start=1):
        block = (
            f"[Source {idx}]\n"
            f"Document: {c['document_name']} ({c['document_type'].upper()})\n"
            f"Version: {c['product_version']}\n"
            f"Section: {c['section_title']}\n"
            f"Page: {c['page_number']}\n"
            f"Content:\n{c['text_content'].strip()}\n"
        )
        blocks.append(block)
    return "\n----------------------------------------\n".join(blocks)


def heuristic_rewrite(
    question: str,
    product_name: str,
    product_version: str,
    provider_note: str = "heuristic_fallback"
) -> Dict[str, Any]:
    """
    High-quality technical query rewriter for offline resilience or provider fallback.
    Strips conversational filler, canonicalizes synonyms, and extracts domain keywords.
    """
    clean_text = question.strip()
    for pattern in CONVERSATIONAL_FILLERS:
        clean_text = re.sub(pattern, "", clean_text, flags=re.IGNORECASE).strip()

    clean_text = re.sub(r"[?!.,;]+$", "", clean_text).strip()

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

    intent = "general_documentation_query"
    lower_q = question.lower()
    if "export" in lower_q or "report" in lower_q or "schedule" in lower_q:
        intent = "reporting_and_exports"
    elif "price" in lower_q or "plan" in lower_q or "cost" in lower_q or "quota" in lower_q:
        intent = "pricing_and_plans"
    elif "role" in lower_q or "permission" in lower_q or "admin" in lower_q or "agent" in lower_q:
        intent = "user_roles_and_permissions"
    elif "sla" in lower_q or "breach" in lower_q:
        intent = "sla_and_policies"
    elif "routing" in lower_q or "round robin" in lower_q or "assign" in lower_q:
        intent = "ticket_routing_rules"
    elif "ai" in lower_q or "copilot" in lower_q or "nexaflow" in lower_q:
        intent = "ai_and_automation"

    if mapped_terms:
        rewritten_query = " ".join(mapped_terms).capitalize() + f" in {product_name} {product_version}"
    else:
        rewritten_query = clean_text.capitalize() + f" in {product_name} {product_version}"

    for term in mapped_terms:
        for token in re.findall(r"\b[a-zA-Z0-9_\-]+\b", term):
            if len(token) > 2 and token.lower() not in keywords:
                keywords.append(token.lower())

    return {
        "original_query": question,
        "rewritten_query": rewritten_query,
        "search_keywords": keywords[:8],
        "intent": intent,
        "rewriter_used": provider_note,
        "reasoning": f"NLP rewriter applied: conversational syntax normalized to formal {intent} documentation terms."
    }


def synthesize_grounded_fallback(
    question: str,
    product_version: str,
    product_name: str,
    chunks: List[Dict[str, Any]]
) -> str:
    """
    Extractive answer synthesis engine for offline/fallback mode.
    Directly extracts grounded factual statements from retrieved chunks with exact citations.
    """
    if not chunks:
        return (
            f"I cannot find verified information regarding this in the available NexaDesk {product_version} documentation. "
            f"Please contact our support team or check the documentation portal."
        )

    top_chunk = chunks[0]
    doc_name = top_chunk["document_name"]
    section = top_chunk["section_title"]
    page = top_chunk["page_number"]
    content = top_chunk["text_content"].strip()
    citation_tag = f"[Doc: {doc_name}, Section: {section}, Page: {page}]"

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    response_lines = [
        f"According to the **{product_name} {product_version}** documentation regarding *{section}*:\n"
    ]

    extracted_points = []
    for p in paragraphs:
        clean_p = re.sub(r"^#+\s*", "", p)
        if clean_p.lower().startswith("nexadesk") or "support" in clean_p.lower() or "tier" in clean_p.lower() or "feature" in clean_p.lower():
            extracted_points.append(clean_p)
        elif any(clean_p.startswith(prefix) for prefix in ["1.", "2.", "3.", "-", "*"]):
            extracted_points.append(clean_p)

    if not extracted_points:
        extracted_points = paragraphs[:2]

    for pt in extracted_points[:3]:
        response_lines.append(f"{pt}\n")

    response_lines.append(f"\n*Source Reference:* {citation_tag}")
    return "\n".join(response_lines).strip()

