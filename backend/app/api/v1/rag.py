from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from app.core.logging import logger
from app.models.schemas import (
    IndexingSyncResponse,
    StandardApiResponse,
    VectorSearchRequest,
    VectorSearchResponse,
    VectorSearchResultItem,
)
from app.rag.pipeline import rag_pipeline
from app.rag.vector_store import chroma_vector_store

router = APIRouter(prefix="/rag", tags=["Vector Indexing & Retrieval"])


@router.post(
    "/index",
    response_model=IndexingSyncResponse,
    summary="Synchronize SQLite Chunks to ChromaDB",
    description="Reads all ingested document chunks from SQLite and indexes their vector embeddings into ChromaDB."
)
def sync_vector_index() -> IndexingSyncResponse:
    try:
        result = rag_pipeline.sync_all_from_sqlite()
        return IndexingSyncResponse(**result)
    except Exception as e:
        logger.error(f"Error during vector index synchronization: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector indexing failed: {str(e)}"
        )


@router.get(
    "/status",
    summary="Get Vector Indexing Status",
    description="Provides detailed status of ChromaDB vector store, total indexed vectors, version breakdown, and SQLite sync state."
)
def get_indexing_status() -> Dict[str, Any]:
    try:
        return rag_pipeline.get_pipeline_info()
    except Exception as e:
        logger.error(f"Error checking indexing status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve vector index status: {str(e)}"
        )


@router.post(
    "/search",
    response_model=VectorSearchResponse,
    summary="Version-Aware Semantic Vector Search",
    description=(
        "Executes vector similarity search against ChromaDB strictly filtered by product version. "
        "Guarantees that a query like 'What are the report export options?' returns distinct "
        "results for v1.0, v2.0, and v3.0 without cross-version contamination."
    )
)
def search_vector_store(payload: VectorSearchRequest) -> VectorSearchResponse:
    try:
        raw_results = rag_pipeline.search(
            query=payload.query,
            product_version=payload.product_version,
            product_name=payload.product_name,
            document_type=payload.document_type,
            document_name=payload.document_name,
            top_k=payload.top_k
        )

        items = [VectorSearchResultItem(**r) for r in raw_results]
        return VectorSearchResponse(
            query=payload.query,
            product_version=payload.product_version,
            total_results=len(items),
            results=items
        )
    except Exception as e:
        logger.error(f"Vector search failed for '{payload.query}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector search failed: {str(e)}"
        )


@router.post(
    "/reindex",
    response_model=IndexingSyncResponse,
    summary="Reset and Re-Index Vector Store",
    description="Clears all vectors in ChromaDB collection and rebuilds them fresh from SQLite."
)
def reindex_all() -> IndexingSyncResponse:
    try:
        chroma_vector_store.reset_collection()
        result = rag_pipeline.sync_all_from_sqlite()
        return IndexingSyncResponse(**result)
    except Exception as e:
        logger.error(f"Error during re-indexing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Re-indexing failed: {str(e)}"
        )

