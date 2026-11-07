"""
Verification script: Test the affected user roles question across NexaDesk v1.0, v2.0, and v3.0
using live Qwen 3.5 4B inference.
"""
import sys
import time
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings
from app.rag.pipeline import rag_pipeline
from app.evaluation.evaluator import ComprehensiveRAGEvaluator
from app.database.connection import init_database

settings = get_settings()


def run_version_tests():
    print("=" * 80)
    print(" TESTING USER ROLES QUERY ACROSS NEXADESK v1.0, v2.0, AND v3.0 (Qwen 3.5 4B)")
    print("=" * 80)
    print(f"Provider:  {settings.LLM_PROVIDER}")
    print(f"Model:     {settings.OLLAMA_MODEL}")
    print(f"Base URL:  {settings.OLLAMA_BASE_URL}\n")

    init_database()
    evaluator = ComprehensiveRAGEvaluator(mode="live_llm")

    test_versions = ["v1.0", "v2.0", "v3.0"]
    queries = {
        "v1.0": "What user roles are available in NexaDesk v1.0?",
        "v2.0": "What user roles are available in NexaDesk v2.0?",
        "v3.0": "What user roles are available in NexaDesk v3.0?"
    }

    test_cases = {
        "v1.0": {
            "id": "test_roles_v1",
            "category": "product_features",
            "question": queries["v1.0"],
            "product_name": "NexaDesk",
            "product_version": "v1.0",
            "expected_relevant_document": "user_roles_guide.docx",
            "expected_section": "Standard Roles in v1.0",
            "expected_key_facts": ["administrator", "agent"],
            "prohibited_keywords": ["team lead", "custom roles"],
            "should_abstain": False
        },
        "v2.0": {
            "id": "test_roles_v2",
            "category": "product_features",
            "question": queries["v2.0"],
            "product_name": "NexaDesk",
            "product_version": "v2.0",
            "expected_relevant_document": "rbac_and_round_robin.docx",
            "expected_section": "Enhanced RBAC Roles",
            "expected_key_facts": ["admin", "manager", "agent", "viewer", "team lead"],
            "prohibited_keywords": ["saml sso", "scim"],
            "should_abstain": False
        },
        "v3.0": {
            "id": "test_roles_v3",
            "category": "product_features",
            "question": queries["v3.0"],
            "product_name": "NexaDesk",
            "product_version": "v3.0",
            "expected_relevant_document": "enterprise_features.md",
            "expected_section": "Enterprise Access Control",
            "expected_key_facts": ["custom role creator", "saml", "scim"],
            "prohibited_keywords": [],
            "should_abstain": False
        }
    }

    results = {}
    for ver in test_versions:
        print(f"\n--- Testing NexaDesk {ver} ---")
        case = test_cases[ver]
        start_t = time.time()
        eval_result = evaluator.evaluate_case(case)
        elapsed = time.time() - start_t

        results[ver] = eval_result

        print(f"Question:             {eval_result['query']}")
        print(f"Rewritten Query:      {eval_result['rewritten_query']}")
        print(f"Version Correctness:  {eval_result['version_correctness']} (Contamination: {eval_result['cross_version_contamination']})")
        print(f"Prohibited Hits:      {eval_result['prohibited_hits']}")
        print(f"Faithfulness Score:   {eval_result['faithfulness']}")
        print(f"Citations Count:      {eval_result['citations_count']}")
        print(f"Latency:              {eval_result['latency_ms']} ms")
        print(f"\nGenerated Answer:\n{eval_result['answer_preview']}")

    print("\n" + "=" * 80)
    print(" SUMMARY OF MULTI-VERSION TESTING RESULTS")
    print("=" * 80)
    all_passed = True
    for ver, res in results.items():
        is_ok = (res["version_correctness"] == 1.0 and not res["cross_version_contamination"])
        status = "PASSED" if is_ok else "FAILED"
        if not is_ok:
            all_passed = False
        print(f"NexaDesk {ver:<5}: Status: {status} | Version Correctness: {res['version_correctness']} | Faithfulness: {res['faithfulness']} | Contamination: {res['cross_version_contamination']}")

    if all_passed:
        print("\nALL 3 VERSIONS PASSED: Zero cross-version contamination, 100% version correctness across v1.0, v2.0, and v3.0.")
    else:
        print("\nTEST FAILED: Some versions had contamination.")
        sys.exit(1)


if __name__ == "__main__":
    run_version_tests()

