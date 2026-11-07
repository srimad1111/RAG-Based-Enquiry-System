"""
Phase 6 Automated Tests: RAG Triad Evaluation & System Analytics.
Validates:
1. Benchmark dataset loading and case structure.
2. Context Relevance, Groundedness, and Version Isolation scoring logic.
3. Automated benchmark suite execution.
4. Analytics API endpoints (/api/v1/analytics/overview, /api/v1/analytics/report).
"""
import pytest
from app.database.connection import init_database
from app.rag.pipeline import rag_pipeline
from app.services.evaluation_service import evaluation_service
from app.api.v1.analytics import get_analytics_overview, get_evaluation_report


@pytest.fixture(scope="module", autouse=True)
def setup_evaluation_test():
    """Initialize DB and sync ChromaDB vectors."""
    init_database()
    rag_pipeline.sync_all_from_sqlite()


def test_benchmark_dataset_integrity():
    """Verify that the evaluation benchmark dataset loads and contains required fields."""
    cases = evaluation_service.load_benchmark_dataset()
    assert len(cases) >= 10
    for c in cases:
        assert "id" in c
        assert "query" in c
        assert "product_version" in c
        assert c["product_version"] in ["v1.0", "v2.0", "v3.0"]
        assert "should_abstain" in c


def test_evaluate_single_valid_case():
    """Verify evaluation metric computation on a valid version-specific query."""
    case = {
        "id": "test_eval_1",
        "query": "How do report exports work in NexaDesk?",
        "product_version": "v1.0",
        "expected_document": "reporting_and_exports.md",
        "expected_section": "Manual Report Exports in v1.0",
        "expected_keywords": ["manual", "csv"],
        "prohibited_keywords": ["scheduled"],
        "query_type": "version_differentiating",
        "should_abstain": False
    }

    res = evaluation_service.evaluate_case(case)
    assert res["case_id"] == "test_eval_1"
    assert res["product_version"] == "v1.0"
    assert res["version_isolation"] == 1.0
    assert res["context_relevance"] > 0.0
    assert res["groundedness"] > 0.5
    assert res["abstained"] is False
    assert res["abstention_correct"] is True
    assert res["latency_ms"] > 0.0


def test_evaluate_abstention_case():
    """Verify evaluation metric computation on an out-of-domain query."""
    case = {
        "id": "test_eval_abstain",
        "query": "What is the authentic recipe for baking chocolate chip cookies?",
        "product_version": "v3.0",
        "expected_document": None,
        "expected_section": None,
        "expected_keywords": [],
        "prohibited_keywords": [],
        "query_type": "out_of_domain",
        "should_abstain": True
    }

    res = evaluation_service.evaluate_case(case)
    assert res["abstained"] is True
    assert res["abstention_correct"] is True
    assert res["citations_count"] == 0


def test_analytics_api_endpoints():
    """Verify analytics endpoints return valid operational and benchmark metrics."""
    overview = get_analytics_overview()
    assert "rag_triad" in overview
    assert "version_isolation_accuracy" in overview
    assert overview["version_isolation_accuracy"] == 100.0

    report = get_evaluation_report()
    assert "rag_triad_scores" in report
    assert "version_safety" in report
    assert report["version_safety"]["version_isolation_accuracy_percentage"] == 100.0

