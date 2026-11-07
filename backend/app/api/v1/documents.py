from fastapi import APIRouter
from app.models.schemas import DocumentOverviewResponse, DocumentVersionSummary
from app.services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documentation Catalog"])


@router.get(
    "/overview",
    response_model=DocumentOverviewResponse,
    summary="Get Overview of All Documentation Versions",
    description="Returns files and statistics for all supported NexaDesk versions (v1.0, v2.0, v3.0)."
)
def get_documents_overview() -> DocumentOverviewResponse:
    return document_service.get_all_versions_overview()


@router.get(
    "/version/{version}",
    response_model=DocumentVersionSummary,
    summary="Get Documents by Specific Version",
    description="Returns file list for a specific version: v1.0, v2.0, or v3.0."
)
def get_version_documents(version: str) -> DocumentVersionSummary:
    return document_service.get_version_summary(version)
