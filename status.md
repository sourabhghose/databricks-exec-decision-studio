# Executive Decision Studio — Project Status
**Last updated:** 2026-04-06 (session 8)

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
| LLM endpoint | `databricks-claude-sonnet-4-6` ✅ |
| SQL Warehouse | `33baaa9523773520` (Process Intelligence Warehouse) |
| MLflow model | `ausnet_process_intel_catalog.eds_agents.rag_chain` |
| MLflow experiment | `/Users/sourabh.ghose@databricks.com/EDS_rag_chain_experiment` |

---

## React Frontend (Navigation)

### Tab Structure

```
Overview  |  AI Assistant ▾  |  Market Intel  |  KPI Dashboard  |  Risk Register
          |   ├ Strategic Chat               Decisions  |  Action Items  |  Document Library
          |   ├ AI Briefing                  Audit Log  |  About
          |   ├ Simulation
          └   └ Data Insights
```

| Tab | Component | Backend |
|-----|-----------|---------|
| **Overview** *(default)* | `Overview.tsx` | `GET /api/overview` |
| AI Assistant → Strategic Chat | `Chat.tsx` | `POST /api/chat/stream` (SSE streaming RAG) |
| AI Assistant → AI Briefing | `Briefing.tsx` | `POST /api/briefing/stream` (SSE) |
| AI Assistant → Simulation | `ScenarioSimulator.tsx` | `POST /api/simulate/stream` (SSE) |
| AI Assistant → Data Insights | `GenieInsights.tsx` | `POST /api/genie/query` |
| Market Intel | `MarketIntelligence.tsx` | `GET /api/market/news`, `/stocks`, `/carbon` |
| KPI Dashboard | `KPIDashboard.tsx` | `GET /api/kpi` |
| Risk Register | `RiskRegister.tsx` | `GET /api/risks` |
| Decisions | `DecisionRegister.tsx` | `GET /api/decisions` |
| Action Items | `ActionItems.tsx` | `GET /api/actions` |
| Document Library | `DocumentLibrary.tsx` | `GET /api/documents` |
| Audit Log | `AuditLog.tsx` | `GET /api/audit` |
| About | `About.tsx` | — |

### Key frontend features
- **AI Assistant dropdown** — Bot icon tab with four sub-items (Strategic Chat, AI Briefing, Simulation, Data Insights); shows active sub-tab name inline; closes on outside click
- **Scenario Simulator** — Bear/Base/Bull decision simulation grounded in live Alinta KPI/financial/risk data; 15 Alinta-specific quick-start templates; SSE streaming with `result` event pattern for reliable JSON delivery; drill-down narrative per scenario; save to Decision Register
- **Executive Overview drill-down** — every metric clickable: hero stat cards, KPI performance cards, risk/action charts; right-side drawer with AI analysis panel
- **Inline chat charts** — Recharts `BarChart`/`LineChart` inside assistant messages via SSE `{"type":"chart"}` event
- **AI Briefing** — SSE streaming; 4 briefing types; markdown table rendering; PDF/PPTX/MD export
- **Document Library** — 22-doc grid with classification badges, tier labels, format icons, 4-dimension filter panel, click-to-expand modal
- **Market Intelligence** — competitor/regulatory news (GDELT), ASX peer stocks with sparklines (Yahoo Finance), ACCU/LGC carbon prices with trend charts
- **Document Upload** — uploads to UC Volume, triggers ingestion job
- **32 C-level sample questions** — 6 color-coded categories in Strategic Chat sidebar
- Alinta Energy brand: orange `#F47920`, dark mode default, light/dark toggle

---

## Backend (FastAPI)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/overview` | GET | Aggregated executive overview |
| `/api/overview/drilldown` | GET | Drill-down detail + AI analysis |
| `/api/chat/stream` | POST | SSE streaming RAG chat with inline charts |
| `/api/kpi` | GET | KPI time series |
| `/api/risks` | GET | Risk register |
| `/api/decisions` | GET | Decision register |
| `/api/decisions/save` | POST | Persist scenario outcome to decision register |
| `/api/actions` | GET | Action items |
| `/api/audit` | GET | Audit log |
| `/api/documents` | GET | Document catalog |
| `/api/documents/upload` | POST | Upload document to UC Volume + trigger ingestion |
| `/api/briefing/stream` | POST | SSE streaming executive briefing |
| `/api/market/news` | GET | Competitor & regulatory news (GDELT) |
| `/api/market/stocks` | GET | ASX peer stock comparison (Yahoo Finance) |
| `/api/market/carbon` | GET | ACCU/LGC carbon market prices (CER) |
| `/api/simulate/templates` | GET | 15 pre-built Alinta scenario templates |
| `/api/simulate/stream` | POST | SSE Bear/Base/Bull scenario simulation + drill-down |
| `/api/export/pptx` | POST | Export chat response as branded PPTX |
| `/api/genie/query` | POST | AI/BI Genie natural-language data query |
| `/api/health` | GET | Health check with JS bundle info |

### Live data status
- **Live data confirmed working** (`demo: false`) — warehouse discovery fixed to accept STOPPED warehouses
- **SP grants automated** — `00_init_schemas.py` discovers app SP UUID via Apps+SCIM API and runs 18 GRANT statements dynamically
- **Simulate endpoint** grounded in live KPI, financial, and risk data from Unity Catalog

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

## Recent Changes (Session 6 — 2026-04-06)

| Change | Detail |
|--------|--------|
| **Scenario Simulator tab** | New AI Assistant sub-tab "Simulation" (formerly "Scenarios"); Bear/Base/Bull decision simulation with live data grounding |
| **SSE result event** | Backend emits `{"type":"result"}` with complete assembled JSON after token stream; frontend parses from this event — eliminates chunk-boundary token loss |
| **Recommendation bias fix** | Prompt updated with explicit Bear/Bull/Base selection criteria; LLM no longer defaults to Base |
| **15 quick-start templates** | Added 10 new Alinta-specific scenarios: Battery Storage, Newman Gas, Retail Pricing, M&A Distributed Energy, Carbon/Net Zero, Hydrogen, Digital/AI Transformation, FY2027 Dividend, Cybersecurity OT |
| **AI Assistant dropdown** | Strategic Chat, AI Briefing, Simulation grouped under "AI Assistant" dropdown with Bot icon; active sub-tab shown inline |
| **Tab reorder** | Market Intel moved to position 3 (after AI Assistant dropdown) |
| **Deploy source path fix** | All deploys now use `eds-app/app` as source-code-path (was incorrectly using `eds-app/` root, serving stale backend) |
| **deploy.sh script** | `scripts/deploy.sh` created: 4-step deploy (build → sync → import-dir dist → apps deploy) with correct source path |

---

## Recent Changes (Session 7 — 2026-04-06)

| Change | Detail |
|--------|--------|
| **Data Insights tab (Genie)** | New AI Assistant sub-tab powered by Databricks AI/BI Genie; natural-language queries over 5 EDS Unity Catalog tables; multi-turn conversation; markdown narrative with bullet rendering; data table (20-row preview + show all) |
| **Genie automation notebook** | `notebooks/00_setup/06_create_genie_space.py` — idempotent; creates space via `POST /api/2.0/data-rooms/` with 5 EDS tables + 10 curated questions; patches `app/app.yaml` in workspace |
| **Genie Space live** | Space ID `01f13192ed5f16dfa0e16eb3e33c3a94` created and active; SP granted `CAN_RUN` via `PUT /api/2.0/permissions/genie/{id}`; `GENIE_SPACE_ID` env var hardcoded in `app.yaml` |
| **`/api/genie/query` route** | `app/server/routes/genie.py` — Conversation API with 60s polling (`/0` chunk suffix for query-result); 5-category demo fallback |
| **`eds_genie_job` DAB job** | Added to `databricks.yml`; wired as 3rd task in `eds_full_install_job` (after SP grants) |
| **18 quick-question chips** | Persistent chips (don't hide after conversation starts); 18 Alinta-specific questions |
| **Overview Genie search bar** | Search input below the header row; matches dashboard theme; arrow-up submit; navigates to Data Insights and auto-submits question |
| **Markdown narrative rendering** | `**bold**` rendered as `<strong>`; ` - item` bullet separators rendered as orange-dot bullet list |
| **Query result fix** | Appended `/0` chunk index to query-result URL — rows now populate correctly |

---

## Genie Space

| Property | Value |
|----------|-------|
| Space ID | `01f13192ed5f16dfa0e16eb3e33c3a94` |
| Display name | EDS — Executive Data Explorer |
| Warehouse | `33baaa9523773520` |
| Tables | kpi_timeseries, risk_register, financial_data, action_items, decision_register |
| SP permission | `CAN_RUN` ✅ |
| `GENIE_SPACE_ID` env var | Set in `app.yaml` ✅ |

---

## Pending / Blocked

| Item | Status | Notes |
|------|--------|-------|
| Rename catalog to `eds` | **BLOCKED** | Requires metastore/account admin — current user lacks `CREATE CATALOG` on metastore |
| Connect chat to Supervisor Agent | **Pending** | Chat calls LLM directly; Supervisor Agent registered in MLflow but not wired to `/api/chat` |
| Document count tile | **Pending** | Count tile in Overview does not update after document upload |

---

## DAB Bundle

```
Bundle:  exec-decision-studio
Target:  dev
Profile: fe-vm-ausnet-process-intel
App source (workspace): /Workspace/Users/sourabh.ghose@databricks.com/eds-app/app
```

### Deploy app update (canonical workflow)
```bash
./scripts/deploy.sh fe-vm-ausnet-process-intel
```

Which runs:
```bash
# 1. Build frontend
cd app/frontend && npm run build

# 2. Sync all source files (excludes node_modules, .venv, __pycache__, .git)
databricks sync . /Workspace/Users/sourabh.ghose@databricks.com/eds-app \
  --exclude node_modules --exclude .venv --exclude __pycache__ --exclude .git \
  --profile $PROFILE --full

# 3. Upload built frontend dist (gitignored — must be uploaded separately)
databricks workspace import-dir app/frontend/dist \
  /Workspace/Users/sourabh.ghose@databricks.com/eds-app/app/frontend/dist \
  --overwrite --profile $PROFILE

# 4. Deploy app (source-code-path must point to eds-app/app, NOT eds-app/)
databricks apps deploy exec-decision-studio \
  --source-code-path /Workspace/Users/sourabh.ghose@databricks.com/eds-app/app \
  --profile $PROFILE
```

> **IMPORTANT:** `source-code-path` must be `eds-app/app` (not `eds-app/`). The root `eds-app/` contains stale legacy files — deploying from there serves an old backend without the simulate routes.

> **NOTE:** `databricks bundle deploy` only updates jobs/notebooks — NOT the app. Always use `deploy.sh`.

### Re-run order (full rebuild)
```bash
databricks bundle deploy --profile=fe-vm-ausnet-process-intel
databricks jobs run-now 386141348959921 --profile=fe-vm-ausnet-process-intel  # setup + SP grants
databricks jobs run-now 950647315295103 --profile=fe-vm-ausnet-process-intel  # ingestion
databricks jobs run-now 110001778150925 --profile=fe-vm-ausnet-process-intel  # RAG
databricks jobs run-now 307588500376638 --profile=fe-vm-ausnet-process-intel  # agents
```
