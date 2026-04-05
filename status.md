# Executive Decision Studio — Project Status
**Last updated:** 2026-04-05 (session 5)

---

## App

| Property | Value |
|----------|-------|
| Name | `exec-decision-studio` |
| URL | https://exec-decision-studio-7474646159107961.aws.databricksapps.com |
| Compute | ACTIVE |
| App | RUNNING |
| Workspace | https://fevm-ausnet-process-intel.cloud.databricks.com |
| CLI Profile | `fe-vm-ausnet-process-intel` |

---

## Catalog

| Property | Value |
|----------|-------|
| Catalog | `ausnet_process_intel_catalog` |
| Workspace storage | `s3://ausnet-process-intel-ext-s3-049629455384-65nhp7/` |

### Schemas

| Schema | Purpose |
|--------|---------|
| `eds_raw` | Staged documents ingested from volume |
| `eds_processed` | Chunked + embedded document segments |
| `eds_synthetic` | Synthetic source data (documents, KPIs, financials, risks) |
| `eds_actions` | Action items and decision register |
| `eds_audit` | Agent interaction audit trail |
| `eds_evaluation` | RAG evaluation QA pairs |
| `eds_vectors` | Vector Search index |

### Volume

```
/Volumes/ausnet_process_intel_catalog/eds_raw/documents/
  tier1/   ← 9 docs  (RESTRICTED/CONFIDENTIAL — Board / C-Suite)
  tier2/   ← 4 docs  (CONFIDENTIAL — ELT)
  tier3/   ← 2 docs  (INTERNAL — Senior Management)
  tier4/   ← 0 docs  (All Staff)
```

Each file: `{doc_id}.txt` with YAML frontmatter + full document text.

---

## Databricks Jobs

| Job ID | Name | Last Status |
|--------|------|-------------|
| 386141348959921 | [EDS] 00 - Setup & Synthetic Data | SUCCESS |
| 950647315295103 | [EDS] 01 - Document Ingestion & Embedding | SUCCESS |
| 110001778150925 | [EDS] 02 - RAG Chain Setup | SUCCESS |
| 307588500376638 | [EDS] 03 - Deploy Agents | SUCCESS |

---

## Infrastructure

| Component | Name / Value |
|-----------|-------------|
| Vector Search endpoint | `eds-vector-search` |
| VS index | `ausnet_process_intel_catalog.eds_vectors.document_chunks_index` |
| Embedding model | `databricks-gte-large-en` |
| LLM endpoint | `databricks-claude-sonnet-4-6` ✅ (upgraded from llama-3.3-70b) |
| SQL Warehouse | `33baaa9523773520` (Process Intelligence Warehouse) |
| MLflow model | `ausnet_process_intel_catalog.eds_agents.rag_chain` |
| MLflow experiment | `/Users/sourabh.ghose@databricks.com/EDS_rag_chain_experiment` |

---

## React Frontend (11 tabs)

| Tab | Component | Backend |
|-----|-----------|---------|
| **Overview** *(default)* | `Overview.tsx` | `GET /api/overview` |
| Strategic Chat | `Chat.tsx` | `POST /api/chat/stream` (SSE streaming RAG) |
| KPI Dashboard | `KPIDashboard.tsx` | `GET /api/kpi` |
| Risk Register | `RiskRegister.tsx` | `GET /api/risks` |
| Decisions | `DecisionRegister.tsx` | `GET /api/decisions` |
| Action Items | `ActionItems.tsx` | `GET /api/actions` |
| Document Library | `DocumentLibrary.tsx` | `GET /api/documents` |
| AI Briefing | `Briefing.tsx` | `POST /api/briefing/stream` (SSE) |
| Market Intel | `MarketIntelligence.tsx` | `GET /api/market/news`, `/api/market/stocks`, `/api/market/carbon` |
| Audit Log | `AuditLog.tsx` | `GET /api/audit` |
| About | `About.tsx` | — |

### Key frontend features
- **Executive Overview drill-down** — every metric is clickable: 4 hero stat cards (KPIs / Risks / Actions / AI Queries), 6 KPI performance cards, Risk Distribution bar chart, KPI Health Status pie chart, Action Items bar chart; each opens a right-side drawer via `ReactDOM.createPortal` with an AI analysis panel (`ai_query('databricks-claude-sonnet-4-6', ...)`) + full item list; `GET /api/overview/drilldown?metric=&filter_key=&filter_val=` backend
- **Inline chat charts** — Recharts `BarChart`/`LineChart` rendered inside assistant messages via SSE `{"type":"chart"}` event
- **AI Briefing** — SSE streaming with 4 briefing types (Weekly, Board, Investor, Crisis); live reporting period from `kpi_timeseries`; markdown table rendering; PDF/PPTX/MD export; context built inside generator (fixes proxy 502); `max_tokens: 4000`
- **Document Library** — 22-doc grid with classification badges, tier labels, format icons, 4-dimension filter panel, click-to-expand modal
- **Market Intelligence** — 3-panel tab: competitor/regulatory news (GDELT, live), ASX peer stocks with sparklines (Yahoo Finance, live), ACCU/LGC carbon prices with trend charts + strategic implications (CER quarterly)
- **Markdown table rendering** — LLM `|pipe|tables|` parsed into proper `<table>` HTML with `thead`/`tbody`, striped rows, Alinta-themed headers (both Briefing and Chat)
- **PDF / PPTX / MD export** — PDF (browser print dialog), PPTX (python-pptx via `/api/export/pptx`), Markdown download; available at bottom of briefing and on every chat assistant message
- **Document Upload** — "Upload Document" button in Document Library header; uploads file to `UC Volume /tier4/`, triggers ingestion job 950647315295103; shows progress/success/error toast
- **32 C-level sample questions** — 6 color-coded categories replace role dropdown in Strategic Chat sidebar
- Alinta Energy brand: orange `#F47920`, **dark mode default**, light/dark toggle
- Code-split chunks: `vendor`, `charts` (540 KB recharts), `icons`

---

## Backend (FastAPI)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/overview` | GET | Aggregated executive overview (KPIs, risks, decisions, actions, audit, docs) |
| `/api/overview/drilldown` | GET | Drill-down detail + AI analysis for any metric; params: `metric`, `filter_key`, `filter_val` |
| `/api/chat` | POST | Synchronous RAG chat |
| `/api/chat/stream` | POST | SSE streaming RAG chat with inline chart events |
| `/api/kpi` | GET | KPI time series |
| `/api/risks` | GET | Risk register |
| `/api/decisions` | GET | Decision register |
| `/api/actions` | GET | Action items |
| `/api/audit` | GET | Audit log |
| `/api/documents` | GET | Document catalog (22 docs with metadata) |
| `/api/documents/upload` | POST | Upload document to UC Volume + trigger ingestion job 950647315295103 |
| `/api/briefing/stream` | POST | SSE streaming executive briefing |
| `/api/market/news` | GET | Competitor & regulatory news (GDELT, free, no key) |
| `/api/market/stocks` | GET | ASX peer stock comparison (Yahoo Finance, free, no key) |
| `/api/market/carbon` | GET | ACCU/LGC carbon market prices (CER quarterly data) |
| `/api/export/pptx` | POST | Export chat response as branded PPTX (python-pptx) |
| `/api/health` | GET | Health check |

### Live data status
- **Live data confirmed working** (`demo: false`) — warehouse discovery fixed to accept STOPPED warehouses
- **SP grants automated** — `00_init_schemas.py` discovers app SP UUID via Apps+SCIM API and runs 18 GRANT statements dynamically; survives app recreation
- **app.yaml** — warehouse resource `33baaa9523773520` injected as `DATABRICKS_WAREHOUSE_ID` env var

---

## Document Pipeline (22 synthetic documents)

| Doc ID | Title | Classification | Tier |
|--------|-------|---------------|------|
| DOC-001 | FY2025 Group Strategy Review | RESTRICTED | 1 |
| DOC-002 | Loy Yang B Transition Options | RESTRICTED | 1 |
| DOC-003 | 1H FY25 Financial Results | CONFIDENTIAL | 2 |
| DOC-004 | Competitive Intelligence Report | CONFIDENTIAL | 2 |
| DOC-005 | ESG & Climate Risk Report | CONFIDENTIAL | 1 |
| DOC-006 | Yandin Stage 2 Investment Case | RESTRICTED | 1 |
| DOC-007 | Enterprise Risk Management | CONFIDENTIAL | 2 |
| DOC-008 | WEM Capacity Mechanism Submission | INTERNAL | 3 |
| DOC-009 | FY2026 Budget Paper | RESTRICTED | 1 |
| DOC-010 | Cybersecurity & OT Security Update | RESTRICTED | 1 |
| DOC-011 | Retail Transformation Q2 FY25 | CONFIDENTIAL | 2 |
| DOC-012 | People & Culture Strategy | INTERNAL | 3 |
| DOC-013 | Trading & Hedging Strategy | RESTRICTED | 1 |
| DOC-014 | Board Skills & Governance | RESTRICTED | 1 |
| DOC-015 | Capital Allocation Framework | RESTRICTED | 1 |
| DOC-016 to DOC-022 | Additional synthetic docs | Various | Various |

---

## Recent Changes (Session 5 — 2026-04-05)

| Change | Detail |
|--------|--------|
| AI Briefing — reporting period | Live period fetched from `kpi_timeseries MAX(period)`; emitted as SSE `meta` event; shown in header |
| AI Briefing — markdown tables | `renderMarkdown()` now detects `\|pipe\|table\|` blocks, skips separator rows, renders styled HTML `<table>` |
| AI Briefing — export | PDF (print dialog), PPTX (python-pptx), MD download — visible at bottom of content after generation |
| AI Briefing — 502 fix | Context building moved inside SSE generator; `StreamingResponse` returned immediately; `max_tokens` 1800→4000 |
| AI Briefing — footer removed | Removed boilerplate "Generated by..." disclaimer text |

---

## Pending / Blocked

| Item | Status | Notes |
|------|--------|-------|
| Rename catalog to `eds` | **BLOCKED** | Requires metastore/account admin — current user lacks `CREATE CATALOG` on metastore |
| Connect chat to Supervisor Agent | **Pending** | Chat currently calls LLM directly; Supervisor Agent registered in MLflow but not wired to `/api/chat` |
| Vector Search re-sync check | **Pending** | VS returned 0 results at one point; may need `sync()` call verification |

---

## DAB Bundle

```
Bundle:  exec-decision-studio
Target:  dev
Profile: fe-vm-ausnet-process-intel
Bundle path (workspace): /Workspace/Users/sourabh.ghose@databricks.com/.bundle/exec-decision-studio/dev/files/
App source (workspace):  /Workspace/Users/sourabh.ghose@databricks.com/eds-app
```

### Re-run order (full rebuild)
```bash
databricks bundle deploy --profile=fe-vm-ausnet-process-intel
databricks jobs run-now 386141348959921 --profile=fe-vm-ausnet-process-intel  # setup + SP grants
databricks jobs run-now 950647315295103 --profile=fe-vm-ausnet-process-intel  # ingestion
databricks jobs run-now 110001778150925 --profile=fe-vm-ausnet-process-intel  # RAG
databricks jobs run-now 307588500376638 --profile=fe-vm-ausnet-process-intel  # agents
```

### Deploy app update (CORRECT workflow)
```bash
APP_DIR="/Users/sourabh.ghose/Cursor-Projects/Databricks Executive Decision Studio/app"
WS_PATH="/Workspace/Users/sourabh.ghose@databricks.com/executive-decision-studio"
PROFILE="fe-vm-ausnet-process-intel"

# 1. Build frontend
cd "$APP_DIR/frontend" && npm run build

# 2. Sync all backend files (excludes node_modules, .venv, frontend/src, etc.)
cd "$APP_DIR" && databricks sync . "$WS_PATH" --profile "$PROFILE" \
  --exclude "frontend/src" --exclude "frontend/node_modules" \
  --exclude "frontend/public" --exclude "__pycache__" --exclude ".venv" --full

# 3. Upload built frontend (import-dir overwrites individual files)
databricks workspace import-dir "$APP_DIR/frontend/dist" "$WS_PATH/frontend/dist" \
  --overwrite --profile "$PROFILE"

# 4. Redeploy
databricks apps deploy exec-decision-studio \
  --source-code-path "$WS_PATH" --profile "$PROFILE"
```

> NOTE: `databricks bundle deploy` only updates jobs/notebooks — NOT the app. Always use the 4-step workflow above.
