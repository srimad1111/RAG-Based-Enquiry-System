from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.system import router as system_router
from app.api.v1.ingestion import router as documents_router
from app.api.v1.rag import router as rag_router
from app.api.v1.chat import router as chat_router
from app.api.v1.analytics import router as analytics_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(system_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(analytics_router)

__all__ = ["api_v1_router"]
