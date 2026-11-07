"""
Demonstration script for Phase 5: Grounded Answer Generation with Citations & Version Safety.
Runs the complete end-to-end RAG enquiry pipeline:
1. Grounded answer generation across NexaDesk v1.0, v2.0, and v3.0.
2. Verifiable source citations linking to actual retrieved document chunks.
3. Multi-turn conversation with SQLite history.
4. Confidence & abstention guard on unanswerable/out-of-scope inquiries.
"""
import sys
from pathlib import Path

# Add backend to PYTHONPATH
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.pipeline import rag_pipeline
from app.rag.generator import grounded_generator


def run_demonstration():
    print("=" * 95)
    print("PHASE 5 DEMONSTRATION: GROUNDED ANSWER GENERATION WITH CITATIONS & VERSION SAFETY")
    print("=" * 95)

    test_query = "Why can't I schedule my reports like before?"
    print(f"\nCUSTOMER QUESTION: \"{test_query}\"")
    print("DEMONSTRATING VERSION-GROUNDED GENERATION ACROSS v1.0, v2.0, and v3.0:\n")

    for ver in ["v1.0", "v2.0", "v3.0"]:
        print("-" * 95)
        print(f"TARGET PRODUCT VERSION: NexaDesk [{ver}]")
        print("-" * 95)

        res = rag_pipeline.answer_customer_enquiry(
            question=test_query,
            product_version=ver,
            product_name="NexaDesk",
            top_k=2
        )

        print(f"\n[Generated Support Answer]:\n{res['answer']}\n")
        print(f"Rewritten Query: \"{res['rewritten_query']}\"")
        print(f"Abstained: {res['abstained']} | Model Used: {res['model_used']} | Latency: {res['latency_ms']} ms")
        print("\n[Verifiable Source Citations]:")
        for c in res["citations"]:
            print(f"  - Citation #{c.citation_id}: {c.document_name} ({c.document_type.upper()}) | Section: \"{c.section_title}\" | Page: {c.page_number}")
            print(f"    Snippet: {c.snippet[:120].strip()}...")

    # 2. Test Multi-Turn Conversation Thread
    print("\n" + "=" * 95)
    print("--- MULTI-TURN CONVERSATION THREAD WITH SQLITE HISTORY ---")
    print("=" * 95)
    conv_id = "demo_thread_101"

    turn1 = rag_pipeline.answer_customer_enquiry(
        question="What are the user roles and permission levels?",
        product_version="v1.0",
        conversation_id=conv_id
    )
    print(f"\n[Turn 1 User]: What are the user roles and permission levels?")
    print(f"[Turn 1 Assistant]: {turn1['answer'][:200]}...")

    turn2 = rag_pipeline.answer_customer_enquiry(
        question="Can viewers modify tickets?",
        product_version="v1.0",
        conversation_id=conv_id
    )
    print(f"\n[Turn 2 User (Follow-up)]: Can viewers modify tickets?")
    print(f"[Turn 2 Assistant]: {turn2['answer'][:200]}...")

    # Read back conversation history from SQLite
    history = grounded_generator.get_conversation_history(conv_id)
    print(f"\nStored SQLite Conversation Thread ({len(history)} messages logged under {conv_id}):")
    for msg in history:
        print(f"  - [{msg['role'].upper()}]: {msg['content'][:90].strip()}...")

    # 3. Test Abstention on Out-of-Scope Query
    print("\n" + "=" * 95)
    print("--- CONFIDENCE & ABSTENTION ON OUT-OF-SCOPE ENQUIRY ---")
    print("=" * 95)
    out_of_scope_q = "What is the authentic recipe for baking chocolate chip cookies?"
    print(f"Query: \"{out_of_scope_q}\" (Version: v3.0)")
    abstain_res = rag_pipeline.answer_customer_enquiry(
        question=out_of_scope_q,
        product_version="v3.0"
    )
    print(f"Abstained: {abstain_res['abstained']}")
    print(f"Response:\n{abstain_res['answer']}")
    print(f"Citations count: {len(abstain_res['citations'])}")


if __name__ == "__main__":
    run_demonstration()

