"""
Phase 7: Single Command CLI Runner for Comprehensive RAG Evaluation.
Usage:
  python -m app.evaluation.run_evaluation
  or
  python scripts/run_evaluation.py
"""
import sys
import time
from pathlib import Path

# Add backend directory to sys.path if invoked from scripts/ or root
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.connection import init_database
from app.rag.pipeline import rag_pipeline
from app.evaluation.evaluator import (
    ComprehensiveRAGEvaluator,
    CSV_REPORT_FILE,
    SUMMARY_JSON_FILE,
    DOCS_ERROR_REPORT_FILE,
)


def run_evaluation_cli():
    print("=" * 86)
    print("   PROJECT 32: NEXADESK RAG CUSTOMER ENQUIRY SYSTEM - COMPREHENSIVE BENCHMARK   ")
    print("=" * 86)

    # 1. Database & ChromaDB Synchronization
    print("\n[1/3] Synchronizing SQLite document chunks with ChromaDB and BM25 index...")
    init_database()
    sync_res = rag_pipeline.sync_all_from_sqlite()
    print(f"      Verified: {sync_res['total_indexed_in_chroma']} chunks indexed across versions.")

    # 2. Run Comprehensive Evaluator
    evaluator = ComprehensiveRAGEvaluator()
    total_q = len(evaluator.dataset)
    print(f"\n[2/3] Executing Evaluation Suite over {total_q} Ground-Truth Test Questions...")
    start_t = time.time()
    summary = evaluator.run_full_evaluation()
    total_duration = time.time() - start_t

    # 3. Print Rich Results Dashboard
    print("\n" + "=" * 86)
    print("   PHASE 7: COMPREHENSIVE RAG EVALUATION BENCHMARK RESULTS   ")
    print("=" * 86)
    print(f"Timestamp:                    {summary['timestamp']}")
    print(f"Total Benchmark Test Cases:   {summary['total_benchmark_cases']}")
    print(f"In-Domain Questions:          {summary['in_domain_cases']}")
    print(f"Out-of-Domain (Abstentions):  {summary['out_of_domain_cases']}")
    print(f"Evaluation Runtime:           {total_duration:.2f} seconds")

    print("\n" + "-" * 86)
    print("1. 3-WAY RETRIEVAL METHOD COMPARISON (Configs A, B, C)")
    print("-" * 86)
    rc = summary["retrieval_comparison"]
    print(f"{'Retrieval Configuration':<36} | {'Recall@1':<10} | {'Recall@3':<10} | {'Recall@5':<10} | {'MRR':<8}")
    print("-" * 86)
    print(f"{'Config A (Original + Dense)':<36} | {rc['config_a_original_dense']['recall_1']:>9}% | {rc['config_a_original_dense']['recall_3']:>9}% | {rc['config_a_original_dense']['recall_5']:>9}% | {rc['config_a_original_dense']['mrr']:>8.3f}")
    print(f"{'Config B (Rewritten + Dense)':<36} | {rc['config_b_rewritten_dense']['recall_1']:>9}% | {rc['config_b_rewritten_dense']['recall_3']:>9}% | {rc['config_b_rewritten_dense']['recall_5']:>9}% | {rc['config_b_rewritten_dense']['mrr']:>8.3f}")
    print(f"{'Config C (Rewritten + Hybrid RRF)':<36} | {rc['config_c_rewritten_hybrid']['recall_1']:>9}% | {rc['config_c_rewritten_hybrid']['recall_3']:>9}% | {rc['config_c_rewritten_hybrid']['recall_5']:>9}% | {rc['config_c_rewritten_hybrid']['mrr']:>8.3f}")
    print("-" * 86)
    print(f"  * Query Rewriting Uplift:   +{rc['query_rewriting_improvement_mrr']} MRR gain over raw questions")
    print(f"  * Hybrid RRF Fusion Uplift: +{rc['hybrid_fusion_improvement_mrr']} MRR gain over raw questions")

    print("\n" + "-" * 86)
    print("2. VERSION-AWARENESS & ISOLATION ACCURACY")
    print("-" * 86)
    va = summary["version_awareness"]
    print(f"  * Version Correctness Rate:        {va['version_correctness_percentage']}% (Zero temporal version bleed)")
    print(f"  * Cross-Version Contaminations:    {va['cross_version_contaminations_detected']} detected")
    for ver, d in va.get("per_version", {}).items():
        print(f"    - NexaDesk {ver:<5}: Correctness {d['version_correctness_pct']:>5.1f}% | Faithfulness: {d['faithfulness']:>5.3f} | Latency: {d['avg_latency_ms']:>6.1f} ms")

    print("\n" + "-" * 86)
    print("3. ANSWER QUALITY & CITATIONS")
    print("-" * 86)
    aq = summary["answer_quality"]
    print(f"  * Groundedness / Faithfulness:     {(aq['faithfulness'] * 100):.1f}% (Factual adherence to retrieved docs)")
    print(f"  * Answer Relevance:                {(aq['answer_relevance'] * 100):.1f}% (Direct question address)")
    print(f"  * Citation Correctness:            {(aq['citation_correctness'] * 100):.1f}% (Valid chunk anchors)")
    print(f"  * Citation Completeness:           {(aq['citation_completeness'] * 100):.1f}% (Expected facts cited)")
    print(f"  * Unsupported Claims:              {aq['unsupported_claims_detected']} detected")

    print("\n" + "-" * 86)
    print("4. ABSTENTION & REFUSAL GUARD")
    print("-" * 86)
    ab = summary["abstention_evaluation"]
    print(f"  * Abstention Recall:               {ab['abstention_recall_percentage']}% (Out-of-domain questions refused)")
    print(f"  * Abstention Precision:            {ab['abstention_precision_percentage']}% (Legitimate abstentions)")
    print(f"  * Correct Abstention Rate:         {ab['correct_abstention_rate_percentage']}% (Overall abstention accuracy)")

    print("\n" + "-" * 86)
    print("5. SUPPORT ESCALATION AVOIDANCE (Estimated)")
    print("-" * 86)
    esc = summary["support_escalation_avoidance"]
    print(f"  * Estimated Escalation Avoidance:  {esc['estimated_escalation_avoidance_percentage']}%")
    print(f"  * Successfully Resolved Cases:     {esc['resolved_cases_count']} of {esc['total_in_domain']} in-domain queries")
    print(f"    Note: {esc['metric_definition']}")

    print("\n" + "-" * 86)
    print("6. LATENCY PERCENTILES")
    print("-" * 86)
    lat = summary["latency_benchmarks"]
    print(f"  * Average: {lat['avg_latency_ms']} ms | p50 (Median): {lat['p50_ms']} ms | p90: {lat['p90_ms']} ms | p95: {lat['p95_ms']} ms")

    print("\n" + "=" * 86)
    print("7. GENERATED EVALUATION REPORTS & ARTIFACTS")
    print("=" * 86)
    print(f"  [CSV Dataset Results] : {CSV_REPORT_FILE}")
    print(f"  [Summary JSON Report] : {SUMMARY_JSON_FILE}")
    print(f"  [Markdown Error Doc]  : {DOCS_ERROR_REPORT_FILE}")
    print("=" * 86 + "\n")


if __name__ == "__main__":
    run_evaluation_cli()

