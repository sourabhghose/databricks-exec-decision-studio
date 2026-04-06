"""POST /api/simulate/stream — AI-driven Bear/Base/Bull scenario simulation."""

import json
import time
import requests
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from server.config import (
    CATALOG,
    LLM_ENDPOINT,
    AGENT_PROMPTS,
    TIER_MAP,
    get_token,
    get_warehouse_id,
    get_workspace_url,
)

router = APIRouter()

# ── Pre-built Alinta-specific decision templates ──────────────────────────────

DECISION_TEMPLATES = [
    {
        "label": "Loy Yang B Retirement",
        "text": (
            "Should Alinta Energy retire Loy Yang B in 2028 (accelerated), "
            "maintain the 2030 base-case timeline, or pursue life extension to 2033 "
            "pending regulatory support? Assess financial, operational, and ESG implications."
        ),
    },
    {
        "label": "Yandin Stage 2",
        "text": (
            "Should Alinta proceed with Yandin Wind Farm Stage 2 FID now (132MW, $285M), "
            "defer 12 months pending WEM capacity mechanism clarity, "
            "or divest the development rights? Consider energy market conditions and capital position."
        ),
    },
    {
        "label": "Retail Transformation",
        "text": (
            "Should Alinta accelerate the Retail Transformation Program ($45M, 18 months), "
            "maintain the current steady-state delivery plan, "
            "or pause and redirect capital to generation assets? "
            "Consider NPS trends, customer churn, and competitive pressure from Origin and AGL."
        ),
    },
    {
        "label": "Capital Structure",
        "text": (
            "Should Alinta increase leverage to fund renewable investment (target gearing 45%), "
            "issue equity to maintain balance sheet headroom, "
            "or adopt a hybrid approach with asset recycling? "
            "Consider interest rate environment, credit rating, and dividend policy commitments."
        ),
    },
    {
        "label": "WEM Capacity Mechanism",
        "text": (
            "How should Alinta respond to the WEM Capacity Mechanism outcome? "
            "Options: bid aggressively with all dispatchable capacity, "
            "hold current portfolio and hedge via contracts, "
            "or exit the WEM market and focus on SWIS bilateral contracts. "
            "Assess revenue certainty, policy risk, and competitive dynamics."
        ),
    },
]


# ── SQL helper (shared pattern with briefing.py) ──────────────────────────────

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
            json={"warehouse_id": wh, "statement": sql, "wait_timeout": "50s"},
            timeout=60,
        )
        if not r.ok:
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
        print(f"[SQL/simulate] {e}")
        return []


# ── Live data context builders ────────────────────────────────────────────────

def _fetch_kpi_context() -> str:
    rows = _run_sql(f"""
        SELECT kpi_name, business_unit,
               ROUND(CAST(value AS DOUBLE), 2)  AS value,
               ROUND(CAST(target AS DOUBLE), 2) AS target,
               unit
        FROM {CATALOG}.eds_synthetic.kpi_timeseries
        WHERE period = (SELECT MAX(period) FROM {CATALOG}.eds_synthetic.kpi_timeseries)
        ORDER BY business_unit, kpi_name
        LIMIT 10
    """)
    if not rows:
        return (
            "Revenue: $842M (target $850M), EBITDA Margin: 18.2% (target 18.0%), "
            "LYB Availability: 93.5% (target 93.0%), Customer NPS: 22 (target 25), "
            "Retail Churn: 14.2% (target 12.0%), Capex: $285M (budget $290M)"
        )
    lines = [
        f"{r['kpi_name']} ({r.get('business_unit','')}):"
        f" {r['value']} {r.get('unit','')} vs target {r['target']} {r.get('unit','')}"
        for r in rows
    ]
    return "; ".join(lines)


def _fetch_financial_context() -> str:
    rows = _run_sql(f"""
        SELECT business_unit,
               ROUND(SUM(CAST(revenue AS DOUBLE)) / 1e6, 1)  AS revenue_m,
               ROUND(SUM(CAST(ebitda AS DOUBLE))  / 1e6, 1)  AS ebitda_m,
               ROUND(SUM(CAST(capex AS DOUBLE))   / 1e6, 1)  AS capex_m
        FROM {CATALOG}.eds_synthetic.financial_data
        WHERE fiscal_year = (SELECT MAX(fiscal_year) FROM {CATALOG}.eds_synthetic.financial_data)
        GROUP BY business_unit
        ORDER BY revenue_m DESC
        LIMIT 6
    """)
    if not rows:
        return (
            "Generation: Revenue $520M, EBITDA $105M, Capex $190M; "
            "Retail: Revenue $280M, EBITDA $42M, Capex $28M; "
            "Networks: Revenue $42M, EBITDA $8M, Capex $12M"
        )
    parts = [
        f"{r['business_unit']}: Revenue ${r['revenue_m']}M, "
        f"EBITDA ${r['ebitda_m']}M, Capex ${r['capex_m']}M"
        for r in rows
    ]
    return "; ".join(parts)


def _fetch_risk_context() -> str:
    rows = _run_sql(f"""
        SELECT risk_id, category, description, rating, risk_score, owner
        FROM {CATALOG}.eds_synthetic.risk_register
        WHERE rating IN ('Critical', 'High')
        ORDER BY CAST(risk_score AS DOUBLE) DESC
        LIMIT 5
    """)
    if not rows:
        return (
            "[Critical] WEM Capacity Mechanism — policy uncertainty threatening generation economics; "
            "[Critical] LYB Plant Risk — ageing asset outage probability rising; "
            "[High] Cyber/OT Security — SCADA vulnerability remediation underway; "
            "[High] Regulatory Compliance — emissions reporting obligations increasing"
        )
    parts = [
        f"[{r['rating']}] {r['category']}: {str(r.get('description',''))[:100]}"
        for r in rows
    ]
    return "; ".join(parts)


# ── Request model ─────────────────────────────────────────────────────────────

class SimulateRequest(BaseModel):
    decision: str
    role: str = "Board Director / CEO"
    drilldown_branch: Optional[str] = None   # "Bear"|"Base"|"Bull" for phase 2
    drilldown_scenario: Optional[dict] = None  # pass the selected scenario object back


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get("/api/simulate/templates")
async def get_templates():
    return {"templates": DECISION_TEMPLATES}


@router.post("/api/simulate/stream")
async def simulate_stream(req: SimulateRequest):
    """Stream Bear/Base/Bull scenario simulation or a drill-down narrative."""

    tier = TIER_MAP.get(req.role, 4)
    if tier > 2:
        async def _denied():
            yield f"data: {json.dumps({'type': 'error', 'content': 'Access restricted to Board and Executive Leadership Team.'})}\n\n"
        return StreamingResponse(_denied(), media_type="text/event-stream")

    tok = get_token()
    url = get_workspace_url()
    decision = req.decision.strip()
    drilldown_branch = req.drilldown_branch
    drilldown_scenario = req.drilldown_scenario

    def event_stream():
        start = time.time()

        # ── Fetch grounding data ──────────────────────────────────────────────
        kpi_context = _fetch_kpi_context()
        financial_context = _fetch_financial_context()
        risk_context = _fetch_risk_context()

        # ── Demo fallback ─────────────────────────────────────────────────────
        if not tok:
            demo_json = json.dumps({
                "decision": decision,
                "scenarios": [
                    {
                        "label": "Bear",
                        "probability": 0.25,
                        "headline": "Adverse market conditions erode margins and delay strategic milestones.",
                        "key_assumptions": [
                            "Energy prices fall 15% below forecast",
                            "WEM capacity payments not materialised",
                            "Regulatory delays increase capital costs by 20%",
                            "Retail churn accelerates to 18%",
                        ],
                        "kpi_impact": {
                            "EBITDA Margin": {"baseline": 18.2, "projected": 14.5, "unit": "%"},
                            "Revenue": {"baseline": 842.0, "projected": 720.0, "unit": "$M"},
                            "LYB Availability": {"baseline": 93.5, "projected": 88.0, "unit": "%"},
                        },
                        "risk_factors": [
                            "Accelerated asset retirement costs exceeding provision",
                            "Debt covenant breach risk at gearing above 50%",
                            "Reputational damage from delayed transition commitments",
                        ],
                        "strategic_rationale": (
                            "The bear case assumes policy headwinds and adverse spot prices force "
                            "margin compression across generation and retail. Capital constraints "
                            "limit the speed of renewable replacement, extending thermal exposure."
                        ),
                    },
                    {
                        "label": "Base",
                        "probability": 0.55,
                        "headline": "Steady execution of transition strategy delivers stable returns through FY27.",
                        "key_assumptions": [
                            "Energy prices broadly in line with forward curve",
                            "WEM capacity mechanism provides partial revenue certainty",
                            "Yandin Stage 2 commissioned Q2 FY27 on schedule",
                            "Retail NPS recovers to 24 by FY26",
                        ],
                        "kpi_impact": {
                            "EBITDA Margin": {"baseline": 18.2, "projected": 19.1, "unit": "%"},
                            "Revenue": {"baseline": 842.0, "projected": 875.0, "unit": "$M"},
                            "LYB Availability": {"baseline": 93.5, "projected": 92.0, "unit": "%"},
                        },
                        "risk_factors": [
                            "Execution risk on Yandin Stage 2 EPC contract",
                            "Retail competitive pressure from Origin and AGL digital offerings",
                        ],
                        "strategic_rationale": (
                            "The base case represents disciplined execution of the approved capital "
                            "programme with manageable risk exposure. EBITDA growth is underpinned "
                            "by renewable commissioning and retail platform modernisation."
                        ),
                    },
                    {
                        "label": "Bull",
                        "probability": 0.20,
                        "headline": "Favourable policy and market conditions accelerate renewable transition and margin expansion.",
                        "key_assumptions": [
                            "Energy prices 10% above forecast due to tight NEM supply",
                            "WEM capacity payments fully materialise at target rates",
                            "Carbon credit prices increase 25%, improving ESG economics",
                            "Retail NPS reaches 30 driven by digital platform success",
                        ],
                        "kpi_impact": {
                            "EBITDA Margin": {"baseline": 18.2, "projected": 23.5, "unit": "%"},
                            "Revenue": {"baseline": 842.0, "projected": 960.0, "unit": "$M"},
                            "LYB Availability": {"baseline": 93.5, "projected": 94.5, "unit": "%"},
                        },
                        "risk_factors": [
                            "Overheating risk if acceleration outpaces organisational capability",
                            "Supply chain constraints on renewable equipment delivery",
                        ],
                        "strategic_rationale": (
                            "The bull case is driven by aligned policy support and strong wholesale "
                            "pricing. Early FID on additional renewable projects would be warranted, "
                            "with potential to increase FY26 dividend payout above the 60% floor."
                        ),
                    },
                ],
                "recommended": "Base",
                "recommendation_rationale": (
                    "The Base scenario offers the most reliable risk-adjusted return given current "
                    "market visibility. It maintains strategic optionality for acceleration if "
                    "bull-case conditions emerge in H2 FY25."
                ),
            }, indent=2)

            if drilldown_branch:
                demo_drilldown = (
                    f"## Implementation Roadmap — {drilldown_branch} Scenario\n\n"
                    "- **Q1 FY26** — Board resolution and management mandate issued; "
                    "programme governance structure established (Owner: CEO)\n"
                    "- **Q1–Q2 FY26** — EPC contract execution and financial close; "
                    "hedging programme activated (Owner: CFO / COO)\n"
                    "- **Q2–Q3 FY26** — Construction commencement; monthly Board progress reporting "
                    "against milestones (Owner: COO)\n"
                    "- **Q3 FY26** — Mid-point review with scenario reassessment; "
                    "trigger review if KPIs deviate >10% (Owner: CRO)\n"
                    "- **Q4 FY26–Q2 FY27** — Commissioning and commercial operation; "
                    "post-implementation review (Owner: CFO)\n\n"
                    "## Risk Mitigations\n\n"
                    "- **Execution risk** — Fixed-price EPC contract with liquidated damages; "
                    "weekly site progress reporting\n"
                    "- **Regulatory risk** — Proactive AEMO and ERA engagement; "
                    "regulatory affairs team embedded in project\n"
                    "- **Market risk** — Forward hedge book locked for 36 months at commissioning\n\n"
                    "## 90-Day Board Actions\n\n"
                    "1. Approve binding resolution endorsing selected scenario and capital authority\n"
                    "2. Commission independent review of scenario assumptions by external adviser\n"
                    "3. Establish Board sub-committee for quarterly programme oversight\n\n"
                    "## Key Metrics to Track\n\n"
                    "- EBITDA vs scenario forecast (monthly, CFO report)\n"
                    "- Construction milestone completion rate (monthly, COO report)\n"
                    "- Wholesale energy price vs hedge book (monthly, Trading report)\n"
                    "- Retail NPS and churn rate (monthly, CMO report)\n"
                )
                for chunk in demo_drilldown.split(" "):
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk + ' '})}\n\n"
            else:
                for chunk in demo_json.split("\n"):
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk + chr(10)})}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'latency_ms': int((time.time() - start) * 1000)})}\n\n"
            return

        # ── Live LLM path ─────────────────────────────────────────────────────
        if drilldown_branch and drilldown_scenario:
            # Phase 2: drill-down narrative for selected branch
            risk_factors = drilldown_scenario.get("risk_factors", [])
            system_prompt = (
                AGENT_PROMPTS["scenario_drilldown"]
                .replace("{branch}", drilldown_branch)
                .replace("{decision}", decision)
            )
            user_prompt = (
                f"Selected scenario: {drilldown_branch}\n"
                f"Decision: {decision}\n"
                f"Scenario headline: {drilldown_scenario.get('headline', '')}\n"
                f"Risk factors: {'; '.join(risk_factors)}\n"
                f"Key assumptions: {'; '.join(drilldown_scenario.get('key_assumptions', []))}\n\n"
                "Produce the full drill-down now."
            )
            max_tokens = 3000
        else:
            # Phase 1: scenario tree generation
            system_prompt = AGENT_PROMPTS["scenario"]
            user_prompt = (
                f"Real Alinta Energy data context:\n"
                f"KPIs: {kpi_context}\n"
                f"Financials: {financial_context}\n"
                f"Open risks: {risk_context}\n\n"
                f"Decision to simulate: {decision}\n\n"
                "Generate the scenario JSON now."
            )
            max_tokens = 4000

        payload = {
            "model": LLM_ENDPOINT,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.4,
            "stream": True,
        }

        try:
            with requests.post(
                f"{url}/serving-endpoints/{LLM_ENDPOINT}/invocations",
                headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                json=payload,
                stream=True,
                timeout=240,
            ) as resp:
                if not resp.ok:
                    yield f"data: {json.dumps({'type': 'error', 'content': f'LLM error {resp.status_code}'})}\n\n"
                else:
                    finish_reason = "unknown"
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        text = line.decode("utf-8") if isinstance(line, bytes) else line
                        if not text.startswith("data: "):
                            continue
                        chunk_str = text[6:]
                        if chunk_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk_str)
                            choice = data.get("choices", [{}])[0]
                            fr = choice.get("finish_reason")
                            if fr:
                                finish_reason = fr
                            content = choice.get("delta", {}).get("content", "")
                            if content:
                                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                        except Exception:
                            pass
                    print(
                        f"[SIMULATE] branch={drilldown_branch or 'tree'} "
                        f"finish={finish_reason} "
                        f"latency={int((time.time() - start) * 1000)}ms"
                    )
        except Exception as e:
            print(f"[SIMULATE] stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'latency_ms': int((time.time() - start) * 1000)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
