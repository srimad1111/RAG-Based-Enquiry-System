import os
from functools import lru_cache
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel

# Automatically load environment variables from backend/.env or root .env
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv()


def _parse_list(val: str) -> List[str]:
    return [item.strip() for item in val.split(",") if item.strip()]


class Settings(BaseModel):
    """Application configuration loaded from environment variables."""

    # Project Information
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "NexaDesk RAG Customer Enquiry System")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    # Server Settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")

    # CORS
    ALLOWED_ORIGINS: List[str] = _parse_list(
        os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    )

    # AI / LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))

    # Storage & Persistence Paths (relative to backend folder)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "storage/chroma_db")
    UPLOADS_DIRECTORY: str = os.getenv("UPLOADS_DIRECTORY", "storage/uploads")
    DOCUMENTS_DIRECTORY: str = os.getenv("DOCUMENTS_DIRECTORY", "data/documents/NexaDesk")
    PROCESSED_DIRECTORY: str = os.getenv("PROCESSED_DIRECTORY", "data/processed")
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "app/database/nexadesk.db")

    # Product Versioning
    DEFAULT_PRODUCT_VERSION: str = os.getenv("DEFAULT_PRODUCT_VERSION", "v3.0")
    SUPPORTED_PRODUCT_VERSIONS: List[str] = _parse_list(
        os.getenv("SUPPORTED_PRODUCT_VERSIONS", "v1.0,v2.0,v3.0")
    )

    # Ingestion & Chunking Parameters (Phase 2)
    DEFAULT_CHUNK_SIZE: int = int(os.getenv("DEFAULT_CHUNK_SIZE", 800))
    DEFAULT_CHUNK_OVERLAP: int = int(os.getenv("DEFAULT_CHUNK_OVERLAP", 150))
    SUPPORTED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md", ".markdown"]

    @property
    def chroma_path(self) -> Path:
        return (self.BASE_DIR / self.CHROMA_PERSIST_DIRECTORY).resolve()

    @property
    def uploads_path(self) -> Path:
        return (self.BASE_DIR / self.UPLOADS_DIRECTORY).resolve()

    @property
    def documents_path(self) -> Path:
        return (self.BASE_DIR / self.DOCUMENTS_DIRECTORY).resolve()

    @property
    def processed_path(self) -> Path:
        return (self.BASE_DIR / self.PROCESSED_DIRECTORY).resolve()

    @property
    def sqlite_path(self) -> Path:
        return (self.BASE_DIR / self.SQLITE_DB_PATH).resolve()


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
