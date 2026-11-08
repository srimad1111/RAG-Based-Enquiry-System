"""
Phase 4 Automated Tests: Query Rewriting and Version-Aware Hybrid Retrieval.
Validates:
1. Transformation of informal customer questions into technical queries.
2. Lexical BM25 retrieval partitioned by product version.
3. Dense vs sparse vs hybrid RRF rank fusion.
4. Strict multi-version isolation across v1.0, v2.0, and v3.0.
5. 3-way retrieval strategy comparison (raw dense vs rewritten dense vs rewritten hybrid).
6. Non-existent version safety (transparent refusal, no silent fallback).
"""
import pytest
from app.database.connection import init_database
from app.rag.bm25_retriever import bm25_retriever
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.pipeline import rag_pipeline
from app.rag.query_rewriter import query_rewriter
from app.models.schemas import (
    QueryRewriteRequest,
    HybridRetrievalRequest,
    RetrievalComparisonRequest,
)
from app.api.v1.rag import (
    rewrite_customer_query,
    retrieve_hybrid_context,
    compare_retrieval_strategies,
)


@pytest.fixture(scope="module", autouse=True)
def setup_hybrid_pipeline():
    """Ensure SQLite and vector store indices are ready."""
    init_database()
    rag_pipeline.sync_all_from_sqlite()


def test_query_rewriter_informal_to_technical():
    """
    Test Phase 4 Part A:
    Transforms informal/complaining customer questions into documentation-style queries.
    """
    informal_q = "Why can't I schedule my reports like before?"
    result = query_rewriter.rewrite(
        customer_question=informal_q,
        product_name="NexaDesk",
        product_version="v2.0"
    )

    assert result["original_query"] == informal_q
    assert len(result["rewritten_query"]) > 0
    # Must identify key technical concepts
    rewritten_lower = result["rewritten_query"].lower()
    assert "report" in rewritten_lower or "export" in rewritten_lower
    assert len(result["search_keywords"]) > 0
    assert len(result["intent"]) > 0
    assert (
        result["rewriter_used"] in ["heuristic_fallback", "gemini-1.5-flash"]
        or "ollama" in result["rewriter_used"]
        or "qwen" in result["rewriter_used"]
    )


def test_bm25_retriever_version_isolation():
    """
    Test Phase 4 Part C:
    Verifies that BM25 retrieves chunks strictly from the requested product version.
    """
    # 1. Search v1.0
    res_v1 = bm25_retriever.search("manual export csv", product_version="v1.0", top_k=3)
    assert len(res_v1) > 0
    for chunk in res_v1:
        assert chunk["product_version"] == "v1.0"
        assert chunk["sparse_score"] > 0.0
        assert chunk["retrieval_method"] == "bm25"

    # 2. Search v2.0
    res_v2 = bm25_retriever.search("scheduled recurring exports", product_version="v2.0", top_k=3)
    assert len(res_v2) > 0
    for chunk in res_v2:
        assert chunk["product_version"] == "v2.0"

    # 3. Search v3.0
    res_v3 = bm25_retriever.search("automated ai trigger copilot", product_version="v3.0", top_k=3)
    assert len(res_v3) > 0
    for chunk in res_v3:
        assert chunk["product_version"] == "v3.0"


def test_version_aware_hybrid_retrieval_isolation():
    """
    CRITICAL TEST: Version-Aware Hybrid Retrieval Disambiguation
    Informal Query: 'Why can't I schedule my reports like before?'
    - In v1.0: Must return reporting_and_exports.md (manual exports only).
    - In v2.0: Must return reporting_and_exports.md (scheduled recurring exports).
    - In v3.0: Must return reporting_and_exports.md (AI autonomous exports).
    Guarantees no cross-version leakage in hybrid results.
    """
    customer_q = "Why can't I schedule my reports like before?"

    # Execute for v1.0
    v1_hybrid = rag_pipeline.execute_hybrid_retrieval(
        customer_question=customer_q,
        product_version="v1.0",
        enable_query_rewriting=True,
        retrieval_mode="hybrid",
        top_k=3
    )
    assert v1_hybrid["total_retrieved"] > 0
    assert v1_hybrid["product_version"] == "v1.0"
    for item in v1_hybrid["results"]:
        assert item["product_version"] == "v1.0"
    # Top chunk in v1.0 must reflect manual exports
    top_v1_text = v1_hybrid["results"][0]["text_content"]
    assert "manual" in top_v1_text.lower()
    assert "v1.0" in top_v1_text or "csv" in top_v1_text.lower()

    # Execute for v2.0
    v2_hybrid = rag_pipeline.execute_hybrid_retrieval(
        customer_question=customer_q,
        product_version="v2.0",
        enable_query_rewriting=True,
        retrieval_mode="hybrid",
        top_k=3
    )
    assert v2_hybrid["total_retrieved"] > 0
    assert v2_hybrid["product_version"] == "v2.0"
    for item in v2_hybrid["results"]:
        assert item["product_version"] == "v2.0"
    top_v2_text = v2_hybrid["results"][0]["text_content"]
    assert "scheduled" in top_v2_text.lower()

    # Execute for v3.0
    v3_hybrid = rag_pipeline.execute_hybrid_retrieval(
        customer_question=customer_q,
        product_version="v3.0",
        enable_query_rewriting=True,
        retrieval_mode="hybrid",
        top_k=3
    )
    assert v3_hybrid["total_retrieved"] > 0
    assert v3_hybrid["product_version"] == "v3.0"
    for item in v3_hybrid["results"]:
        assert item["product_version"] == "v3.0"
    top_v3_text = v3_hybrid["results"][0]["text_content"]
    assert "automated" in top_v3_text.lower() or "copilot" in top_v3_text.lower()


def test_three_way_retrieval_comparison():
    """
    Test Phase 4 Part E:
    Executes comparison across:
    1. Raw query + dense retrieval
    2. Rewritten query + dense retrieval
    3. Rewritten query + hybrid retrieval (RRF)
    """
    customer_q = "How much do I have to pay per user and can I get a discount for paying for a whole year?"
    comparison = rag_pipeline.compare_retrieval_methods(
        customer_question=customer_q,
        product_version="v2.0",
        top_k=3
    )

    assert comparison["original_query"] == customer_q
    assert len(comparison["rewritten_query"]) > 0
    assert len(comparison["raw_dense_results"]) > 0
    assert len(comparison["rewritten_dense_results"]) > 0
    assert len(comparison["rewritten_hybrid_results"]) > 0

    # Verify that hybrid results contain both RRF scores and maintain version integrity
    for r in comparison["rewritten_hybrid_results"]:
        assert r["product_version"] == "v2.0"
        assert r["rrf_score"] > 0.0
        assert r["retrieval_method"] == "hybrid"


def test_nonexistent_version_safety():
    """
    Test Phase 4 Part B:
    If the requested version has no relevant documentation, return an appropriate message
    instead of silently using another version.
    """
    res = rag_pipeline.execute_hybrid_retrieval(
        customer_question="How do I configure SLA rules?",
        product_version="v99.0",
        enable_query_rewriting=True,
        retrieval_mode="hybrid"
    )

    assert res["total_retrieved"] == 0
    assert len(res["results"]) == 0
    assert "No documentation exists for requested product version 'v99.0'" in res["status_message"]
    assert res["diagnostics"]["version_found"] is False


def test_api_endpoints_integration():
    """
    Test FastAPI endpoints for Phase 4:
    - /api/v1/rag/rewrite
    - /api/v1/rag/retrieve
    - /api/v1/rag/compare
    """
    # 1. Test Rewrite API
    rewrite_req = QueryRewriteRequest(
        customer_question="Can you tell me how round robin ticket assignment works?",
        product_name="NexaDesk",
        product_version="v2.0"
    )
    rewrite_resp = rewrite_customer_query(rewrite_req)
    assert rewrite_resp.original_query == rewrite_req.customer_question
    assert len(rewrite_resp.rewritten_query) > 0
    assert len(rewrite_resp.search_keywords) > 0

    # 2. Test Retrieve API
    retrieve_req = HybridRetrievalRequest(
        customer_question="Can you tell me how round robin ticket assignment works?",
        product_name="NexaDesk",
        product_version="v2.0",
        retrieval_mode="hybrid",
        top_k=2
    )
    retrieve_resp = retrieve_hybrid_context(retrieve_req)
    assert retrieve_resp.total_retrieved > 0
    assert retrieve_resp.product_version == "v2.0"
    for r in retrieve_resp.results:
        assert r.product_version == "v2.0"

    # 3. Test Compare API
    compare_req = RetrievalComparisonRequest(
        customer_question="What are the admin role permissions?",
        product_version="v1.0",
        top_k=2
    )
    compare_resp = compare_retrieval_strategies(compare_req)
    assert compare_resp.original_query == compare_req.customer_question
    assert len(compare_resp.raw_dense_results) > 0
    assert len(compare_resp.rewritten_hybrid_results) > 0

