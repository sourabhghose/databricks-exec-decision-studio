"""GET /api/overview — Aggregated summary for the Executive Overview dashboard."""

import requests
from fastapi import APIRouter, Query
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


def _run_sql_slow(sql: str) -> list:
    """Same as _run_sql but with a 60s wait_timeout for slow queries like ai_query."""
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
            print(f"[SQL/overview/slow] HTTP {r.status_code}: {r.text[:200]}")
            return []
        d = r.json()
        if d.get("status", {}).get("state") != "SUCCEEDED":
            print(f"[SQL/overview/slow] state={d.get('status', {}).get('state')}")
            return []
        result = d.get("result", {})
        if not result.get("data_array"):
            return []
        cols = [c["name"] for c in d.get("manifest", {}).get("schema", {}).get("columns", [])]
        return [dict(zip(cols, row)) for row in result["data_array"]]
    except Exception as e:
        print(f"[SQL/overview/slow] {e}")
        return []


def _get_ai_analysis(prompt: str) -> str:
    """Call ai_query with Claude Sonnet 4.6. Escape single quotes for SQL."""
    safe = prompt.replace("'", "''")
    rows = _run_sql_slow(f"SELECT ai_query('databricks-claude-sonnet-4-6', '{safe}') as analysis")
    if rows and rows[0].get("analysis"):
        return str(rows[0]["analysis"])
    return ""


_DEMO_ANALYSIS: dict[str, str] = {
    "kpis": (
        "## KEY CONCERNS\n"
        "- Customer satisfaction has declined 3.2% below target across the Retail segment, signalling potential churn risk.\n"
        "- Network reliability KPI is trending Yellow — two consecutive months below the 99.5% threshold.\n\n"
        "## RECOMMENDED ACTIONS\n"
        "- Convene a cross-functional review of the Retail NPS programme within 2 weeks.\n"
        "- Engage Network Operations to investigate root causes for the reliability dip and report back by next board cycle.\n\n"
        "## BOARD ESCALATION ITEMS\n"
        "- If customer satisfaction does not recover within 60 days, consider accelerating the digital transformation roadmap investment."
    ),
    "risks": (
        "## TOP RISKS REQUIRING BOARD ATTENTION\n"
        "- Regulatory compliance risk remains elevated following recent AEMO rule changes; critical rating.\n"
        "- Cybersecurity posture risk has risen to High due to increased threat actor activity in the energy sector.\n\n"
        "## MITIGATION PRIORITIES\n"
        "- Legal and Compliance team should complete the regulatory gap analysis by end of quarter.\n"
        "- IT Security to present an updated threat remediation plan at the next executive committee.\n\n"
        "## NEXT STEPS\n"
        "- Assign dedicated risk owners with fortnightly status updates to the board risk committee.\n"
        "- Consider engaging an independent cyber-security auditor for Q3."
    ),
    "actions": (
        "## OVERDUE ESCALATION\n"
        "- 3 action items are overdue by more than 14 days; owners have not provided status updates.\n"
        "- Two overdue items relate to the network upgrade programme which is on the critical path.\n\n"
        "## RESOURCE BOTTLENECKS\n"
        "- Engineering bandwidth is constrained — 6 open items are assigned to the same two team leads.\n\n"
        "## RECOMMENDED NEXT STEPS\n"
        "- COO to conduct a 30-minute triage call with overdue item owners this week.\n"
        "- Consider re-allocating one contractor resource from the innovation pipeline to clear critical blockers."
    ),
    "queries": (
        "## USAGE PATTERNS\n"
        "- Most queries over the last 7 days relate to regulatory compliance and network performance topics.\n"
        "- The Risk Intelligence agent handles 40% of all queries, indicating high board interest in risk posture.\n\n"
        "## KNOWLEDGE GAPS\n"
        "- Several queries returned low-confidence responses on wholesale market price forecasting.\n"
        "- Limited coverage detected for questions about renewables procurement strategy.\n\n"
        "## RECOMMENDATIONS TO IMPROVE AI COVERAGE\n"
        "- Ingest the latest AEMO Quarterly Energy Dynamics report into the document corpus.\n"
        "- Add a dedicated renewables strategy knowledge base to improve coverage of green energy queries."
    ),
}


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


@router.get("/api/overview/drilldown")
async def get_drilldown(metric: str = Query(..., description="One of: kpis, risks, actions, queries")):
    """Return full item list + AI analysis for a given metric."""

    if metric == "kpis":
        return await _drilldown_kpis()
    elif metric == "risks":
        return await _drilldown_risks()
    elif metric == "actions":
        return await _drilldown_actions()
    elif metric == "queries":
        return await _drilldown_queries()
    else:
        return {"metric": metric, "items": [], "analysis": "Unknown metric requested."}


async def _drilldown_kpis() -> dict:
    rows = _run_sql(f"""
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

    if not rows:
        rows = DEMO_KPIS

    items = []
    for r in rows:
        pct = float(r.get("pct") or r.get("pct_vs_target") or 0)
        status = "Green" if abs(pct) < 5 else ("Red" if pct < -10 else "Yellow")
        items.append({
            "kpi_name": r.get("kpi_name", ""),
            "business_unit": r.get("business_unit", ""),
            "category": r.get("category", ""),
            "value": float(r.get("value", 0)),
            "unit": r.get("unit", ""),
            "target": float(r.get("target", 0)),
            "pct_vs_target": pct,
            "status": status,
            "is_anomaly": str(r.get("is_anomaly", "")).lower() in ("true", "1"),
        })

    # Build prompt in Python then pass to ai_query
    summary_lines = []
    for it in items[:30]:
        summary_lines.append(
            f"- {it['kpi_name']} ({it['business_unit']}): value={it['value']} {it['unit']}, "
            f"target={it['target']} {it['unit']}, delta={it['pct_vs_target']:+.1f}%, status={it['status']}"
            + (" [ANOMALY]" if it["is_anomaly"] else "")
        )
    prompt = (
        "You are a strategic executive analyst for Alinta Energy. "
        "Review the following KPI performance data and provide a concise executive briefing. "
        "Structure your response with these sections: KEY CONCERNS, RECOMMENDED ACTIONS, BOARD ESCALATION ITEMS. "
        "Maximum 250 words.\n\nKPI DATA:\n" + "\n".join(summary_lines)
    )

    analysis = _get_ai_analysis(prompt) or _DEMO_ANALYSIS["kpis"]
    return {"metric": "kpis", "items": items, "analysis": analysis}


async def _drilldown_risks() -> dict:
    rows = _run_sql(f"""
        SELECT risk_id, category, description, likelihood, consequence,
               rating, risk_score, owner, status
        FROM {CATALOG}.eds_synthetic.risk_register
        WHERE status != 'closed'
        ORDER BY risk_score DESC
    """)

    if not rows:
        rows = list(DEMO_RISKS)

    items = [dict(r) for r in rows]

    # Build prompt from top 20
    summary_lines = []
    for r in items[:20]:
        summary_lines.append(
            f"- [{r.get('rating', '')}] {r.get('description', '')} "
            f"(score={r.get('risk_score', '')}, owner={r.get('owner', '')}, category={r.get('category', '')})"
        )
    prompt = (
        "You are a risk management executive at Alinta Energy. "
        "Review the following open risk register items and provide a concise board briefing. "
        "Structure your response with: TOP RISKS REQUIRING BOARD ATTENTION, MITIGATION PRIORITIES, NEXT STEPS. "
        "Maximum 250 words.\n\nRISK DATA:\n" + "\n".join(summary_lines)
    )

    analysis = _get_ai_analysis(prompt) or _DEMO_ANALYSIS["risks"]
    return {"metric": "risks", "items": items, "analysis": analysis}


async def _drilldown_actions() -> dict:
    rows = _run_sql(f"""
        SELECT action_id, title, description, status, owner, due_date,
               priority, related_decision_id
        FROM {CATALOG}.eds_actions.action_items
        ORDER BY CASE status
            WHEN 'overdue' THEN 1
            WHEN 'open' THEN 2
            WHEN 'in_progress' THEN 3
            ELSE 4
        END
    """)

    if not rows:
        rows = list(DEMO_ACTIONS) if DEMO_ACTIONS else []

    items = [dict(r) for r in rows]

    summary_lines = []
    for r in items[:30]:
        summary_lines.append(
            f"- [{r.get('status', '').upper()}] {r.get('title', '')} "
            f"(owner={r.get('owner', '')}, due={r.get('due_date', 'N/A')}, priority={r.get('priority', 'N/A')})"
        )
    prompt = (
        "You are a COO-level executive at Alinta Energy reviewing the action item register. "
        "Provide a concise executive briefing covering: OVERDUE ESCALATION, RESOURCE BOTTLENECKS, RECOMMENDED NEXT STEPS. "
        "Maximum 220 words.\n\nACTION ITEMS:\n" + "\n".join(summary_lines)
    )

    analysis = _get_ai_analysis(prompt) or _DEMO_ANALYSIS["actions"]
    return {"metric": "actions", "items": items, "analysis": analysis}


async def _drilldown_queries() -> dict:
    rows = _run_sql(f"""
        SELECT interaction_id, agent_name, query_text, response_summary,
               confidence_score, latency_ms, user_role,
               CAST(timestamp AS STRING) as timestamp
        FROM {CATALOG}.eds_audit.agent_interactions
        ORDER BY timestamp DESC
        LIMIT 30
    """)

    if not rows:
        rows = []

    items = [dict(r) for r in rows]

    summary_lines = []
    for r in items[:30]:
        conf = r.get("confidence_score", "")
        conf_str = f"{float(conf) * 100:.0f}%" if conf else "N/A"
        summary_lines.append(
            f"- Agent: {r.get('agent_name', 'Unknown')} | "
            f"Query: {str(r.get('query_text', ''))[:100]} | "
            f"Confidence: {conf_str} | "
            f"Role: {r.get('user_role', 'N/A')}"
        )
    prompt = (
        "You are a Chief Digital Officer at Alinta Energy reviewing AI assistant usage patterns. "
        "Analyse the following recent AI agent interactions and provide a concise briefing covering: "
        "USAGE PATTERNS, KNOWLEDGE GAPS, RECOMMENDATIONS TO IMPROVE AI COVERAGE. "
        "Maximum 200 words.\n\nRECENT QUERIES:\n" + "\n".join(summary_lines)
    )

    analysis = _get_ai_analysis(prompt) or _DEMO_ANALYSIS["queries"]
    return {"metric": "queries", "items": items, "analysis": analysis}
