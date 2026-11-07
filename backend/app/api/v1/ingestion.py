from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from app.core.config import get_settings
from app.core.logging import logger
from app.models.schemas import (
    ChunkDetail,
    DocumentListResponse,
    DocumentOverviewResponse,
    DocumentRecord,
    DocumentUploadResponse,
    DocumentVersionSummary,
    IngestionStatsResponse,
    StandardApiResponse,
)
from app.services.document_service import document_service
from app.services.ingestion_service import ingestion_service

settings = get_settings()
router = APIRouter(prefix="/documents", tags=["Documents & Ingestion"])


# ==============================================================================
# Static / Catalog Overview Routes (Declared First to avoid {document_id} clash)
# ==============================================================================

@router.get(
    "/overview",
    response_model=DocumentOverviewResponse,
    summary="Get Overview of Base Documentation Versions",
    description="Returns source files in data/documents/NexaDesk across v1.0, v2.0, and v3.0."
)
def get_documents_overview() -> DocumentOverviewResponse:
    return document_service.get_all_versions_overview()


@router.get(
    "/stats/overview",
    response_model=IngestionStatsResponse,
    summary="Get Ingestion Statistics",
    description="Returns aggregate counts of ingested documents and chunks grouped by version, file type, and category."
)
def get_ingestion_stats() -> IngestionStatsResponse:
    return ingestion_service.get_stats()


@router.get(
    "/version/{version}",
    response_model=DocumentVersionSummary,
    summary="Get Base Documents by Version",
    description="Returns source documentation files for a specific version: v1.0, v2.0, or v3.0."
)
def get_version_documents(version: str) -> DocumentVersionSummary:
    return document_service.get_version_summary(version)


# ==============================================================================
# Ingested Documents Management (CRUD & Upload)
# ==============================================================================

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin Upload Document (PDF, DOCX, TXT, MD)",
    description=(
        "Uploads a company documentation file, extracts text and layout metadata, "
        "chunks content using configurable recursive splitting, detects duplicates, "
        "and indexes metadata into SQLite."
    )
)
def upload_document(
    file: UploadFile = File(..., description="Document file (.pdf, .docx, .txt, .md)"),
    product_name: str = Form("NexaDesk", description="Product name (e.g. NexaDesk)"),
    product_version: str = Form(..., description="Target release version (e.g. v1.0, v2.0, v3.0)"),
    category: str = Form("User Guide", description="Documentation category (e.g. User Guide, API, Pricing, SLA)"),
    chunk_size: Optional[int] = Form(None, description="Max chunk size (default: 800)"),
    chunk_overlap: Optional[int] = Form(None, description="Chunk overlap (default: 150)"),
    replace_existing: bool = Form(False, description="Replace if duplicate detected")
) -> DocumentUploadResponse:
    filename = file.filename or "uploaded_document"
    try:
        content_bytes = file.file.read()
        if not content_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        upload_result = ingestion_service.ingest_file(
            file_bytes=content_bytes,
            filename=filename,
            product_name=product_name,
            product_version=product_version,
            category=category,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            replace_existing=replace_existing
        )

        if upload_result.duplicate_detected and not upload_result.replaced_previous:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=upload_result.message
            )

        return upload_result

    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error during upload of '{filename}': {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error uploading '{filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List Ingested Documents",
    description="Retrieve all ingested documents with optional filtering by product_version, category, or document_type."
)
def list_documents(
    product_version: Optional[str] = Query(None, description="Filter by version (e.g. v1.0, v2.0, v3.0)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    document_type: Optional[str] = Query(None, description="Filter by file type (pdf, docx, txt, md)")
) -> DocumentListResponse:
    docs = ingestion_service.list_documents(
        product_version=product_version,
        category=category,
        document_type=document_type
    )
    total_chunks = sum(d.chunk_count for d in docs)
    return DocumentListResponse(
        total_documents=len(docs),
        total_chunks=total_chunks,
        documents=docs,
        filtered_version=product_version
    )


@router.get(
    "/{document_id}",
    response_model=DocumentRecord,
    summary="Get Ingested Document Details",
    description="Retrieve metadata for a specific document by its ID."
)
def get_document_by_id(document_id: str) -> DocumentRecord:
    doc = ingestion_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found."
        )
    return doc


@router.get(
    "/{document_id}/chunks",
    response_model=List[ChunkDetail],
    summary="Get Ingested Document Chunks",
    description="Retrieve all structured chunks and preserved metadata for a specific document."
)
def get_document_chunks(document_id: str) -> List[ChunkDetail]:
    doc = ingestion_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found."
        )
    return ingestion_service.get_document_chunks(document_id)


@router.delete(
    "/{document_id}",
    response_model=StandardApiResponse,
    summary="Delete Ingested Document and Chunks",
    description="Removes the document, its chunks, and associated storage files."
)
def delete_document(document_id: str) -> StandardApiResponse:
    success = ingestion_service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found or already deleted."
        )
    return StandardApiResponse(
        success=True,
        message=f"Document '{document_id}' and all associated chunks were successfully deleted."
    )
