# NexaDesk-RAG: Customer Enquiry System over Company Documentation

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/VectorStore-ChromaDB-FF6F00?style=flat-square)](https://www.trychroma.com)
[![TailwindCSS](https://img.shields.io/badge/UI-Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)
[![Pytest](https://img.shields.io/badge/Tests-45%2F45_Passing-brightgreen?style=flat-square)](https://docs.pytest.org)
[![LLM](https://img.shields.io/badge/LLM_Provider-Gemini_%7C_Ollama-blueviolet?style=flat-square)](https://ai.google.dev)

**Project Title:** Project 32: RAG-Based Customer Enquiry System over Company Documentation  
**Domain:** Artificial Intelligence & Machine Learning / Natural Language Processing  
**Product:** NexaDesk (SaaS Customer Support & Ticketing Platform)  
**Supported Documentation Releases:** `v1.0`, `v2.0`, `v3.0`  
**Current Milestone:** Phases 1–6 Fully Implemented, Integrated, and Verified  

---

## 📖 Overview

NexaDesk-RAG is a full-stack, enterprise-grade AI customer enquiry system specifically engineered to resolve customer support enquiries with strict grounding in multi-version product documentation.

As software products evolve through releases, features are added, parameters modified, and capabilities deprecated. Standard RAG architectures frequently suffer from **temporal version leakage** (e.g. advising a v1.0 customer to use v2.0 scheduled report exports or v3.0 AI Copilot capabilities). NexaDesk-RAG eliminates this via:

1. **Strict Versioned Ingestion & Partitioning:** Documents across PDF, DOCX, TXT, and Markdown are parsed, recursively chunked, and tagged with version metadata (`v1.0`, `v2.0`, `v3.0`).
2. **Version-Aware Hybrid Retrieval:** Combines dense semantic representations (ChromaDB + `all-MiniLM-L6-v2`) with sparse lexical matching (BM25Okapi) using **Reciprocal Rank Fusion (RRF, $k=60$)**.
3. **Automated Query Rewriting:** Normalizes colloquial, frustrated customer phrasing into formal documentation terminology.
4. **Sufficiency & Abstention Guard:** Assesses retrieval confidence to decline out-of-domain questions gracefully and offer escalation to human support agents.
5. **Grounded Answer Generation with Citations:** Produces step-by-step instructions with verifiable citations `[Doc: ..., Section: ..., Page: ...]`.
6. **Interchangeable LLM Provider System:** Switch seamlessly between **Google Gemini API** (cloud) and **Ollama** (local offline model) via `.env`.
7. **Production SaaS Dashboard:** Full React + Vite dashboard featuring live KPI tracking, document catalog manager, chat assistant, and RAG Triad evaluation harness.

---

## 🏗️ Project Architecture & Folder Structure

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
│   │   │   │   ├── ollama_provider.py # Local Ollama REST API provider
│   │   │   │   └── factory.py    # Runtime provider factory
│   │   │   ├── bm25_retriever.py # BM25Okapi sparse lexical retriever
│   │   │   ├── hybrid_retriever.py # Reciprocal Rank Fusion (RRF) ranker
│   │   │   ├── query_rewriter.py # Provider-backed query rewriting
│   │   │   ├── generator.py      # Grounded answer synthesis & citation builder
│   │   │   ├── vector_store.py   # ChromaDB persistent vector manager
│   │   │   └── pipeline.py       # End-to-end RAG orchestrator
│   │   ├── services/             # Core business logic
│   │   │   ├── document_service.py # Multi-format document parser & chunker
│   │   │   ├── evaluation_service.py # RAG Triad benchmark suite
│   │   │   └── health_service.py   # Subsystem diagnostics
│   │   ├── utils/                # Helper utilities and storage validators
│   │   │   └── helpers.py
│   │   └── main.py               # FastAPI factory, CORS, exception handlers
│   ├── data/
│   │   ├── documents/NexaDesk/   # Multi-version document corpus (v1.0, v2.0, v3.0)
│   │   ├── evaluation/results/   # Automated benchmark outputs
│   │   └── processed/            # Structured text chunks
│   ├── storage/
│   │   ├── chroma_db/            # Persistent local ChromaDB vector index
│   │   └── uploads/              # Custom document upload storage
│   ├── tests/                    # 45 Unit and Integration Tests (100% Passing)
│   ├── .env.example              # Backend environment template
│   └── requirements.txt          # Backend Python dependencies
├── frontend/
│   ├── public/                   # Public assets & icons
│   ├── src/
│   │   ├── assets/               # Static styles
│   │   ├── components/
│   │   │   ├── analytics/        # Evaluation & benchmark analytics UI
│   │   │   ├── chat/             # Customer Assistant with citation inspector
│   │   │   ├── common/           # Badges, spinners, alerts
│   │   │   ├── dashboard/        # KPI cards & subsystem health
│   │   │   ├── documents/        # Document Catalog Explorer & Uploader
│   │   │   └── layout/           # Navbar, footer, navigation tabs
│   │   ├── context/              # SystemContext (version & health state)
│   │   ├── hooks/                # useHealth, useDocuments
│   │   ├── pages/                # DashboardPage
│   │   ├── services/             # Axios client services (chat, docs, analytics, rag, health)
│   │   ├── App.jsx               # Root tab navigation layout
│   │   └── main.jsx              # React entrypoint
│   ├── package.json              # Frontend npm dependencies
│   ├── tailwind.config.js        # Tailwind CSS config
│   └── vite.config.js            # Vite bundler config
├── docs/
│   ├── architecture.md           # System diagrams & data flows
│   ├── methodology.md            # Mathematical formulation & RRF design
│   ├── evaluation.md             # RAG Triad benchmark methodology & results
│   └── api_documentation.md      # Comprehensive REST API reference
├── scripts/
│   ├── generate_sample_docs.py   # Generates v1.0, v2.0, v3.0 documentation
│   ├── run_evaluation.py         # Evaluation benchmark harness runner
│   └── setup_project.py          # Environment verification & DB setup
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python:** 3.10+ (Tested on Python 3.13)
- **Node.js:** v18+ (Tested on Node.js v24 & npm 11)

---

### 2. Configuration (`backend/.env`)

Configure the LLM engine of your choice in `backend/.env`:

#### Option A: Google Gemini API (Cloud)
```env
LLM_PROVIDER="gemini"
GEMINI_API_KEY="your_actual_gemini_api_key_here"
GEMINI_MODEL="gemini-1.5-flash"
```

#### Option B: Ollama (Local Offline Model)
```env
LLM_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3"
OLLAMA_TIMEOUT=60
```

*(If Ollama is selected but offline, the pipeline automatically falls back to deterministic extractive synthesis without crashing).*

---

### 3. Start the Backend (FastAPI)

```powershell
# From project root:
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```
- **API Health:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 4. Start the Frontend (React + Vite)

```powershell
cd frontend
npm install
npm run dev
```
- **Web Application:** **[http://127.0.0.1:5173/](http://127.0.0.1:5173/)**

---

### 5. Run the Automated Test Suite

```powershell
# Run all 45 unit and integration tests:
python -m pytest backend/tests/ -v
```

---

### 6. Run the Academic Benchmark Suite

```powershell
python scripts/run_evaluation.py
```

Benchmark output:
```
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
```

---

## 📚 Technical Documentation Index

For in-depth explanations, mathematical formulas, and endpoint references:
1. [Architecture & System Design](docs/architecture.md)
2. [Methodology & Hybrid Retrieval Formulation](docs/methodology.md)
3. [Evaluation Metrics & Benchmark Results](docs/evaluation.md)
4. [Complete REST API Reference](docs/api_documentation.md)

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
- [x] **Additional Task: Interchangeable LLM Provider Subsystem**
  - Abstract `BaseLLMProvider` interface
  - Separate `GeminiProvider` and `OllamaProvider`
  - Runtime switching via `LLM_PROVIDER=gemini` or `LLM_PROVIDER=ollama` in `.env`
- [x] **Phase 6: Frontend Integration & Admin Dashboard**
  - Upgraded Admin Dashboard with live KPI cards, documents table, and system health
  - Upgraded Customer Chat Assistant with product selector, copy answer, and citation modal
  - Evaluation & Analytics dashboard with live RAG Triad benchmark execution
  - Comprehensive documentation suite in `docs/`
