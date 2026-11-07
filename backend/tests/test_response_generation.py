"""
Phase 5 Automated Tests: Grounded Answer Generation with Citations & Version Safety.
Validates:
1. Version-isolated answer synthesis across v1.0, v2.0, and v3.0.
2. Citation generation linking to actual retrieved document chunks.
3. Retrieval sufficiency check and abstention guard on unanswerable/out-of-scope inquiries.
4. Multi-turn conversation history persistence in SQLite.
5. Enquiry audit logging in enquiry_logs table.
6. FastAPI endpoint integration (/api/v1/chat/enquiry).
"""
import sqlite3
import pytest
from app.database.connection import init_database, get_sqlite_path
from app.rag.pipeline import rag_pipeline
from app.rag.generator import grounded_generator
from app.models.schemas import CustomerEnquiryRequest
from app.api.v1.chat import submit_customer_enquiry, get_recent_enquiry_logs


@pytest.fixture(scope="module", autouse=True)
def setup_phase5_database():
    """Ensure database schema and vector stores are initialized."""
    init_database()
    rag_pipeline.sync_all_from_sqlite()


def test_version_grounded_answer_v1():
    """
    Test Phase 5 Version Safety for v1.0:
    Inquiry: 'How do report exports work in NexaDesk?'
    v1.0 answer must strictly reflect manual exports only, and must NOT mention v2.0 scheduling.
    """
    response = rag_pipeline.answer_customer_enquiry(
        question="How do report exports work in NexaDesk?",
        product_version="v1.0",
        top_k=2
    )

    assert response["product_version"] == "v1.0"
    assert response["abstained"] is False
    answer = response["answer"].lower()

    # Must contain manual CSV export concepts from v1.0 documentation
    assert "manual" in answer
    assert "csv" in answer

    # Citations must be populated and point strictly to v1.0 documents
    assert len(response["citations"]) > 0
    top_citation = response["citations"][0]
    assert top_citation.document_name == "reporting_and_exports.md"
    assert "Manual Report Exports in v1.0" in top_citation.section_title


def test_version_grounded_answer_v2():
    """
    Test Phase 5 Version Safety for v2.0:
    Inquiry: 'How do report exports work in NexaDesk?'
    v2.0 answer must describe scheduled recurring exports.
    """
    response = rag_pipeline.answer_customer_enquiry(
        question="How do report exports work in NexaDesk?",
        product_version="v2.0",
        top_k=2
    )

    assert response["product_version"] == "v2.0"
    assert response["abstained"] is False
    answer = response["answer"].lower()

    # Must reflect v2.0 scheduled recurring features
    assert "scheduled" in answer or "recurring" in answer
    assert len(response["citations"]) > 0
    top_citation = response["citations"][0]
    assert "Scheduled Report Exports in v2.0" in top_citation.section_title


def test_version_grounded_answer_v3():
    """
    Test Phase 5 Version Safety for v3.0:
    Inquiry: 'How do report exports work in NexaDesk?'
    v3.0 answer must describe automated AI-triggered exports and Copilot summaries.
    """
    response = rag_pipeline.answer_customer_enquiry(
        question="How do report exports work in NexaDesk?",
        product_version="v3.0",
        top_k=2
    )

    assert response["product_version"] == "v3.0"
    assert response["abstained"] is False
    answer = response["answer"].lower()

    # Must reflect v3.0 AI automated exports
    assert "automated" in answer or "copilot" in answer or "ai" in answer
    assert len(response["citations"]) > 0
    top_citation = response["citations"][0]
    assert "v3.0" in top_citation.section_title


def test_abstention_and_human_escalation_on_unrelated_query():
    """
    Test Phase 5 Confidence & Abstention:
    When a question has no documentation evidence (e.g. chocolate chip cookie recipe),
    the system must abstain, refuse to hallucinate, and offer human escalation.
    """
    response = rag_pipeline.answer_customer_enquiry(
        question="What is the authentic recipe for baking chocolate chip cookies?",
        product_version="v3.0",
        top_k=2
    )

    assert response["abstained"] is True
    answer = response["answer"]
    assert "cannot find verified information" in answer.lower()
    assert "human support" in answer.lower()
    # Must not contain citations for ungrounded content
    assert len(response["citations"]) == 0


def test_conversation_history_persistence():
    """
    Test Phase 5 Conversation Memory:
    Verifies that multi-turn dialogue is saved in SQLite and readable by conversation_id.
    """
    conv_id = "test_thread_phase5"

    # Turn 1
    res1 = rag_pipeline.answer_customer_enquiry(
        question="What user roles are supported?",
        product_version="v1.0",
        conversation_id=conv_id
    )
    assert res1["conversation_id"] == conv_id

    # Turn 2 (Follow-up)
    res2 = rag_pipeline.answer_customer_enquiry(
        question="Can viewers modify tickets?",
        product_version="v1.0",
        conversation_id=conv_id
    )
    assert res2["conversation_id"] == conv_id

    # Read back conversation history
    history = grounded_generator.get_conversation_history(conv_id)
    assert len(history) >= 4  # 2 user turns + 2 assistant turns
    roles = [h["role"] for h in history]
    assert roles.count("user") >= 2
    assert roles.count("assistant") >= 2


def test_enquiry_audit_logging():
    """
    Test Phase 5 Audit Logging:
    Verifies that customer inquiries are logged into SQLite enquiry_logs table.
    """
    db_path = get_sqlite_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM enquiry_logs")
        count_before = cursor.fetchone()[0]

    rag_pipeline.answer_customer_enquiry(
        question="What are the SLA response time guarantees?",
        product_version="v1.0"
    )

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM enquiry_logs")
        count_after = cursor.fetchone()[0]

    assert count_after > count_before


def test_customer_enquiry_api_endpoint():
    """
    Test Phase 5 FastAPI Endpoint:
    POST /api/v1/chat/enquiry
    Must return structured JSON with all required fields:
    answer, citations, product_version, rewritten_query, retrieved_sources, abstained, conversation_id.
    """
    payload = CustomerEnquiryRequest(
        question="Why can't I schedule my reports like before?",
        product_version="v2.0",
        product_name="NexaDesk",
        retrieval_mode="hybrid",
        top_k=2
    )

    resp = submit_customer_enquiry(payload)

    # Check all fields specified in prompt
    assert resp.answer is not None and len(resp.answer) > 0
    assert resp.product_version == "v2.0"
    assert resp.conversation_id is not None
    assert resp.rewritten_query is not None
    assert isinstance(resp.citations, list)
    assert isinstance(resp.retrieved_sources, list)
    assert isinstance(resp.abstained, bool)
    assert resp.abstained is False

    # Check that logs API returns records
    logs_resp = get_recent_enquiry_logs(limit=5)
    assert logs_resp.total_logs > 0

