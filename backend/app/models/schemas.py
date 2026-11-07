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


# ==============================================================================
# Phase 4: Query Rewriting & Version-Aware Hybrid Retrieval Schemas
# ==============================================================================

class QueryRewriteRequest(BaseModel):
    """Payload to request query transformation from informal to technical documentation phrasing."""
    customer_question: str = Field(..., description="Informal customer question or raw inquiry")
    product_name: str = Field("NexaDesk", description="Product name")
    product_version: str = Field(..., description="Target product version, e.g. v1.0, v2.0, v3.0")


class QueryRewriteResponse(BaseModel):
    """Structured response from query rewriter module."""
    original_query: str
    rewritten_query: str
    search_keywords: List[str]
    intent: str
    rewriter_used: str  # 'gemini-1.5-flash' or 'heuristic_fallback'
    reasoning: Optional[str] = None


class HybridRetrievalRequest(BaseModel):
    """Request payload for version-aware hybrid retrieval."""
    customer_question: str = Field(..., description="Customer inquiry or raw search query")
    product_name: str = Field("NexaDesk", description="Product name")
    product_version: str = Field(..., description="Strict target product version (e.g. v1.0, v2.0, v3.0)")
    enable_query_rewriting: bool = Field(True, description="Whether to transform query via Gemini rewriter")
    retrieval_mode: str = Field("hybrid", description="'hybrid', 'dense_only', or 'sparse_only'")
    top_k: int = Field(4, ge=1, le=20, description="Number of candidate chunks to retrieve")
    dense_weight: float = Field(0.6, ge=0.0, le=1.0, description="Weight for dense semantic vector retrieval in RRF")
    sparse_weight: float = Field(0.4, ge=0.0, le=1.0, description="Weight for sparse BM25 retrieval in RRF")
    similarity_threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity / RRF score threshold")
    document_type: Optional[str] = Field(None, description="Filter by file type (pdf, docx, txt, md)")
    document_name: Optional[str] = Field(None, description="Filter by specific document filename")


class RetrievedChunkItem(BaseModel):
    """Normalized retrieved chunk item with detailed scoring transparency."""
    chunk_id: str
    document_id: str
    document_name: str
    product_name: str
    product_version: str
    document_type: str
    section_title: str
    page_number: int
    text_content: str
    dense_score: Optional[float] = None
    sparse_score: Optional[float] = None
    rrf_score: float
    rank: int
    retrieval_method: str  # 'hybrid', 'dense', 'bm25'
    metadata: Dict[str, Any] = {}


class HybridRetrievalResponse(BaseModel):
    """Structured response for hybrid retrieval containing debugging and transparency metrics."""
    original_query: str
    rewritten_query: Optional[str] = None
    search_keywords: List[str] = []
    product_name: str
    product_version: str
    retrieval_mode: str
    total_retrieved: int
    results: List[RetrievedChunkItem]
    status_message: str
    diagnostics: Dict[str, Any] = {}


class RetrievalComparisonRequest(BaseModel):
    """Request payload to compare retrieval approaches on the same query."""
    customer_question: str = Field(..., description="Informal customer question to evaluate")
    product_version: str = Field(..., description="Target version (v1.0, v2.0, v3.0)")
    product_name: str = Field("NexaDesk", description="Product name")
    top_k: int = Field(3, ge=1, le=10, description="Top K results per method")


class RetrievalComparisonResponse(BaseModel):
    """Side-by-side comparison across: raw dense, rewritten dense, and rewritten hybrid."""
    original_query: str
    rewritten_query: str
    search_keywords: List[str]
    product_version: str
    raw_dense_results: List[RetrievedChunkItem]
    rewritten_dense_results: List[RetrievedChunkItem]
    rewritten_hybrid_results: List[RetrievedChunkItem]
    summary_analysis: Dict[str, Any]


# ==============================================================================
# Phase 5: LLM Response Generation, Grounded Synthesis & Citation Schemas
# ==============================================================================

class CitationItem(BaseModel):
    """Structured verifiable citation reference attached to generated answers."""
    citation_id: int
    document_name: str
    document_type: str
    section_title: str
    page_number: int
    chunk_id: str
    snippet: str
    relevance_score: float


class CustomerEnquiryRequest(BaseModel):
    """Payload for conversational customer enquiry with LLM answer synthesis."""
    question: str = Field(..., description="Customer question or support enquiry")
    product_version: str = Field(..., description="Strict target product version, e.g. v1.0, v2.0, v3.0")
    product_name: str = Field("NexaDesk", description="Product name")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for multi-turn thread tracking")
    session_id: Optional[str] = Field(None, description="Alias for conversation_id")
    retrieval_mode: str = Field("hybrid", description="'hybrid', 'dense_only', or 'sparse_only'")
    top_k: int = Field(4, ge=1, le=10, description="Max candidate chunks for context window")
    enable_rewriting: bool = Field(True, description="Enable query rewriting for informal inquiries")
    temperature: float = Field(0.1, ge=0.0, le=1.0, description="Sampling temperature for LLM synthesis")
    api_key: Optional[str] = Field(None, description="Optional user-supplied Gemini API key")


class CustomerEnquiryResponse(BaseModel):
    """
    Final customer enquiry response envelope matching exact capstone specification:
    - answer
    - citations
    - product_version
    - rewritten_query
    - retrieved_sources
    - abstained
    - conversation_id
    """
    answer: str
    citations: List[CitationItem]
    product_version: str
    rewritten_query: Optional[str] = None
    retrieved_sources: List[Dict[str, Any]] = []
    abstained: bool = False
    conversation_id: str
    product_name: str = "NexaDesk"
    original_query: str
    model_used: str = "gemini-1.5-flash"
    latency_ms: float = 0.0
    timestamp: datetime = Field(default_factory=get_utc_now)


class EnquiryHistoryItem(BaseModel):
    """Stored enquiry log entry for audit and evaluation."""
    id: int
    session_id: str
    user_query: str
    product_version: str
    response_text: str
    sources_count: int
    created_at: str


class EnquiryHistoryResponse(BaseModel):
    """List of historical customer inquiries."""
    total_logs: int
    history: List[EnquiryHistoryItem]


