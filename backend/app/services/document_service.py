from pathlib import Path
from typing import List
from app.core.config import get_settings
from app.core.logging import logger
from app.models.schemas import DocumentOverviewResponse, DocumentVersionSummary

settings = get_settings()


class DocumentService:
    """Service to scan and manage versioned product documentation for NexaDesk."""

    def __init__(self):
        self.docs_base_path = settings.documents_path

    def get_version_summary(self, version: str) -> DocumentVersionSummary:
        """Scan and summarize files for a given version directory."""
        if version not in settings.SUPPORTED_PRODUCT_VERSIONS:
            raise ValueError(
                f"Unsupported version '{version}'. Must be one of: {settings.SUPPORTED_PRODUCT_VERSIONS}"
            )
        version_dir = self.docs_base_path / version
        if not version_dir.exists():
            version_dir.mkdir(parents=True, exist_ok=True)

        files = [
            f.name for f in version_dir.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]

        return DocumentVersionSummary(
            version=version,
            file_count=len(files),
            files=sorted(files),
            directory_path=str(version_dir)
        )

    def get_all_versions_overview(self) -> DocumentOverviewResponse:
        """Inspect all configured versions (v1.0, v2.0, v3.0)."""
        summaries: List[DocumentVersionSummary] = []
        total_docs = 0

        for version in settings.SUPPORTED_PRODUCT_VERSIONS:
            summary = self.get_version_summary(version)
            summaries.append(summary)
            total_docs += summary.file_count

        return DocumentOverviewResponse(
            product_name="NexaDesk",
            versions=summaries,
            total_documents=total_docs
        )


document_service = DocumentService()

