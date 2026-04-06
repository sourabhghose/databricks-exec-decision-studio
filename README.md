# Executive Decision Studio

**Agentic AI Strategic Intelligence Platform for Alinta Energy**

A production Databricks App that gives board directors, the CFO, and the C-suite real-time access to strategic intelligence — powered by Claude Sonnet 4.6, RAG over 22 board documents, live SQL KPIs, Bear/Base/Bull scenario simulation, and a multi-agent architecture on Databricks Mosaic AI.

---

## What it does

| Capability | Detail |
|------------|--------|
| **Strategic Chat** | RAG-powered Q&A over 22 classified board documents; SSE streaming with inline Recharts visualisations; 32 C-level sample questions; PDF / PPTX / MD export |
| **AI Briefing** | On-demand executive briefings (Weekly, Board, Investor, Crisis); 4 000-token Claude response; markdown tables; PDF / PPTX / MD export |
| **Scenario Simulation** | Bear / Base / Bull decision simulation grounded in live Alinta KPI, financial, and risk data; 15 Alinta-specific quick-start templates; drill-down narrative; save to Decision Register |
| **Executive Overview** | Live KPI cards, risk heatmap, action items, decision log — every metric clickable to drill-down drawer with AI analysis |
| **Market Intelligence** | Live competitor news (GDELT), ASX peer stocks with sparklines (Yahoo Finance), carbon prices with trend charts (CER) |
| **KPI Dashboard** | 12 KPIs across 4 business units with trend sparklines and status badges |
| **Risk Register** | Enterprise risk register with likelihood/consequence matrix |
| **Decision Register** | Board & ELT decision tracker with implementation status; accepts scenario outcomes |
| **Action Items** | Executive action register with owner and due-date tracking |
| **Document Library** | 22-doc corpus with classification tiers, format icons, filter panel, click-to-expand, document upload to UC Volume |
| **Audit Log** | Full agent interaction audit trail |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Databricks App                            │
│                                                                 │
│  React 18 (Vite + TypeScript + Tailwind CSS)                    │
│  ├── AI Assistant dropdown (Strategic Chat / Briefing / Sim)    │
│  ├── SSE streaming — token + result + chart events              │
│  ├── Recharts inline charts, PDF/PPTX/MD export                 │
│  └── Alinta Energy dark-mode brand (#F47920 orange)             │
│                                                                 │
│  FastAPI (uvicorn)                                              │
│  ├── 19 routes — overview, chat, briefing, simulate, KPI …      │
│  ├── SQL Warehouse for live data (Unity Catalog)                │
│  └── Databricks serving endpoint (Claude Sonnet 4.6)           │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                    Databricks Workspace                         │
│                                                                 │
│  Unity Catalog: ausnet_process_intel_catalog                    │
│  ├── eds_synthetic  — KPIs, risks, decisions, financials        │
│  ├── eds_processed  — chunked + embedded doc segments           │
│  ├── eds_vectors    — Vector Search index                       │
│  ├── eds_agents     — MLflow RAG chain model                    │
│  ├── eds_actions    — action items + decision register          │
│  └── eds_audit      — agent interaction log                     │
│                                                                 │
│  Vector Search endpoint:  eds-vector-search                     │
│  Embedding model:         databricks-gte-large-en               │
│  LLM:                     databricks-claude-sonnet-4-6          │
└─────────────────────────────────────────────────────────────────┘
```

### Navigation

```
Overview  │  AI Assistant ▾         │  Market Intel  │  KPI Dashboard  │  Risk Register
          │   ├ Strategic Chat      │  Decisions  │  Action Items  │  Document Library
          │   ├ AI Briefing         │  Audit Log  │  About
          └   └ Simulation
```

### Scenario Simulation flow

```
Board defines decision
        │
        ▼
POST /api/simulate/stream
        │
        ├── Fetch live context (KPIs, financials, risks from Unity Catalog)
        │
        ├── Claude Sonnet 4.6 → Bear / Base / Bull JSON (streaming tokens)
        │        └── result event (complete JSON for reliable parsing)
        │
        ├── Frontend renders 3 scenario cards
        │        probability bar · headline · KPI impact table · risk factors
        │
        ├── Board selects branch → drill-down stream
        │        Implementation Roadmap · Risk Mitigations
        │        90-Day Board Actions · Key Metrics
        │
        └── Save to Decision Register → POST /api/decisions/save
```

---

## Repository layout

```
.
├── app/                              # Databricks App source (source-code-path)
│   ├── app.py                        # FastAPI entrypoint
│   ├── app.yaml                      # Databricks App config (resources, env)
│   ├── requirements.txt
│   ├── server/
│   │   ├── config.py                 # Auth, LLM prompts, warehouse helpers
│   │   └── routes/
│   │       ├── overview.py           # GET /api/overview + /drilldown
│   │       ├── chat.py               # POST /api/chat/stream (SSE + RAG)
│   │       ├── briefing.py           # POST /api/briefing/stream (SSE)
│   │       ├── simulate.py           # POST /api/simulate/stream (SSE Bear/Base/Bull)
│   │       ├── kpi.py
│   │       ├── risks.py
│   │       ├── decisions.py          # GET + POST /api/decisions/save
│   │       ├── actions.py
│   │       ├── audit.py
│   │       ├── documents.py          # GET + POST /upload
│   │       ├── market.py             # news · stocks · carbon
│   │       ├── export.py             # POST /api/export/pptx
│   │       └── …
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx               # Navigation + tab routing
│       │   └── components/           # 12 React tab components
│       ├── vite.config.ts
│       └── package.json
├── notebooks/
│   ├── 00_setup/
│   │   ├── 00_init_schemas.py        # Schema + synthetic data + SP grants banner
│   │   └── 05_grant_app_permissions.py  # Standalone SP grants (run after deploy)
│   ├── 01_ingestion/                 # Document chunking + embedding
│   ├── 02_rag/                       # RAG chain (LangChain + MLflow)
│   └── 03_agents/                    # Supervisor agent deployment
├── scripts/
│   └── deploy.sh                     # Canonical 4-step deploy workflow
├── databricks.yml                    # DAB bundle (jobs + app resource)
├── status.md                         # Live deployment state + endpoints
├── DEMO.md                           # 15-min board-level demo script
└── PRD - Agentic AI Strategic Intelligence Platform.md
```

---

## Deploying

### Prerequisites

- Databricks CLI ≥ 0.229 authenticated to a **Serverless** workspace
- Node ≥ 18 + npm

### 1. Deploy infrastructure

```bash
# Authenticate
databricks auth login https://<workspace>.cloud.databricks.com --profile <profile>

# Deploy DAB bundle (creates jobs + binds app resource)
databricks bundle deploy --profile=<profile>

# Run setup jobs in order
databricks jobs run-now <job_00>  # Schema + synthetic data
databricks jobs run-now <job_01>  # Document ingestion + embedding
databricks jobs run-now <job_02>  # RAG chain → MLflow
databricks jobs run-now <job_03>  # Supervisor agent endpoint
```

### 2. Deploy the app

Use the provided script — handles build, sync, dist upload, and deploy in one step:

```bash
./scripts/deploy.sh <profile>
# e.g. ./scripts/deploy.sh fe-vm-ausnet-process-intel
```

Which runs:
```bash
# 1. Build frontend
cd app/frontend && npm run build

# 2. Sync all source files (respects .gitignore exclusions)
databricks sync . /Workspace/Users/<you>/eds-app \
  --exclude node_modules --exclude .venv --exclude __pycache__ --exclude .git \
  --profile $PROFILE --full

# 3. Upload built dist/ (gitignored — must be uploaded separately)
databricks workspace import-dir app/frontend/dist \
  /Workspace/Users/<you>/eds-app/app/frontend/dist \
  --overwrite --profile $PROFILE

# 4. Deploy (source-code-path = eds-app/app, NOT eds-app/)
databricks apps deploy exec-decision-studio \
  --source-code-path /Workspace/Users/<you>/eds-app/app \
  --profile $PROFILE
```

> **Important:** `source-code-path` must point to `eds-app/app` (where `app.yaml` lives), not the project root.

### 3. Grant SP permissions

After the first deploy, run the permissions notebook to grant the app's service principal access to Unity Catalog, the SQL warehouse, and the Vector Search index:

```bash
databricks jobs run-now <eds_grant_permissions_job_id> --profile=<profile>
```

Or manually in the Databricks UI: run `notebooks/00_setup/05_grant_app_permissions.py`.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide icons |
| **Backend** | FastAPI, uvicorn, python-pptx, requests |
| **LLM** | Claude Sonnet 4.6 via Databricks Model Serving |
| **RAG** | LangChain, MLflow (models-from-code), Databricks Vector Search |
| **Embeddings** | `databricks-gte-large-en` |
| **Data** | Databricks SQL Warehouse, Unity Catalog, Delta Lake |
| **Deployment** | Databricks Apps, Databricks Asset Bundles (DABs) |
| **Auth** | Service principal (auto-injected by Databricks Apps runtime) |

---

## Key design decisions

**SSE streaming with `result` event** — `/api/chat/stream`, `/api/briefing/stream`, and `/api/simulate/stream` use Server-Sent Events. The scenario simulator additionally emits a `result` event carrying the complete assembled JSON after all token fragments, eliminating chunk-boundary parsing failures across HTTP/2 frames.

**`StreamingResponse` returned immediately** — context fetching (SQL, embeddings) and LLM calls happen inside the generator, so the response is returned before any blocking work begins. This prevents the Databricks Apps proxy from timing out on slow queries.

**Demo fallback on every route** — every API route checks for a live SQL warehouse and token. If unavailable, it returns realistic hardcoded demo data (`"demo": true` in the response). The app never shows empty state.

**SP grants at runtime** — `05_grant_app_permissions.py` discovers the app's service principal UUID via the Apps API + SCIM, then issues all required `GRANT` statements dynamically. Permissions survive app recreation.

**Scenario grounding in live data** — before calling Claude, `/api/simulate/stream` fetches the latest KPIs, financial summary by business unit, and open High/Critical risks from Unity Catalog. This grounds Bear/Base/Bull projections in real Alinta numbers rather than hallucinated percentages.

---

## Status

See [status.md](status.md) for live deployment details, all API routes, job IDs, and infrastructure endpoints.

See [DEMO.md](DEMO.md) for the 15-minute board-level demo walkthrough.
