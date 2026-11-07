import shutil
from pathlib import Path
import pytest
from app.core.config import get_settings
from app.services.chunking_service import chunking_service
from app.services.ingestion_service import ingestion_service
from app.services.parser_service import parser_service

settings = get_settings()
DOCS_DIR = settings.documents_path


def test_pdf_extraction_real_file():
    """Verify PyMuPDF extracts pages, text and headings from real sample PDF."""
    pdf_path = DOCS_DIR / "v1.0" / "email_and_sla_policy.pdf"
    assert pdf_path.exists(), f"Sample PDF not found at {pdf_path}"

    blocks = parser_service.extract_pdf(pdf_path)
    assert len(blocks) >= 2, "Expected at least 2 pages/blocks from sample PDF"
    assert blocks[0].page_number == 1
    assert "POP3" in blocks[0].text or "Email" in blocks[0].text
    assert blocks[1].page_number == 2
    assert "SLA" in blocks[1].text or "Deadlines" in blocks[1].text


def test_docx_extraction_real_file():
    """Verify python-docx extracts paragraphs and headings from real sample DOCX."""
    docx_path = DOCS_DIR / "v2.0" / "rbac_and_round_robin.docx"
    assert docx_path.exists(), f"Sample DOCX not found at {docx_path}"

    blocks = parser_service.extract_docx(docx_path)
    assert len(blocks) >= 1
    combined_text = " ".join(b.text for b in blocks).lower()
    assert "round-robin" in combined_text or "rbac" in combined_text


def test_txt_and_md_extraction():
    """Verify TXT and Markdown extraction."""
    txt_path = DOCS_DIR / "v3.0" / "pricing_and_quotas.txt"
    assert txt_path.exists()
    txt_blocks = parser_service.extract_txt(txt_path)
    assert len(txt_blocks) >= 1
    assert "$99" in txt_blocks[0].text

    md_path = DOCS_DIR / "v1.0" / "getting_started.md"
    assert md_path.exists()
    md_blocks = parser_service.extract_markdown(md_path)
    assert len(md_blocks) >= 1
    assert "NexaDesk" in md_blocks[0].text


def test_chunking_service_configurable():
    """Verify recursive chunker with 800 char size and 150 char overlap."""
    pdf_path = DOCS_DIR / "v1.0" / "email_and_sla_policy.pdf"
    blocks = parser_service.extract_pdf(pdf_path)

    chunks = chunking_service.split_blocks(
        blocks=blocks,
        document_id="doc_test123",
        document_name="email_and_sla_policy.pdf",
        product_name="NexaDesk",
        product_version="v1.0",
        category="Technical Policy",
        document_type="pdf",
        upload_timestamp="2026-11-07T12:00:00Z",
        chunk_size=800,
        chunk_overlap=150
    )

    assert len(chunks) >= 2
    for c in chunks:
        # Requirement 7 & 8: Check length & non-empty
        assert len(c.text_content) <= 900
        assert len(c.text_content.strip()) > 15
        # Requirement 9: Verify metadata
        assert c.metadata.document_id == "doc_test123"
        assert c.metadata.product_version == "v1.0"
        assert c.metadata.document_type == "pdf"
        assert c.metadata.chunk_id == c.id
        assert c.metadata.page_number in [1, 2]


def test_full_ingestion_pipeline_pdf():
    """Test full ingestion of a real PDF into SQLite and verify chunk metadata."""
    pdf_path = DOCS_DIR / "v2.0" / "omnichannel_and_webhooks.pdf"
    file_bytes = pdf_path.read_bytes()

    res = ingestion_service.ingest_file(
        file_bytes=file_bytes,
        filename="omnichannel_and_webhooks.pdf",
        product_name="NexaDesk",
        product_version="v2.0",
        category="Integrations",
        chunk_size=800,
        chunk_overlap=150,
        replace_existing=True
    )

    assert res.success is True
    assert res.chunks_created >= 2
    doc_id = res.document.id

    # Retrieve chunks from DB
    chunks = ingestion_service.get_document_chunks(doc_id)
    assert len(chunks) == res.chunks_created
    assert chunks[0].metadata.product_version == "v2.0"
    assert chunks[0].metadata.document_type == "pdf"
    assert "SendGrid" in chunks[0].text_content or "Webhooks" in chunks[0].text_content

    # Clean up test document
    ingestion_service.delete_document(doc_id)
    assert ingestion_service.get_document(doc_id) is None


def test_duplicate_detection_workflow():
    """Test duplicate detection and replacement workflow."""
    txt_path = DOCS_DIR / "v1.0" / "pricing_and_quotas.txt"
    file_bytes = txt_path.read_bytes()

    # 1. First upload
    res1 = ingestion_service.ingest_file(
        file_bytes=file_bytes,
        filename="pricing_and_quotas.txt",
        product_name="NexaDesk",
        product_version="v1.0",
        category="Pricing",
        replace_existing=True
    )
    assert res1.success is True
    doc_id = res1.document.id

    # 2. Second upload without replace_existing -> Expect duplicate detection
    res2 = ingestion_service.ingest_file(
        file_bytes=file_bytes,
        filename="pricing_and_quotas.txt",
        product_name="NexaDesk",
        product_version="v1.0",
        category="Pricing",
        replace_existing=False
    )
    assert res2.duplicate_detected is True
    assert res2.success is False
    assert "Duplicate document detected" in res2.message

    # 3. Third upload with replace_existing=True -> Expect replacement
    res3 = ingestion_service.ingest_file(
        file_bytes=file_bytes,
        filename="pricing_and_quotas.txt",
        product_name="NexaDesk",
        product_version="v1.0",
        category="Pricing",
        replace_existing=True
    )
    assert res3.success is True
    assert res3.replaced_previous is True

    # Clean up
    ingestion_service.delete_document(res3.document.id)


def test_ingestion_stats_and_filtering():
    """Verify document listing by version and overview stats."""
    docx_path = DOCS_DIR / "v3.0" / "nexaflow_studio_guide.docx"
    file_bytes = docx_path.read_bytes()

    res = ingestion_service.ingest_file(
        file_bytes=file_bytes,
        filename="nexaflow_studio_guide.docx",
        product_name="NexaDesk",
        product_version="v3.0",
        category="Workflow",
        replace_existing=True
    )
    assert res.success is True

    # Filter by version v3.0
    v3_docs = ingestion_service.list_documents(product_version="v3.0")
    assert any(d.id == res.document.id for d in v3_docs)

    # Filter by other version v1.0
    v1_docs = ingestion_service.list_documents(product_version="v1.0")
    assert not any(d.id == res.document.id for d in v1_docs)

    # Stats
    stats = ingestion_service.get_stats()
    assert stats.total_documents >= 1
    assert stats.by_version["v3.0"]["documents"] >= 1

    # Cleanup
    ingestion_service.delete_document(res.document.id)
