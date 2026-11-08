"""
Phase 8: End-to-End System Integration, Verification, and Performance Testing Suite.
Tests all components of NexaDesk:
- Component Connectivity and System Health
- RAG Pipeline with Qwen 3.5 4B via Ollama
- Multi-Version Document Isolation (v1.0, v2.0, v3.0)
- Grounded Synthesis, Verifiable Citations, and Abstention
- Security and Input Validation Hardening
- Performance Latency Benchmarks
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
import requests

BACKEND_URL = "http://127.0.0.1:8000/api/v1"
OLLAMA_URL = "http://127.0.0.1:11434"
FRONTEND_URL = "http://127.0.0.1:5173"

class Phase8TestSuite:
    def __init__(self):
        self.results = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "integration_checks": {},
            "e2e_scenarios": {},
            "security_checks": {},
            "performance_metrics": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0
            }
        }

    def record_test(self, category: str, test_name: str, passed: bool, details: Any):
        self.results[category][test_name] = {
            "status": "PASSED" if passed else "FAILED",
            "details": details
        }
        self.results["summary"]["total_tests"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
            print(f"  [PASS] {test_name}", flush=True)
        else:
            self.results["summary"]["failed"] += 1
            print(f"  [FAIL] {test_name}: {details}", flush=True)

    def run_integration_checks(self):
        print("\n=== 1. System Integration Checks ===")
        
        # 1.1 Backend Health
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=5)
            health = r.json()
            is_healthy = r.status_code == 200 and health.get("status") == "healthy"
            components = health.get("components", {})
            chroma_ok = components.get("chroma_storage", {}).get("status") == "healthy"
            sqlite_ok = components.get("sqlite_database", {}).get("status") == "healthy"
            self.record_test("integration_checks", "Backend Health & Storage", is_healthy and chroma_ok and sqlite_ok, {
                "status_code": r.status_code,
                "chroma_chunks": components.get("chroma_storage", {}).get("details", {}).get("total_chunks_indexed"),
                "sqlite_status": components.get("sqlite_database", {}).get("status")
            })
        except Exception as e:
            self.record_test("integration_checks", "Backend Health & Storage", False, str(e))

        # 1.2 Ollama Daemon & Qwen 3.5 4B
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            tags = r.json().get("models", [])
            has_qwen = any(m.get("name") == "qwen3.5:4b" or "qwen3.5:4b" in m.get("name", "") for m in tags)
            self.record_test("integration_checks", "Ollama Qwen 3.5 4B Availability", r.status_code == 200 and has_qwen, {
                "models_found": [m.get("name") for m in tags]
            })
        except Exception as e:
            self.record_test("integration_checks", "Ollama Qwen 3.5 4B Availability", False, str(e))

        # 1.3 Frontend Webpack/Vite Server
        try:
            r = requests.get(FRONTEND_URL, timeout=5)
            self.record_test("integration_checks", "Frontend Web Server", r.status_code == 200, {
                "status_code": r.status_code,
                "content_type": r.headers.get("content-type")
            })
        except Exception as e:
            self.record_test("integration_checks", "Frontend Web Server", False, str(e))

        # 1.4 LLM Configuration Endpoint
        try:
            r = requests.get(f"{BACKEND_URL}/chat/config", timeout=5)
            cfg = r.json()
            active_prov = cfg.get("active_provider")
            active_model = cfg.get("llm_model")
            self.record_test("integration_checks", "Active LLM Provider Config", active_prov == "ollama" and "qwen3.5:4b" in active_model, {
                "active_provider": active_prov,
                "llm_model": active_model,
                "supported_versions": cfg.get("supported_versions")
            })
        except Exception as e:
            self.record_test("integration_checks", "Active LLM Provider Config", False, str(e))

        # 1.5 Document Catalog Overview
        try:
            r = requests.get(f"{BACKEND_URL}/documents/overview", timeout=5)
            docs = r.json()
            total_docs = docs.get("total_documents", 0)
            self.record_test("integration_checks", "Document Catalog Overview", total_docs >= 18, {
                "total_documents": total_docs,
                "versions": [v.get("version") for v in docs.get("versions", [])]
            })
        except Exception as e:
            self.record_test("integration_checks", "Document Catalog Overview", False, str(e))

        # 1.6 Ingestion & Chunking Stats
        try:
            r = requests.get(f"{BACKEND_URL}/documents/stats/overview", timeout=5)
            stats = r.json()
            total_chunks = stats.get("total_chunks", 0)
            self.record_test("integration_checks", "SQLite Document Chunks Ingestion", total_chunks >= 30, {
                "total_chunks": total_chunks,
                "total_documents": stats.get("total_documents")
            })
        except Exception as e:
            self.record_test("integration_checks", "SQLite Document Chunks Ingestion", False, str(e))

        # 1.7 Analytics Overview
        try:
            r = requests.get(f"{BACKEND_URL}/analytics/overview", timeout=5)
            analytics = r.json()
            self.record_test("integration_checks", "Analytics Telemetry Endpoint", r.status_code == 200, {
                "total_queries": analytics.get("total_queries"),
                "avg_latency_ms": analytics.get("avg_latency_ms"),
                "abstained_queries": analytics.get("abstained_queries")
            })
        except Exception as e:
            self.record_test("integration_checks", "Analytics Telemetry Endpoint", False, str(e))

    def run_e2e_scenarios(self):
        print("\n=== 2. End-to-End Chat & RAG Scenarios ===")

        # Scenario 1: Supported Normal Query on v1.0
        try:
            payload = {
                "question": "How are tickets assigned to team members in NexaDesk v1.0?",
                "product_version": "v1.0",
                "enable_rewriting": True,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json=payload, timeout=120)
            lat = round((time.time() - start) * 1000, 2)
            data = r.json()
            passed = (
                r.status_code == 200
                and not data.get("abstained", True)
                and len(data.get("citations", [])) > 0
                and data.get("product_version") == "v1.0"
            )
            self.record_test("e2e_scenarios", "Scenario 1: v1.0 Ticket Assignment (Supported)", passed, {
                "latency_ms": lat,
                "citations": [c.get("document_name") for c in data.get("citations", [])],
                "answer_snippet": data.get("answer", "")[:120] + "..."
            })
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 1: v1.0 Ticket Assignment (Supported)", False, str(e))

        # Scenario 2: Supported Query on v2.0 (Round-Robin & Automation)
        try:
            payload = {
                "question": "What automated ticket routing features and round robin algorithms exist in v2.0?",
                "product_version": "v2.0",
                "enable_rewriting": True,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json=payload, timeout=120)
            lat = round((time.time() - start) * 1000, 2)
            data = r.json()
            passed = (
                r.status_code == 200
                and not data.get("abstained", True)
                and len(data.get("citations", [])) > 0
                and data.get("product_version") == "v2.0"
            )
            self.record_test("e2e_scenarios", "Scenario 2: v2.0 Round-Robin & Routing (Supported)", passed, {
                "latency_ms": lat,
                "citations": [c.get("document_name") for c in data.get("citations", [])],
                "answer_snippet": data.get("answer", "")[:120] + "..."
            })
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 2: v2.0 Round-Robin & Routing (Supported)", False, str(e))

        # Scenario 3: Supported Query on v3.0 (AI Copilot)
        try:
            payload = {
                "question": "What AI Copilot and automated draft features are introduced in NexaDesk v3.0?",
                "product_version": "v3.0",
                "enable_rewriting": True,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json=payload, timeout=120)
            lat = round((time.time() - start) * 1000, 2)
            data = r.json()
            passed = (
                r.status_code == 200
                and not data.get("abstained", True)
                and len(data.get("citations", [])) > 0
                and data.get("product_version") == "v3.0"
            )
            self.record_test("e2e_scenarios", "Scenario 3: v3.0 AI Copilot (Supported)", passed, {
                "latency_ms": lat,
                "citations": [c.get("document_name") for c in data.get("citations", [])],
                "answer_snippet": data.get("answer", "")[:120] + "..."
            })
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 3: v3.0 AI Copilot (Supported)", False, str(e))

        # Scenario 4: Unsupported Out-of-Scope Query (Must Abstain)
        try:
            payload = {
                "question": "Can I pay my NexaDesk monthly subscription using Bitcoin or Ethereum cryptocurrency?",
                "product_version": "v3.0",
                "enable_rewriting": True,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json=payload, timeout=120)
            lat = round((time.time() - start) * 1000, 2)
            data = r.json()
            # Must abstain because cryptocurrency payment is nowhere in the docs
            passed = r.status_code == 200 and data.get("abstained", False) is True
            self.record_test("e2e_scenarios", "Scenario 4: Out-of-Scope Query Abstention", passed, {
                "latency_ms": lat,
                "abstained": data.get("abstained"),
                "answer": data.get("answer")
            })
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 4: Out-of-Scope Query Abstention", False, str(e))

        # Scenario 5: Ambiguous Query (Query Rewriting Test)
        try:
            payload = {
                "question": "Can I change who does the work?",
                "product_version": "v1.0",
                "enable_rewriting": True,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json=payload, timeout=120)
            lat = round((time.time() - start) * 1000, 2)
            data = r.json()
            rewritten = data.get("rewritten_query", "")
            passed = (
                r.status_code == 200
                and not data.get("abstained", True)
                and len(rewritten) > 0
                and rewritten != payload["question"]
            )
            self.record_test("e2e_scenarios", "Scenario 5: Ambiguous Query Rewriting", passed, {
                "original": payload["question"],
                "rewritten": rewritten,
                "answer_snippet": data.get("answer", "")[:120] + "..."
            })
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 5: Ambiguous Query Rewriting", False, str(e))

        # Scenario 6: Multi-Chunk Multi-Topic Synthesis (Pricing + SLA)
        try:
            payload = {
                "question": "What plans are available in v1.0 and what is the SLA guarantee for tickets?",
                "product_version": "v1.0",
                "enable_rewriting": True,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json=payload, timeout=120)
            lat = round((time.time() - start) * 1000, 2)
            data = r.json()
            citations = data.get("citations", [])
            doc_names = set(c.get("document_name", "") for c in citations)
            passed = r.status_code == 200 and not data.get("abstained", True) and len(doc_names) >= 2
            self.record_test("e2e_scenarios", "Scenario 6: Multi-Chunk Synthesis (Pricing + SLA)", passed, {
                "documents_cited": list(doc_names),
                "total_citations": len(citations),
                "latency_ms": lat
            })
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 6: Multi-Chunk Synthesis (Pricing + SLA)", False, str(e))

        # Scenario 7: Temporal Version Boundary Test (Asking v1.0 about v3.0 Copilot)
        try:
            payload = {
                "question": "How do I configure AI Copilot draft responses in NexaDesk v1.0?",
                "product_version": "v1.0",
                "enable_rewriting": True,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json=payload, timeout=120)
            lat = round((time.time() - start) * 1000, 2)
            data = r.json()
            # AI Copilot was not introduced until v3.0, so v1.0 MUST abstain!
            passed = r.status_code == 200 and data.get("abstained", False) is True
            self.record_test("e2e_scenarios", "Scenario 7: Version Temporal Boundary Check (v1.0 Abstains on v3.0 Feature)", passed, {
                "abstained": data.get("abstained"),
                "answer": data.get("answer")
            })
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 7: Version Temporal Boundary Check (v1.0 Abstains on v3.0 Feature)", False, str(e))

        # Scenario 8: Version Isolation Across v1.0, v2.0, v3.0
        try:
            query = "What are the report export formats available?"
            passed_isolation = True
            iso_details = {}
            for ver in ["v1.0", "v2.0", "v3.0"]:
                r = requests.post(f"{BACKEND_URL}/chat/enquiry", json={
                    "question": query,
                    "product_version": ver,
                    "top_k": 3
                }, timeout=120)
                d = r.json()
                citations = d.get("citations", [])
                iso_details[ver] = {
                    "citations": [c.get("document_name") for c in citations],
                    "abstained": d.get("abstained")
                }
                # Check that every citation has product_version matching requested version
                for c in citations:
                    if c.get("product_version") and c.get("product_version") != ver:
                        passed_isolation = False
            self.record_test("e2e_scenarios", "Scenario 8: Strict Multi-Version Isolation (v1/v2/v3)", passed_isolation, iso_details)
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 8: Strict Multi-Version Isolation (v1/v2/v3)", False, str(e))

        # Scenario 9: Verifiable Citation Precision Check
        try:
            payload = {
                "question": "What is the Starter Tier agent seat limit in NexaDesk v1.0?",
                "product_version": "v1.0",
                "top_k": 3
            }
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json=payload, timeout=120)
            data = r.json()
            citations = data.get("citations", [])
            valid_citations = True
            for c in citations:
                if not c.get("chunk_id") or not c.get("document_name") or not (c.get("snippet") or c.get("text_snippet")):
                    valid_citations = False
            self.record_test("e2e_scenarios", "Scenario 9: Verifiable Citation Schema Validation", valid_citations and len(citations) > 0, {
                "citations_count": len(citations),
                "sample_citation": citations[0] if citations else None
            })
        except Exception as e:
            self.record_test("e2e_scenarios", "Scenario 9: Verifiable Citation Schema Validation", False, str(e))

    def run_security_checks(self):
        print("\n=== 3. Security and Input Validation Checks ===")

        # 3.1 Empty Query Rejection
        try:
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json={
                "question": "   ",
                "product_version": "v3.0"
            }, timeout=5)
            self.record_test("security_checks", "Empty/Whitespace Query Rejection (HTTP 400)", r.status_code == 400, {
                "status_code": r.status_code,
                "response": r.json()
            })
        except Exception as e:
            self.record_test("security_checks", "Empty/Whitespace Query Rejection (HTTP 400)", False, str(e))

        # 3.2 Oversized Query (> 2000 chars) Rejection
        try:
            long_query = "What is NexaDesk? " * 150  # ~2700 chars
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json={
                "question": long_query,
                "product_version": "v3.0"
            }, timeout=5)
            self.record_test("security_checks", "Excessive Query Length Rejection (HTTP 400)", r.status_code == 400, {
                "status_code": r.status_code,
                "response": r.json()
            })
        except Exception as e:
            self.record_test("security_checks", "Excessive Query Length Rejection (HTTP 400)", False, str(e))

        # 3.3 Unsupported Version Rejection
        try:
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json={
                "question": "What is the pricing?",
                "product_version": "v99.0"
            }, timeout=5)
            self.record_test("security_checks", "Unsupported Version Rejection (HTTP 400)", r.status_code == 400, {
                "status_code": r.status_code,
                "response": r.json()
            })
        except Exception as e:
            self.record_test("security_checks", "Unsupported Version Rejection (HTTP 400)", False, str(e))

        # 3.4 Path Traversal Protection on Document Version Endpoint
        try:
            r = requests.get(f"{BACKEND_URL}/documents/version/..%2F..%2Fstorage", timeout=5)
            self.record_test("security_checks", "Path Traversal on Version Endpoint (Blocked 400/404)", r.status_code in (400, 404), {
                "status_code": r.status_code,
                "response": r.json()
            })
        except Exception as e:
            self.record_test("security_checks", "Path Traversal on Version Endpoint (Blocked 400/404)", False, str(e))

        # 3.5 SQL Injection Hardening in Chat & Version Filtering
        try:
            sqli_payload = "'; DROP TABLE documents; --"
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json={
                "question": "What is NexaDesk?",
                "product_version": sqli_payload
            }, timeout=5)
            # Must reject with 400 without crashing or running SQL
            r_docs = requests.get(f"{BACKEND_URL}/documents/stats/overview", timeout=5)
            docs_intact = r_docs.status_code == 200 and r_docs.json().get("total_documents", 0) > 0
            self.record_test("security_checks", "SQL Injection Resistance & Parameterization", r.status_code == 400 and docs_intact, {
                "status_code": r.status_code,
                "documents_still_intact": docs_intact
            })
        except Exception as e:
            self.record_test("security_checks", "SQL Injection Resistance & Parameterization", False, str(e))

        # 3.6 File Upload Validation (Oversized File Rejection)
        try:
            # Send file exceeding 25MB limit
            dummy_oversized = b"0" * (26 * 1024 * 1024)
            files = {"file": ("big_doc.txt", dummy_oversized, "text/plain")}
            data = {"product_version": "v3.0", "category": "Test"}
            r = requests.post(f"{BACKEND_URL}/documents/upload", files=files, data=data, timeout=10)
            self.record_test("security_checks", "Oversized File Upload Rejection (HTTP 413)", r.status_code == 413, {
                "status_code": r.status_code,
                "response": r.json() if r.headers.get("content-type") == "application/json" else r.text[:100]
            })
        except Exception as e:
            self.record_test("security_checks", "Oversized File Upload Rejection (HTTP 413)", False, str(e))

        # 3.7 File Upload Path Traversal Sanitization
        try:
            dummy_content = b"# Security Test\nPath traversal test content."
            files = {"file": ("../../evil_traversal.txt", dummy_content, "text/plain")}
            data = {"product_version": "v3.0", "category": "Test"}
            r = requests.post(f"{BACKEND_URL}/documents/upload", files=files, data=data, timeout=10)
            # The backend should either sanitize the filename to evil_traversal.txt or reject it, but NEVER write outside target_version_dir
            res = r.json()
            # Clean up if uploaded
            if res.get("document") and res["document"].get("id"):
                doc_id = res["document"]["id"]
                requests.delete(f"{BACKEND_URL}/documents/{doc_id}")
            self.record_test("security_checks", "File Upload Path Traversal Sanitization", r.status_code in (201, 400), {
                "status_code": r.status_code,
                "message": res.get("message")
            })
        except Exception as e:
            self.record_test("security_checks", "File Upload Path Traversal Sanitization", False, str(e))

    def run_performance_checks(self):
        print("\n=== 4. Performance Latency Measurements ===")

        # Measure standalone query rewriting latency
        try:
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/rag/rewrite", json={
                "customer_question": "Can I change who does the work?",
                "product_version": "v1.0"
            }, timeout=30)
            rewriting_ms = round((time.time() - start) * 1000, 2)
            self.record_test("performance_metrics", "Query Rewriter Latency (Qwen 3.5 4B)", r.status_code == 200, {
                "latency_ms": rewriting_ms,
                "rewritten_query": r.json().get("rewritten_query")
            })
        except Exception as e:
            self.record_test("performance_metrics", "Query Rewriter Latency (Qwen 3.5 4B)", False, str(e))

        # Measure Dense (ChromaDB) Retrieval Latency
        try:
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/rag/search", json={
                "query": "ticket assignment and escalation",
                "product_version": "v1.0",
                "top_k": 4
            }, timeout=10)
            dense_ms = round((time.time() - start) * 1000, 2)
            self.record_test("performance_metrics", "ChromaDB Dense Vector Retrieval Latency", r.status_code == 200, {
                "latency_ms": dense_ms,
                "results_count": len(r.json().get("results", []))
            })
        except Exception as e:
            self.record_test("performance_metrics", "ChromaDB Dense Vector Retrieval Latency", False, str(e))

        # Measure Hybrid RRF Retrieval Latency
        try:
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/rag/retrieve", json={
                "customer_question": "How do I route tickets?",
                "product_version": "v2.0",
                "enable_query_rewriting": False,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }, timeout=10)
            hybrid_ms = round((time.time() - start) * 1000, 2)
            self.record_test("performance_metrics", "Hybrid RRF Retrieval Latency (Dense + BM25)", r.status_code == 200, {
                "latency_ms": hybrid_ms,
                "results_count": len(r.json().get("results", []))
            })
        except Exception as e:
            self.record_test("performance_metrics", "Hybrid RRF Retrieval Latency (Dense + BM25)", False, str(e))

        # Measure Total End-to-End Chat Enquiry Latency (Rewriting + Hybrid Retrieval + Qwen Generation)
        try:
            start = time.time()
            r = requests.post(f"{BACKEND_URL}/chat/enquiry", json={
                "question": "What are the automated routing rules in NexaDesk v2.0?",
                "product_version": "v2.0",
                "enable_rewriting": True,
                "retrieval_mode": "hybrid",
                "top_k": 4
            }, timeout=60)
            total_e2e_ms = round((time.time() - start) * 1000, 2)
            data = r.json()
            retrieval_lat = data.get("retrieval_latency_ms", 0)
            gen_lat = data.get("generation_latency_ms", 0)
            self.record_test("performance_metrics", "Total Grounded RAG Latency (E2E with Qwen 3.5 4B)", r.status_code == 200, {
                "total_e2e_ms": total_e2e_ms,
                "retrieval_latency_ms": retrieval_lat,
                "generation_latency_ms": gen_lat,
                "citations_count": len(data.get("citations", []))
            })
        except Exception as e:
            self.record_test("performance_metrics", "Total Grounded RAG Latency (E2E with Qwen 3.5 4B)", False, str(e))

    def save_report(self, filepath: str = "backend/data/evaluation/results/phase8_test_results.json"):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[Report Saved] Phase 8 detailed results written to: {filepath}")
        print(f"Summary: {self.results['summary']['passed']}/{self.results['summary']['total_tests']} tests passed.")


if __name__ == "__main__":
    suite = Phase8TestSuite()
    suite.run_integration_checks()
    suite.run_e2e_scenarios()
    suite.run_security_checks()
    suite.run_performance_checks()
    suite.save_report()

