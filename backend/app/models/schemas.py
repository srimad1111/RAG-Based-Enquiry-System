from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ComponentHealth(BaseModel):
    """Health status of an individual system component."""
    status: str = Field(..., description="Component status: healthy, degraded, or error")
    message: str = Field(..., description="Operational detail or reason")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class HealthResponse(BaseModel):
    """Complete system health-check response."""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(default_factory=get_utc_now, description="UTC timestamp of check")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application semantic version")
    environment: str = Field(..., description="Current environment (development/production)")
    components: Dict[str, ComponentHealth] = Field(..., description="Status breakdown of subsystems")


class SystemInfoResponse(BaseModel):
    """General information about the system and configured product versions."""
    project_name: str
    app_version: str
    environment: str
    default_product_version: str
    supported_product_versions: List[str]
    storage_directories: Dict[str, str]
    rag_status: str


class DocumentVersionSummary(BaseModel):
    """Summary of documentation files available for a given product version."""
    version: str
    file_count: int
    files: List[str]
    directory_path: str


class DocumentOverviewResponse(BaseModel):
    """Overview of all NexaDesk documentation versions available."""
    product_name: str = "NexaDesk"
    versions: List[DocumentVersionSummary]
    total_documents: int


class StandardApiResponse(BaseModel):
    """Standardized API response envelope."""
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=get_utc_now)
