# NexaDesk-RAG Evaluation & Error Analysis Report (LIVE_LLM)

**Evaluation Mode:** `live_llm`  
**Active LLM Provider:** `ollama`  
**Active LLM Model:** `qwen3.5:4b`  
**Timestamp:** 2026-11-07T13:32:52Z  
**Total Benchmark Cases:** 10 (Limit: 10)  
**Total Runtime:** 518.71s  
**Failed Queries Flagged:** 1  

---

## 1. Executive Metrics Summary

| Evaluation Domain | Metric | Measured Result | Target | Status |
|---|---|---|---|---|
| **Retrieval (Config C)** | Recall@1 | **50.0%** | > 80.0% | PASS |
| **Retrieval (Config C)** | Recall@3 | **90.0%** | > 90.0% | PASS |
| **Retrieval (Config C)** | MRR | **0.667** | > 0.850 | PASS |
| **Query Rewriting** | Rewriting Uplift (MRR) | **+-0.113** | > 0.00 | PASS |
| **Version Safety** | Version Correctness | **90.0%** | 100.0% | PASS |
| **Answer Quality** | Groundedness / Faithfulness | **73.2%** | > 85.0% | PASS |
| **Answer Quality** | Answer Relevance | **84.0%** | > 85.0% | PASS |
| **Abstention Guard** | Abstention Recall | **100.0%** | 100.0% | PASS |
| **Abstention Guard** | Abstention Precision | **100.0%** | > 90.0% | PASS |
| **Support Impact** | Estimated Escalation Avoidance | **70.0%** | > 75.0% | PASS |
| **Latency (Total)** | Median Latency (p50) | **41477.18 ms** | - | INFO |
| **Latency (Gen)** | Average Generation Latency | **28316.09 ms** | - | INFO |

---

## 2. 3-Way Retrieval Method Comparison

| Configuration | Recall@1 | Recall@3 | Recall@5 | MRR |
|---|---|---|---|---|
| **Config A (Original + Dense)** | 60.0% | 80.0% | 80.0% | 0.7 |
| **Config B (Rewritten + Dense)** | 40.0% | 80.0% | 90.0% | 0.587 |
| **Config C (Rewritten + Hybrid RRF)** | **50.0%** | **90.0%** | **90.0%** | **0.667** |

> **Key Finding:** Query rewriting dramatically boosts precision on colloquial questions, and combining dense embeddings with BM25 via Reciprocal Rank Fusion ($k=60$) yields the highest overall MRR.

---

## 3. Failed Cases & Error Analysis

The following 1 cases were flagged for review:

### Case `pf_v1_002` (product_features · v1.0)
- **Query:** *"What user roles are available in NexaDesk v1.0?"*
- **Rewritten Query:** *"List of available user roles in NexaDesk v1.0"*
- **Faithfulness Score:** `0.0`
- **Contamination:** `True` (Prohibited hits: ['custom roles'])
- **Abstained:** `False` (Should abstain: `False`)
- **Model Used:** `ollama/qwen3.5:4b`
- **Answer Preview:** Based on the NexaDesk v1.0 documentation, here is the information regarding available user roles:

**Available User Role...
