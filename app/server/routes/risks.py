"""GET /api/risks — Enterprise risk register."""

import requests
from fastapi import APIRouter
from server.config import CATALOG, LLM_ENDPOINT, get_token, get_warehouse_id, get_workspace_url

router = APIRouter()

DEMO_RISKS = [
    {"risk_id": "RSK-001", "category": "regulatory", "description": "WEM capacity mechanism policy uncertainty may adversely impact generation asset economics and investment decisions", "likelihood": "Likely", "consequence": "Major", "rating": "Critical", "risk_score": 20, "owner": "CFO / Regulatory Affairs", "mitigation": "Active engagement with AEMO and EPWA; WEM submission lodged Q1 FY25", "status": "open"},
    {"risk_id": "RSK-002", "category": "operational", "description": "Loy Yang B unplanned outage due to ageing plant and limited spare parts availability", "likelihood": "Possible", "consequence": "Catastrophic", "rating": "Critical", "risk_score": 19, "owner": "COO / Generation", "mitigation": "Enhanced predictive maintenance programme; spare parts inventory review complete", "status": "in_progress"},
    {"risk_id": "RSK-003", "category": "market", "description": "Sustained wholesale electricity price decline below marginal cost of generation assets", "likelihood": "Possible", "consequence": "Major", "rating": "High", "risk_score": 15, "owner": "CRO / Trading", "mitigation": "Dynamic hedging strategy; 65% FY25 generation hedged at floor prices", "status": "open"},
    {"risk_id": "RSK-004", "category": "ESG", "description": "Carbon regulatory risk — accelerated transition to emissions trading scheme increases compliance cost", "likelihood": "Likely", "consequence": "Major", "rating": "High", "risk_score": 16, "owner": "CSO / Strategy", "mitigation": "Net zero roadmap developed; renewable pipeline investment $1.2B committed", "status": "in_progress"},
    {"risk_id": "RSK-005", "category": "cyber", "description": "OT/SCADA system cyber intrusion leading to operational disruption or safety event", "likelihood": "Unlikely", "consequence": "Catastrophic", "rating": "High", "risk_score": 16, "owner": "CISO / Operations", "mitigation": "OT cybersecurity uplift program underway; ISO 27001 certification FY25", "status": "in_progress"},
    {"risk_id": "RSK-006", "category": "market", "description": "Retail customer churn acceleration due to price competition and digital disruptors", "likelihood": "Likely", "consequence": "Moderate", "rating": "High", "risk_score": 12, "owner": "CMO / Retail", "mitigation": "Retail transformation program launched; NPS recovery plan targeting +5pts by FY26", "status": "open"},
    {"risk_id": "RSK-007", "category": "financial", "description": "Refinancing risk — $800M debt maturity in FY26 in rising interest rate environment", "likelihood": "Possible", "consequence": "Major", "rating": "High", "risk_score": 15, "owner": "CFO / Treasury", "mitigation": "Pre-emptive refinancing commenced Q3 FY25; diversified lender base maintained", "status": "in_progress"},
    {"risk_id": "RSK-008", "category": "regulatory", "description": "ESG disclosure mandate non-compliance — ASRS standards effective FY26", "likelihood": "Possible", "consequence": "Moderate", "rating": "Medium", "risk_score": 10, "owner": "CFO / Sustainability", "mitigation": "ASRS gap analysis complete; data collection systems upgrade in progress", "status": "open"},
    {"risk_id": "RSK-009", "category": "operational", "description": "Yandin Wind Farm construction delays due to supply chain disruption", "likelihood": "Possible", "consequence": "Moderate", "rating": "Medium", "risk_score": 9, "owner": "COO / Projects", "mitigation": "Early procurement; contractual schedule protections with EPC contractor", "status": "open"},
    {"risk_id": "RSK-010", "category": "ESG", "description": "Water licence restriction risk at thermal generation sites in drought conditions", "likelihood": "Unlikely", "consequence": "Major", "rating": "Medium", "risk_score": 10, "owner": "COO / Environment", "mitigation": "Water efficiency investment; alternative cooling options assessed", "status": "accepted"},
]


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
        print(f"[SQL risks] {e}")
        return []


@router.get("/api/risks")
async def get_risks():
    rows = _run_sql(f"""
        SELECT risk_id, category, description, likelihood, consequence,
               rating, risk_score, owner, mitigation, status
        FROM {CATALOG}.eds_synthetic.risk_register
        ORDER BY risk_score DESC
        LIMIT 50
    """)
    if not rows:
        return {"data": DEMO_RISKS, "demo": True}
    return {"data": rows, "demo": False}


# ── AI Insights ───────────────────────────────────────────────────────────────

DEMO_RISK_INSIGHT = (
    "The risk register shows two Critical-rated risks requiring board-level attention: WEM regulatory "
    "uncertainty (Score 20) threatens generation asset economics, and Loy Yang B operational risk (Score 19) "
    "reflects the consequences of ageing plant. Both require active management beyond current mitigations. "
    "The $800M FY26 debt refinancing risk has moved to High and should be pre-emptively addressed before "
    "market conditions tighten. **Recommended action:** CFO to present refinancing options at the next board meeting "
    "alongside an updated LYB risk tolerance position."
)


def _call_llm(prompt: str) -> str | None:
    """Call Claude directly via serving endpoint. Returns text or None on failure."""
    tok = get_token()
    url = get_workspace_url()
    if not tok or not url:
        return None
    try:
        r = requests.post(
            f"{url}/serving-endpoints/{LLM_ENDPOINT}/invocations",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
            json={
                "model": LLM_ENDPOINT,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.3,
            },
            timeout=60,
        )
        if not r.ok:
            print(f"[risks/llm] {r.status_code} {r.text[:200]}")
            return None
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[risks/llm] {e}")
        return None


@router.get("/api/risks/ai_insights")
async def risk_ai_insights(risk_id: str = ""):
    """AI analysis for a specific risk or overall risk register."""
    if risk_id:
        rows = _run_sql(f"""
            SELECT risk_id, category, description, likelihood, consequence,
                   rating, risk_score, owner, mitigation, status
            FROM {CATALOG}.eds_synthetic.risk_register
            WHERE risk_id = '{risk_id.replace("'", "")}'
        """)
        risk = (rows or DEMO_RISKS)
        risk = next((r for r in risk if r.get("risk_id") == risk_id), None)
        if not risk:
            return {"insight": "Risk not found.", "demo": True}

        prompt = (
            f"You are Alinta Energy's Enterprise Risk Advisor. Analyse this risk:\n"
            f"[{risk['rating']}] {risk['description']}\n"
            f"Likelihood: {risk['likelihood']}, Consequence: {risk['consequence']}, "
            f"Score: {risk['risk_score']}/25, Owner: {risk['owner']}.\n"
            f"Current mitigation: {risk.get('mitigation', 'None stated')}.\n\n"
            "Provide: (1) a 2-sentence assessment of whether the current mitigation is sufficient, "
            "(2) one specific additional action to reduce this risk in the next 90 days, "
            "(3) two early warning indicators to monitor. Be precise and commercially candid."
        )
        insight = _call_llm(prompt)
        if insight:
            return {"insight": insight, "demo": False, "risk_id": risk_id}
        return {"insight": f"Mitigation: {risk.get('mitigation', 'None stated')}", "demo": True, "risk_id": risk_id}

    # Overall risk register summary
    rows = _run_sql(f"""
        SELECT rating, COUNT(*) as cnt, MAX(risk_score) as max_score
        FROM {CATALOG}.eds_synthetic.risk_register
        GROUP BY rating ORDER BY max_score DESC
    """)
    summary = ", ".join([f"{r['rating']}: {r['cnt']} risks" for r in rows]) if rows else "Critical: 2, High: 5, Medium: 3"

    prompt = (
        f"You are Alinta Energy's Chief Risk Officer advisor. Risk register summary: {summary}. "
        "In 3 sentences: identify the dominant risk theme, the most urgent single action, "
        "and whether the overall risk profile is improving or deteriorating. Be candid."
    )
    insight = _call_llm(prompt)
    if insight:
        return {"insight": insight, "demo": False}
    return {"insight": DEMO_RISK_INSIGHT, "demo": True}
