"""
GET /api/actions — Board action items, with demo fallback.
"""

import requests
from fastapi import APIRouter

from server.config import CATALOG, get_token, get_warehouse_id, get_workspace_url

router = APIRouter()

DEMO_ACTIONS = [
    {"action_id": "ACT-001", "title": "Board decision on Loy Yang B retirement timeline", "owner": "CEO", "due_date": "2025-06-30", "priority": "Critical", "status": "Open", "business_unit": "Generation", "source_doc_id": "DOC-002"},
    {"action_id": "ACT-002", "title": "Submit WEM capacity mechanism response", "owner": "Regulatory Affairs", "due_date": "2025-04-30", "priority": "Critical", "status": "In Progress", "business_unit": "Trading", "source_doc_id": "DOC-008"},
    {"action_id": "ACT-003", "title": "Yandin Stage 2 FID approval", "owner": "CFO", "due_date": "2025-07-15", "priority": "High", "status": "Open", "business_unit": "Generation", "source_doc_id": "DOC-006"},
    {"action_id": "ACT-004", "title": "Retail NPS improvement plan launch", "owner": "CMO", "due_date": "2025-05-01", "priority": "High", "status": "In Progress", "business_unit": "Retail", "source_doc_id": "DOC-011"},
    {"action_id": "ACT-005", "title": "Net zero pathway board presentation", "owner": "CSO", "due_date": "2025-05-15", "priority": "High", "status": "Open", "business_unit": "Group", "source_doc_id": "DOC-005"},
    {"action_id": "ACT-006", "title": "Capital allocation framework sign-off", "owner": "CFO", "due_date": "2025-04-15", "priority": "High", "status": "Completed", "business_unit": "Group", "source_doc_id": "DOC-015"},
    {"action_id": "ACT-007", "title": "OT cybersecurity remediation phase 1", "owner": "CISO", "due_date": "2025-06-01", "priority": "Critical", "status": "In Progress", "business_unit": "Group", "source_doc_id": "DOC-010"},
    {"action_id": "ACT-008", "title": "Trading hedging strategy review", "owner": "CRO", "due_date": "2025-05-31", "priority": "Medium", "status": "Open", "business_unit": "Trading", "source_doc_id": "DOC-013"},
    {"action_id": "ACT-009", "title": "Board skills matrix refresh", "owner": "Company Secretary", "due_date": "2025-04-30", "priority": "Medium", "status": "Completed", "business_unit": "Group", "source_doc_id": "DOC-014"},
    {"action_id": "ACT-010", "title": "FY2026 budget board approval", "owner": "CFO", "due_date": "2025-05-30", "priority": "High", "status": "Open", "business_unit": "Group", "source_doc_id": "DOC-009"},
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
        print(f"[SQL/ACTIONS] {e}")
        return []


@router.get("/api/actions")
async def get_actions():
    rows = _run_sql(f"""
        SELECT action_id, title, owner, due_date, priority, status, business_unit, source_doc_id
        FROM {CATALOG}.eds_actions.action_items
        ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
                 due_date
        LIMIT 50
    """)

    if not rows:
        return {"data": DEMO_ACTIONS, "demo": True}

    out = []
    for r in rows:
        out.append({
            "action_id": r.get("action_id", ""),
            "title": r.get("title", ""),
            "owner": r.get("owner", ""),
            "due_date": r.get("due_date", ""),
            "priority": r.get("priority", "Medium"),
            "status": r.get("status", "Open"),
            "business_unit": r.get("business_unit", ""),
            "source_doc_id": r.get("source_doc_id", ""),
        })

    return {"data": out, "demo": False}


# ── AI Insights ───────────────────────────────────────────────────────────────

DEMO_ACTION_INSIGHT = (
    "The action register has 3 overdue items including ACT-002 (WEM Capacity Mechanism submission, "
    "Critical) which passed its April deadline and requires immediate escalation to the CEO. "
    "The Yandin Stage 2 FID (ACT-003) and FY26 Budget approval (ACT-010) are the highest-value "
    "pending items and should be progressed in parallel this month. "
    "**Priority:** Schedule an emergency governance meeting to close ACT-002 and assign accountable executive."
)


def _run_sql_slow(sql: str) -> list:
    tok = get_token()
    wh = get_warehouse_id()
    url = get_workspace_url()
    if not tok or not wh:
        return []
    try:
        r = requests.post(
            f"{url}/api/2.0/sql/statements",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
            json={"warehouse_id": wh, "statement": sql, "wait_timeout": "60s"},
            timeout=75,
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
        print(f"[SQL/actions slow] {e}")
        return []


@router.get("/api/actions/ai_insights")
async def actions_ai_insights():
    """AI prioritisation narrative for the action register via ai_query."""
    rows = _run_sql(f"""
        SELECT action_id, title, owner, due_date, priority, status, business_unit
        FROM {CATALOG}.eds_actions.action_items
        ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
                 due_date
        LIMIT 20
    """)
    use_demo = not rows
    actions = DEMO_ACTIONS if use_demo else rows

    overdue = [a for a in actions if a.get("due_date") and str(a.get("due_date", "")) < "2026-04-05" and a.get("status") not in ("Completed", "complete")]
    critical = [a for a in actions if a.get("priority") in ("Critical", "critical")]
    open_count = len([a for a in actions if a.get("status") in ("Open", "open")])

    prompt = (
        f"You are Alinta Energy's Board Secretary and Chief of Staff advisor. "
        f"Action register: {len(actions)} total actions, {open_count} open, "
        f"{len(overdue)} overdue: {[a['title'][:60] for a in overdue[:3]]}. "
        f"Critical priority actions: {[a['title'][:60] for a in critical[:3]]}. "
        "Provide a 3-sentence executive briefing: which actions pose the greatest governance risk if delayed, "
        "recommended sequencing for the next 2 weeks, and any actions that should be escalated to the Board. "
        "Be specific and action-oriented."
    ).replace("'", "''")

    result = _run_sql_slow(f"SELECT ai_query('databricks-claude-sonnet-4-6', '{prompt}') as insight")
    if result and result[0].get("insight"):
        return {"insight": str(result[0]["insight"]), "demo": False}
    return {"insight": DEMO_ACTION_INSIGHT, "demo": True}
