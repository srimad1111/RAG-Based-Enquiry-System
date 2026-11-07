"""
Demonstration script for Phase 3: Version-Aware Vector Retrieval Disambiguation.
Demonstrates that the exact same enquiry yields version-specific, isolated results
across NexaDesk v1.0, v2.0, and v3.0 without cross-version contamination.
"""
import sys
from pathlib import Path

# Add backend to PYTHONPATH
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.pipeline import rag_pipeline


def demonstrate_query(query: str, title: str):
    print("=" * 80)
    print(f"QUERY: \"{query}\"")
    print(f"FOCUS: {title}")
    print("=" * 80)

    for ver in ["v1.0", "v2.0", "v3.0"]:
        results = rag_pipeline.search(query=query, product_version=ver, top_k=1)
        if not results:
            print(f"[{ver}] No results found.")
            continue
        
        top = results[0]
        meta = top["metadata"]
        score = top["similarity_score"]
        print(f"\n--- [{ver}] (Doc: {meta.get('document_name')}, Type: {meta.get('document_type')}, Sim Score: {score:.3f}) ---")
        print(f"Section: {meta.get('section_title')}")
        text = top.get("text_content") or top.get("content", "")
        print(f"Content:\n{text.strip()}")
    print("\n")


if __name__ == "__main__":
    demonstrate_query(
        query="How do report exports work in NexaDesk?",
        title="Evolution from Manual CSV -> Scheduled Cron -> NexaFlow AI Autonomous"
    )

    demonstrate_query(
        query="What are the pricing tiers and ticket quotas?",
        title="Tier Evolution across v1.0 ($29/$79) -> v2.0 ($39/$99) -> v3.0 ($49/Custom Enterprise)"
    )
