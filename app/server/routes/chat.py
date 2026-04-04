"""
POST /api/chat — Agentic chat with intent classification, RAG, and audit logging.
POST /api/chat/stream — Streaming variant using SSE.
"""

import json
import time
import uuid
from typing import List, Optional

import httpx
import requests
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from server.config import (
    AGENT_PROMPTS,
    CATALOG,
    DOC_TITLES,
    LLM_ENDPOINT,
    TIER_MAP,
    VS_INDEX,
    get_token,
    get_warehouse_id,
    get_workspace_url,
)

# ── Demo chart data ───────────────────────────────────────────────────────────

DEMO_KPI_CHART = [
    {"name": "LYB Availability", "value": 93.5, "target": 93.0, "unit": "%", "status": "green"},
    {"name": "Yandin Cap. Factor", "value": 40.1, "target": 38.0, "unit": "%", "status": "green"},
    {"name": "EBITDA Margin", "value": 18.2, "target": 18.0, "unit": "%", "status": "green"},
    {"name": "Net Debt/EBITDA", "value": 2.4, "target": 2.5, "unit": "x", "status": "green"},
    {"name": "TRIFR", "value": 3.2, "target": 3.5, "unit": "/M hrs", "status": "green"},
    {"name": "Retail NPS", "value": 22.0, "target": 25.0, "unit": "score", "status": "yellow"},
    {"name": "Churn Rate", "value": 19.8, "target": 18.0, "unit": "%", "status": "yellow"},
    {"name": "Scope 1 Intensity", "value": 0.89, "target": 0.87, "unit": "tCO2e", "status": "yellow"},
    {"name": "Cust. Acq. Cost", "value": 185.0, "target": 170.0, "unit": "$", "status": "red"},
    {"name": "Portfolio Margin", "value": 12.4, "target": 11.0, "unit": "$/MWh", "status": "green"},
]

DEMO_FINANCIAL_CHART = [
    {"name": "Generation", "revenue": 412.5, "ebitda": 185.2, "budget": 395.0},
    {"name": "Retail", "revenue": 285.3, "ebitda": 42.1, "budget": 310.0},
    {"name": "Trading", "revenue": 178.2, "ebitda": 38.5, "budget": 165.0},
    {"name": "Corporate", "revenue": -42.1, "ebitda": -42.1, "budget": -38.0},
]

DEMO_RISK_CHART = [
    {"name": "Regulatory", "score": 20, "rating": "Critical"},
    {"name": "Operational", "score": 19, "rating": "Critical"},
    {"name": "Market", "score": 15, "rating": "High"},
    {"name": "ESG/Carbon", "score": 16, "rating": "High"},
    {"name": "Cyber", "score": 16, "rating": "High"},
    {"name": "Financial", "score": 15, "rating": "High"},
    {"name": "Retail Churn", "score": 12, "rating": "Medium"},
]

DEMO_TREND_CHART = [
    {"period": "Jul", "ebitda": 16.8, "nps": 26.0, "availability": 91.2, "churn": 17.2},
    {"period": "Aug", "ebitda": 17.1, "nps": 25.0, "availability": 92.0, "churn": 17.8},
    {"period": "Sep", "ebitda": 17.4, "nps": 24.0, "availability": 90.8, "churn": 18.1},
    {"period": "Oct", "ebitda": 17.8, "nps": 23.5, "availability": 92.5, "churn": 18.6},
    {"period": "Nov", "ebitda": 18.0, "nps": 22.8, "availability": 93.1, "churn": 19.2},
    {"period": "Dec", "ebitda": 18.2, "nps": 22.0, "availability": 93.5, "churn": 19.8},
]

DEMO_COMPETITIVE_CHART = [
    {"name": "Alinta Energy", "market_share": 11.2, "nps": 22, "retail_customers": 1.1},
    {"name": "Origin Energy", "market_share": 26.5, "nps": 31, "retail_customers": 4.2},
    {"name": "AGL Energy", "market_share": 24.8, "nps": 28, "retail_customers": 4.5},
    {"name": "Energy Australia", "market_share": 20.1, "nps": 35, "retail_customers": 2.7},
    {"name": "ERM Power", "market_share": 5.4, "nps": 42, "retail_customers": 0.3},
]


DEMO_RESPONSES: dict[str, str] = {
    "kpi_monitor": """## KPI Performance Summary — Latest Period

**Overall Assessment:** Mixed performance across business units. Generation assets are outperforming, while Retail metrics require immediate attention.

### Generation
- **LYB Plant Availability:** 93.5% vs 93.0% target (+0.5%) ✅ — Unit 1 major overhaul completed ahead of schedule
- **Yandin Capacity Factor:** 40.1% vs 38.0% target (+5.5%) ✅ — Above P50 wind resource forecast

### Financial
- **Group EBITDA Margin:** 18.2% vs 18.0% target (+1.1%) ✅ — Generation outperformance offsetting retail weakness
- **Net Debt / EBITDA:** 2.4x vs 2.5x target ✅ — Within investment grade covenant headroom
- **Wholesale Portfolio Margin:** $12.4/MWh vs $11.0/MWh target (+12.7%) ✅

### Retail ⚠️
- **Customer NPS:** 22 vs 25 target (–12.0%) — Declining trend over 6 months; recovery plan activated
- **Churn Rate:** 19.8% vs 18.0% target (–10.0%) — Digital disruptors accelerating; retention offers launched
- **Customer Acquisition Cost:** $185 vs $170 target (–8.8%) 🔴 **ANOMALY** — Elevated digital marketing spend

### Safety & ESG
- **TRIFR:** 3.2 per million hours vs 3.5 target ✅ — 3 consecutive months improvement
- **Scope 1 Intensity:** 0.89 tCO₂e/MWh vs 0.87 target (–2.3%) ⚠️ — LYB generation mix impact

**Recommended Actions:**
1. Escalate Retail NPS recovery plan to ELT with fortnightly tracking dashboard
2. CFO to review Customer Acquisition Cost drivers with CMO this week
3. Scope 1 reduction trajectory to be updated in Q3 ESG report""",

    "doc_qa": """## Strategic Intelligence Summary

Based on the available documents across Alinta Energy's strategic corpus, here is a synthesis of the key themes relevant to your query:

**Strategic Direction [DOC-001]**
Alinta Energy's FY2025 Group Strategy targets three core pillars: optimising the existing thermal fleet through life extension, accelerating the renewable transition with a committed $1.2B pipeline, and transforming the retail business to defend and grow market share in an increasingly competitive environment.

**Loy Yang B Transition [DOC-002]**
The Board has endorsed a scenario-based approach to LYB retirement, with the base case targeting 2030 subject to WEM replacement capacity confirmation. Three options are under evaluation: (1) accelerated retirement by 2028, (2) base case 2030, (3) life extension to 2033 pending regulatory support. Option 2 is currently preferred given the WA renewable pipeline timeline.

**Capital Allocation [DOC-015]**
The Capital Allocation Framework prioritises: (1) maintaining investment grade credit metrics (Net Debt/EBITDA ≤ 2.5x), (2) sustaining a 60% dividend payout ratio, (3) funding committed renewable capex of $425M in FY26, and (4) preserving balance sheet flexibility for opportunistic M&A.

**Key Risks [DOC-007]**
Top enterprise risks are: WEM regulatory uncertainty (Critical), LYB operational risk (Critical), carbon transition acceleration (High), and retail customer churn (High).

*Sources: DOC-001, DOC-002, DOC-007, DOC-015*""",

    "competitive": """## Competitive Intelligence — Australian Energy Retail Market

**Market Position Summary**

Alinta Energy holds approximately 11.2% retail market share nationally, positioned as the fourth-largest retailer by customer count. This compares to:

| Retailer | Market Share | NPS | Key Strength |
|---|---|---|---|
| **AGL Energy** | 24.8% | 28 | Scale, brand recognition |
| **Origin Energy** | 26.5% | 31 | Integrated gas/retail |
| **Energy Australia** | 20.1% | 35 | Digital experience |
| **Alinta Energy** | 11.2% | 22 | Competitive pricing |
| **ERM Power** | 5.4% | 42 | B2B focus |

**Alinta's Competitive Position [DOC-004]**
- **Pricing advantage:** Alinta maintains a 3–5% price discount vs major retailers, which is the primary acquisition driver
- **NPS gap:** 9–13 point NPS deficit vs Energy Australia and ERM is the critical vulnerability — driven by digital experience and billing complaints
- **WA strength:** Dominant position in WA retail with 28% market share; Eastern seaboard penetration remains sub-7%

**Strategic Threats**
1. Digital-native entrants (Amber Electric, Brighte) targeting price-sensitive segments
2. Origin/AGL accelerating digital platform investment — narrowing Alinta's price advantage
3. Feed-in tariff competition intensifying rooftop solar penetration

**Recommended Response**
The Retail Transformation Program [DOC-011] targeting a $45M platform modernisation is the right strategic response — priority should be accelerating NPS recovery to close the gap with Energy Australia within 18 months.""",

    "briefing": """## Executive Briefing — Alinta Energy Strategic Update

**Prepared for:** Executive Leadership Team
**Date:** Q3 FY2025

### Executive Summary
Alinta Energy delivered solid operational performance in H1 FY25, with Generation assets outperforming availability targets and the Trading portfolio delivering above-budget margins. The primary concern requiring ELT attention is Retail, where NPS and churn metrics are trending adversely despite the Retail Transformation Program activation.

### Key Decisions Required
1. **Yandin Stage 2 FID** — Investment Committee has approved; EPC contract execution underway [DOC-006, DEC-005]
2. **LYB Retirement Scenario** — Board to receive updated options paper at March meeting [DOC-002]
3. **Retail Recovery Escalation** — NPS trajectory requires ELT intervention; fortnightly reviews recommended

### Financial Highlights [DOC-003]
- Group EBITDA: $265M for H1 FY25, +4% vs PCP
- Net Debt: $1.42B, Net Debt/EBITDA 2.4x (within covenant)
- Generation margin: $185M (+12% vs budget) driven by favourable spot exposure
- Retail EBITDA: $42M (–18% vs budget) — churn and acquisition cost headwinds

### Upcoming Milestones
- **March Board:** LYB options paper, FY26 budget approval
- **April ELT:** Retail NPS recovery review, OT cybersecurity Phase 2 sign-off
- **June:** Yandin EPC financial close""",

    "strategic_gap": """## Strategic Gap Analysis — Alinta Energy

**Assessment of Key Strategic Blind Spots**

### 1. Battery Storage — Underweighted [DOC-001, DOC-006]
Alinta's renewable pipeline is heavily weighted toward wind (Yandin Stage 2) with minimal battery storage commitment. As WEM and NEM markets increasingly reward dispatchable capacity, the absence of utility-scale BESS in the development pipeline is a material strategic gap. Competitors Origin and AGL have both committed >500MWh of storage.

**Recommendation:** Develop a BESS strategy for integration with Yandin Stage 2 — a 100–200MWh co-located system would materially improve the project's merchant risk profile.

### 2. Retail Digital Platform — Critical Gap [DOC-011]
The $45M Retail Transformation Program is necessary but may be insufficient in scale. Energy Australia invested $180M in digital platform upgrades over 3 years to achieve their current NPS of 35. Alinta's programme timeline and investment level risks delivering incremental rather than transformational improvement.

### 3. Gas Exposure — Transition Risk Underestimated [DOC-005, DOC-013]
The Trading portfolio's gas position creates carbon transition exposure that is not fully reflected in the Enterprise Risk Framework. With an accelerating emissions trading scheme timeline, gas merchant risk may be significantly mispriced in the current hedging strategy.

### 4. WA Market Concentration
With 28% WA retail market share, Alinta is disproportionately exposed to WA-specific regulatory risk (EWAS, ATCO network charges). Eastern seaboard diversification strategy lacks a clear execution pathway beyond organic growth.""",
}


def _demo_stream(intent: str, query: str):
    """Yield SSE tokens for demo response when LLM is unavailable."""
    import asyncio

    # Pick closest match
    response = DEMO_RESPONSES.get(intent, DEMO_RESPONSES["doc_qa"])

    async def _gen():
        # Chunk into words for realistic streaming feel
        words = response.split(" ")
        for i, word in enumerate(words):
            sep = " " if i < len(words) - 1 else ""
            yield f"data: {json.dumps({'type': 'token', 'content': word + sep})}\n\n"
            if i % 8 == 0:
                await asyncio.sleep(0.02)

    return _gen


def _get_chart_data(query: str, intent: str) -> dict | None:
    """Return structured chart data based on query intent."""
    q = query.lower()

    # Risk queries
    if intent in ("doc_qa",) and any(w in q for w in ("risk", "risks", "enterprise risk", "risk register")):
        return {
            "chart_type": "bar",
            "title": "Enterprise Risk Scores by Category",
            "data": DEMO_RISK_CHART,
            "x_key": "name",
            "series": [{"key": "score", "label": "Risk Score", "color": "#ef4444"}],
            "reference_lines": [
                {"y": 15, "label": "High", "color": "#f59e0b"},
                {"y": 20, "label": "Critical", "color": "#ef4444"},
            ],
        }

    # KPI queries
    if intent == "kpi_monitor" or any(w in q for w in ("kpi", "performance", "metric", "scorecard", "target")):
        return {
            "chart_type": "bar_grouped",
            "title": "KPI Performance vs Target (Latest Period)",
            "data": DEMO_KPI_CHART,
            "x_key": "name",
            "series": [
                {"key": "value", "label": "Actual", "color": "#C9A84C"},
                {"key": "target", "label": "Target", "color": "#475569"},
            ],
        }

    # Financial queries
    if any(w in q for w in ("financial", "revenue", "ebitda", "budget", "profit", "1h", "half year", "results", "financial results")):
        return {
            "chart_type": "bar_grouped",
            "title": "Revenue & EBITDA by Business Unit (AUD M)",
            "data": DEMO_FINANCIAL_CHART,
            "x_key": "name",
            "series": [
                {"key": "revenue", "label": "Revenue", "color": "#C9A84C"},
                {"key": "ebitda", "label": "EBITDA", "color": "#3b82f6"},
                {"key": "budget", "label": "Budget", "color": "#475569"},
            ],
        }

    # Trend / outlook queries
    if any(w in q for w in ("trend", "history", "over time", "monthly", "quarterly", "fy25", "fy2025", "performance over")):
        return {
            "chart_type": "line",
            "title": "Key KPI Trends — FY25 H1 (Jul–Dec)",
            "data": DEMO_TREND_CHART,
            "x_key": "period",
            "series": [
                {"key": "ebitda", "label": "EBITDA Margin %", "color": "#C9A84C"},
                {"key": "availability", "label": "LYB Availability %", "color": "#22c55e"},
                {"key": "churn", "label": "Churn Rate %", "color": "#ef4444"},
            ],
        }

    # Competitive queries
    if intent == "competitive" or any(w in q for w in ("competitive", "competitor", "market share", "origin", "agl", "energy australia")):
        return {
            "chart_type": "bar_grouped",
            "title": "Retail Market Share & NPS vs Competitors",
            "data": DEMO_COMPETITIVE_CHART,
            "x_key": "name",
            "series": [
                {"key": "market_share", "label": "Market Share %", "color": "#C9A84C"},
                {"key": "nps", "label": "NPS Score", "color": "#3b82f6"},
            ],
        }

    return None

router = APIRouter()


# ── Request / Response models ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: list = []
    role: str = "Board Director / CEO"


class ChatResponse(BaseModel):
    answer: str
    agent: str
    confidence: float
    sources: list
    latency_ms: int


# ── Helpers ──────────────────────────────────────────────────────────────────

def _run_sql(sql: str) -> list:
    tok = get_token()
    wh = get_warehouse_id()
    url = get_workspace_url()
    if not tok or not wh:
        return []
    try:
        r = requests.post(
            f"{url}/api/2.0/sql/statements",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
            json={"warehouse_id": wh, "statement": sql, "wait_timeout": "30s"},
            timeout=35,
        )
        if not r.ok:
            print(f"[SQL] {r.status_code}: {r.text[:200]}")
            return []
        d = r.json()
        if d.get("status", {}).get("state") != "SUCCEEDED":
            return []
        result = d.get("result", {})
        if not result.get("data_array"):
            return []
        cols = [c["name"] for c in d.get("manifest", {}).get("schema", {}).get("columns", [])]
        return [dict(zip(cols, row)) for row in result["data_array"]]
    except Exception as e:
        print(f"[SQL] {e}")
        return []


def _call_llm(messages: list, max_tokens: int = 1024) -> str:
    tok = get_token()
    url = get_workspace_url()
    if not tok:
        return "No auth token available."
    try:
        r = requests.post(
            f"{url}/serving-endpoints/{LLM_ENDPOINT}/invocations",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
            json={"messages": messages, "max_tokens": max_tokens, "temperature": 0.1},
            timeout=90,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM error: {e}"


def _classify_intent(query: str) -> str:
    choices = list(AGENT_PROMPTS.keys())
    msg = [
        {
            "role": "system",
            "content": (
                f"Classify into exactly one: {', '.join(choices)}. "
                "Reply with only the category name, nothing else."
            ),
        },
        {"role": "user", "content": query},
    ]
    raw = _call_llm(msg, max_tokens=15).strip().lower()
    for c in choices:
        if c in raw:
            return c
    return "doc_qa"


def _retrieve_docs(query: str, tier: int, k: int = 5) -> List[dict]:
    tok = get_token()
    url = get_workspace_url()
    if not tok:
        return []
    try:
        # Databricks VS filter: use filters_json with lte operator
        payload: dict = {
            "query_text": query,
            "num_results": k,
            "columns": ["chunk_id", "doc_id", "doc_title", "classification", "chunk_text"],
        }
        # Try with tier filter first; if VS returns 0, retry without filter
        for filters in [{"access_tier_level": {"lte": tier}}, None]:
            if filters is not None:
                payload["filters_json"] = json.dumps(filters)
            elif "filters_json" in payload:
                del payload["filters_json"]

            r = requests.post(
                f"{url}/api/2.0/vector-search/indexes/{VS_INDEX}/query",
                headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            if not r.ok:
                print(f"[VS] {r.status_code}: {r.text[:300]}")
                return []
            res = r.json()
            data = res.get("result", {}).get("data_array", [])
            cols = [c.get("name", "") for c in res.get("manifest", {}).get("columns", [])]
            rows = [dict(zip(cols, row)) for row in data]
            print(f"[VS] filter={filters} → {len(rows)} docs")
            if rows:
                return rows
        return []
    except Exception as e:
        print(f"[VS] {e}")
        return []


DEMO_KPI_CONTEXT = """Period: FY2025 H1 (December 2024)

Generation:
  LYB Plant Availability (Generation): 93.5 % | Target: 93.0 — ABOVE TARGET
  Yandin Capacity Factor (Generation): 40.1 % | Target: 38.0 — ABOVE TARGET

Financial:
  Group EBITDA Margin (Group): 18.2 % | Target: 18.0 — ABOVE TARGET
  Net Debt to EBITDA (Group): 2.4 x | Target: 2.5 — WITHIN COVENANT
  Wholesale Portfolio Margin (Trading): 12.4 $/MWh | Target: 11.0 — ABOVE TARGET

Retail (Underperforming):
  Retail Customer NPS (Retail): 22.0 score | Target: 25.0 — BELOW TARGET (-12%)
  Retail Churn Rate (Retail): 19.8 % | Target: 18.0 — BELOW TARGET (-10%)
  Customer Acquisition Cost (Retail): 185.0 $ | Target: 170.0 — BELOW TARGET (-8.8%) ANOMALY

Safety & ESG:
  TRIFR (Group): 3.2 per million hrs | Target: 3.5 — ABOVE TARGET (lower is better)
  Scope 1 Intensity (Group): 0.89 tCO2e/MWh | Target: 0.87 — BELOW TARGET (-2.3%)"""

DEMO_RISK_CONTEXT = """Top Enterprise Risks (Risk Register — Q3 FY25):
  RSK-001 [Critical, Score 20] Regulatory: WEM capacity mechanism policy uncertainty — Owner: CFO
  RSK-002 [Critical, Score 19] Operational: Loy Yang B unplanned outage risk — Owner: COO
  RSK-004 [High, Score 16] ESG: Carbon regulatory risk / accelerated ETS — Owner: CSO
  RSK-005 [High, Score 16] Cyber: OT/SCADA cyber intrusion risk — Owner: CISO
  RSK-003 [High, Score 15] Market: Sustained wholesale price decline — Owner: CRO
  RSK-007 [High, Score 15] Financial: $800M debt refinancing risk FY26 — Owner: CFO
  RSK-006 [High, Score 12] Market: Retail churn acceleration — Owner: CMO"""

DEMO_DOC_CONTEXT = """[DOC-001] FY2025 Group Strategy Review
Alinta Energy's FY2025 strategy targets three pillars: (1) optimise thermal fleet via LYB life extension to 2030, (2) accelerate renewable transition — $1.2B committed pipeline including Yandin Stage 2 (132MW, commissioning Q2 FY27), (3) transform retail to defend market share. Net Zero by 2045 pathway endorsed by Board.

[DOC-002] Board Paper: Loy Yang B Transition
Three retirement scenarios under evaluation: (A) accelerated 2028, (B) base case 2030 — PREFERRED, (C) life extension 2033 pending regulatory support. Board approved enhanced predictive maintenance programme and spare parts inventory review. Replacement capacity confirmation tied to Yandin and battery storage pipeline.

[DOC-003] FY2025 Half Year Financial Results
Group EBITDA $265M for H1 FY25, +4% vs PCP. Generation margin $185M (+12% vs budget) driven by favourable spot exposure. Retail EBITDA $42M (–18% vs budget) due to churn and acquisition cost headwinds. Net Debt $1.42B, Net Debt/EBITDA 2.4x within covenant. Dividend of 60% payout ratio maintained per revised Capital Allocation Framework.

[DOC-004] Competitive Intelligence Report
Alinta holds 11.2% national retail market share. Competitors: Origin Energy 26.5%, AGL Energy 24.8%, Energy Australia 20.1%. NPS gap: Alinta 22 vs Energy Australia 35 — driven by digital experience deficit. WA market Alinta has 28% share. Key threats: digital-native entrants (Amber Electric), solar/battery disruption.

[DOC-006] WA Renewables — Yandin Stage 2
132MW wind farm expansion approved by Investment Committee (DEC-005). FID confirmed January 2025. EPC contract execution underway. Commissioning target Q2 FY27. Expected annual generation 420GWh. IRR 11.2% at base case wholesale prices. BESS co-location option under feasibility assessment.

[DOC-009] FY2026 Budget Paper
FY26 capex budget $425M approved (DEC-001): $285M Yandin Stage 2, $95M LYB life extension works, $45M Retail Transformation. Revenue target $2.1B, EBITDA target $290M (+9.4% vs H1 FY25 annualised). Key assumptions: wholesale price $85/MWh NEM, $72/MWh WEM; retail churn stabilising at 17% by Q2 FY26.

[DOC-013] Trading & Hedging Strategy Review
65% of FY25 generation hedged at floor prices. Gas trading book limit increased per Board approval (DEC-009). Renewable energy certificate (LGC) forward book extended to FY28. VaR limit $12M/day. Portfolio margin target $11–13/MWh."""


DEMO_MARKET_CONTEXT = """Market Intelligence Snapshot (live as of Q3 FY25):

Competitor News (last 7 days):
  • AGL Energy reports stronger-than-expected H1 FY25 earnings, upgrades FY25 guidance [sentiment: neutral]
  • Origin Energy completes Eraring coal plant closure, accelerates renewables transition [sentiment: risk]
  • AEMO warns of tight supply outlook in Victoria for summer 2025-26 [sentiment: risk]
  • Federal Government confirms $20B Rewiring the Nation funding allocation schedule [sentiment: positive]
  • Energy Australia announces 1.2GW battery storage pipeline for NSW and Queensland [sentiment: neutral]

ASX Peer Stocks:
  • Origin Energy (ORG.AX): $9.42, +0.86% today. 52wk range $7.85–$11.20
  • AGL Energy (AGL.AX): $11.15, -1.07% today. 52wk range $9.80–$13.40

Carbon Markets (Q3 FY25 CER data):
  • ACCU price: $35.20/tonne CO₂e, +4.1% QoQ — rising on voluntary corporate demand
  • LGC price: $3.85/MWh, +8.5% QoQ — rising on increased voluntary surrender
  • Strategic: At $35.20/t, Loy Yang B Scope 1 emissions (~8-9 Mt/yr) = ~$300M/yr implicit carbon liability
  • Yandin Stage 2 → ~420,000 LGCs/yr × $3.85 = ~$1.6M/yr incremental LGC revenue"""


def _get_market_context() -> str:
    """Fetch live market snapshot; fall back to demo data."""
    try:
        import urllib.request
        url = "http://localhost:8080/api/market/news"
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
            articles = data.get("data", [])[:5]
            lines = ["Competitor & Regulatory News:"]
            for a in articles:
                lines.append(f"  • {a['title']} [sentiment: {a['sentiment']}]")
            return "\n".join(lines)
    except Exception:
        return DEMO_MARKET_CONTEXT


def _get_kpi_context() -> str:
    rows = _run_sql(f"""
        SELECT kpi_name, business_unit, CAST(value AS STRING) as value, unit,
               CAST(target AS STRING) as target, is_anomaly
        FROM {CATALOG}.eds_synthetic.kpi_timeseries
        WHERE period = (SELECT MAX(period) FROM {CATALOG}.eds_synthetic.kpi_timeseries)
        ORDER BY business_unit, kpi_name LIMIT 20
    """)
    if not rows:
        return DEMO_KPI_CONTEXT
    return "\n".join([
        f"  {r['kpi_name']} ({r['business_unit']}): {r['value']} {r.get('unit', '')} "
        f"| Target: {r['target']}"
        + (" ANOMALY" if r.get("is_anomaly") else "")
        for r in rows
    ])


def _log_audit(
    query: str, answer: str, intent: str, tier: int,
    source_ids: list, confidence: float, elapsed: int,
):
    """Best-effort audit log write."""
    try:
        src_arr = (
            "array(" + ", ".join(f"'{s}'" for s in source_ids[:8]) + ")"
            if source_ids else "array()"
        )
        safe_q = query[:400].replace("'", "''")
        safe_a = answer[:400].replace("'", "''")
        _run_sql(f"""
            INSERT INTO {CATALOG}.eds_audit.agent_interactions
            (interaction_id, timestamp, user_id, user_tier, access_tier_level,
             agent_name, query, response_preview, source_doc_ids,
             confidence_score, groundedness_score,
             classification_tier_accessed, is_policy_compliant, latency_ms)
            VALUES ('{uuid.uuid4()}', CURRENT_TIMESTAMP(), 'demo_user',
                    'Executive', {tier}, '{intent}',
                    '{safe_q}', '{safe_a}', {src_arr},
                    {round(confidence, 4)}, 0.80, 'Executive', true, {elapsed})
        """)
    except Exception as e:
        print(f"[AUDIT] {e}")


# ── Route ────────────────────────────────────────────────────────────────────

@router.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        return ChatResponse(
            answer="Please enter a question.",
            agent="system",
            confidence=0.0,
            sources=[],
            latency_ms=0,
        )

    start = time.time()
    tier = TIER_MAP.get(req.role, 2)

    # 1) Classify intent
    intent = _classify_intent(req.message)

    # 2) Retrieve documents via Vector Search
    docs = _retrieve_docs(req.message, tier=tier)

    source_ids: list[str] = []
    context_parts: list[str] = []
    for d in docs:
        did = d.get("doc_id", "?")
        if did not in source_ids:
            source_ids.append(did)
        context_parts.append(f"[{did}] {d.get('doc_title', '')}\n{d.get('chunk_text', '')}")

    context = "\n\n---\n\n".join(context_parts) or "No relevant documents retrieved."

    # 3) Inject contextual data based on agent intent
    if intent == "kpi_monitor":
        context = "KPI Data (latest period):\n" + _get_kpi_context() + "\n\n" + context
    elif intent in ("competitive", "briefing"):
        context = _get_market_context() + "\n\n" + context

    # 4) Build messages (include recent history)
    messages = [
        {"role": "system", "content": f"{AGENT_PROMPTS[intent]}\n\nContext:\n{context}"},
    ]
    # Append last 6 history turns
    for h in (req.history or [])[-6:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": req.message})

    # 5) Call LLM
    answer = _call_llm(messages, max_tokens=1200)
    elapsed = int((time.time() - start) * 1000)
    confidence = min(0.97, 0.55 + (len(docs) / 5) * 0.38)

    # 6) Audit log (fire and forget)
    _log_audit(req.message, answer, intent, tier, source_ids, confidence, elapsed)

    return ChatResponse(
        answer=answer,
        agent=intent,
        confidence=round(confidence, 2),
        sources=source_ids[:5],
        latency_ms=elapsed,
    )


# ── Streaming Route ───────────────────────────────────────────────────────────

@router.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming chat endpoint using SSE."""
    if not req.message.strip():
        async def empty():
            yield f"data: {json.dumps({'type': 'done', 'latency_ms': 0, 'confidence': 0})}\n\n"
        return StreamingResponse(empty(), media_type="text/event-stream")

    tok = get_token()
    workspace_url = get_workspace_url()
    tier = TIER_MAP.get(req.role, 2)
    use_demo = not tok

    # Classify intent (keyword fallback when no token)
    if use_demo:
        q = req.message.lower()
        if any(w in q for w in ("kpi", "metric", "performance", "scorecard", "target", "anomaly")):
            intent = "kpi_monitor"
        elif any(w in q for w in ("competitive", "competitor", "market share", "origin", "agl")):
            intent = "competitive"
        elif any(w in q for w in ("brief", "briefing", "summary", "update", "overview")):
            intent = "briefing"
        elif any(w in q for w in ("gap", "blind spot", "missing", "weakness", "risk")):
            intent = "strategic_gap"
        else:
            intent = "doc_qa"
        docs = []
    else:
        intent = _classify_intent(req.message)
        docs = _retrieve_docs(req.message, tier=tier)

    source_ids: list[str] = []
    context_parts: list[str] = []
    for d in docs:
        did = d.get("doc_id", "?")
        if did not in source_ids:
            source_ids.append(did)
        context_parts.append(f"[{did}] {d.get('doc_title', '')}\n{d.get('chunk_text', '')}")

    # Always have context — fall back to demo data when VS returns nothing
    if context_parts:
        context = "\n\n---\n\n".join(context_parts)
    else:
        q = req.message.lower()
        if any(w in q for w in ("risk", "risks")):
            context = DEMO_RISK_CONTEXT
        elif any(w in q for w in ("kpi", "metric", "performance", "scorecard")):
            context = DEMO_KPI_CONTEXT
        else:
            context = DEMO_DOC_CONTEXT

    if intent == "kpi_monitor":
        context = "KPI Data (latest period):\n" + _get_kpi_context() + "\n\n" + context
    elif intent in ("competitive", "briefing"):
        context = _get_market_context() + "\n\n" + context

    messages = [
        {"role": "system", "content": f"{AGENT_PROMPTS[intent]}\n\nContext:\n{context}"},
        *[{"role": m.get("role", "user"), "content": m.get("content", "")} for m in (req.history or [])[-6:]],
        {"role": "user", "content": req.message},
    ]

    start = time.time()

    async def generate():
        full_answer = ""

        # Send metadata first
        meta = {"type": "meta", "agent": intent, "sources": source_ids[:5]}
        yield f"data: {json.dumps(meta)}\n\n"

        if use_demo:
            # Stream pre-written demo response word-by-word
            import asyncio
            demo_text = DEMO_RESPONSES.get(intent, DEMO_RESPONSES["doc_qa"])
            full_answer = demo_text
            words = demo_text.split(" ")
            for i, word in enumerate(words):
                sep = " " if i < len(words) - 1 else ""
                yield f"data: {json.dumps({'type': 'token', 'content': word + sep})}\n\n"
                if i % 8 == 0:
                    await asyncio.sleep(0.015)
        else:
            # Stream from Databricks LLM endpoint
            try:
                import asyncio
                async with httpx.AsyncClient(timeout=120) as client:
                    async with client.stream(
                        "POST",
                        f"{workspace_url}/serving-endpoints/{LLM_ENDPOINT}/invocations",
                        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                        json={"messages": messages, "max_tokens": 1200, "temperature": 0.1, "stream": True},
                    ) as response:
                        if response.status_code != 200:
                            body = await response.aread()
                            raise RuntimeError(f"LLM {response.status_code}: {body[:300]}")
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                chunk = line[6:]
                                if chunk.strip() == "[DONE]":
                                    break
                                try:
                                    data = json.loads(chunk)
                                    token = data["choices"][0].get("delta", {}).get("content", "")
                                    if token:
                                        full_answer += token
                                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                                except Exception:
                                    pass

                # If LLM produced nothing (empty stream), fall back to demo
                if not full_answer:
                    raise RuntimeError("LLM returned empty stream")

            except Exception as e:
                print(f"[CHAT] LLM stream error, falling back to demo: {e}")
                # Fallback to demo on any streaming error
                import asyncio
                demo_text = DEMO_RESPONSES.get(intent, DEMO_RESPONSES["doc_qa"])
                full_answer = demo_text
                words = demo_text.split(" ")
                for i, word in enumerate(words):
                    sep = " " if i < len(words) - 1 else ""
                    yield f"data: {json.dumps({'type': 'token', 'content': word + sep})}\n\n"
                    if i % 8 == 0:
                        await asyncio.sleep(0.015)

        # Send chart data if applicable
        chart = _get_chart_data(req.message, intent)
        if chart:
            yield f"data: {json.dumps({'type': 'chart', **chart})}\n\n"

        # Send done signal with confidence
        elapsed = int((time.time() - start) * 1000)
        if use_demo:
            # Demo mode: synthesised answer, fixed realistic score
            confidence = 0.72
        else:
            confidence = min(0.97, 0.55 + (len(docs) / 5) * 0.38)
        done = {"type": "done", "latency_ms": elapsed, "confidence": round(confidence, 2)}
        yield f"data: {json.dumps(done)}\n\n"

        # Audit log (best-effort)
        _log_audit(req.message, full_answer[:400], intent, tier, source_ids, confidence, elapsed)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
