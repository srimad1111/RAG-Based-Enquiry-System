# NexaDesk-RAG: Customer Enquiry System over Company Documentation

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/VectorStore-ChromaDB-FF6F00?style=flat-square)](https://www.trychroma.com)
[![TailwindCSS](https://img.shields.io/badge/UI-Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)
[![Pytest](https://img.shields.io/badge/Tests-45%2F45_Passing-brightgreen?style=flat-square)](https://docs.pytest.org)
[![Active LLM](https://img.shields.io/badge/Active_LLM-Ollama_%2F_Qwen_3.5_4B-blueviolet?style=flat-square)](https://ollama.ai)
[![Milestone](https://img.shields.io/badge/Phase_8-Deployment_Ready-success?style=flat-square)]()

**Project Title:** Project 32: RAG-Based Customer Enquiry System over Company Documentation  
**Domain:** Artificial Intelligence & Machine Learning / Natural Language Processing  
**Product:** NexaDesk (SaaS Customer Support & Ticketing Platform)  
**Supported Documentation Releases:** `v1.0`, `v2.0`, `v3.0`  
**Current Milestone:** Phases 1–8 Fully Implemented, Integrated, Hardened, and Verified  
**Active Inference Engine:** Local Ollama (`qwen3.5:4b`)  

---

## 📖 Overview

NexaDesk-RAG is an enterprise-grade AI customer enquiry platform engineered to resolve multi-version technical support queries with strict grounding, verifiable citations, and version isolation across software releases.

When SaaS products update, features change, parameters evolve, and legacy APIs get deprecated. Standard RAG architectures frequently suffer from **temporal version leakage** (e.g. advising a `v1.0` customer to use `v2.0` scheduled report exports or `v3.0` AI Copilot capabilities). NexaDesk-RAG prevents temporal contamination through:

1. **Strict Versioned Ingestion & Partitioning:** Documents across PDF, DOCX, TXT, and Markdown are ingested, chunked, and tagged with version metadata (`v1.0`, `v2.0`, `v3.0`).
2. **Version-Aware Hybrid Retrieval:** Combines dense semantic representations (ChromaDB + `all-MiniLM-L6-v2`) with sparse lexical matching (BM25Okapi) using **Reciprocal Rank Fusion (RRF, $k=60$)**.
3. **Automated Query Rewriting:** Normalizes colloquial, informal, or complaining customer phrasing into structured documentation queries via local **Qwen 3.5 4B**.
4. **Sufficiency & Abstention Guard:** Assesses retrieval confidence to decline out-of-domain questions gracefully and offer escalation to human support agents.
5. **Grounded Answer Generation with Citations:** Produces step-by-step instructions with verifiable citations `[Doc: ..., Section: ..., Page: ...]`.
6. **Active Local LLM Engine (Ollama / Qwen 3.5 4B):** Runs fully locally without cloud API dependencies or recurring SaaS costs.
7. **Premium Enterprise UI:** Dark-first design system (`#0B1020` base, `#141E33` surface, `#F1F5FF` text) with high contrast, minimal clutter, interactive RAG Triad visualizations, and live knowledge base explorer.

---

## 🏗️ Project Architecture & Directory Layout

```
NexaDesk-RAG/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI routers and endpoints
│   │   │   ├── v1/               # Version 1 API routes (health, system, documents, rag, chat, analytics)
│   │   │   └── __init__.py
│   │   ├── core/                 # App configuration & logging
│   │   │   ├── config.py         # Pydantic BaseSettings (.env loading & provider settings)
│   │   │   └── logging.py        # Centralized logger
│   │   ├── database/             # SQLite connection & schema migrations
│   │   │   └── connection.py     # SQLite init with documents, chunks, logs, messages
│   │   ├── models/               # Pydantic request and response schemas
│   │   │   └── schemas.py
│   │   ├── rag/                  # Core RAG engine
│   │   │   ├── providers/        # Interchangeable LLM Provider Subsystem
│   │   │   │   ├── base.py       # BaseLLMProvider contract
│   │   │   │   ├── common.py     # Shared prompts, formatters, and fallback synthesis
│   │   │   │   ├── gemini_provider.py # Google Gemini API provider
│   │   │   │   ├── ollama_provider.py # Local Ollama REST API provider (Qwen 3.5 4B)
│   │   │   │   └── factory.py    # Runtime provider factory
│   │   │   ├── bm25_retriever.py # BM25Okapi sparse lexical retriever
│   │   │   ├── hybrid_retriever.py # Reciprocal Rank Fusion (RRF) ranker
│   │   │   ├── query_rewriter.py # Provider-backed query rewriting
│   │   │   ├── generator.py      # Grounded answer synthesis & citation builder
│   │   │   ├── vector_store.py   # ChromaDB persistent vector manager
│   │   │   └── pipeline.py       # End-to-end RAG orchestrator
│   │   ├── services/             # Core business logic
│   │   │   ├── document_service.py   # Multi-format document parser & chunker
│   │   │   ├── evaluation_service.py # RAG Triad benchmark suite
│   │   │   ├── health_service.py     # Subsystem diagnostics
│   │   │   └── ingestion_service.py  # Ingestion workflow & path security
│   │   ├── utils/                # Helper utilities and storage validators
│   │   │   └── helpers.py
│   │   └── main.py               # FastAPI factory, CORS, exception handlers
│   ├── data/
│   │   ├── documents/NexaDesk/   # Multi-version document corpus (v1.0, v2.0, v3.0)
│   │   ├── evaluation/results/   # Automated benchmark outputs & historical runs
│   │   └── processed/            # Structured text chunks
│   ├── storage/
│   │   ├── chroma_db/            # Persistent local ChromaDB vector index
│   │   └── uploads/              # Custom document upload storage
│   ├── tests/                    # 45 Unit and Integration Tests (100% Passing)
│   ├── .env                      # Active backend environment
│   └── requirements.txt          # Backend Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── analytics/        # Evaluation & benchmark analytics UI
│   │   │   ├── chat/             # Customer Assistant with citation inspector
│   │   │   ├── common/           # High-contrast badges, cards, metrics
│   │   │   ├── dashboard/        # KPI cards & subsystem health
│   │   │   ├── documents/        # Document Catalog Explorer & Uploader
│   │   │   └── layout/           # Sidebar navigation & header
│   │   ├── pages/                # App views
│   │   ├── services/             # Axios API services
│   │   └── App.jsx               # Root tab navigation layout
│   ├── package.json              # Frontend npm dependencies
│   └── vite.config.js            # Vite bundler config
├── docs/
│   ├── architecture.md           # System architecture & component breakdown
│   ├── methodology.md            # Mathematical formulation & RRF design
│   ├── evaluation.md             # 112-case baseline evaluation methodology
│   ├── qwen_evaluation_comparison.md # Offline vs. Live Qwen comparative analysis
│   └── api_documentation.md      # Comprehensive REST API reference
├── scripts/
│   ├── phase8_e2e_verification.py # Automated 27-check Phase 8 verification suite
│   ├── start_backend.py          # Production backend startup entrypoint
│   ├── run_evaluation.py         # Evaluation benchmark harness runner
│   └── generate_sample_docs.py   # Multi-version corpus generator
└── README.md
```

---

## 📊 Evaluation & Benchmarks: Offline Baseline vs. Live Qwen 3.5 4B

To provide transparent, reproducible empirical validation, NexaDesk-RAG maintains both an extensive 112-question offline baseline and an authentic 10-question live neural evaluation powered by local **Qwen 3.5 4B**:

| Metric | Offline Baseline (112 Questions) | Live Qwen 3.5 4B (10 Questions) | Analysis & Significance |
| :--- | :---: | :---: | :--- |
| **Execution Mode** | Deterministic extractive fallback | Live local neural generation via Ollama | Validates real local LLM capabilities |
| **Active Model** | Rule-based semantic extractor | `qwen3.5:4b` | 4-billion parameter local model |
| **Context Relevance** | **52.9%** | **50.0%** | Stable lexical + dense retrieval performance |
| **Groundedness / Faithfulness** | **65.6%** | **73.2%** (+7.6%) | **Live Qwen generates richer, more grounded steps** |
| **Answer Relevance** | **84.5%** | **84.0%** | Consistent alignment with user enquiry intent |
| **Version Isolation Accuracy** | **100.0%** | **90.0%** | 9/10 strictly version-safe; 1 edge case diagnosed |
| **Abstention Recall** | **70.0%** | **100.0%** (+30.0%) | **100% correct refusal on unanswerable queries** |
| **Average End-to-End Latency** | **27.5 ms** | **40,168 ms** (~40s) | Neural decoding on local CPU/GPU vs. in-memory text |
| **Citation Correctness** | **100.0%** | **100.0%** | All generated citations map to genuine source chunks |

> **Historical Report Artifacts:**
> - Offline Baseline Report: `backend/data/evaluation/results/evaluation_summary_offline_fallback_baseline.json`
> - Live Qwen Report: `backend/data/evaluation/results/runs/evaluation_summary_qwen_live_llm.json`
> - Comparative Analysis: [`docs/qwen_evaluation_comparison.md`](docs/qwen_evaluation_comparison.md)

---

## 🛡️ Security Hardening Verified in Phase 8

During Phase 8, comprehensive enterprise security hardening was applied and validated:

1. **Strict Payload & Upload Caps:** File uploads (`POST /api/v1/documents/upload`) are capped at **25MB**, returning HTTP 413 `Payload Too Large` on oversized payloads.
2. **Path Traversal Protection:** Input filenames are sanitized using `Path(filename).name` basenames and validated to remain strictly within version-allocated directories (`is_relative_to`), preventing `../` directory escapes.
3. **Query Length & Format Validation:** Chat queries are validated for non-empty content and capped at **2000 characters** with strict UTF-8 sanitization.
4. **Version Whitelisting:** All endpoints validate the target version against `SUPPORTED_PRODUCT_VERSIONS` (`v1.0`, `v2.0`, `v3.0`), rejecting invalid or arbitrary versions with HTTP 400.
5. **SQL Injection Resistance:** All database queries utilize parameterized SQL queries (`?`) with foreign keys enabled, verified resilient against `' OR '1'='1` injection payloads.
6. **CORS Boundary Enforcement:** CORS middleware strictly enforces allowed origins (`http://localhost:5173`, `http://127.0.0.1:5173`).

---

## 🚀 Quickstart & Demonstration Runbook

### 1. Prerequisites
- **Python:** 3.10+ (Tested on Python 3.13)
- **Node.js:** v18+ (Tested on Node.js v24 & npm 11)
- **Ollama:** Installed locally with model `qwen3.5:4b` (`ollama pull qwen3.5:4b`)

---

### 2. Configuration (`backend/.env`)

The backend is preconfigured for local Ollama inference:

```env
PROJECT_NAME="NexaDesk RAG Customer Enquiry System"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG=True
HOST="127.0.0.1"
PORT=8000
API_V1_STR="/api/v1"
ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"

# Active LLM Provider
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3.5:4b
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_TIMEOUT=120

# Storage
CHROMA_PERSIST_DIRECTORY="storage/chroma_db"
UPLOADS_DIRECTORY="storage/uploads"
DOCUMENTS_DIRECTORY="data/documents/NexaDesk"
SQLITE_DB_PATH="app/database/nexadesk.db"
DEFAULT_PRODUCT_VERSION="v3.0"
SUPPORTED_PRODUCT_VERSIONS="v1.0,v2.0,v3.0"
```

---

### 3. Start All Services

Open three terminal windows:

#### Terminal 1: Start Ollama Daemon
```powershell
ollama serve
```

#### Terminal 2: Start FastAPI Backend
```powershell
python scripts/start_backend.py
```
*API is accessible at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

#### Terminal 3: Start React Frontend
```powershell
cd frontend
npm run dev
```
*Web dashboard is accessible at **[http://127.0.0.1:5173/](http://127.0.0.1:5173/)***

---

### 4. Execute Automated Verification Suites

#### A. Run Phase 8 End-to-End Verification (27/27 Checks)
```powershell
python scripts/phase8_e2e_verification.py
```
*Verifies 7 system integrations, 9 customer enquiry workflows, 7 security vectors, and 4 performance benchmarks.*

#### B. Run Full Pytest Test Suite (45/45 Tests)
```powershell
python -m pytest backend/tests/ -v
```
*Runs all 45 unit and integration tests across health, vector indexing, hybrid retrieval, providers, ingestion, response generation, and evaluation with 100% pass rate.*

---

## 🎯 Implementation Roadmap Status

- [x] **Phase 1: Project Setup & Full-Stack Foundation**
  - Modular project structure & clean directory boundaries
  - Persistent SQLite and ChromaDB directories
  - Health check & diagnostics API (`/api/v1/health`)
  - Initial React frontend with live backend connectivity
- [x] **Phase 2: Document Ingestion & Processing Pipeline**
  - Multi-format parsing for PDF (PyMuPDF), DOCX (python-docx), TXT, and Markdown
  - Configurable recursive text chunker (800 chars, 150 overlap)
  - Duplicate detection workflow (SHA-256 and name+version collision detection)
  - Document management API (`/api/v1/documents/*`)
- [x] **Phase 3: Version-Aware Vector Indexing**
  - Local embedding generation via `sentence-transformers/all-MiniLM-L6-v2`
  - Persistent ChromaDB storage with composite metadata filtering
  - Multi-version isolation (`v1.0`, `v2.0`, `v3.0`)
- [x] **Phase 4: Query Rewriting & Hybrid Retrieval**
  - Query Rewriter (colloquial to technical documentation syntax)
  - BM25Okapi lexical retrieval with domain stop-words
  - Reciprocal Rank Fusion (RRF, $k=60$)
  - 3-Way Retrieval Method Comparison matrix
- [x] **Phase 5: Grounded Answer Generation with Citations**
  - Version-isolated grounded answer generation
  - Verifiable citation anchoring `[Doc: ..., Section: ..., Page: ...]`
  - Retrieval Sufficiency check & Abstention Guard (human escalation offer)
  - Multi-turn conversation history persistence in SQLite
- [x] **Phase 6: Frontend Integration & SaaS Dashboard**
  - Admin Dashboard with live KPI cards, document catalog, and subsystem health
  - Customer Chat Assistant with product version selector and citation modal
  - Evaluation & Analytics dashboard with RAG Triad visualizations
- [x] **Phase 7: Live Local LLM Evaluation & Diagnostics**
  - Integration of **Qwen 3.5 4B** (`qwen3.5:4b`) via Ollama
  - 10-question live benchmark run with RAG Triad scoring
  - Diagnosis and remediation of version isolation edge cases
  - Creation of comparative analysis between offline baseline and live LLM
- [x] **Phase 8: Final System Integration, Security Hardening & Deployment Readiness**
  - End-to-end integration across frontend, FastAPI, ChromaDB, BM25, and Ollama
  - 9 customer enquiry E2E scenarios verified
  - 7 enterprise security checks implemented and validated
  - Query rewriting latency optimization (`num_predict: 128`, ~2.5s)
  - 45/45 pytest test suite passing cleanly (100% pass rate)
  - Frontend production build verified (`npm run build` 0 errors)
  - Comprehensive documentation and runbooks completed
