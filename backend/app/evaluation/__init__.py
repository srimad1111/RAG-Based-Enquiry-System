"""
Evaluation Framework Package.
Exports comprehensive benchmark dataset, evaluator engine, and report paths.
"""
from app.evaluation.dataset import BENCHMARK_CASES, get_benchmark_dataset
from app.evaluation.evaluator import (
    ComprehensiveRAGEvaluator,
    comprehensive_evaluator,
    CSV_REPORT_FILE,
    SUMMARY_JSON_FILE,
    ERROR_ANALYSIS_FILE,
)

__all__ = [
    "BENCHMARK_CASES",
    "get_benchmark_dataset",
    "ComprehensiveRAGEvaluator",
    "comprehensive_evaluator",
    "CSV_REPORT_FILE",
    "SUMMARY_JSON_FILE",
    "ERROR_ANALYSIS_FILE",
]

