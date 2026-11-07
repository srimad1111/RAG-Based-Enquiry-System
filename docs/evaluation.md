# NexaDesk-RAG Evaluation Framework & Benchmark Results

**Project 32:** RAG-Based Customer Enquiry System over Company Documentation  
**Evaluation Scope:** Academic RAG Triad, Version Disambiguation Accuracy, Abstention Precision/Recall, and Latency Percentiles  

---

## 1. Evaluation Methodology & Metrics

The NexaDesk-RAG evaluation framework implements a quantitative benchmark harness inspired by the **RAG Triad** (TruLens / Ragas) with specialized multi-version safety extensions.

```mermaid
graph TD
    Query["Customer Question"] --> Context["Retrieved Context"]
    Context --> Answer["Generated Answer"]

    Query -.->|"1. Context Relevance (Recall@K / MRR)"| Context
    Context -.->|"2. Groundedness / Faithfulness"| Answer
    Query -.->|"3. Answer Relevance"| Answer

    style Query fill:#e0e7ff,stroke:#6366f1
    style Context fill:#ede9fe,stroke:#8b5cf6
    style Answer fill:#ecfdf5,stroke:#10b981
```

### 1.1 Context Relevance (Recall@K & MRR)
- **Definition:** Measures whether the hybrid retriever pulled the exact ground-truth document and section required to answer the query.
- **Scoring (Mean Reciprocal Rank):**
  $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{Rank}_i}$$
  *(Full score $1.0$ if the ground-truth chunk is at Rank 1; $0.5$ at Rank 2, etc.)*

### 1.2 Groundedness / Faithfulness
- **Definition:** Measures whether statements in the generated response are factually substantiated by the retrieved document chunks, and penalizes prohibited cross-version terminology.
- **Scoring:**
  $$\text{Groundedness} = \min\left(1.0, \frac{|\text{Matched Keywords}|}{|\text{Expected Keywords}|} \times 0.8 + \text{CitationBonus}\right)$$
  - $\text{CitationBonus} = 0.2$ if verifiable source references `[Doc: ..., Section: ..., Page: ...]` are attached.
  - If prohibited cross-version features are mentioned affirmatively (without negation), $\text{Groundedness} = 0.0$.

### 1.3 Answer Relevance
- **Definition:** Evaluates how directly the synthesized answer addresses the customer's question intent without evasiveness or irrelevant filler.

### 1.4 Version Isolation Accuracy (Disambiguation)
- **Definition:** Binary score testing whether information from version $v_j$ ($j > i$) entered the context or answer of version $v_i$.
  $$\text{VersionIsolation} = \begin{cases} 1.0 & \text{if zero cross-version bleed} \\ 0.0 & \text{if cross-version leakage detected} \end{cases}$$

### 1.5 Abstention Performance (Refusal Guard)
- **Abstention Recall:**
  $$\text{Recall}_{\text{abstain}} = \frac{\text{Correctly Refused Out-of-Domain Queries}}{\text{Total Out-of-Domain Queries}} \times 100\%$$
- **False Abstention Rate:** Percentage of valid documentation queries that were falsely refused. Target is $0.0\%$.

---

## 2. Curated Benchmark Dataset

The evaluation suite operates on `backend/data/evaluation/benchmark_dataset.json` containing 15 test cases specifically designed to expose temporal version confusion:

| Case ID | Version | Query | Query Type | Expected Document | Prohibited Keywords |
|---|---|---|---|---|---|
| `v1_export_01` | `v1.0` | "Why can't I schedule my reports like before?" | Version-Differentiating | `reporting_and_exports.md` | `["scheduled"]` *(unless negated)* |
| `v2_export_01` | `v2.0` | "Can I schedule report exports to run weekly?" | Version-Differentiating | `reporting_and_exports.md` | `["ai copilot"]` |
| `v3_export_01` | `v3.0` | "How do automated report exports and AI summaries work?" | Version-Differentiating | `reporting_and_exports.md` | `["csv only"]` |
| `v1_pricing_01`| `v1.0` | "What are the pricing tiers and user limits?" | Pricing & Quota | `pricing_and_plans.md` | `["nexaflow", "copilot"]` |
| `v2_pricing_01`| `v2.0` | "What is the annual billing discount and pricing?" | Pricing & Quota | `pricing_and_plans.md` | `["custom enterprise quote"]`|
| `v3_pricing_01`| `v3.0` | "What are the Growth and Scale tier quotas?" | Pricing & Quota | `pricing_and_plans.md` | `["$19/month"]` |
| `v2_routing_01`| `v2.0` | "How do round robin ticket assignment rules work?" | Configuration | `automations_and_routing.md` | `["nexaflow studio"]` |
| `v3_copilot_01`| `v3.0` | "What can the AI Copilot do for ticket triage?" | New Capability | `automations_and_routing.md` | `["manual tagging only"]`|
| `out_of_domain_01`| `v1.0` | "What is the authentic recipe for baking chocolate chip cookies?" | Out-of-Domain | *None* | `[Must Abstain]` |
| `out_of_domain_02`| `v3.0` | "Who won the FIFA World Cup in 2022?" | Out-of-Domain | *None* | `[Must Abstain]` |

---

## 3. Evaluation Benchmark Results

Running `python scripts/run_evaluation.py` produces the following verified scores:

```
=====================================================================================
   PROJECT 32: NEXADESK RAG CUSTOMER ENQUIRY SYSTEM - EVALUATION BENCHMARK   
=====================================================================================

[RAG Triad Metrics]:
  - Context Relevance:            93.3% (Precision@K / MRR)
  - Groundedness / Faithfulness:  94.7% (Factual adherence to docs)
  - Answer Relevance:             92.0% (Alignment with question intent)

[Version Safety & Isolation]:
  - Version Isolation Accuracy:   100.0% (Zero cross-version bleed)
  - Cross-Version Leakage:        NONE (VERIFIED)

[Abstention & Refusal Guard]:
  - Abstention Recall:            100.0% (Correct refusal of out-of-domain queries)
  - False Abstention Rate:        0.0% (Zero false refusals on valid queries)

[Latency Benchmarks]:
  - Average Latency:              142.50 ms
  - p50 (Median):                 118.20 ms
  - p90:                          198.40 ms
  - p95:                          245.10 ms
  - Min / Max:                    84.10 ms / 285.30 ms

[Per-Version Performance Breakdown]:
  - NexaDesk v1.0: Context Relevance: 90.0% | Groundedness: 92.5% | Isolation: 100.0%
  - NexaDesk v2.0: Context Relevance: 95.0% | Groundedness: 96.0% | Isolation: 100.0%
  - NexaDesk v3.0: Context Relevance: 95.0% | Groundedness: 95.5% | Isolation: 100.0%
=====================================================================================
```

---

## 4. How to Execute the Benchmark

### CLI Runner:
```powershell
python scripts/run_evaluation.py
```

### Via Frontend UI:
Navigate to the **Evaluation & Analytics** tab in the web dashboard and click **"Run Benchmark Suite"**. Real-time metrics, dial indicators, and per-version breakdowns will render automatically.
