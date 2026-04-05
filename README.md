# Executive Decision Studio

**Agentic AI Strategic Intelligence Platform for Alinta Energy**

A production Databricks App that gives board directors, the CFO, and the C-suite real-time access to strategic intelligence — powered by Claude Sonnet 4.6, RAG over 22 board documents, live SQL KPIs, and a multi-agent supervisor architecture on Databricks Mosaic AI.

**Live demo:** https://exec-decision-studio-7474646159107961.aws.databricksapps.com

---

## What it does

| Capability | Detail |
|------------|--------|
| **Strategic Chat** | RAG-powered Q&A over 22 classified board documents; supervisor agent routes queries; SSE streaming with inline Recharts visualisations |
| **Executive Overview** | Live KPI cards, risk heatmap, action items, decision log — every metric clickable to drill-down drawer with AI analysis |
| **AI Briefing** | On-demand executive briefings (Weekly, Board, Investor, Crisis); 4 000-token Claude response; markdown tables; PDF / PPTX / MD export |
| **KPI Dashboard** | 12 KPIs across 4 business units with trend sparklines and status badges |
| **Risk Register** | Enterprise risk register with likelihood/consequence matrix |
| **Decision Log** | Board & ELT decision tracker with implementation status |
| **Action Items** | Executive action register with owner and due-date tracking |
| **Document Library** | 22-doc corpus with classification tiers, format icons, filter panel, click-to-expand, document upload |
| **Market Intelligence** | Live competitor news (GDELT), ASX peer stocks (Yahoo Finance), carbon prices (CER) |
| **Audit Log** | Full agent interaction audit trail |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Databricks App                           │
│                                                             │
│  React (Vite + TypeScript + Tailwind)                       │
│  ├── 11 tabs, SSE streaming, Recharts, PDF/PPTX export      │
│  └── Alinta Energy dark-mode brand (#F47920 orange)         │
│                                                             │
│  FastAPI (uvicorn)                                          │
│  ├── 17 routes — KPI, risks, decisions, chat, briefing      │
│  ├── SQL Warehouse for live data (Unity Catalog)            │
│  └── Databricks serving endpoint (Claude Sonnet 4.6)        │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                 Databricks Workspace                        │
│                                                             │
│  Unity Catalog: ausnet_process_intel_catalog                │
│  ├── eds_synthetic  — KPIs, risks, decisions, financials    │
│  ├── eds_processed  — chunked + embedded doc segments       │
│  ├── eds_vectors    — Vector Search index                   │
│  ├── eds_agents     — MLflow RAG chain model                │
│  ├── eds_actions    — action items                          │
│  └── eds_audit      — agent interaction log                 │
│                                                             │
│  Vector Search endpoint: eds-vector-search                  │
│  Embedding model:        databricks-gte-large-en            │
│  LLM:                    databricks-claude-sonnet-4-6       │
│  Supervisor endpoint:    eds-supervisor (MLflow)            │
└─────────────────────────────────────────────────────────────┘
```

### Agent Architecture

The supervisor follows a Mosaic AI Agent Bricks pattern:

```
User query
    │
    ▼
Supervisor Agent (eds-supervisor endpoint)
    ├── RAG Chain        — document retrieval + synthesis
    ├── KPI Analyst      — live KPI data interpretation
    ├── Risk Analyst     — risk register analysis
    ├── Decision Tracker — board decision status
    └── Market Intel     — competitor / regulatory context
```

---

## Repository layout

```
.
├── app/                          # Databricks App source
│   ├── app.py                    # FastAPI entrypoint
│   ├── app.yaml                  # Databricks App config (resources, env)
│   ├── requirements.txt          # Python dependencies
│   ├── server/
│   │   ├── config.py             # Auth, warehouse, token helpers
│   │   └── routes/
│   │       ├── overview.py       # GET /api/overview + /drilldown
│   │       ├── chat.py           # POST /api/chat/stream (SSE + RAG)
│   │       ├── briefing.py       # POST /api/briefing/stream (SSE)
│   │       ├── kpi.py            # GET /api/kpi
│   │       ├── risks.py          # GET /api/risks
│   │       ├── decisions.py      # GET /api/decisions
│   │       ├── actions.py        # GET /api/actions
│   │       ├── audit.py          # GET /api/audit
│   │       ├── documents.py      # GET /api/documents + POST /upload
│   │       ├── market.py         # GET /api/market/news|stocks|carbon
│   │       └── export.py         # POST /api/export/pptx
│   └── frontend/
│       ├── src/components/       # 11 React tab components
│       ├── vite.config.ts
│       └── package.json
├── notebooks/
│   ├── 00_init/                  # Schema setup, synthetic data, SP grants
│   ├── 01_ingestion/             # Document chunking + embedding
│   ├── 02_rag/                   # RAG chain (LangChain + MLflow)
│   └── 03_agents/                # Supervisor agent deployment
├── scripts/
│   └── deploy_supervisor.py      # End-to-end automation script
├── databricks.yml                # DAB bundle (5 jobs)
├── status.md                     # Live deployment state
├── DEMO.md                       # 15-min demo script
└── PRD - Agentic AI Strategic Intelligence Platform.md
```

---

## Deploying from scratch

### Prerequisites

- Databricks CLI ≥ 0.229 authenticated to a **Serverless** workspace
- `uv` or `pip` for Python
- `node` ≥ 18 + `npm` for frontend builds

### 1. Deploy infrastructure (DAB bundle + jobs)

```bash
# Authenticate
databricks auth login https://<your-workspace>.cloud.databricks.com --profile <profile>

# Deploy bundle (creates 5 jobs)
databricks bundle deploy --profile=<profile>

# Run jobs in order
databricks jobs run-now <job_id_00> --profile=<profile>   # Setup + synthetic data + SP grants
databricks jobs run-now <job_id_01> --profile=<profile>   # Document ingestion + embedding
databricks jobs run-now <job_id_02> --profile=<profile>   # RAG chain → MLflow model
databricks jobs run-now <job_id_03> --profile=<profile>   # Supervisor agent endpoint
```

Job IDs are printed after `bundle deploy`. Alternatively run the full automation:

```bash
python scripts/deploy_supervisor.py --profile=<profile>
```

### 2. Deploy the app

```bash
APP_DIR="app"
WS_PATH="/Workspace/Users/<you>/eds-app"
PROFILE="<profile>"

# Build frontend
cd "$APP_DIR/frontend" && npm install && npm run build && cd ..

# Sync backend
databricks sync . "$WS_PATH" --profile "$PROFILE" \
  --exclude "frontend/src" --exclude "frontend/node_modules" \
  --exclude "__pycache__" --exclude ".venv"

# Upload built frontend
databricks workspace import-dir "$APP_DIR/frontend/dist" "$WS_PATH/frontend/dist" \
  --overwrite --profile "$PROFILE"

# Create and deploy app
databricks apps create eds --source-code-path "$WS_PATH" --profile "$PROFILE"
databricks apps deploy eds --source-code-path "$WS_PATH" --profile "$PROFILE"
```

### 3. Add app resources (UI)

In **Compute → Apps → eds → Edit**, add:

| Resource | Type | Permission |
|----------|------|------------|
| SQL Warehouse | `sql_warehouse` | CAN_USE |
| Claude Sonnet 4.6 | `serving_endpoint` → `databricks-claude-sonnet-4-6` | CAN_QUERY |

Redeploy after adding resources.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide icons |
| **Backend** | FastAPI, uvicorn, python-pptx, requests |
| **LLM** | Claude Sonnet 4.6 via Databricks serving endpoint |
| **RAG** | LangChain, MLflow (models-from-code), Databricks Vector Search |
| **Embeddings** | `databricks-gte-large-en` |
| **Data** | Databricks SQL Warehouse, Unity Catalog, Delta Lake |
| **Deployment** | Databricks Apps, Databricks Asset Bundles |
| **Auth** | Service principal (auto-injected by Databricks Apps runtime) |

---

## Key design decisions

**SSE streaming** — both `/api/chat/stream` and `/api/briefing/stream` use Server-Sent Events with typed events (`meta`, `token`, `chart`, `done`). The `StreamingResponse` is returned before any SQL or LLM calls to prevent proxy timeouts.

**Demo fallback** — every route checks for a live SQL warehouse. If no token or warehouse is available, it returns realistic hardcoded demo data so the app never shows empty state.

**SP grants at runtime** — job 00 discovers the app's service principal UUID via the Apps API and issues all required `GRANT` statements dynamically, so permissions survive app recreation.

**models-from-code** — the RAG chain is logged to MLflow by writing the chain definition to a temp `.py` file and passing the path (LangChain v1 requirement). The registered model is served via a Databricks Model Serving endpoint with a `ModelSignature`.

---

## Demo script

See [DEMO.md](DEMO.md) for the full 15-minute board-level demo walkthrough.

---

## Status

See [status.md](status.md) for live deployment details, job IDs, infrastructure endpoints, and re-run instructions.
