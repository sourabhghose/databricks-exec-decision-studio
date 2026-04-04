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
            json={"warehouse_id": wh, "statement": sql, "wait_timeout": "30s"},
            timeout=35,
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
