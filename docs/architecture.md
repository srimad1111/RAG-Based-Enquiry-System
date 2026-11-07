# NexaDesk-RAG System Architecture

**Project Title:** Project 32: RAG-Based Customer Enquiry System over Company Documentation  
**Product:** NexaDesk (SaaS Customer Support & Ticketing Platform)  
**Supported Documentation Versions:** `v1.0`, `v2.0`, `v3.0`

---

## 1. High-Level Architecture Overview

The NexaDesk-RAG system is a modular, multi-tier application designed to provide accurate, grounded, and version-aware customer support answers from historical and contemporary company documentation.

```mermaid
graph TD
    subgraph Frontend ["Client Tier (React + Vite + Tailwind CSS)"]
        UI["Modern Single Page Application"]
        ChatComp["Chat & Inquiry Interface"]
        DashComp["Version & Health Dashboard"]
        DocComp["Document Catalog & Explorer"]
        ApiClient["Axios API Client (src/services/api.js)"]
        UI --> ChatComp
        UI --> DashComp
        UI --> DocComp
        ChatComp --> ApiClient
        DashComp --> ApiClient
        DocComp --> ApiClient
    end

    subgraph Backend ["Application Tier (FastAPI)"]
        Router["FastAPI Router (/api/v1)"]
        HealthService["Health & Diagnostics Service"]
        DocService["Versioned Document Service"]
        RAGModule["RAG Engine (app/rag)"]
        DBModule["Database Layer (app/database)"]

        Router --> HealthService
        Router --> DocService
        Router --> RAGModule
        Router --> DBModule
    end

    subgraph AI_RAG ["RAG & AI Subsystem"]
        ChromaStore["ChromaDB Vector Store (Persistent)"]
        BM25["BM25 Keyword Index"]
        Embeddings["Sentence Transformers"]
        GeminiLLM["Google Gemini API (gemini-1.5-flash)"]
        
        RAGModule --> ChromaStore
        RAGModule --> BM25
        RAGModule --> Embeddings
        RAGModule --> GeminiLLM
    end

    subgraph Storage ["Storage & Persistence Tier"]
        SQLiteDB[("SQLite Database (nexadesk.db)")]
        DocStore["Versioned Docs (v1.0, v2.0, v3.0)"]
        ChromaStorage["Local Chroma Directory (storage/chroma_db)"]
        UploadStorage["Upload Directory (storage/uploads)"]

        DBModule --> SQLiteDB
        DocService --> DocStore
        ChromaStore --> ChromaStorage
    end

    ApiClient -->|HTTP / JSON (CORS Enabled)| Router
```

---

## 2. Component Breakdown

### 2.1 Frontend Tier (`frontend/`)
- **Technology:** React 18, Vite, Tailwind CSS, Axios, Lucide React.
- **Organization:**
  - `src/components/common/`: Reusable UI elements (cards, badges, modals, spinners).
  - `src/components/chat/`: Conversational interface supporting version toggle and citation displays.
  - `src/components/dashboard/`: System diagnostic indicators and backend health monitoring.
  - `src/components/documents/`: Documentation browser organized by NexaDesk versions.
  - `src/services/`: Isolated Axios service layer with centralized error handling.

### 2.2 Application Backend (`backend/app/`)
- **Technology:** FastAPI, Pydantic v2, Python 3.10+.
- **Design Principles:**
  - Strict separation of routing (`app/api/`), business logic (`app/services/`), data models (`app/models/`), and RAG pipeline (`app/rag/`).
  - Asynchronous handlers with CORS middleware.
  - Centralized settings via `pydantic-settings` reading `.env`.
  - Comprehensive logging with request tracking.

### 2.3 RAG Subsystem (`backend/app/rag/`)
- **Hybrid Retrieval:** Dense vector retrieval via ChromaDB paired with sparse lexical retrieval via BM25 to prevent missed technical terminology.
- **Version Isolation:** Every chunk and embedding is partitioned by product version metadata (`v1.0`, `v2.0`, `v3.0`).
- **Generation:** Grounded context injection into Gemini 1.5 Flash with strict guardrails to prevent temporal version confusion.

### 2.4 Data & Storage Tier
- **Local Persistent ChromaDB:** Persisted at `backend/storage/chroma_db/`.
- **SQLite Database:** Handles enquiry logs, user feedback, and audit trails at `backend/app/database/nexadesk.db`.
- **Raw Documentation:** Structured in `backend/data/documents/NexaDesk/{v1.0, v2.0, v3.0}/`.

