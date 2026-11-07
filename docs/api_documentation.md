# NexaDesk-RAG API Documentation

**Base URL (Development):** `http://127.0.0.1:8000/api/v1`  
**Interactive Swagger UI:** `http://127.0.0.1:8000/docs`  
**ReDoc Reference:** `http://127.0.0.1:8000/redoc`

---

## 1. System & Health Endpoints

### 1.1 Root Endpoint
- **Method:** `GET /`
- **Description:** Returns basic project status, API version, and documentation links.

### 1.2 Full System Health Check
- **Method:** `GET /api/v1/health`
- **Description:** Performs end-to-end diagnostics on all backend subsystems.

### 1.3 Ping Probe
- **Method:** `GET /api/v1/health/ping`
- **Description:** Lightweight liveness probe for load balancers.

### 1.4 System Metadata & Configuration
- **Method:** `GET /api/v1/system/info`
- **Description:** Returns product versioning configuration and storage directory mappings.

---

## 2. Document Ingestion & Processing Endpoints (Phase 2)

### 2.1 Admin Document Upload
- **Method:** `POST /api/v1/documents/upload`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Binary file (.pdf, .docx, .txt, .md)
  - `product_name`: Fictional product name (e.g. `NexaDesk`)
  - `product_version`: Target release version (`v1.0`, `v2.0`, `v3.0`)
  - `category`: Documentation category (e.g. `User Guide`, `SLA & Protocols`, `Pricing & Quotas`, `Access Control & Roles`)
  - `chunk_size`: Max chunk characters (default: `800`)
  - `chunk_overlap`: Chunk overlap characters (default: `150`)
  - `replace_existing`: Boolean (`true`/`false`)
- **Status Codes:**
  - `201 Created`: Document successfully extracted, chunked, and saved in SQLite.
  - `409 Conflict`: Duplicate document detected (SHA-256 or name+version collision) when `replace_existing=false`.
  - `422 Unprocessable Entity`: Validation failure (unsupported extension or invalid version).

### 2.2 List Ingested Documents
- **Method:** `GET /api/v1/documents`
- **Query Parameters:**
  - `product_version`: Filter by release version (`v1.0`, `v2.0`, `v3.0`)
  - `category`: Filter by category string
  - `document_type`: Filter by format (`pdf`, `docx`, `txt`, `md`)
- **Response `200 OK`:**
  ```json
  {
    "total_documents": 18,
    "total_chunks": 36,
    "documents": [
      {
        "id": "doc_6730a1d0b1e4",
        "document_name": "email_and_sla_policy.pdf",
        "product_name": "NexaDesk",
        "product_version": "v1.0",
        "category": "SLA & Protocols",
        "document_type": "pdf",
        "chunk_count": 2,
        "status": "completed",
        "created_at": "2026-11-07 11:21:13"
      }
    ]
  }
  ```

### 2.3 Get Ingestion Statistics
- **Method:** `GET /api/v1/documents/stats/overview`
- **Response `200 OK`:**
  ```json
  {
    "total_documents": 18,
    "total_chunks": 36,
    "by_version": {
      "v1.0": { "documents": 6, "chunks": 12 },
      "v2.0": { "documents": 6, "chunks": 12 },
      "v3.0": { "documents": 6, "chunks": 12 }
    },
    "by_type": {
      "pdf": 3,
      "docx": 3,
      "txt": 3,
      "md": 9
    }
  }
  ```

### 2.4 Get Document Chunks & Metadata
- **Method:** `GET /api/v1/documents/{document_id}/chunks`
- **Response `200 OK`:**
  ```json
  [
    {
      "id": "doc_6730a1d0b1e4_c0001",
      "document_id": "doc_6730a1d0b1e4",
      "chunk_index": 1,
      "text_content": "POP3 Email Polling Configuration...",
      "char_count": 482,
      "section_title": "POP3 Email Polling Configuration",
      "page_number": 1,
      "metadata": {
        "document_id": "doc_6730a1d0b1e4",
        "document_name": "email_and_sla_policy.pdf",
        "product_name": "NexaDesk",
        "product_version": "v1.0",
        "document_type": "pdf",
        "section_title": "POP3 Email Polling Configuration",
        "page_number": 1,
        "upload_timestamp": "2026-11-07T11:21:13.123456Z",
        "chunk_id": "doc_6730a1d0b1e4_c0001",
        "category": "SLA & Protocols"
      }
    }
  ]
  ```

### 2.5 Delete Document
- **Method:** `DELETE /api/v1/documents/{document_id}`
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "message": "Document 'doc_6730a1d0b1e4' and all associated chunks were successfully deleted."
  }
  ```
