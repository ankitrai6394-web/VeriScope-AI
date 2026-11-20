# VeriScope AI 🔬

**Autonomous Multi-Agent Research & Fact-Checking Platform**

> Built for **Hack2skill PromptWars x Agent X 2.0** | Problem Statement **PS03 – Multi-Agent Research & Fact-Checking**

---

## Overview

VeriScope AI is a genuinely intelligent research assistant powered by **7 specialized autonomous AI agents** that independently research a topic, collect external evidence, extract atomic factual claims, verify them against independent sources, detect contradictions, and synthesize a structured research dossier — all without fabricating a single citation.

This is not a chatbot. It is a full-stack multi-agent research and verification platform.

---

## Problem Statement Addressed

**PS03:** Build a sophisticated multi-agent AI system that independently researches a given topic, collects evidence, verifies factual claims, detects contradictions between sources and generates a structured research report with transparent citations.

---

## Chosen Vertical

**Problem Statement PS03: Multi-Agent Research & Fact-Checking**

In the modern information ecosystem, LLMs often hallucinate or present unverified assertions as fact. VeriScope AI addresses this challenge by implementing an institutional-grade, multi-agent research architecture that mimics a collaborative team of human investigative journalists, research analysts, and fact-checkers.

---

## Approach & Core Logic

1. **Decomposition over Generalization:** Complex queries cannot be reliably answered in a single LLM prompt. The system breaks queries into sub-questions and orthogonal search queries.
2. **Strict Evidence Grounding:** Claims are only extracted from actual retrieved textual evidence. No claim is accepted without mapping to an explicit `source_id`.
3. **Multi-Perspective Verification:** Claims are classified using a 5-tier taxonomy (`SUPPORTED`, `CONTRADICTED`, `PARTIALLY_SUPPORTED`, `INSUFFICIENT_EVIDENCE`, `CONFLICTING_EVIDENCE`). LLM generation is never accepted as proof.
4. **Discrepancy Diagnosis:** When two sources disagree (e.g. 84% adoption vs 22% hiring decline), Agent 6 investigates the methodological root cause (divergent timeframes, sample populations, or operational definitions) rather than arbitrarily declaring one source false.
5. **Fail-Safe Deterministic Fallback:** In the absence of live API keys, the system operates seamlessly in Demo Mode using authentic, empirically-curated data, preventing unexpected failures during evaluation.

---

## How the Solution Works

1. **User Submission:** The user submits a research question via the React workspace UI or REST API.
2. **Planning & Discovery:** Agent 1 generates sub-questions and search queries; Agent 2 executes live web search (via Tavily) or curated retrieval, deduplicating URLs and enforcing SSRF guards.
3. **Atomic Extraction:** Agent 3 extracts discrete factual statements and quantitative metrics, binding each to its original source citation (`SRC-001`, `SRC-002`, etc.).
4. **Parallel Analysis:** Agents 4 and 5 run concurrently via Python's `asyncio.gather()`:
   - Agent 4 evaluates claims against independent cross-source evidence.
   - Agent 5 computes transparent credibility scores based on domain authority, recency, and primary vs. secondary status.
5. **Contradiction Resolution:** Agent 6 cross-examines findings across all sources, flagging nuanced contradictions.
6. **Synthesis:** Agent 7 compiles an 11-section research dossier with executive summaries, findings tables, limitations, and transparent citation links.
7. **Interactive Dashboard:** Results are presented in real time with interactive charts, source explorers, and detailed agent telemetry audit logs.

---

## Assumptions Made

1. **Source Veracity vs Authority:** A recognized institutional domain (e.g., `.gov`, `.edu`, NASSCOM, WEF) signifies reputable methodology, but individual claims within these sources still require corroboration.
2. **Confidence Metric Interpretation:** Numerical confidence scores (0.0 to 1.0) represent model-assessed evidence alignment rather than mathematically calibrated statistical probabilities.
3. **Search Provider Availability:** When external search APIs (Tavily) or LLM endpoints (Gemini) are unconfigured or encounter rate limits, the system assumes the evaluator requires a reliable demonstration of the multi-agent logic, smoothly activating verified demo datasets without hallucinating live results.
4. **Storage Model:** SQLite with WAL mode is assumed sufficient for single-user and competition evaluation environments. In enterprise deployment, connection configuration points directly to PostgreSQL.
5. **Query Scope:** The platform assumes research queries are focused on factual, empirical, or socio-economic questions rather than purely subjective, creative, or speculative prompts.

---

## Key Features

| Feature | Description |
|---|---|
| ✅ **7 Specialized Agents** | Each agent has a unique role, strict Pydantic I/O contract, and independent testability |
| 🔍 **Multi-Source Discovery** | Integrates Tavily Search API or falls back to verified deterministic demo data |
| 📊 **5-Stage Verification Taxonomy** | SUPPORTED / CONTRADICTED / PARTIALLY_SUPPORTED / CONFLICTING_EVIDENCE / INSUFFICIENT_EVIDENCE |
| 🔀 **Contradiction Diagnosis** | Investigates divergence causes: date, population, definition, methodology |
| 📖 **11-Section Research Dossier** | Full structured report with transparent citations (CLM-xxx / SRC-xxx) |
| 🛡️ **Security Hardened** | SSRF protection, prompt injection sandboxing, input length caps, secret masking |
| 🧪 **Demo Mode** | Deterministic verified data works without any paid API credentials |
| ⚡ **Async Concurrent Pipeline** | Agents 4 and 5 run concurrently via `asyncio.gather` for efficiency |
| ♿ **Accessible UI** | WCAG 2.1 AA practices: keyboard nav, ARIA labels, semantic HTML |

---

## Multi-Agent Architecture

```
USER QUERY
    │
    ▼
[Agent 1] Research Planner
    │   Decomposes query → 3-5 sub-questions + search queries
    ▼
[Agent 2] Research Discovery
    │   Retrieves URLs, titles, snippets, deduplicates, SSRF-checks
    ▼
[Agent 3] Evidence Extraction
    │   Extracts atomic factual claims (CLM-001...) mapped to sources (SRC-001...)
    │
    ├──────────────────────────────────────┐
    ▼                                      ▼
[Agent 4] Fact Verification       [Agent 5] Source Reliability
    │  5-stage epistemic status         │   Domain trust, recency, primary/secondary
    └─────────────────┬────────────────┘
                      ▼
           [Agent 6] Contradiction Detection
               │   Root-cause analysis of divergences
               ▼
           [Agent 7] Report Generation
               │   11-section structured research dossier
               ▼
         FINAL VERIFIED RESEARCH DOSSIER
```

---

## Technology Stack

### Backend
- **Python 3.11+** / **FastAPI** / **Pydantic v2** / **SQLAlchemy (async)** / **SQLite + aiosqlite**

### Frontend
- **React 18** / **Vite** / **TypeScript** / **Tailwind CSS** / **Lucide React** / **Recharts** / **React Router v6**

### AI & Search
- **Gemini 1.5 Flash** (default) or **OpenAI GPT-4o** via configurable adapter
- **Tavily Search API** for live web research
- **Deterministic Mock Providers** for demo mode

---

## Project Structure

```
veriscope-ai/
├── backend/
│   ├── app/
│   │   ├── agents/        # 7 specialized autonomous agents
│   │   ├── api/           # FastAPI route handlers
│   │   ├── core/          # Config, settings
│   │   ├── database/      # Async SQLAlchemy engine + base
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── providers/     # LLM + Search provider adapters
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Orchestration engine
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/         # 6 application pages
│       ├── layouts/       # Navbar + Footer
│       ├── services/      # API client (Axios)
│       ├── types/         # TypeScript interfaces
│       └── utils/         # Formatting helpers
├── docs/
│   ├── PROBLEM_REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   └── TESTING.md
├── .env.example
├── .gitignore
└── README.md
```

---

## Installation & Setup (Windows)

### Prerequisites
- Python 3.11+ 
- Node.js 18+
- npm 8+

### 1. Clone the Repository

```bash
git clone <repository-url>
cd veriscope-ai
```

### 2. Configure Environment Variables

```bash
copy .env.example .env
```

Edit `.env`:

```env
# LLM Provider (leave blank for demo mode)
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash

# Search Provider (leave blank for demo mode)
SEARCH_PROVIDER=tavily
SEARCH_API_KEY=your_tavily_api_key_here

DATABASE_URL=sqlite:///./veriscope.db
```

> **Demo Mode**: Leave both API keys blank — VeriScope AI runs fully on verified deterministic sample data with no paid API required.

### 3. Backend Setup

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be live at: **http://127.0.0.1:8000**  
Swagger docs: **http://127.0.0.1:8000/docs**

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be live at: **http://localhost:5173**

---

## Running Tests

```bash
# Backend tests (zero API keys required - all use mock providers)
python -m pytest -v

# Frontend build validation
cd frontend && npm run build
```

Expected: **11/11 backend tests pass** | **Frontend build: ✓**

---

## API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/research` | Start a new research session |
| `GET` | `/api/research/{id}/status` | Poll live agent execution progress |
| `GET` | `/api/research/{id}/claims` | Get verified claims with status |
| `GET` | `/api/research/{id}/sources` | Get scored source list |
| `GET` | `/api/research/{id}/report` | Get final 11-section dossier |
| `GET` | `/api/research/{id}/agents` | Get agent telemetry audit log |
| `GET` | `/api/research/history` | Get session history |
| `DELETE` | `/api/research/{id}` | Delete a session |
| `GET` | `/api/health` | Backend health + provider status |

Full interactive docs at `/docs` after starting the backend.

---

## Application Pages

| Page | Route | Description |
|---|---|---|
| Landing | `/` | Hero, feature cards, multi-agent visualization |
| Workspace | `/workspace` | Research input, real-time agent telemetry |
| Results | `/results/:id` | Verified claims, contradictions, source explorer, dossier |
| Agent Activity | `/results/:id/agents` | Full structured JSON output per agent |
| History | `/history` | Paginated past investigations |
| Settings | `/settings` | Provider status, security diagnostics |

---

## Evaluation Alignment

| Criterion | Implementation |
|---|---|
| **Code Quality** | Modular architecture, Pydantic v2 schemas, typed Python + TypeScript, single-responsibility agents |
| **Security** | SSRF blocking, prompt injection isolation, input capping (500 chars), zero secrets in API responses |
| **Efficiency** | Async FastAPI, concurrent Agent 4+5 via `asyncio.gather`, source deduplication, bounded LLM calls |
| **Testing** | 11 automated tests covering all 7 agents, REST APIs, health checks, error scenarios |
| **Accessibility** | WCAG 2.1 AA: semantic HTML, focus indicators, ARIA labels, keyboard nav, reduced motion support |
| **PS03 Alignment** | Full 7-agent pipeline: planning → discovery → extraction → verification → reliability → contradiction → report |

---

## Limitations

- LLM confidence values are model assessments, not calibrated probabilities.
- In demo mode, source data is authentic but fixed — it does not reflect real-time web content.
- SQLite is used for simplicity; a production deployment would use PostgreSQL.

---

## Competition Submission

- Repository: Single `main` branch only.
- Size: Below 10 MB (excludes `node_modules`, `venv`, `.env`, SQLite files).
- Branch restriction: `main` only.

---

> VeriScope AI — Research Smarter. Verify Better.
