# NexaDesk-RAG API Documentation

**Base URL (Development):** `http://127.0.0.1:8000/api/v1`  
**Interactive Swagger UI:** `http://127.0.0.1:8000/docs`  
**ReDoc Reference:** `http://127.0.0.1:8000/redoc`  
**Version:** `1.0.0` (Phases 1–6 Complete)

---

## 1. System & Health Endpoints

### 1.1 Root Endpoint
- **Method:** `GET /`
- **Description:** Returns API status, active version, and documentation links.

### 1.2 Full System Health Check
- **Method:** `GET /api/v1/health`
- **Description:** Runs comprehensive end-to-end diagnostics on all backend subsystems:
  - SQLite database connectivity and chunk count
  - ChromaDB persistent vector collection status
  - Filesystem storage permissions (`storage/chroma_db`, `storage/uploads`)
  - Supported product version status

### 1.3 Ping Probe
- **Method:** `GET /api/v1/health/ping`
- **Description:** Lightweight liveness check returning `{"status": "pong", "timestamp": ...}`.

### 1.4 System Metadata & Settings
- **Method:** `GET /api/v1/system/info`
- **Description:** Returns configuration metadata, default version (`v3.0`), supported releases (`v1.0`, `v2.0`, `v3.0`), and storage paths.

---

## 2. Document Ingestion & Processing Endpoints (Phase 2 & 3)

### 2.1 Admin Document Upload
- **Method:** `POST /api/v1/documents/upload`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Binary file (.pdf, .docx, .txt, .md)
  - `product_name`: Product name (default: `NexaDesk`)
  - `product_version`: Target release (`v1.0`, `v2.0`, `v3.0`)
  - `category`: Documentation category (`User Guide`, `SLA & Protocols`, `Pricing & Quotas`, `Access Control & Roles`)
  - `chunk_size`: Max chunk characters (default: `800`)
  - `chunk_overlap`: Chunk overlap characters (default: `150`)
  - `replace_existing`: Boolean flag (`true`/`false`)
- **Responses:**
  - `201 Created`: Document parsed, chunked, saved in SQLite, and indexed into ChromaDB.
  - `409 Conflict`: Duplicate file detected (SHA-256 or name+version match).
  - `422 Unprocessable Entity`: Invalid extension or unverified version.

### 2.2 List Ingested Documents
- **Method:** `GET /api/v1/documents`
- **Query Parameters:** `product_version`, `category`, `document_type`, `limit`, `offset`
- **Response `200 OK`:** Returns list of document records with chunk counts and processing status.

### 2.3 Document Ingestion Statistics
- **Method:** `GET /api/v1/documents/stats/overview`
- **Response `200 OK`:** Returns document and chunk counts grouped by product version and document format.

### 2.4 Get Document Chunks
- **Method:** `GET /api/v1/documents/{document_id}/chunks`
- **Response `200 OK`:** Returns structured chunk segments with character lengths, section titles, page numbers, and metadata.

### 2.5 Delete Document (Cascaded)
- **Method:** `DELETE /api/v1/documents/{document_id}`
- **Response `200 OK`:** Deletes the document record and chunks from SQLite, and purges corresponding embeddings from ChromaDB.

---

## 3. Hybrid RAG & Vector Retrieval Endpoints (Phase 3 & 4)

### 3.1 Vector Store Status
- **Method:** `GET /api/v1/rag/status`
- **Response `200 OK`:** Returns ChromaDB collection name, total vectors, embedding model (`all-MiniLM-L6-v2`), and per-version chunk counts.

### 3.2 Dense Vector Search
- **Method:** `POST /api/v1/rag/search`
- **Payload:**
  ```json
  {
    "query": "How do report exports work?",
    "product_version": "v1.0",
    "top_k": 4
  }
  ```
- **Response `200 OK`:** Returns top semantic vector matches filtered strictly by target version.

### 3.3 Query Rewriter
- **Method:** `POST /api/v1/rag/rewrite`
- **Payload:**
  ```json
  {
    "query": "Why can't I schedule my reports like before?",
    "product_name": "NexaDesk",
    "product_version": "v2.0"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "original_query": "Why can't I schedule my reports like before?",
    "rewritten_query": "Scheduled report export functionality, configuration and availability in NexaDesk v2.0",
    "search_keywords": ["scheduled", "report", "export", "configuration"],
    "intent": "reporting_and_exports",
    "rewriter_used": "gemini-1.5-flash",
    "reasoning": "Normalized colloquial question into formal documentation search query"
  }
  ```

### 3.4 Version-Aware Hybrid Retrieval
- **Method:** `POST /api/v1/rag/retrieve`
- **Payload:**
  ```json
  {
    "customer_question": "Can I connect NexaDesk to Slack channels?",
    "product_version": "v2.0",
    "retrieval_mode": "hybrid",
    "top_k": 4,
    "enable_query_rewriting": true
  }
  ```
- **Response `200 OK`:** Returns fused rank list generated via Reciprocal Rank Fusion ($k=60$) combining ChromaDB dense search with BM25 lexical search.

### 3.5 3-Way Retrieval Method Comparison
- **Method:** `POST /api/v1/rag/compare`
- **Description:** Runs side-by-side comparison for a query across:
  1. **Raw Dense:** Unmodified question queried directly in ChromaDB.
  2. **Rewritten Dense:** Rewritten query in ChromaDB.
  3. **Rewritten Hybrid:** Rewritten query with Dense + BM25 Reciprocal Rank Fusion.

---

## 4. Customer Enquiry & Chat Assistant Endpoints (Phase 5)

### 4.1 Submit Customer Enquiry
- **Method:** `POST /api/v1/chat/enquiry`
- **Payload:**
  ```json
  {
    "question": "How do report exports work in NexaDesk?",
    "product_version": "v1.0",
    "product_name": "NexaDesk",
    "conversation_id": "conv_1731000000000",
    "retrieval_mode": "hybrid",
    "top_k": 4,
    "enable_rewriting": true,
    "temperature": 0.1
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "answer": "In NexaDesk v1.0, report exports are supported manually in CSV and PDF formats via the Admin Analytics tab. Scheduled exports are not supported in v1.0 [Doc: reporting_and_exports.md, Section: Manual Report Exports in v1.0, Page: 1].",
    "citations": [
      {
        "citation_id": 1,
        "document_name": "reporting_and_exports.md",
        "document_type": "markdown",
        "section_title": "Manual Report Exports in v1.0",
        "page_number": 1,
        "chunk_id": "chunk_v1_001",
        "snippet": "NexaDesk v1.0 supports manual report exports to CSV and PDF...",
        "relevance_score": 0.85
      }
    ],
    "product_version": "v1.0",
    "rewritten_query": "Manual report export formats and procedures in NexaDesk v1.0",
    "retrieved_sources": [...],
    "abstained": false,
    "conversation_id": "conv_1731000000000",
    "model_used": "gemini/gemini-1.5-flash",
    "latency_ms": 118.5
  }
  ```

### 4.2 Conversation Thread History
- **Method:** `GET /api/v1/chat/history/{conversation_id}`
- **Response `200 OK`:** Returns previous user and assistant turns for the given conversation ID.

### 4.3 Enquiry Audit Logs
- **Method:** `GET /api/v1/chat/logs?limit=20`
- **Response `200 OK`:** Returns recent customer enquiry logs recorded in SQLite `enquiry_logs`.

### 4.4 LLM Configuration & Diagnostics
- **Method:** `GET /api/v1/chat/config`
- **Response `200 OK`:**
  ```json
  {
    "status": "ready",
    "active_provider": "gemini",
    "llm_model": "gemini-1.5-flash",
    "gemini_model": "gemini-1.5-flash",
    "gemini_api_key_configured": true,
    "ollama_model": "llama3",
    "ollama_base_url": "http://localhost:11434",
    "supported_versions": ["v1.0", "v2.0", "v3.0"]
  }
  ```

### 4.5 LLM Providers Health Status
- **Method:** `GET /api/v1/chat/providers`
- **Response `200 OK`:** Reports connectivity and health diagnostics for both Google Gemini and local Ollama.

---

## 5. Analytics & Evaluation Benchmark Endpoints (Phase 6)

### 5.1 System Analytics Overview
- **Method:** `GET /api/v1/analytics/overview`
- **Response `200 OK`:**
  ```json
  {
    "total_queries": 42,
    "successful_responses": 40,
    "abstained_queries": 2,
    "enquiries_by_version": { "v1.0": 14, "v2.0": 16, "v3.0": 12 },
    "enquiries_by_retrieval_mode": { "hybrid": 38, "dense_only": 4 },
    "avg_latency_ms": 134.2,
    "has_evaluation_report": true,
    "version_isolation_accuracy": 100.0,
    "abstention_recall": 100.0
  }
  ```

### 5.2 Latest Benchmark Report
- **Method:** `GET /api/v1/analytics/report`
- **Response `200 OK`:** Returns the latest saved evaluation benchmark report or empty state status.

### 5.3 Trigger Evaluation Benchmark
- **Method:** `POST /api/v1/analytics/evaluate`
- **Description:** Runs the automated RAG Triad benchmark suite across all 15 test queries, computes metrics, persists the JSON report, and returns aggregate scores.
