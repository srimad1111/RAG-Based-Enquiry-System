# NexaDesk-RAG API Documentation

**Base URL (Development):** `http://127.0.0.1:8000/api/v1`  
**Interactive Swagger UI:** `http://127.0.0.1:8000/docs`  
**ReDoc Reference:** `http://127.0.0.1:8000/redoc`

---

## 1. System & Health Endpoints

### 1.1 Root Endpoint
- **Method:** `GET`
- **Path:** `/`
- **Description:** Returns basic project status, API version, and documentation links.
- **Response `200 OK`:**
  ```json
  {
    "project": "NexaDesk RAG Customer Enquiry System",
    "version": "1.0.0",
    "status": "operational",
    "documentation": "/docs",
    "health_check": "/api/v1/health",
    "supported_versions": ["v1.0", "v2.0", "v3.0"]
  }
  ```

---

### 1.2 Full System Health Check
- **Method:** `GET`
- **Path:** `/api/v1/health`
- **Description:** Performs end-to-end diagnostics on all backend subsystems.
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-11-07T10:30:00.000000",
    "app_name": "NexaDesk RAG Customer Enquiry System",
    "version": "1.0.0",
    "environment": "development",
    "components": {
      "api_core": {
        "status": "healthy",
        "message": "FastAPI application router and middleware active"
      },
      "sqlite_database": {
        "status": "healthy",
        "message": "SQLite database connected and tables verified"
      },
      "chroma_storage": {
        "status": "healthy",
        "message": "ChromaDB persistent directory exists and is writable"
      },
      "file_storage": {
        "status": "healthy",
        "message": "All required upload and data directories are verified"
      },
      "gemini_api": {
        "status": "standby",
        "message": "Placeholder key present; awaiting API key for Phase 2"
      }
    }
  }
  ```

---

### 1.3 Ping Probe
- **Method:** `GET`
- **Path:** `/api/v1/health/ping`
- **Description:** Lightweight liveness probe for load balancers.
- **Response `200 OK`:**
  ```json
  {
    "ping": "pong"
  }
  ```

---

### 1.4 System Metadata & Configuration
- **Method:** `GET`
- **Path:** `/api/v1/system/info`
- **Description:** Returns product versioning configuration and storage directory mappings.
- **Response `200 OK`:**
  ```json
  {
    "project_name": "NexaDesk RAG Customer Enquiry System",
    "app_version": "1.0.0",
    "environment": "development",
    "default_product_version": "v3.0",
    "supported_product_versions": ["v1.0", "v2.0", "v3.0"],
    "storage_directories": {
      "chroma_db": "D:\\EMESYS\\...\\storage\\chroma_db",
      "uploads": "D:\\EMESYS\\...\\storage\\uploads",
      "documents": "D:\\EMESYS\\...\\data\\documents\\NexaDesk",
      "sqlite_db": "D:\\EMESYS\\...\\app\\database\\nexadesk.db"
    },
    "rag_status": "Phase 1: Foundation & Scaffold (scaffolded)"
  }
  ```

---

## 2. Documentation Catalog Endpoints

### 2.1 Multi-Version Documentation Overview
- **Method:** `GET`
- **Path:** `/api/v1/documents/overview`
- **Description:** Scans and lists all documentation files across v1.0, v2.0, and v3.0.
- **Response `200 OK`:**
  ```json
  {
    "product_name": "NexaDesk",
    "total_documents": 9,
    "versions": [
      {
        "version": "v1.0",
        "file_count": 3,
        "files": ["getting_started.md", "pricing_and_plans.md", "ticket_management.md"]
      },
      {
        "version": "v2.0",
        "file_count": 3,
        "files": ["automations_and_routing.md", "getting_started.md", "pricing_and_plans.md"]
      },
      {
        "version": "v3.0",
        "file_count": 3,
        "files": ["ai_copilot_features.md", "getting_started.md", "pricing_and_plans.md"]
      }
    ]
  }
  ```

---

## 3. Standard Error Envelope
All error responses follow a uniform JSON structure:
```json
{
  "success": false,
  "error": {
    "code": 404,
    "message": "Resource not found",
    "path": "/api/v1/unknown"
  }
}
```

