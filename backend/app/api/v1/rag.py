from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from app.core.logging import logger
from app.models.schemas import (
    IndexingSyncResponse,
    StandardApiResponse,
    VectorSearchRequest,
    VectorSearchResponse,
    VectorSearchResultItem,
    QueryRewriteRequest,
    QueryRewriteResponse,
    HybridRetrievalRequest,
    HybridRetrievalResponse,
    RetrievalComparisonRequest,
    RetrievalComparisonResponse,
    RetrievedChunkItem,
)
from app.rag.pipeline import rag_pipeline
from app.rag.query_rewriter import query_rewriter
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


# ==============================================================================
# Phase 4: Query Rewriting and Version-Aware Hybrid Retrieval Endpoints
# ==============================================================================

@router.post(
    "/rewrite",
    response_model=QueryRewriteResponse,
    summary="Transform Informal Inquiry into Technical Query (Phase 4 Part A)",
    description=(
        "Transforms a conversational or frustrated customer support question into formal, "
        "documentation-oriented search queries using Gemini API (with heuristic fallback)."
    )
)
def rewrite_customer_query(payload: QueryRewriteRequest) -> QueryRewriteResponse:
    try:
        res = query_rewriter.rewrite(
            customer_question=payload.customer_question,
            product_name=payload.product_name,
            product_version=payload.product_version
        )
        return QueryRewriteResponse(**res)
    except Exception as e:
        logger.error(f"Error during query rewriting: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query rewriting failed: {str(e)}"
        )


@router.post(
    "/retrieve",
    response_model=HybridRetrievalResponse,
    summary="Version-Aware Hybrid Retrieval (Phase 4 Part C & D)",
    description=(
        "Executes the full Phase 4 retrieval sequence: Query Rewriting -> Version Filtering -> "
        "Dense ChromaDB Retrieval -> Sparse BM25 Retrieval -> Reciprocal Rank Fusion (RRF). "
        "Strictly prevents other product versions from leaking into context."
    )
)
def retrieve_hybrid_context(payload: HybridRetrievalRequest) -> HybridRetrievalResponse:
    try:
        data = rag_pipeline.execute_hybrid_retrieval(
            customer_question=payload.customer_question,
            product_version=payload.product_version,
            product_name=payload.product_name,
            enable_query_rewriting=payload.enable_query_rewriting,
            retrieval_mode=payload.retrieval_mode,
            top_k=payload.top_k,
            dense_weight=payload.dense_weight,
            sparse_weight=payload.sparse_weight,
            similarity_threshold=payload.similarity_threshold,
            document_type=payload.document_type,
            document_name=payload.document_name
        )
        # Convert chunk dicts to schema items
        chunk_items = [RetrievedChunkItem(**item) for item in data["results"]]
        data["results"] = chunk_items
        return HybridRetrievalResponse(**data)
    except Exception as e:
        logger.error(f"Error during hybrid retrieval: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid retrieval failed: {str(e)}"
        )


@router.post(
    "/compare",
    response_model=RetrievalComparisonResponse,
    summary="Compare Retrieval Methods (Phase 4 Part E)",
    description=(
        "Compares three retrieval strategies on the same customer question: "
        "1. Raw Query + Dense Retrieval, 2. Rewritten Query + Dense Retrieval, 3. Rewritten Query + Hybrid Retrieval."
    )
)
def compare_retrieval_strategies(payload: RetrievalComparisonRequest) -> RetrievalComparisonResponse:
    try:
        data = rag_pipeline.compare_retrieval_methods(
            customer_question=payload.customer_question,
            product_version=payload.product_version,
            product_name=payload.product_name,
            top_k=payload.top_k
        )
        # Convert items
        data["raw_dense_results"] = [RetrievedChunkItem(**r) for r in data["raw_dense_results"]]
        data["rewritten_dense_results"] = [RetrievedChunkItem(**r) for r in data["rewritten_dense_results"]]
        data["rewritten_hybrid_results"] = [RetrievedChunkItem(**r) for r in data["rewritten_hybrid_results"]]
        return RetrievalComparisonResponse(**data)
    except Exception as e:
        logger.error(f"Error comparing retrieval methods: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval comparison failed: {str(e)}"
        )


