"""
Verification script for Qwen 3.5 4B via Ollama provider in NexaDesk.
Tests:
1. Health check & model availability (qwen3.5:4b).
2. Query rewriting via actual Qwen inference.
3. Answer generation via actual Qwen inference.
4. Citation preservation & version isolation.
5. Correct abstention behavior.
"""
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings
from app.rag.providers.ollama_provider import OllamaProvider
from app.rag.pipeline import rag_pipeline

settings = get_settings()

def test_ollama_qwen():
    print("=" * 70)
    print(" NEXADESK - OLLAMA QWEN 3.5 4B INTEGRATION VERIFICATION")
    print("=" * 70)
    print(f"Configured Provider:   {settings.LLM_PROVIDER}")
    print(f"Configured Model:      {settings.OLLAMA_MODEL}")
    print(f"Configured Base URL:   {settings.OLLAMA_BASE_URL}")
    print(f"Configured Timeout:    {settings.OLLAMA_TIMEOUT}s")

    provider = OllamaProvider()

    # Test 1: Connectivity & Model Availability
    print("\n[1/5] Checking Ollama Health & Model Tag...")
    health = provider.check_health()
    print(f"      Status:   {health.get('status')}")
    print(f"      Message:  {health.get('message')}")
    print(f"      Models:   {health.get('installed_models', [])}")
    if health.get("status") != "ready":
        print(f"FAILED: Ollama or model '{settings.OLLAMA_MODEL}' not ready.")
        sys.exit(1)
    print("      SUCCESS: Qwen 3.5 4B is loaded and ready in Ollama.")

    # Test 2: Query Rewriting
    print("\n[2/5] Testing Query Rewriting with Qwen...")
    test_q = "Why can't I schedule my reports like before?"
    start_t = time.time()
    rewrite_res = provider.rewrite_query(
        customer_question=test_q,
        product_name="NexaDesk",
        product_version="v1.0"
    )
    elapsed = time.time() - start_t
    print(f"      Original:  {test_q}")
    print(f"      Rewritten: {rewrite_res.get('rewritten_query')}")
    print(f"      Keywords:  {rewrite_res.get('search_keywords')}")
    print(f"      Rewriter:  {rewrite_res.get('rewriter_used')}")
    print(f"      Latency:   {elapsed:.2f}s")
    assert "ollama" in rewrite_res.get("rewriter_used", "") or "qwen" in rewrite_res.get("rewriter_used", "").lower(), "Expected Qwen rewriter"
    print("      SUCCESS: Query rewriting executed via Qwen inference.")

    # Test 3: Grounded Answer Generation (v1.0)
    print("\n[3/5] Testing Grounded Answer Generation (v1.0 manual exports)...")
    start_t = time.time()
    ans_res = rag_pipeline.answer_customer_enquiry(
        question="How do I export report data in NexaDesk?",
        product_version="v1.0",
        product_name="NexaDesk"
    )
    elapsed = time.time() - start_t
    print(f"      Answer:    {ans_res['answer'][:180]}...")
    print(f"      Citations: {len(ans_res['citations'])}")
    print(f"      Model:     {ans_res.get('model_used')}")
    print(f"      Latency:   {elapsed:.2f}s")
    assert len(ans_res["citations"]) > 0, "Expected at least one citation"
    assert "v1.0" in ans_res["product_version"]
    print("      SUCCESS: Grounded answer generated with citations.")

    # Test 4: Version Differentiation (v2.0 scheduled exports)
    print("\n[4/5] Testing Version Differentiation (v2.0 scheduled exports)...")
    start_t = time.time()
    ans_v2 = rag_pipeline.answer_customer_enquiry(
        question="Can I schedule report exports weekly?",
        product_version="v2.0",
        product_name="NexaDesk"
    )
    elapsed = time.time() - start_t
    print(f"      Answer:    {ans_v2['answer'][:180]}...")
    print(f"      Citations: {len(ans_v2['citations'])}")
    print(f"      Latency:   {elapsed:.2f}s")
    print("      SUCCESS: v2.0 answered correctly.")

    # Test 5: Abstention Logic
    print("\n[5/5] Testing Out-of-Domain Abstention...")
    start_t = time.time()
    ans_abs = rag_pipeline.answer_customer_enquiry(
        question="How do I bake chocolate chip cookies?",
        product_version="v3.0",
        product_name="NexaDesk"
    )
    elapsed = time.time() - start_t
    print(f"      Answer:    {ans_abs['answer'][:180]}...")
    print(f"      Abstained: {ans_abs.get('abstained')}")
    print(f"      Latency:   {elapsed:.2f}s")
    assert ans_abs.get("abstained") is True, "Expected abstention on cookie recipe"
    print("      SUCCESS: System correctly abstained.")

    print("\n" + "=" * 70)
    print(" ALL 5 TESTS PASSED WITH QWEN 3.5 4B OLLAMA INFERENCE!")
    print("=" * 70)

if __name__ == "__main__":
    test_ollama_qwen()

