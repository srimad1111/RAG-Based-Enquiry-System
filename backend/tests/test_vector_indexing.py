import pytest
from app.rag.pipeline import rag_pipeline
from app.rag.vector_store import chroma_vector_store
from app.services.ingestion_service import ingestion_service


@pytest.fixture(autouse=True)
def ensure_indexed():
    """Ensure ChromaDB has current chunks from SQLite."""
    rag_pipeline.sync_all_from_sqlite()


def test_embedding_model_and_dimensions():
    """Verify that SentenceTransformer generates 384-dimensional embeddings."""
    emb_fn = chroma_vector_store.embedding_fn
    vectors = emb_fn(["NexaDesk customer enquiry query"])
    assert len(vectors) == 1
    assert len(vectors[0]) == 384, f"Expected 384-dim vector, got {len(vectors[0])}"


def test_vector_store_persistence_and_metadata():
    """Verify vectors are stored in ChromaDB with complete required metadata."""
    status = chroma_vector_store.get_status()
    assert status["total_chunks_indexed"] >= 20
    assert status["by_version"]["v1.0"] > 0
    assert status["by_version"]["v2.0"] > 0
    assert status["by_version"]["v3.0"] > 0

    # Query v1.0 chunks directly to inspect metadata
    res = chroma_vector_store.search_vectors(
        query="POP3 email configuration",
        product_version="v1.0",
        top_k=2
    )
    assert len(res) > 0
    first = res[0]
    meta = first["metadata"]
    # Check all required metadata fields
    assert meta["product_name"] == "NexaDesk"
    assert meta["product_version"] == "v1.0"
    assert "document_id" in meta
    assert "document_name" in meta
    assert "document_type" in meta
    assert "section_title" in meta
    assert "page_number" in meta
    assert "chunk_id" in meta


def test_metadata_filtering_capabilities():
    """Verify metadata filtering across product_version, document_type, and document_name."""
    # 1. Filter by document_type = pdf
    pdf_results = chroma_vector_store.search_vectors(
        query="email and policy",
        product_version="v1.0",
        document_type="pdf",
        top_k=3
    )
    assert len(pdf_results) > 0
    for r in pdf_results:
        assert r["metadata"]["document_type"] == "pdf"
        assert r["metadata"]["product_version"] == "v1.0"

    # 2. Filter by document_name
    doc_results = chroma_vector_store.search_vectors(
        query="pricing plans",
        product_version="v1.0",
        document_name="pricing_and_plans.md",
        top_k=2
    )
    assert len(doc_results) > 0
    for r in doc_results:
        assert r["metadata"]["document_name"] == "pricing_and_plans.md"


def test_version_isolation_report_exports():
    """
    CRITICAL TEST: Version-Aware Retrieval Disambiguation
    Query: 'How do report exports work in NexaDesk?'
    - v1.0 must return manual report exports only.
    - v2.0 must return scheduled report exports.
    - v3.0 must return automated and AI triggered report exports.
    Verifies that no cross-version leakage occurs.
    """
    test_query = "How do report exports work in NexaDesk?"

    # --- Query Version 1.0 ---
    v1_results = chroma_vector_store.search_vectors(
        query=test_query,
        product_version="v1.0",
        top_k=2
    )
    assert len(v1_results) > 0
    v1_text = " ".join(r["text_content"] for r in v1_results)
    assert "manual" in v1_text.lower()
    assert "scheduled report delivery" in v1_text.lower() or "not supported" in v1_text.lower()
    # Ensure v2/v3 terms do not appear as valid v1 features
    assert "automated triggered exports" not in v1_text.lower()

    # --- Query Version 2.0 ---
    v2_results = chroma_vector_store.search_vectors(
        query=test_query,
        product_version="v2.0",
        top_k=2
    )
    assert len(v2_results) > 0
    v2_text = " ".join(r["text_content"] for r in v2_results)
    assert "scheduled report exports" in v2_text.lower() or "recurring schedules" in v2_text.lower()
    assert "manual report exports only" not in v2_text.lower()

    # --- Query Version 3.0 ---
    v3_results = chroma_vector_store.search_vectors(
        query=test_query,
        product_version="v3.0",
        top_k=2
    )
    assert len(v3_results) > 0
    v3_text = " ".join(r["text_content"] for r in v3_results)
    assert "automated" in v3_text.lower() or "ai copilot" in v3_text.lower()
    assert "anomaly" in v3_text.lower() or "threshold" in v3_text.lower()


def test_version_isolation_pricing():
    """Verify distinct pricing retrieved per version for same query."""
    pricing_query = "What is the starter or monthly pricing plan?"

    # v1.0 -> $19
    v1_res = chroma_vector_store.search_vectors(query=pricing_query, product_version="v1.0", top_k=2)
    v1_text = " ".join(r["text_content"] for r in v1_res)
    assert "$19" in v1_text
    assert "annual" not in v1_text.lower() or "not available" in v1_text.lower()

    # v2.0 -> $29 and 15% annual discount
    v2_res = chroma_vector_store.search_vectors(query=pricing_query, product_version="v2.0", top_k=2)
    v2_text = " ".join(r["text_content"] for r in v2_res)
    assert "$29" in v2_text or "$79" in v2_text
    assert "15%" in v2_text

    # v3.0 -> $99 and 20% annual discount
    v3_res = chroma_vector_store.search_vectors(query=pricing_query, product_version="v3.0", top_k=2)
    v3_text = " ".join(r["text_content"] for r in v3_res)
    assert "$99" in v3_text or "$189" in v3_text
    assert "20%" in v3_text


def test_idempotent_indexing_avoids_duplicates():
    """Verify running indexing repeatedly does not inflate chunk count."""
    status_before = chroma_vector_store.get_status()["total_chunks_indexed"]
    # Re-sync all chunks
    rag_pipeline.sync_all_from_sqlite()
    status_after = chroma_vector_store.get_status()["total_chunks_indexed"]
    assert status_before == status_after, "Duplicate embeddings were created during re-index!"


def test_single_document_deletion_isolation():
    """Verify deleting one document does not accidentally delete other documents."""
    # 1. Ingest a temporary test document
    temp_bytes = b"# Temporary Isolation Test\n\nThis is temporary data strictly for isolation testing."
    upload_res = ingestion_service.ingest_file(
        file_bytes=temp_bytes,
        filename="temp_isolation_doc.md",
        product_name="NexaDesk",
        product_version="v3.0",
        category="General",
        replace_existing=True
    )
    temp_doc_id = upload_res.document.id

    # Verify temp doc is in ChromaDB
    res_before = chroma_vector_store.search_vectors(
        query="isolation testing data",
        product_version="v3.0",
        document_name="temp_isolation_doc.md"
    )
    assert len(res_before) > 0

    total_chunks_before = chroma_vector_store.get_status()["total_chunks_indexed"]

    # 2. Delete the temporary document
    ingestion_service.delete_document(temp_doc_id)

    # 3. Verify ONLY temp doc is removed from ChromaDB
    res_after = chroma_vector_store.search_vectors(
        query="isolation testing data",
        product_version="v3.0",
        document_name="temp_isolation_doc.md"
    )
    assert len(res_after) == 0

    total_chunks_after = chroma_vector_store.get_status()["total_chunks_indexed"]
    assert total_chunks_after == total_chunks_before - upload_res.chunks_created

    # Ensure other documents still exist and are searchable
    other_res = chroma_vector_store.search_vectors(
        query="pricing",
        product_version="v3.0"
    )
    assert len(other_res) > 0
