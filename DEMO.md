# Executive Decision Studio — Demo Script
**Alinta Energy | Agentic AI Strategic Intelligence Platform**
**Audience:** Board Directors, CFO, C-Suite, ELT  
**Duration:** 15–20 minutes  
**URL:** https://exec-decision-studio-7474646159107961.aws.databricksapps.com

---

## Opening (1 min)

> "This is the Executive Decision Studio — a Databricks-native multi-agent AI platform built for Alinta Energy's Board and C-suite. It gives senior leaders real-time access to strategic intelligence drawn from 22 board documents, 12 live KPIs, risk registers, and board decisions — all powered by Claude Sonnet 4.6 on Databricks."

---

## 1. Executive Overview (2 min)

**Tab: Overview**

Point out:
- 4 stat cards across the top: Active KPIs, Open Risks, Action Items, AI Queries (7d)
- Status indicator (top right) — green/amber/red based on critical risks + overdue actions
- KPI hero cards — 6 KPIs with progress bars, trend arrows, status colour-coding
- Three charts: Risk distribution, KPI health donut, Action items horizontal bar
- Top 5 open risks with rating badges and risk scores
- Recent 4 board decisions with implementation status
- System intelligence footer: doc corpus size, avg AI latency, confidence, query volume

> "In one view, the board can see the health of the business — which KPIs are off-track, what risks are elevated, and what decisions are pending implementation."

---

## 2. Strategic Chat — Document Intelligence (4 min)

**Tab: Strategic Chat**

### Demo query 1 — Document Q&A
```
What is the current strategy for the Loy Yang B transition?
```
> Shows RAG retrieval from [DOC-002], streaming response with citations, inline chart.

### Demo query 2 — KPI Monitoring
```
How are we tracking against our retail targets and what's driving the NPS shortfall?
```
> Routes to KPI Monitor agent, shows KPI data context, anomaly flags.

### Demo query 3 — Competitive Intelligence
```
How does Alinta's market position compare to Origin and AGL?
```
> Routes to Competitive Intel agent, shows comparative bar chart of market share.

### Demo query 4 — Strategic Gap
```
What are the key gaps in our FY2026 strategy versus AEMO ISP projections?
```
> Routes to Strategic Gap Advisor, shows structured gap analysis.

**Point out during chat:**
- Agent label below each response (which specialist agent handled it)
- Confidence score and latency in the footer
- Inline Recharts visualisations embedded in responses
- Streaming token-by-token (real-time)
- Role selector — change to "Board Director / CEO" for Tier 1 access

---

## 3. KPI Dashboard (2 min)

**Tab: KPI Dashboard**

- 4 hero metric cards: Group EBITDA, Customer NPS, Plant Availability, Net Debt/EBITDA
- Trend line chart showing last 6 periods across KPIs
- Full KPI table with anomaly flags (⚠️ triangle on anomalous KPIs)
- Status badges: Green / Yellow / Red vs target

> "Every KPI has a live status vs target, and the anomaly detection runs Z-score analysis over 36 months of history. The 3 retail KPIs are all in red or yellow — that's the key strategic story right now."

---

## 4. Risk Register (2 min)

**Tab: Risk Register**

- Summary cards: Critical (2), High (5), Medium (2), Low (1)
- 5×5 heat map (likelihood × consequence) — click a cell to see risks
- Category filter: regulatory, market, operational, ESG, cyber, financial
- Click any risk to expand — shows mitigation strategy

> "The heat map immediately shows where concentration risk sits. The two critical risks — WEM capacity mechanism and Loy Yang B outage — are both in the upper-right quadrant."

---

## 5. AI Briefing (2 min)

**Tab: AI Briefing**

1. Select role: "Board Director / CEO"
2. Select briefing type: "Board Pack"
3. Check topics: Strategy, Financials, Risk
4. Click "Generate Briefing"

> "The system produces a board-ready briefing in under 30 seconds, with structured headings, executive summaries, and full document citations. Export it as a markdown file for your board pack."

---

## 6. Document Library (1 min)

**Tab: Document Library**

- 22 documents with classification badges (RESTRICTED / CONFIDENTIAL / INTERNAL)
- Tier labels showing access level required
- Filter by: classification, business unit, format, tier
- Click any document to see full metadata and summary

> "All 22 strategic documents are indexed, classified, and access-controlled. Board papers are Tier 1 RESTRICTED — only visible to Board and C-suite roles."

---

## 7. About — Architecture (1 min)

**Tab: About**

Point out the architecture diagram:
- Supervisor Agent in the centre — intent classification, routing, access control
- 5 specialist agents branching off
- Claude Sonnet 4.6 at the top powering LLM calls
- Vector Search + Unity Catalog feeding in from below
- Audit Trail recording every interaction

> "This is the Supervisor pattern — a single orchestrator that classifies intent and routes to the right specialist agent. Every interaction is logged to an immutable audit trail in Unity Catalog."

---

## Closing (1 min)

> "This is fully Databricks-native — the data lives in Unity Catalog, the LLM runs on Databricks Foundation Model API, the vector search uses Databricks Vector Search, and the app itself runs on Databricks Apps. Everything governed, audited, and traceable.
>
> For Alinta, this means the Board has real-time access to strategic intelligence — without needing to search through 22 separate documents or wait for a human analyst to pull the numbers together."

---

## Key Talking Points

| Point | Detail |
|-------|--------|
| **Not a chatbot** | It's a multi-agent orchestration system — each query goes to a specialist agent |
| **RAG, not hallucination** | Every answer is grounded in Alinta's actual board documents with citations |
| **Access control** | 4 tiers — Board sees everything; All Staff sees public content only |
| **Audit trail** | Every query, response, confidence score, and latency logged immutably |
| **Live data** | KPIs, risks, decisions, and actions are live from Unity Catalog tables |
| **Databricks-native** | Unity Catalog, Vector Search, Foundation Models, Apps — all Databricks |

---

## Common Questions

**Q: Can we connect it to real Alinta data?**  
A: Yes — swap the synthetic `eds_synthetic.*` tables with live Alinta data sources. The schema is designed to match typical enterprise data structures.

**Q: How is access controlled in production?**  
A: The app uses Databricks OAuth SP authentication. Row-level access control in the VS retriever filters documents by `access_tier_level`. Adding SSO/Entra integration is the next step.

**Q: Can we add more agents?**  
A: Yes — the Supervisor Agent pattern makes it trivial to add new specialist agents. Common additions: Financial Modelling Agent, HR/People Agent, Regulatory Affairs Agent.

**Q: What's the latency?**  
A: Claude Sonnet 4.6 typically responds in 2–4 seconds for a full streamed answer. The streaming UI makes it feel instant.

**Q: Is it production-ready?**  
A: This is a working prototype demonstrating the architecture. Production would need: real data connectors, SSO integration, Entra/AD role mapping, and a formal review of the LLM outputs.
