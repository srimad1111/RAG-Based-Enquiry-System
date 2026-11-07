"""
Phase 6: Automated RAG Triad Evaluation Runner Script.
Executes the evaluation benchmark suite over NexaDesk v1.0, v2.0, and v3.0 documentation,
computes RAG Triad scores, version isolation accuracy, latency percentiles,
and outputs a formatted report to the terminal and disk.
"""
import sys
import json
from pathlib import Path

# Add backend to PYTHONPATH
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.connection import init_database
from app.rag.pipeline import rag_pipeline
from app.services.evaluation_service import evaluation_service


def main():
    print("=" * 85)
    print("   PROJECT 32: NEXADESK RAG CUSTOMER ENQUIRY SYSTEM - EVALUATION BENCHMARK   ")
    print("=" * 85)

    # 1. Initialize databases
    print("\n[1/3] Verifying SQLite database and ChromaDB vector store synchrony...")
    init_database()
    sync_res = rag_pipeline.sync_all_from_sqlite()
    print(f"      Status: Synchronized {sync_res['total_indexed_in_chroma']} chunks in ChromaDB.")

    # 2. Run Benchmark Suite
    print("\n[2/3] Executing RAG Triad Benchmark over curated multi-version dataset...")
    report = evaluation_service.run_benchmark_suite()

    # 3. Print Results Summary
    print("\n" + "=" * 85)
    print("   EVALUATION BENCHMARK RESULTS SUMMARY   ")
    print("=" * 85)
    print(f"Timestamp:              {report['timestamp']}")
    print(f"Total Test Cases:       {report['total_benchmark_cases']}")
    print(f"Overall Status:         {report['overall_status']}")

    triad = report["rag_triad_scores"]
    print("\n[RAG Triad Metrics]:")
    print(f"  - Context Relevance:            {triad['context_relevance'] * 100:.1f}% (Precision@K / MRR)")
    print(f"  - Groundedness / Faithfulness:  {triad['groundedness_faithfulness'] * 100:.1f}% (Factual adherence to docs)")
    print(f"  - Answer Relevance:             {triad['answer_relevance'] * 100:.1f}% (Alignment with question intent)")

    safety = report["version_safety"]
    print("\n[Version Safety & Isolation]:")
    print(f"  - Version Isolation Accuracy:   {safety['version_isolation_accuracy_percentage']:.1f}% (Zero cross-version bleed)")
    print(f"  - Cross-Version Leakage:        {'YES (WARNING)' if safety['cross_version_leakage_detected'] else 'NONE (VERIFIED)'}")

    abstain = report["abstention_guard"]
    print("\n[Abstention & Refusal Guard]:")
    print(f"  - Abstention Recall:            {abstain['abstention_recall_percentage']:.1f}% (Correct refusal of out-of-domain queries)")
    print(f"  - False Abstention Rate:        {abstain['false_abstention_rate_percentage']:.1f}% (False refusals on valid queries)")

    lat = report["latency_benchmarks"]
    print("\n[Latency Benchmarks]:")
    print(f"  - Average Latency:              {lat['avg_latency_ms']:.2f} ms")
    print(f"  - Median (p50):                 {lat['p50_ms']:.2f} ms")
    print(f"  - 95th Percentile (p95):        {lat['p95_ms']:.2f} ms")

    print("\n[Per-Version Performance Breakdown]:")
    for ver, data in report["per_version_performance"].items():
        print(f"  - {ver}: {data['total_queries']} queries | Context Rel: {data['context_relevance']*100:.1f}% | Grounded: {data['groundedness']*100:.1f}% | Isolation: {data['version_isolation_accuracy']:.1f}% | Latency: {data['avg_latency_ms']} ms")

    print("\n" + "=" * 85)
    print(f"[3/3] Detailed report successfully saved to: backend/data/evaluation/results/evaluation_report.json")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    main()
