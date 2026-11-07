import pytest
from app.api.v1.health import get_health_check, ping
from app.api.v1.system import get_system_info
from app.api.v1.documents import get_documents_overview, get_version_documents
from app.database.connection import check_db_health
from app.rag.vector_store import chroma_storage_manager
from app.core.config import get_settings


def test_db_connectivity():
    """Verify that SQLite database is connected and initialized."""
    assert check_db_health() is True


def test_chroma_storage_status():
    """Verify persistent local storage for ChromaDB exists and is writable."""
    status = chroma_storage_manager.check_status()
    assert status["status"] == "ready"
    assert status["directory_exists"] is True
    assert status["writable"] is True


def test_health_check_service():
    """Verify health service returns healthy status and all components."""
    health = get_health_check()
    assert health.status in ["healthy", "degraded"]
    assert "api_core" in health.components
    assert health.components["api_core"].status == "healthy"
    assert "sqlite_database" in health.components
    assert health.components["sqlite_database"].status == "healthy"
    assert "chroma_storage" in health.components
    assert health.components["chroma_storage"].status == "healthy"


def test_ping():
    """Verify ping endpoint."""
    res = ping()
    assert res == {"ping": "pong"}


def test_system_info():
    """Verify system info configuration and multi-version settings."""
    info = get_system_info()
    settings = get_settings()
    assert info.project_name == settings.PROJECT_NAME
    assert "v1.0" in info.supported_product_versions
    assert "v2.0" in info.supported_product_versions
    assert "v3.0" in info.supported_product_versions


def test_documents_overview():
    """Verify multi-version documentation catalog inspection."""
    overview = get_documents_overview()
    assert overview.product_name == "NexaDesk"
    assert overview.total_documents >= 3
    versions = [v.version for v in overview.versions]
    assert "v1.0" in versions
    assert "v2.0" in versions
    assert "v3.0" in versions


def test_specific_version_documents():
    """Verify files exist for v1.0, v2.0, and v3.0."""
    v1_docs = get_version_documents("v1.0")
    assert v1_docs.version == "v1.0"
    assert len(v1_docs.files) > 0

    v2_docs = get_version_documents("v2.0")
    assert v2_docs.version == "v2.0"
    assert len(v2_docs.files) > 0

    v3_docs = get_version_documents("v3.0")
    assert v3_docs.version == "v3.0"
    assert len(v3_docs.files) > 0
