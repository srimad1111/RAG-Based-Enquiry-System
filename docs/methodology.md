# NexaDesk-RAG Project Methodology

**Project 32:** RAG-Based Customer Enquiry System over Company Documentation  
**Academic Focus:** Multi-Version Knowledge Disambiguation, Hybrid Retrieval, Grounded Generation, and Interchangeable LLM Architecture  

---

## 1. Problem Statement & Motivation

Customer enquiry systems in SaaS environments encounter severe challenges due to **temporal version drift**. Software products undergo rapid architectural and functional changes across minor and major releases (e.g., NexaDesk `v1.0` $\rightarrow$ `v2.0` $\rightarrow$ `v3.0`):

1. **Feature Evolution & Replacement:**
   - In **NexaDesk v1.0**, only manual CSV and PDF report exports are supported.
   - In **NexaDesk v2.0**, automated scheduled report exports and webhook integrations are introduced.
   - In **NexaDesk v3.0**, automated scheduled exports, AI Copilot summaries, and NexaFlow Studio routing are added.
2. **Conflicting Pricing & Quotas:**
   - Starter tier in v1.0 is \$19/mo (500 tickets/mo), whereas in v2.0 it is \$29/mo (1,000 tickets/mo) with 15% annual discounts, and v3.0 introduces custom Enterprise quotes.
3. **The Cross-Version Bleed Vulnerability:**
   - Standard semantic vector search often retrieves information from newer documentation when answering queries for older versions, leading to catastrophic hallucinations (e.g. telling a v1.0 customer to configure a feature that does not exist in v1.0).

The objective of this capstone is to develop a mathematically rigorous, version-isolated RAG pipeline that strictly guarantees:
- **Zero Cross-Version Leakage**
- **Verifiable In-Text Citations**
- **Graceful Abstention on Out-of-Domain Inquiries**

---

## 2. Ingestion & Document Processing Methodology

### 2.1 Multi-Format Document Parsing
- **PDF Extraction:** Uses `PyMuPDF` (`fitz`) to preserve structural page numbers, multi-column flows, and document headers.
- **DOCX Extraction:** Uses `python-docx` to iterate through paragraphs, structural headings (`Heading 1`, `Heading 2`), and tabular data.
- **TXT & Markdown:** Parsed with regex heading detection (`#`, `##`, `###`) to preserve section context.

### 2.2 Recursive Character Text Splitting
Documents are chunked using configurable boundary hierarchy:
- Primary separators: `["\n\n", "\n", ". ", " ", ""]`
- Chunk size: **800 characters** (approx. 150–200 tokens)
- Chunk overlap: **150 characters**
- Whitespace normalization and removal of empty/whitespace chunks.

### 2.3 Metadata Attribution
Every indexed chunk is stamped with permanent metadata:
$$\text{Metadata}(c) = \{\text{doc\_id}, \text{doc\_name}, \text{product\_name}, \text{version}, \text{doc\_type}, \text{section}, \text{page}, \text{chunk\_id}\}$$

---

## 3. Query Rewriting & Normalization

Customer questions are frequently colloquial, frustrated, or conversational (e.g., *"Why can't I schedule my reports like before?"*). Dense semantic retrieval and BM25 perform significantly better when queries use official documentation terminology.

### 3.1 Rewriting Algorithm
1. **Colloquial Noise Stripping:** Removes conversational fillers (`"why can't i"`, `"how do i"`, `"where is the"`).
2. **Concept Synonym Canonicalization:** Maps informal phrasing to technical terms (e.g., `"schedule"` $\rightarrow$ `"scheduled recurring configuration"`).
3. **LLM Transformation (Gemini / Ollama):** When active, the LLM executes structured zero-shot query rewriting constrained by JSON schema:
   ```json
   {
     "rewritten_query": "Scheduled report export functionality, configuration and availability",
     "search_keywords": ["scheduled", "report", "export", "configuration"],
     "intent": "reporting_and_exports",
     "reasoning": "Normalized customer inquiry to formal reporting terminology"
   }
   ```
4. **Deterministic Heuristic Fallback:** If the LLM is offline or unconfigured, an NLP rule-based engine transforms the query deterministically, guaranteeing high precision without network latency.

---

## 4. Hybrid Retrieval & Rank Fusion

Retrieval combines dense semantic embeddings with sparse lexical keyword matching.

### 4.1 Dense Vector Search
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- **Metric:** Cosine similarity.
- **Metadata Constraint:**
  $$\mathcal{M} = \{\text{product\_name} == \text{"NexaDesk"}, \text{product\_version} == v_{\text{target}}\}$$

### 4.2 Sparse Lexical Search (BM25Okapi)
- **Tokenization:** Word boundary tokenization with domain stop-word filtering (`nexadesk`, `documentation`, `v1.0`, `v2.0`, `v3.0` are filtered to prevent false positive matches on common branding terms).
- **BM25 Formula:**
  $$\text{BM25}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
  *(Parameters: $k_1 = 1.5, b = 0.75$)*

### 4.3 Reciprocal Rank Fusion (RRF)
Rather than raw score blending (which is vulnerable to uncalibrated embedding cosine scales vs unbounded BM25 scores), the system applies **Reciprocal Rank Fusion**:

$$\text{RRF\_Score}(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{w_m}{k + \text{Rank}_m(d)}$$

Where:
- $k = 60$ (standard smoothing constant to prevent top-rank domination).
- $w_{\text{dense}} = 0.6$, $w_{\text{sparse}} = 0.4$.
- Documents are sorted by $\text{RRF\_Score}(d)$ descending.

---

## 5. Retrieval Sufficiency & Abstention Guard

To prevent hallucinations when a customer asks an unrecorded question (e.g., *"What is the recipe for chocolate chip cookies?"*) or asks about a feature unsupported in their version:

1. **Lexical Match Threshold:** If BM25 matches zero keywords ($\text{sparse\_score} \le 0.0$) and dense similarity $< 0.45$, the query is classified as out-of-domain.
2. **Topical Token Overlap:** Token intersection between query terms and top retrieved passages must be non-zero.
3. **Graceful Abstention:**
   If confidence falls below the sufficiency threshold, the pipeline refuses to answer and triggers the abstention message:
   > *"I cannot find verified information regarding this in the available NexaDesk {product_version} documentation. To ensure you receive accurate guidance, I recommend escalating this enquiry to our human support team."*

---

## 6. Grounded Generation & Citations

1. **System Prompt Enforces Version Fence:**
   - The LLM is instructed: *"Answer using ONLY the retrieved {version} documentation. Never borrow features from other versions."*
2. **Verifiable Citations:**
   Every factual assertion is anchored to:
   $$\text{Citation} = [\text{Doc: } \text{filename}, \text{Section: } \text{title}, \text{Page: } N]$$
3. **Interchangeable Provider Integration:**
   Abstracted via `BaseLLMProvider`. Google Gemini (cloud) and Ollama (local) are interchangeable without modifying downstream retrieval or citation logic.
