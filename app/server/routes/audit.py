"""
GET /api/audit — Audit trail of agent interactions, with demo fallback.
GET /api/audit/chart — Confidence trend data by agent for charting.
"""

import requests
from fastapi import APIRouter, Query

from server.config import CATALOG, get_token, get_warehouse_id, get_workspace_url

router = APIRouter()

DEMO_AUDIT = [
    {
        "timestamp": "2025-04-03 09:12:04",
        "user_tier": "Executive",
        "agent_name": "doc_qa",
        "query_preview": "What are the strategic options for the Loy Yang B transition?",
        "confidence": 0.88,
        "latency_ms": 2341,
        "compliant": True,
    },
    {
        "timestamp": "2025-04-03 09:05:31",
        "user_tier": "ELT",
        "agent_name": "kpi_monitor",
        "query_preview": "Summarise latest KPI performance across all business units",
        "confidence": 0.95,
        "latency_ms": 1122,
        "compliant": True,
    },
    {
        "timestamp": "2025-04-03 08:58:15",
        "user_tier": "Executive",
        "agent_name": "briefing",
        "query_preview": "Prepare an executive briefing on the WA renewables pipeline",
        "confidence": 0.81,
        "latency_ms": 4580,
        "compliant": True,
    },
    {
        "timestamp": "2025-04-03 08:45:22",
        "user_tier": "Senior Mgmt",
        "agent_name": "competitive",
        "query_preview": "How does Alinta compare to Origin Energy on retail churn?",
        "confidence": 0.76,
        "latency_ms": 3210,
        "compliant": True,
    },
    {
        "timestamp": "2025-04-03 08:32:10",
        "user_tier": "Executive",
        "agent_name": "strategic_gap",
        "query_preview": "Identify blind spots in the FY2025 Group Strategy Review",
        "confidence": 0.84,
        "latency_ms": 5102,
        "compliant": True,
    },
    {
        "timestamp": "2025-04-03 08:20:45",
        "user_tier": "CFO",
        "agent_name": "doc_qa",
        "query_preview": "What were the key financial results and variances in 1H FY25?",
        "confidence": 0.91,
        "latency_ms": 1890,
        "compliant": True,
    },
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
        print(f"[SQL/AUDIT] {e}")
        return []


@router.get("/api/audit")
async def get_audit(
    agent: str = Query(default=""),
    date_from: str = Query(default=""),
    date_to: str = Query(default=""),
):
    filters = []
    if agent:
        safe_agent = agent.replace("'", "")
        filters.append(f"agent_name = '{safe_agent}'")
    if date_from:
        safe_from = date_from[:10].replace("'", "")
        filters.append(f"DATE(timestamp) >= '{safe_from}'")
    if date_to:
        safe_to = date_to[:10].replace("'", "")
        filters.append(f"DATE(timestamp) <= '{safe_to}'")
    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    rows = _run_sql(f"""
        SELECT DATE_FORMAT(timestamp, 'yyyy-MM-dd HH:mm:ss') as ts,
               user_tier, agent_name,
               SUBSTRING(query, 1, 80) as q,
               ROUND(CAST(confidence_score AS DOUBLE), 2) as c,
               latency_ms,
               is_policy_compliant
        FROM {CATALOG}.eds_audit.agent_interactions
        {where}
        ORDER BY timestamp DESC
        LIMIT 50
    """)

    if not rows:
        return {"data": DEMO_AUDIT, "demo": True}

    out = []
    for r in rows:
        out.append({
            "timestamp": r.get("ts", ""),
            "user_tier": r.get("user_tier", ""),
            "agent_name": r.get("agent_name", ""),
            "query_preview": (r.get("q") or "") + "...",
            "confidence": float(r.get("c", 0)),
            "latency_ms": int(r.get("latency_ms") or 0),
            "compliant": str(r.get("is_policy_compliant", "")).lower() in ("true", "1", "yes"),
        })

    return {"data": out, "demo": False}


DEMO_AUDIT_CHART = [
    {"agent_name": "doc_qa",       "avg_confidence": 0.87, "query_count": 8},
    {"agent_name": "kpi_monitor",  "avg_confidence": 0.93, "query_count": 5},
    {"agent_name": "briefing",     "avg_confidence": 0.81, "query_count": 3},
    {"agent_name": "competitive",  "avg_confidence": 0.76, "query_count": 4},
    {"agent_name": "strategic_gap","avg_confidence": 0.84, "query_count": 2},
]


@router.get("/api/audit/chart")
async def audit_chart():
    """Average confidence score per agent (last 30 days) for the trend chart."""
    rows = _run_sql(f"""
        SELECT agent_name,
               ROUND(AVG(CAST(confidence_score AS DOUBLE)), 2) as avg_confidence,
               COUNT(*) as query_count
        FROM {CATALOG}.eds_audit.agent_interactions
        WHERE timestamp >= DATE_SUB(CURRENT_DATE(), 30)
        GROUP BY agent_name
        ORDER BY query_count DESC
    """)
    if not rows:
        return {"data": DEMO_AUDIT_CHART, "demo": True}
    return {
        "data": [
            {
                "agent_name": r.get("agent_name", ""),
                "avg_confidence": float(r.get("avg_confidence", 0)),
                "query_count": int(r.get("query_count", 0)),
            }
            for r in rows
        ],
        "demo": False,
    }
