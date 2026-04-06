"""GET /api/decisions — Board decision register."""

import requests
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from server.config import CATALOG, get_token, get_warehouse_id, get_workspace_url

router = APIRouter()

DEMO_DECISIONS = [
    {"decision_id": "DEC-001", "decision_date": "2025-03-15", "committee": "Board", "description": "Approved FY2026 Capital Expenditure Budget of $425M including $285M for Yandin Wind Farm Stage 2 and $95M for LYB life extension works", "decision_type": "financial", "outcome": "Approved — Board resolution BR-2025-12", "owner": "CFO", "implementation_status": "in_progress"},
    {"decision_id": "DEC-002", "decision_date": "2025-03-15", "committee": "Board", "description": "Endorsed Net Zero by 2045 pathway and approved $1.2B renewable investment programme over 5 years", "decision_type": "strategic", "outcome": "Approved with condition — annual progress reporting to Board", "owner": "CEO", "implementation_status": "in_progress"},
    {"decision_id": "DEC-003", "decision_date": "2025-02-20", "committee": "ELT", "description": "Approved Retail Transformation Program business case — $45M investment to modernise customer platform and reduce churn", "decision_type": "operational", "outcome": "Approved — programme commenced Q1 FY25", "owner": "CMO", "implementation_status": "in_progress"},
    {"decision_id": "DEC-004", "decision_date": "2025-02-20", "committee": "Board", "description": "Approved submission to AEMO WEM Capacity Mechanism consultation — advocating for dispatchable capacity payments", "decision_type": "risk", "outcome": "Approved — submission lodged 28 February 2025", "owner": "Regulatory Affairs", "implementation_status": "complete"},
    {"decision_id": "DEC-005", "decision_date": "2025-01-25", "committee": "IC", "description": "Investment Committee approved Yandin Wind Farm Stage 2 FID — 132MW expansion, commissioning target Q2 FY27", "decision_type": "financial", "outcome": "Approved — FID confirmed; EPC contract execution underway", "owner": "CFO / COO", "implementation_status": "in_progress"},
    {"decision_id": "DEC-006", "decision_date": "2025-01-25", "committee": "RC", "description": "Risk Committee accepted residual risk of Loy Yang B operating to 2030 pending renewable replacement capacity", "decision_type": "risk", "outcome": "Accepted — enhanced monitoring programme implemented", "owner": "CRO", "implementation_status": "complete"},
    {"decision_id": "DEC-007", "decision_date": "2024-12-10", "committee": "Board", "description": "Approved updated Capital Allocation Framework — dividend policy revised to 60% payout ratio from FY25", "decision_type": "financial", "outcome": "Approved — new policy effective 1 January 2025", "owner": "CFO", "implementation_status": "complete"},
    {"decision_id": "DEC-008", "decision_date": "2024-11-20", "committee": "ELT", "description": "Approved OT Cybersecurity Uplift Program — $12M over 18 months to remediate SCADA vulnerabilities", "decision_type": "operational", "outcome": "Approved — Phase 1 commenced", "owner": "CISO", "implementation_status": "in_progress"},
    {"decision_id": "DEC-009", "decision_date": "2024-10-15", "committee": "Board", "description": "Approved Trading Strategy refresh — increased gas trading book limit and expanded renewable trading capability", "decision_type": "strategic", "outcome": "Approved — new limits effective Q2 FY25", "owner": "CRO / Trading", "implementation_status": "complete"},
    {"decision_id": "DEC-010", "decision_date": "2024-09-30", "committee": "ELT", "description": "Deferred Newman Station major refurbishment to FY27 pending mining customer contract renewal", "decision_type": "financial", "outcome": "Deferred — contract negotiations ongoing", "owner": "COO", "implementation_status": "deferred"},
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
        print(f"[SQL decisions] {e}")
        return []


class DecisionSave(BaseModel):
    decision_id: str
    decision_date: str
    committee: str = "Board"
    description: str
    decision_type: str = "strategic"
    outcome: str = ""
    owner: str = "CEO"
    implementation_status: str = "pending"


@router.post("/api/decisions/save")
async def save_decision(req: DecisionSave):
    """Persist a scenario simulation outcome to the decision register."""
    tok = get_token()
    wh = get_warehouse_id()
    url = get_workspace_url()
    if not tok or not wh:
        return {"ok": False, "demo": True}

    desc = req.description.replace("'", "\\'")
    outcome = req.outcome.replace("'", "\\'")
    sql = (
        f"INSERT INTO {CATALOG}.eds_actions.decision_register "
        f"(decision_id, decision_date, committee, description, decision_type, "
        f"outcome, owner, implementation_status) VALUES ("
        f"'{req.decision_id}', '{req.decision_date}', '{req.committee}', "
        f"'{desc}', '{req.decision_type}', '{outcome}', '{req.owner}', "
        f"'{req.implementation_status}')"
    )
    rows = _run_sql(sql)
    return {"ok": True, "decision_id": req.decision_id}


@router.get("/api/decisions")
async def get_decisions():
    rows = _run_sql(f"""
        SELECT decision_id, CAST(decision_date AS STRING) as decision_date,
               committee, description, decision_type, outcome, owner, implementation_status
        FROM {CATALOG}.eds_actions.decision_register
        ORDER BY decision_date DESC
        LIMIT 50
    """)
    if not rows:
        return {"data": DEMO_DECISIONS, "demo": True}
    return {"data": rows, "demo": False}
