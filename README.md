# NexaDesk-RAG: Customer Enquiry System over Company Documentation

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/VectorStore-ChromaDB-FF6F00?style=flat-square)](https://www.trychroma.com)
[![TailwindCSS](https://img.shields.io/badge/UI-Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)

**Project Title:** Project 32: RAG-Based Customer Enquiry System over Company Documentation  
**Domain:** Artificial Intelligence & Machine Learning / Natural Language Processing  
**Fictional Product:** NexaDesk (SaaS Customer Support & Ticketing Platform)  
**Supported Documentation Versions:** `v1.0`, `v2.0`, `v3.0`

---

## 📖 Overview

NexaDesk-RAG is a full-stack, enterprise-grade AI enquiry system designed to accurately resolve customer inquiries grounded in multi-version company documentation. 

As software products evolve through releases, features change, parameters are modified, and capabilities are deprecated. Traditional RAG systems often suffer from **temporal version leakage** (e.g., advising a v1.0 customer to use v3.0 AI Copilot features, or citing deprecated v1.0 POP3 settings to a v2.0 user). NexaDesk-RAG resolves this via:
- **Strict Versioned Ingestion & Partitioning** (`v1.0`, `v2.0`, `v3.0`).
- **Hybrid Retrieval Architecture:** Combining dense vector representations (ChromaDB + Sentence Transformers) with sparse lexical search (BM25).
- **Grounded LLM Generation:** Google Gemini API with mandatory citation referencing.
- **Audit & Analytics Layer:** SQLite query tracking and multi-version benchmark evaluation.

---

## 🏗️ Project Architecture & Folder Structure

```
NexaDesk-RAG/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI routers and endpoints
│   │   │   ├── v1/               # Version 1 API routes (health, system, documents)
│   │   │   └── __init__.py
│   │   ├── core/                 # App configuration & logging
│   │   │   ├── config.py         # Pydantic BaseSettings (.env loading)
│   │   │   └── logging.py        # Centralized logger
│   │   ├── database/             # SQLite connection & metadata tables
│   │   │   └── connection.py
│   │   ├── models/               # Pydantic schemas and response models
│   │   │   └── schemas.py
│   │   ├── rag/                  # RAG components (Phase 2 implementation)
│   │   │   ├── pipeline.py       # Pipeline scaffold & interface
│   │   │   └── vector_store.py   # ChromaDB persistent storage manager
│   │   ├── services/             # Business logic layer
│   │   │   ├── document_service.py # Multi-version document scanner
│   │   │   └── health_service.py   # End-to-end health diagnostics
│   │   ├── utils/                # Helper utilities and storage validators
│   │   │   └── helpers.py
│   │   └── main.py               # FastAPI factory, CORS, exception handlers
│   ├── data/
│   │   ├── documents/NexaDesk/   # Versioned documentation source files
│   │   │   ├── v1.0/
│   │   │   ├── v2.0/
│   │   │   └── v3.0/
│   │   ├── evaluation/results/   # Benchmark evaluation outputs
│   │   └── processed/            # Cleaned & tokenized text chunks
│   ├── storage/
│   │   ├── chroma_db/            # Persistent local ChromaDB vector index
│   │   └── uploads/              # Custom document upload storage
│   ├── tests/                    # Backend unit & integration tests
│   │   └── test_health.py        # Health-check test suite
│   ├── .env.example              # Backend environment template
│   └── requirements.txt          # Backend Python dependencies
├── frontend/
│   ├── public/                   # Public assets & icons
│   ├── src/
│   │   ├── assets/               # Static styles and images
│   │   ├── components/
│   │   │   ├── analytics/        # Evaluation & benchmark analytics UI
│   │   │   ├── chat/             # Interactive chat assistant component
│   │   │   ├── common/           # Reusable badges, spinners, alerts
│   │   │   ├── dashboard/        # Subsystem health cards & diagnostics
│   │   │   ├── documents/        # Multi-version document catalog explorer
│   │   │   └── layout/           # Navbar, footer, and navigation tabs
│   │   ├── context/              # React Context (System & Version State)
│   │   ├── hooks/                # Custom hooks (useHealth, useDocuments)
│   │   ├── pages/                # Main Dashboard page
│   │   ├── services/             # Axios API client & endpoints
│   │   ├── utils/                # Date and status formatters
│   │   ├── App.jsx               # Root application layout
│   │   ├── index.css             # Tailwind base & utilities
│   │   └── main.jsx              # React DOM entrypoint
│   ├── .env.example              # Frontend environment template
│   ├── package.json              # Frontend npm dependencies
│   ├── tailwind.config.js        # Tailwind CSS styling config
│   └── vite.config.js            # Vite bundler configuration
├── docs/
│   ├── architecture.md           # Mermaid architectural diagrams
│   ├── methodology.md            # Problem statement & RAG design
│   ├── evaluation.md             # RAG Triad & version benchmark guide
│   └── api_documentation.md      # REST API reference
├── scripts/
│   ├── generate_sample_docs.py   # Generates v1.0, v2.0, v3.0 sample docs
│   ├── run_evaluation.py         # Evaluation benchmark harness runner
│   └── setup_project.py          # Environment verification & DB setup
├── .gitignore                    # Git exclusion rules
├── README.md                     # Project manual
└── requirements.txt              # Root requirements file
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python:** 3.10 or higher (Tested on Python 3.13)
- **Node.js:** v18 or higher (Tested on Node.js v24 & npm 11)

---

### 2. Automated Project Setup
Run the setup utility to verify directories, copy `.env` templates, and initialize the SQLite database:
```bash
python scripts/setup_project.py
```

Generate the sample NexaDesk product documentation across versions (`v1.0`, `v2.0`, `v3.0`):
```bash
python scripts/generate_sample_docs.py
```

---

### 3. Backend Setup & Startup (FastAPI)

#### A. Navigate to backend directory & install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

*(For Phase 1 health-check testing without full PyTorch/Chroma packages, `fastapi`, `uvicorn`, `pydantic-settings`, and `httpx` are sufficient)*.

#### B. Configure Environment Variables:
Copy `.env.example` to `.env` if not already created:
```bash
# Windows PowerShell
Copy-Item .env.example .env
```
Key configuration parameters:
- `PORT=8000`
- `HOST=127.0.0.1`
- `ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`
- `CHROMA_PERSIST_DIRECTORY=storage/chroma_db`

#### C. Start the FastAPI Development Server:
```bash
# Run from within the backend directory:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Documentation (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative API Documentation (ReDoc): [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health Check Endpoint: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

#### D. Run Backend Tests:
```bash
pytest tests/ -v
```

---

### 4. Frontend Setup & Startup (React + Vite)

#### A. Navigate to frontend directory & install npm dependencies:
```bash
cd frontend
npm install
```

#### B. Configure Environment Variables:
Verify `frontend/.env`:
```env
VITE_API_BASE_URL="http://127.0.0.1:8000/api/v1"
```

#### C. Start Vite Development Server:
```bash
npm run dev
```
Open your browser at: **[http://localhost:5173](http://localhost:5173)**

The React application will automatically ping the FastAPI backend and render the live subsystem health diagnostics, product version selector, document catalog, and conversational interface.

---

## 🔍 Health-Check API Verification

You can verify the backend health check with `curl` or any browser:
```bash
curl http://127.0.0.1:8000/api/v1/health
```

Example JSON response:
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

## 📚 Technical Documentation Index

For in-depth details on system design, formulas, and evaluation benchmarks:
1. [Architecture & System Design](docs/architecture.md)
2. [Methodology & Hybrid RAG Formulation](docs/methodology.md)
3. [Evaluation Metrics & RAG Triad](docs/evaluation.md)
4. [API Endpoints Reference](docs/api_documentation.md)

---

## 🎯 Development Roadmap
- [x] **Phase 1: Project Setup & Full-Stack Foundation** (Complete)
  - Modular project architecture
  - Health check & diagnostics API
  - Persistent local storage for ChromaDB & SQLite
  - React + Vite + Tailwind frontend with live backend communication
  - Versioned sample document generation (`v1.0`, `v2.0`, `v3.0`)
- [ ] **Phase 2: RAG Pipeline & Ingestion**
  - Document chunking with version metadata
  - ChromaDB vector indexing & Sentence Transformers
  - BM25 sparse keyword retriever
  - Reciprocal Rank Fusion (RRF) & Gemini API answer generation
- [ ] **Phase 3: Evaluation & Optimization**
  - Automated RAG Triad evaluation harness
  - Temporal version disambiguation benchmark
  - Streaming responses & citation UI

