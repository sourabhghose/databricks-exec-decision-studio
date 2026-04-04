"""GET /api/overview — Aggregated summary for the Executive Overview dashboard."""

import requests
from fastapi import APIRouter
from server.config import CATALOG, get_token, get_warehouse_id, get_workspace_url
from server.routes.kpi import DEMO_KPIS
from server.routes.risks import DEMO_RISKS
from server.routes.decisions import DEMO_DECISIONS
from server.routes.actions import DEMO_ACTIONS  # type: ignore

router = APIRouter()


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
        print(f"[SQL/overview] {e}")
        return []


@router.get("/api/overview")
async def get_overview():
    demo = False

    # ── KPI hero metrics ───────────────────────────────────────────
    kpi_rows = _run_sql(f"""
        SELECT kpi_name, business_unit, category,
               ROUND(CAST(value AS DOUBLE), 2) as value, unit,
               ROUND(CAST(target AS DOUBLE), 2) as target,
               ROUND((CAST(value AS DOUBLE) - CAST(target AS DOUBLE))
                 / NULLIF(ABS(CAST(target AS DOUBLE)), 0) * 100, 1) as pct,
               is_anomaly
        FROM {CATALOG}.eds_synthetic.kpi_timeseries
        WHERE period = (SELECT MAX(period) FROM {CATALOG}.eds_synthetic.kpi_timeseries)
        ORDER BY business_unit, kpi_name
    """)

    if not kpi_rows:
        demo = True
        kpis = DEMO_KPIS
    else:
        kpis = []
        for r in kpi_rows:
            pct = float(r.get("pct") or 0)
            status = "Green" if abs(pct) < 5 else ("Red" if pct < -10 else "Yellow")
            kpis.append({
                "kpi_name": r["kpi_name"], "business_unit": r["business_unit"],
                "category": r.get("category", ""), "value": float(r["value"]),
                "unit": r.get("unit", ""), "target": float(r["target"]),
                "pct_vs_target": pct, "status": status,
                "is_anomaly": str(r.get("is_anomaly", "")).lower() in ("true", "1"),
            })

    # ── Risk summary ───────────────────────────────────────────────
    risk_rows = _run_sql(f"""
        SELECT rating, COUNT(*) as cnt
        FROM {CATALOG}.eds_synthetic.risk_register
        WHERE status != 'closed'
        GROUP BY rating ORDER BY cnt DESC
    """)
    if not risk_rows:
        risk_summary = {"Critical": 2, "High": 5, "Medium": 2, "Low": 1}
    else:
        risk_summary = {r["rating"]: int(r["cnt"]) for r in risk_rows}

    # ── Top risks ──────────────────────────────────────────────────
    top_risk_rows = _run_sql(f"""
        SELECT risk_id, category, description, likelihood, consequence,
               rating, risk_score, owner, status
        FROM {CATALOG}.eds_synthetic.risk_register
        WHERE status != 'closed'
        ORDER BY risk_score DESC LIMIT 5
    """)
    top_risks = top_risk_rows or DEMO_RISKS[:5]

    # ── Recent decisions ───────────────────────────────────────────
    dec_rows = _run_sql(f"""
        SELECT decision_id, CAST(decision_date AS STRING) as decision_date,
               committee, description, decision_type, implementation_status
        FROM {CATALOG}.eds_actions.decision_register
        ORDER BY decision_date DESC LIMIT 4
    """)
    recent_decisions = dec_rows or DEMO_DECISIONS[:4]

    # ── Action items summary ───────────────────────────────────────
    action_rows = _run_sql(f"""
        SELECT status, COUNT(*) as cnt
        FROM {CATALOG}.eds_actions.action_items
        GROUP BY status
    """)
    if not action_rows:
        action_summary = {"open": 4, "in_progress": 5, "complete": 3, "overdue": 2}
    else:
        action_summary = {r["status"]: int(r["cnt"]) for r in action_rows}

    # ── Audit activity (last 7 days) ───────────────────────────────
    audit_rows = _run_sql(f"""
        SELECT COUNT(*) as total_queries,
               ROUND(AVG(CAST(confidence_score AS DOUBLE)), 2) as avg_confidence,
               ROUND(AVG(CAST(latency_ms AS DOUBLE)), 0) as avg_latency_ms
        FROM {CATALOG}.eds_audit.agent_interactions
        WHERE timestamp >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
    """)
    if audit_rows and audit_rows[0].get("total_queries"):
        audit_stats = {
            "total_queries": int(audit_rows[0]["total_queries"] or 0),
            "avg_confidence": float(audit_rows[0]["avg_confidence"] or 0),
            "avg_latency_ms": float(audit_rows[0]["avg_latency_ms"] or 0),
        }
    else:
        audit_stats = {"total_queries": 47, "avg_confidence": 0.84, "avg_latency_ms": 2340}

    # ── Document stats ─────────────────────────────────────────────
    doc_rows = _run_sql(f"""
        SELECT COUNT(*) as total_chunks
        FROM {CATALOG}.eds_processed.document_chunks
    """)
    total_chunks = int(doc_rows[0]["total_chunks"]) if doc_rows else 1842

    return {
        "demo": demo,
        "kpis": kpis,
        "risk_summary": risk_summary,
        "top_risks": top_risks,
        "recent_decisions": recent_decisions,
        "action_summary": action_summary,
        "audit_stats": audit_stats,
        "doc_stats": {"total_documents": 22, "total_chunks": total_chunks},
    }
