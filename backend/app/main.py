from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import api_v1_router
from app.core.config import get_settings
from app.core.logging import logger
from app.database.connection import init_database
from app.rag.vector_store import chroma_storage_manager
from app.utils.helpers import verify_storage_directories

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for application startup and shutdown."""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.PROJECT_NAME} (v{settings.APP_VERSION})")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")
    logger.info("=" * 60)

    # 1. Initialize SQLite Database
    try:
        init_database()
    except Exception as e:
        logger.error(f"Critical error during database initialization: {e}")

    # 2. Verify all local persistent storage directories
    try:
        dir_status = verify_storage_directories()
        logger.info(f"Local storage directories verified: {dir_status}")
    except Exception as e:
        logger.error(f"Error checking storage directories: {e}")

    # 3. Check persistent ChromaDB storage path
    chroma_check = chroma_storage_manager.check_status()
    logger.info(f"ChromaDB persistent store check: {chroma_check['status']} at {chroma_check['persist_directory']}")

    yield

    logger.info(f"Shutting down {settings.PROJECT_NAME} gracefully...")


def create_application() -> FastAPI:
    """Factory function to build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.APP_VERSION,
        description="RAG-Based Customer Enquiry System over Multi-Version Company Documentation (NexaDesk v1.0, v2.0, v3.0)",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handling: HTTP Exceptions
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP exception on {request.method} {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "path": request.url.path
                }
            }
        )

    # Exception Handling: Validation Errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": 422,
                    "message": "Input validation error",
                    "details": exc.errors(),
                    "path": request.url.path
                }
            }
        )

    # Exception Handling: Unhandled Server Errors
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "An internal server error occurred.",
                    "path": request.url.path
                }
            }
        )

    # Root welcome route
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.APP_VERSION,
            "status": "operational",
            "documentation": "/docs",
            "health_check": f"{settings.API_V1_STR}/health",
            "supported_versions": settings.SUPPORTED_PRODUCT_VERSIONS
        }

    # Mount API v1 router
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = create_application()

