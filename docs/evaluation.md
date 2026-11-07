# NexaDesk-RAG Evaluation Framework

**Project 32:** RAG-Based Customer Enquiry System over Company Documentation  
**Evaluation Target:** Multi-Version Retrieval Accuracy, Generation Faithfulness, and Latency

---

## 1. Evaluation Objectives

The evaluation suite quantitatively validates the system across three core dimensions:
1. **Retrieval Effectiveness:** Does the hybrid retriever fetch the exact relevant passages for a specific product version?
2. **Generation Quality (The RAG Triad):** Are generated responses faithful to retrieved documentation without cross-version contamination?
3. **Version Isolation:** Does the system correctly alter answers when switching between NexaDesk v1.0, v2.0, and v3.0?

---

## 2. Evaluation Metrics

### 2.1 Retrieval Metrics
- **Mean Reciprocal Rank (MRR@K):** Evaluates whether the primary ground-truth passage appears at top ranks.
  $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
- **Hit Rate@K / Precision@K ($K \in \{3, 5\}$):** Percentage of test queries where relevant chunks are present in the top-$K$ retrieved set.

### 2.2 RAG Triad Metrics
- **Context Relevance:** Measures the signal-to-noise ratio in retrieved context passages.
- **Groundedness / Faithfulness:** Detects hallucinations by measuring if statements in the generated response can be inferred directly from the retrieved context.
- **Answer Relevance:** Evaluates whether the generated response directly answers the customer enquiry.

### 2.3 Cross-Version Disambiguation Metric
A customized metric to penalize version leakage:

$$\text{Version Accuracy} = \frac{\sum_{q \in Q_v} \mathbb{I}(\text{ContainsOnlyValidFeatures}(A_q, v))}{|Q_v|}$$

---

## 3. Test Query Benchmark Suite

The evaluation suite includes multi-version test scenarios across:
1. **Pricing & Tier Questions:** e.g., *"Can I get annual discount billing?"*
   - Expected v1.0: Monthly only, no annual discount.
   - Expected v2.0: 15% annual discount.
   - Expected v3.0: 20% annual discount.
2. **Feature Deprecation Questions:** e.g., *"How do I connect email with POP3?"*
   - Expected v1.0: Supported via IMAP/POP3 settings.
   - Expected v2.0: POP3 deprecated; use SendGrid/Mailgun Webhook.
   - Expected v3.0: Use Webhooks or GraphQL API.
3. **AI Capabilities:** e.g., *"Can NexaDesk draft automatic replies?"*
   - Expected v1.0 & v2.0: Not available.
   - Expected v3.0: Supported via NexaDesk AI Copilot.

---

## 4. Execution & Reporting

Benchmark execution will be handled via `scripts/run_evaluation.py` producing JSON artifacts stored in `backend/data/evaluation/results/` for visualization in the frontend analytics view.

