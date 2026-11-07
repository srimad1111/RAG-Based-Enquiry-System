from fastapi import APIRouter
from app.core.config import get_settings
from app.models.schemas import SystemInfoResponse
from app.rag.pipeline import rag_pipeline_stub

settings = get_settings()
router = APIRouter(prefix="/system", tags=["System Information"])


@router.get(
    "/info",
    response_model=SystemInfoResponse,
    summary="Get System and Product Configuration",
    description="Provides application metadata, supported NexaDesk versions, and local storage mappings."
)
def get_system_info() -> SystemInfoResponse:
    rag_info = rag_pipeline_stub.get_pipeline_info()
    return SystemInfoResponse(
        project_name=settings.PROJECT_NAME,
        app_version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        default_product_version=settings.DEFAULT_PRODUCT_VERSION,
        supported_product_versions=settings.SUPPORTED_PRODUCT_VERSIONS,
        storage_directories={
            "chroma_db": str(settings.chroma_path),
            "uploads": str(settings.uploads_path),
            "documents": str(settings.documents_path),
            "sqlite_db": str(settings.sqlite_path),
        },
        rag_status=f"{rag_info['current_phase']} ({rag_info['pipeline_state']})"
    )
