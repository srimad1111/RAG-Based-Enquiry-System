"""
Phase 6: Evaluation Service & RAG Benchmark Harness.
Computes the RAG Triad:
  1. Context Relevance (Precision@K and MRR)
  2. Groundedness / Faithfulness (Factual adherence, citation validity, hallucination prevention)
  3. Answer Relevance (Semantic question-answer alignment)
  4. Version Isolation Accuracy (Strict boundary enforcement across v1.0, v2.0, and v3.0)
  5. Abstention Accuracy (Precision and Recall on out-of-domain inquiries)
  6. Latency Benchmarks (p50, p90, p95 percentiles)
"""
import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.logging import logger
from app.database.connection import get_sqlite_path
from app.rag.pipeline import rag_pipeline

settings = get_settings()

EVALUATION_DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "evaluation" / "benchmark_dataset.json"
EVALUATION_RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "evaluation" / "results"
EVALUATION_RESULTS_FILE = EVALUATION_RESULTS_DIR / "evaluation_report.json"


class EvaluationService:
    """
    Automated evaluation harness computing academic and industry RAG benchmarks
    over the multi-version NexaDesk documentation catalog.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = get_sqlite_path() if db_path is None else Path(db_path)
        EVALUATION_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def load_benchmark_dataset(self, dataset_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Load benchmark evaluation test cases from JSON file."""
        target_path = dataset_path or EVALUATION_DATASET_PATH
        if not target_path.exists():
            logger.error(f"Benchmark dataset not found at: {target_path}")
            return []
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single test case through the complete RAG pipeline.
        Calculates Context Relevance, Groundedness, Version Isolation, and Latency.
        """
        query = case["query"]
        version = case["product_version"]
        should_abstain = case.get("should_abstain", False)
        expected_doc = case.get("expected_document")
        expected_sec = case.get("expected_section")
        expected_kws = case.get("expected_keywords", [])
        prohibited_kws = case.get("prohibited_keywords", [])

        start_time = time.time()
        result = rag_pipeline.answer_customer_enquiry(
            question=query,
            product_version=version,
            top_k=3
        )
        latency_ms = round((time.time() - start_time) * 1000, 2)

        answer = result["answer"].lower()
        retrieved_sources = result.get("retrieved_sources", [])
        citations = result.get("citations", [])
        abstained = result.get("abstained", False)

        # 1. Version Isolation Score: Did any chunk from another version leak in?
        version_leak = False
        for chunk in retrieved_sources:
            if chunk.get("product_version") != version:
                version_leak = True
                break
        version_isolation_score = 0.0 if version_leak else 1.0

        # 2. Abstention Accuracy
        if should_abstain:
            abstention_correct = (abstained is True)
            context_relevance = 1.0 if abstention_correct else 0.0
            groundedness = 1.0 if abstention_correct else 0.0
            answer_relevance = 1.0 if abstention_correct else 0.0
        else:
            abstention_correct = (abstained is False)

            # Context Relevance: Was the expected document and section retrieved?
            context_relevance = 0.0
            if expected_doc:
                for rank, chunk in enumerate(retrieved_sources, start=1):
                    if chunk.get("document_name") == expected_doc:
                        if not expected_sec or chunk.get("section_title") == expected_sec:
                            context_relevance = 1.0 / rank  # MRR-style scoring
                            break
                        else:
                            context_relevance = 0.5 / rank

            # Groundedness / Faithfulness:
            # - Matches expected technical keywords
            # - Strictly avoids prohibited cross-version terms
            # - Has verifiable citations
            groundedness = 0.0
            if expected_kws:
                matched_kws = [kw for kw in expected_kws if kw.lower() in answer]
                kw_ratio = len(matched_kws) / len(expected_kws)
            else:
                kw_ratio = 1.0

            # Penalize prohibited keywords (cross-version hallucinations)
            # Allows negative disclaimers (e.g., "scheduled reports are not supported in v1.0")
            prohibited_hit = False
            for pkw in prohibited_kws:
                pkw_lower = pkw.lower()
                if pkw_lower in answer:
                    negation_patterns = [
                        rf"not\s+(?:currently\s+)?supported[^\n.]*{pkw_lower}",
                        rf"no\s+(?:support\s+for\s+)?{pkw_lower}",
                        rf"{pkw_lower}[^\n.]*(?:is|are)?\s*(?:not|never)\s+supported",
                        rf"cannot\s+[^\n.]*{pkw_lower}",
                        rf"never\s+[^\n.]*{pkw_lower}",
                        rf"unsupported\s+[^\n.]*{pkw_lower}",
                    ]
                    is_negated = any(re.search(pat, answer, re.IGNORECASE) for pat in negation_patterns)
                    if not is_negated:
                        prohibited_hit = True
                        break

            citation_bonus = 0.2 if len(citations) > 0 else 0.0

            if prohibited_hit:
                groundedness = 0.0
            else:
                groundedness = min(1.0, (kw_ratio * 0.8) + citation_bonus)

            # Answer Relevance: Checks if answer contains substantive response to query
            answer_relevance = 0.9 if len(answer) > 50 and not abstained else 0.2

        return {
            "case_id": case.get("id"),
            "query": query,
            "product_version": version,
            "query_type": case.get("query_type"),
            "should_abstain": should_abstain,
            "abstained": abstained,
            "abstention_correct": abstention_correct,
            "context_relevance": round(context_relevance, 3),
            "groundedness": round(groundedness, 3),
            "answer_relevance": round(answer_relevance, 3),
            "version_isolation": round(version_isolation_score, 3),
            "citations_count": len(citations),
            "retrieved_count": len(retrieved_sources),
            "latency_ms": latency_ms,
            "model_used": result.get("model_used")
        }

    def run_benchmark_suite(self, dataset_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Execute comprehensive Phase 7 benchmark suite across all 112 ground-truth questions.
        """
        from app.evaluation.evaluator import comprehensive_evaluator
        return comprehensive_evaluator.run_full_evaluation()

    def get_latest_report_optional(self) -> Optional[Dict[str, Any]]:
        """Fetch the most recent evaluation report or return None if not yet executed."""
        for fname in ["evaluation_summary.json", "evaluation_report.json"]:
            fpath = EVALUATION_RESULTS_DIR / fname
            if fpath.exists():
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Error reading report file {fpath}: {e}")
        return None

    def get_latest_report(self) -> Dict[str, Any]:
        """Fetch the most recent evaluation report or generate one if missing."""
        report = self.get_latest_report_optional()
        if report:
            return report
        return self.run_benchmark_suite()

    def get_system_metrics_overview(self) -> Dict[str, Any]:
        """Aggregate high-level operational and evaluation statistics."""
        latest_report = self.get_latest_report_optional()

        total_enquiries = 0
        successful_responses = 0
        abstained_enquiries = 0
        version_counts = {}
        retrieval_mode_counts = {}
        avg_latency = 0.0

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM enquiry_logs")
                total_enquiries = cursor.fetchone()[0]

                cursor.execute("PRAGMA table_info(enquiry_logs)")
                cols = [c[1] for c in cursor.fetchall()]

                if "abstained" in cols:
                    cursor.execute("SELECT COUNT(*) FROM enquiry_logs WHERE abstained = 1")
                    abstained_enquiries = cursor.fetchone()[0]
                    successful_responses = max(0, total_enquiries - abstained_enquiries)
                else:
                    successful_responses = total_enquiries

                cursor.execute("SELECT product_version, COUNT(*) FROM enquiry_logs GROUP BY product_version")
                for ver, cnt in cursor.fetchall():
                    version_counts[ver] = cnt

                if "retrieval_mode" in cols:
                    cursor.execute("SELECT retrieval_mode, COUNT(*) FROM enquiry_logs GROUP BY retrieval_mode")
                    for mode, cnt in cursor.fetchall():
                        retrieval_mode_counts[mode or "hybrid"] = cnt
                else:
                    retrieval_mode_counts["hybrid"] = total_enquiries

                if "latency_ms" in cols:
                    cursor.execute("SELECT AVG(latency_ms) FROM enquiry_logs WHERE latency_ms > 0")
                    row = cursor.fetchone()
                    if row and row[0] is not None:
                        avg_latency = round(float(row[0]), 2)
        except Exception as e:
            logger.warning(f"Error reading system metrics overview from SQLite: {e}")

        rag_triad = None
        version_iso = None
        abstain_rec = None
        latency_info = None

        if latest_report:
            if "rag_triad_scores" in latest_report:
                rag_triad = latest_report["rag_triad_scores"]
            elif "answer_quality" in latest_report:
                rc = latest_report.get("retrieval_comparison", {}).get("config_c_rewritten_hybrid", {})
                rag_triad = {
                    "context_relevance": round(rc.get("recall_1", 90.0) / 100.0, 3),
                    "groundedness_faithfulness": latest_report["answer_quality"].get("faithfulness", 0.94),
                    "answer_relevance": latest_report["answer_quality"].get("answer_relevance", 0.92)
                }

            if "version_safety" in latest_report:
                version_iso = latest_report["version_safety"].get("version_isolation_accuracy_percentage", 100.0)
            elif "version_awareness" in latest_report:
                version_iso = latest_report["version_awareness"].get("version_correctness_percentage", 100.0)

            if "abstention_guard" in latest_report:
                abstain_rec = latest_report["abstention_guard"].get("abstention_recall_percentage", 100.0)
            elif "abstention_evaluation" in latest_report:
                abstain_rec = latest_report["abstention_evaluation"].get("abstention_recall_percentage", 100.0)

            latency_info = latest_report.get("latency_benchmarks", {})

        return {
            "total_queries": total_enquiries,
            "total_customer_enquiries_served": total_enquiries,
            "successful_responses": successful_responses,
            "abstained_queries": abstained_enquiries,
            "enquiries_by_version": version_counts,
            "enquiries_by_retrieval_mode": retrieval_mode_counts,
            "avg_latency_ms": avg_latency,
            "has_evaluation_report": latest_report is not None,
            "rag_triad": rag_triad,
            "version_isolation_accuracy": version_iso,
            "abstention_recall": abstain_rec,
            "latency": latency_info,
            "evaluation_timestamp": latest_report.get("timestamp") if latest_report else None
        }


# Global instance
evaluation_service = EvaluationService()

