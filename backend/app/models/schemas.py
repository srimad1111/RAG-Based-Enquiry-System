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


# ==============================================================================
# Phase 2: Ingestion & Chunking Schemas
# ==============================================================================

class ChunkMetadata(BaseModel):
    """Structured metadata mandatory for every ingested chunk."""
    document_id: str
    document_name: str
    product_name: str
    product_version: str
    document_type: str
    section_title: Optional[str] = "General"
    page_number: Optional[int] = 1
    upload_timestamp: str
    chunk_id: str
    category: Optional[str] = "General"


class ChunkDetail(BaseModel):
    """Detailed chunk information including text and metadata."""
    id: str
    document_id: str
    chunk_index: int
    text_content: str
    char_count: int
    section_title: Optional[str]
    page_number: Optional[int]
    metadata: ChunkMetadata


class DocumentRecord(BaseModel):
    """Represents a persisted document record in SQLite."""
    id: str
    document_name: str
    file_path: str
    file_size: int
    file_hash: str
    product_name: str
    product_version: str
    category: str
    document_type: str
    chunk_count: int
    status: str
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class DocumentUploadResponse(BaseModel):
    """Response returned upon successfully uploading and processing a document."""
    success: bool
    message: str
    document: DocumentRecord
    chunks_created: int
    duplicate_detected: bool = False
    replaced_previous: bool = False


class DocumentListResponse(BaseModel):
    """Response containing a list of ingested documents."""
    total_documents: int
    total_chunks: int
    documents: List[DocumentRecord]
    filtered_version: Optional[str] = None


class IngestionStatsResponse(BaseModel):
    """Aggregated stats on ingested documents and chunks across versions."""
    total_documents: int
    total_chunks: int
    by_version: Dict[str, Dict[str, int]]
    by_type: Dict[str, int]
    by_category: Dict[str, int]


# ==============================================================================
# Phase 3: Vector Indexing & Search Schemas
# ==============================================================================

class VectorSearchRequest(BaseModel):
    """Payload for version-aware semantic vector search."""
    query: str = Field(..., description="Inquiry search text")
    product_version: Optional[str] = Field(None, description="Target version (e.g. v1.0, v2.0, v3.0)")
    product_name: Optional[str] = Field("NexaDesk", description="Product name")
    document_type: Optional[str] = Field(None, description="Filter by file extension (pdf, docx, txt, md)")
    document_name: Optional[str] = Field(None, description="Filter by specific document filename")
    top_k: int = Field(4, ge=1, le=20, description="Max candidate chunks to retrieve")


class VectorSearchResultItem(BaseModel):
    """Individual vector search result with similarity score and metadata."""
    chunk_id: str
    document_id: str
    text_content: str
    similarity_score: float
    cosine_distance: float
    rank: int
    metadata: Dict[str, Any]


class VectorSearchResponse(BaseModel):
    """Response envelope for vector search queries."""
    query: str
    product_version: Optional[str]
    total_results: int
    results: List[VectorSearchResultItem]


class IndexingSyncResponse(BaseModel):
    """Response returned upon syncing SQLite chunks into ChromaDB."""
    status: str
    chunks_synced: int
    total_indexed_in_chroma: int
    by_version: Dict[str, int]


class StandardApiResponse(BaseModel):
    """Standardized API response envelope."""
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=get_utc_now)
