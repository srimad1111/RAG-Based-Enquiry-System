"""
Demonstration script for Phase 4: Query Rewriting and Version-Aware Hybrid Retrieval.
Runs the complete Phase 4 pipeline across informal customer questions, demonstrating:
1. Query Rewriting from informal to technical documentation phrasing.
2. 3-way retrieval strategy comparison:
   - Raw Query + Dense Retrieval
   - Rewritten Query + Dense Retrieval
   - Rewritten Query + Hybrid Retrieval (RRF)
3. Strict version isolation across v1.0, v2.0, and v3.0 without mixing.
4. Non-existent version safety.
"""
import sys
from pathlib import Path

# Add backend to PYTHONPATH
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.pipeline import rag_pipeline
from app.rag.query_rewriter import query_rewriter


def run_demonstration():
    print("=" * 90)
    print("PHASE 4 DEMONSTRATION: QUERY REWRITING & VERSION-AWARE HYBRID RETRIEVAL")
    print("=" * 90)

    # 1. Test Query Rewriting (Part A)
    informal_queries = [
        "Why can't I schedule my reports like before?",
        "How much do I have to pay per user and can I get a discount for paying for a whole year?",
        "Can someone explain how round robin assignment works?",
        "What are the admin role permissions and how do I add agents?"
    ]

    print("\n--- PART A: QUERY REWRITING (INFORMAL -> TECHNICAL DOCUMENTATION QUERY) ---")
    for q in informal_queries:
        rw = query_rewriter.rewrite(q, product_name="NexaDesk", product_version="v2.0")
        print(f"\n[Customer Inquiry]: \"{q}\"")
        print(f" -> Rewritten Query: \"{rw['rewritten_query']}\"")
        print(f" -> Intent: {rw['intent']} | Keywords: {rw['search_keywords']} | Rewriter: {rw['rewriter_used']}")

    # 2. Test 3-Way Strategy Comparison on the prompt's example query (Part E)
    test_question = "Why can't I schedule my reports like before?"
    target_version = "v2.0"
    print("\n" + "=" * 90)
    print(f"--- PART E: 3-WAY RETRIEVAL COMPARISON on \"{test_question}\" (Version: {target_version}) ---")
    print("=" * 90)

    comparison = rag_pipeline.compare_retrieval_methods(
        customer_question=test_question,
        product_version=target_version,
        top_k=2
    )

    print(f"\nOriginal Query:  \"{comparison['original_query']}\"")
    print(f"Rewritten Query: \"{comparison['rewritten_query']}\"")

    print("\n[Method 1: Raw Query + Dense Retrieval (Informal text into ChromaDB)]")
    for r in comparison["raw_dense_results"]:
        print(f"  Rank {r['rank']}: {r['document_name']} (§ {r['section_title']}) - Dense Sim: {r['dense_score']:.3f}")
        print(f"    Excerpt: {r['text_content'][:130].strip()}...")

    print("\n[Method 2: Rewritten Query + Dense Retrieval (Technical text into ChromaDB)]")
    for r in comparison["rewritten_dense_results"]:
        print(f"  Rank {r['rank']}: {r['document_name']} (§ {r['section_title']}) - Dense Sim: {r['dense_score']:.3f}")
        print(f"    Excerpt: {r['text_content'][:130].strip()}...")

    print("\n[Method 3: Rewritten Query + Hybrid Retrieval (RRF Dense + BM25 Fusion)]")
    for r in comparison["rewritten_hybrid_results"]:
        dense_s = f"{r['dense_score']:.3f}" if r['dense_score'] is not None else "None"
        sparse_s = f"{r['sparse_score']:.3f}" if r['sparse_score'] is not None else "None"
        print(f"  Rank {r['rank']}: {r['document_name']} (§ {r['section_title']}) - RRF: {r['rrf_score']*100:.1f}% [Dense: {dense_s}, BM25: {sparse_s}]")
        print(f"    Excerpt: {r['text_content'][:130].strip()}...")

    # 3. Test Cross-Version Disambiguation (Parts B & D)
    print("\n" + "=" * 90)
    print(f"--- PARTS B & D: STRICT MULTI-VERSION HYBRID ISOLATION FOR \"{test_question}\" ---")
    print("=" * 90)

    for ver in ["v1.0", "v2.0", "v3.0"]:
        res = rag_pipeline.execute_hybrid_retrieval(
            customer_question=test_question,
            product_version=ver,
            enable_query_rewriting=True,
            retrieval_mode="hybrid",
            top_k=1
        )
        top_chunk = res["results"][0] if res["results"] else None
        print(f"\n--- Scope: [{ver}] (Retrieved {res['total_retrieved']} chunks) ---")
        if top_chunk:
            print(f"Doc: {top_chunk['document_name']} | Section: {top_chunk['section_title']} | RRF Score: {top_chunk['rrf_score']*100:.1f}%")
            print(f"Content:\n{top_chunk['text_content'].strip()}")

    # 4. Test Non-Existent Version Safety (Part B)
    print("\n" + "=" * 90)
    print("--- PART B: NON-EXISTENT VERSION SAFETY (v99.0) ---")
    print("=" * 90)
    safety_res = rag_pipeline.execute_hybrid_retrieval(
        customer_question=test_question,
        product_version="v99.0"
    )
    print(f"Total Chunks Retrieved: {safety_res['total_retrieved']}")
    print(f"Status Message: {safety_res['status_message']}")


if __name__ == "__main__":
    run_demonstration()

