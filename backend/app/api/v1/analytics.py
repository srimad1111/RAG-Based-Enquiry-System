"""
Phase 6: Analytics & RAG Evaluation API Endpoints.
Surfaces academic evaluation metrics, RAG Triad scores, version isolation rates,
and benchmark execution triggers.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.logging import logger
from app.services.evaluation_service import evaluation_service

router = APIRouter(prefix="/analytics", tags=["System Analytics & Evaluation"])


@router.get(
    "/overview",
    summary="Get System & RAG Triad Analytics Overview",
    description="Returns aggregate metrics including enquiries served, RAG triad scores, version isolation accuracy, and latency percentiles."
)
def get_analytics_overview() -> Dict[str, Any]:
    try:
        return evaluation_service.get_system_metrics_overview()
    except Exception as e:
        logger.error(f"Error fetching analytics overview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not load analytics overview: {str(e)}"
        )


@router.get(
    "/runs",
    summary="List Evaluation Benchmark Runs",
    description="Returns all recorded benchmark runs including live Qwen inference and offline baseline."
)
def list_evaluation_runs() -> List[Dict[str, Any]]:
    try:
        return evaluation_service.get_runs_index()
    except Exception as e:
        logger.error(f"Error fetching evaluation runs: {e}", exc_info=True)
        return []


@router.get(
    "/report",
    summary="Get Evaluation Benchmark Report",
    description="Fetches a specific evaluation run report or the latest report."
)
def get_evaluation_report(run_file: Optional[str] = Query(None, description="Specific run JSON filename")) -> Dict[str, Any]:
    try:
        report = evaluation_service.get_report_by_name(run_file)
        if not report:
            return {
                "status": "empty",
                "message": "No evaluation benchmark has been executed yet. Run the benchmark to compute RAG Triad scores."
            }
        return report
    except Exception as e:
        logger.error(f"Error fetching evaluation report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not load evaluation report: {str(e)}"
        )


@router.post(
    "/evaluate",
    summary="Trigger RAG Triad Evaluation Benchmark",
    description="Executes the full evaluation suite over the multi-version benchmark dataset and generates a fresh report."
)
def trigger_evaluation_benchmark() -> Dict[str, Any]:
    try:
        report = evaluation_service.run_benchmark_suite()
        return report
    except Exception as e:
        logger.error(f"Error executing evaluation benchmark: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark execution failed: {str(e)}"
        )

