from datetime import datetime, timezone
from typing import Dict
from app.core.config import get_settings
from app.database.connection import check_db_health
from app.models.schemas import ComponentHealth, HealthResponse
from app.rag.vector_store import chroma_storage_manager
from app.utils.helpers import verify_storage_directories

settings = get_settings()


class HealthService:
    """Service to aggregate health metrics across backend subsystems."""

    @staticmethod
    def get_full_health() -> HealthResponse:
        """Run health diagnostics on core, database, vector storage, and file systems."""
        components: Dict[str, ComponentHealth] = {}
        overall_healthy = True

        # 1. API Core
        components["api_core"] = ComponentHealth(
            status="healthy",
            message="FastAPI application router and middleware active",
            details={
                "environment": settings.ENVIRONMENT,
                "debug_mode": settings.DEBUG
            }
        )

        # 2. SQLite Database
        db_ok = check_db_health()
        if db_ok:
            components["sqlite_database"] = ComponentHealth(
                status="healthy",
                message="SQLite database connected and tables verified",
                details={"db_path": str(settings.sqlite_path)}
            )
        else:
            overall_healthy = False
            components["sqlite_database"] = ComponentHealth(
                status="error",
                message="SQLite database is unreachable or cannot be queried",
                details={"db_path": str(settings.sqlite_path)}
            )

        # 3. ChromaDB Persistent Local Storage
        chroma_diag = chroma_storage_manager.check_status()
        if chroma_diag["status"] == "ready":
            components["chroma_storage"] = ComponentHealth(
                status="healthy",
                message="ChromaDB persistent directory exists and is writable",
                details=chroma_diag
            )
        else:
            overall_healthy = False
            components["chroma_storage"] = ComponentHealth(
                status="error",
                message="ChromaDB persistent directory has write or permission issues",
                details=chroma_diag
            )

        # 4. Storage Directories
        storage_status = verify_storage_directories()
        all_dirs_ok = all(storage_status.values())
        if all_dirs_ok:
            components["file_storage"] = ComponentHealth(
                status="healthy",
                message="All required upload and data directories are verified",
                details={"verified_directories": storage_status}
            )
        else:
            components["file_storage"] = ComponentHealth(
                status="degraded",
                message="Some storage directories could not be validated",
                details={"verified_directories": storage_status}
            )

        # 5. Gemini API Configuration status
        gemini_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_placeholder")
        components["gemini_api"] = ComponentHealth(
            status="healthy" if gemini_configured else "standby",
            message="Gemini API Key configured" if gemini_configured else "Placeholder key present; awaiting API key for Phase 2",
            details={
                "model": settings.GEMINI_MODEL,
                "configured": gemini_configured
            }
        )

        return HealthResponse(
            status="healthy" if overall_healthy else "degraded",
            timestamp=datetime.now(timezone.utc),
            app_name=settings.PROJECT_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            components=components
        )


health_service = HealthService()
