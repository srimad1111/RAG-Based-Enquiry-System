from fastapi import APIRouter, status
from app.models.schemas import HealthResponse
from app.services.health_service import health_service

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete System Health Check",
    description="Returns detailed operational status for API core, SQLite database, ChromaDB local storage, and file directories."
)
def get_health_check() -> HealthResponse:
    return health_service.get_full_health()


@router.get(
    "/ping",
    summary="Simple Ping",
    description="Lightweight liveness probe returning pong."
)
def ping():
    return {"ping": "pong"}
