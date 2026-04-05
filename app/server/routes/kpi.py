"""
GET /api/kpi — KPI dashboard data from Delta tables, with demo fallback.
"""

import requests
from fastapi import APIRouter

from server.config import CATALOG, get_token, get_warehouse_id, get_workspace_url

router = APIRouter()

DEMO_KPIS = [
    {
        "kpi_name": "LYB Plant Availability",
        "business_unit": "Generation",
        "category": "operational",
        "value": 93.5,
        "unit": "%",
        "target": 93.0,
        "pct_vs_target": 0.5,
        "status": "Green",
        "is_anomaly": False,
    },
    {
        "kpi_name": "Yandin Capacity Factor",
        "business_unit": "Generation",
        "category": "operational",
        "value": 40.1,
        "unit": "%",
        "target": 38.0,
        "pct_vs_target": 5.5,
        "status": "Green",
        "is_anomaly": False,
    },
    {
        "kpi_name": "Retail Customer NPS",
        "business_unit": "Retail",
        "category": "customer",
        "value": 22.0,
        "unit": "score",
        "target": 25.0,
        "pct_vs_target": -12.0,
        "status": "Yellow",
        "is_anomaly": False,
    },
    {
        "kpi_name": "Group EBITDA Margin",
        "business_unit": "Group",
        "category": "financial",
        "value": 18.2,
        "unit": "%",
        "target": 18.0,
        "pct_vs_target": 1.1,
        "status": "Green",
        "is_anomaly": False,
    },
    {
        "kpi_name": "Net Debt to EBITDA",
        "business_unit": "Group",
        "category": "financial",
        "value": 2.4,
        "unit": "x",
        "target": 2.5,
        "pct_vs_target": 4.0,
        "status": "Green",
        "is_anomaly": False,
    },
    {
        "kpi_name": "Retail Churn Rate",
        "business_unit": "Retail",
        "category": "customer",
        "value": 19.8,
        "unit": "%",
        "target": 18.0,
        "pct_vs_target": -10.0,
        "status": "Yellow",
        "is_anomaly": False,
    },
    {
        "kpi_name": "Scope 1 Intensity",
        "business_unit": "Group",
        "category": "ESG",
        "value": 0.89,
        "unit": "tCO2e/MWh",
        "target": 0.87,
        "pct_vs_target": -2.3,
        "status": "Yellow",
        "is_anomaly": False,
    },
    {
        "kpi_name": "TRIFR",
        "business_unit": "Group",
        "category": "safety",
        "value": 3.2,
        "unit": "per million hrs",
        "target": 3.5,
        "pct_vs_target": 8.6,
        "status": "Green",
        "is_anomaly": False,
    },
    {
        "kpi_name": "Wholesale Portfolio Margin",
        "business_unit": "Trading",
        "category": "financial",
        "value": 12.4,
        "unit": "$/MWh",
        "target": 11.0,
        "pct_vs_target": 12.7,
        "status": "Green",
        "is_anomaly": False,
    },
    {
        "kpi_name": "Customer Acquisition Cost",
        "business_unit": "Retail",
        "category": "financial",
        "value": 185.0,
        "unit": "$",
        "target": 170.0,
        "pct_vs_target": -8.8,
        "status": "Yellow",
        "is_anomaly": True,
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
        print(f"[SQL/KPI] {e}")
        return []


@router.get("/api/kpi")
async def get_kpis():
    rows = _run_sql(f"""
        SELECT kpi_name, business_unit, category,
               ROUND(CAST(value AS DOUBLE), 2) as v, unit,
               ROUND(CAST(target AS DOUBLE), 2) as t,
               ROUND(
                 (CAST(value AS DOUBLE) - CAST(target AS DOUBLE))
                 / NULLIF(ABS(CAST(target AS DOUBLE)), 0) * 100, 1
               ) as pct,
               is_anomaly
        FROM {CATALOG}.eds_synthetic.kpi_timeseries
        WHERE period = (SELECT MAX(period) FROM {CATALOG}.eds_synthetic.kpi_timeseries)
        ORDER BY business_unit, kpi_name
    """)

    if not rows:
        return {"data": DEMO_KPIS, "demo": True}

    out = []
    for r in rows:
        pct = float(r.get("pct") or 0)
        status = "Green" if abs(pct) < 5 else ("Red" if pct < -10 else "Yellow")
        is_anomaly = str(r.get("is_anomaly", "")).lower() in ("true", "1", "yes")
        out.append({
            "kpi_name": r["kpi_name"],
            "business_unit": r["business_unit"],
            "category": r.get("category", ""),
            "value": float(r["v"]),
            "unit": r.get("unit", ""),
            "target": float(r["t"]),
            "pct_vs_target": pct,
            "status": status,
            "is_anomaly": is_anomaly,
        })

    return {"data": out, "demo": False}


# ── KPI Trends ────────────────────────────────────────────────────────────────

DEMO_TRENDS = {
    "Group EBITDA Margin": [
        {"period": "2024-07", "value": 16.8, "unit": "%", "business_unit": "Group"},
        {"period": "2024-08", "value": 17.1, "unit": "%", "business_unit": "Group"},
        {"period": "2024-09", "value": 17.4, "unit": "%", "business_unit": "Group"},
        {"period": "2024-10", "value": 17.8, "unit": "%", "business_unit": "Group"},
        {"period": "2024-11", "value": 18.0, "unit": "%", "business_unit": "Group"},
        {"period": "2024-12", "value": 18.2, "unit": "%", "business_unit": "Group"},
    ],
    "Retail Customer NPS": [
        {"period": "2024-07", "value": 26.0, "unit": "score", "business_unit": "Retail"},
        {"period": "2024-08", "value": 25.0, "unit": "score", "business_unit": "Retail"},
        {"period": "2024-09", "value": 24.0, "unit": "score", "business_unit": "Retail"},
        {"period": "2024-10", "value": 23.5, "unit": "score", "business_unit": "Retail"},
        {"period": "2024-11", "value": 22.8, "unit": "score", "business_unit": "Retail"},
        {"period": "2024-12", "value": 22.0, "unit": "score", "business_unit": "Retail"},
    ],
    "LYB Plant Availability": [
        {"period": "2024-07", "value": 91.2, "unit": "%", "business_unit": "Generation"},
        {"period": "2024-08", "value": 92.0, "unit": "%", "business_unit": "Generation"},
        {"period": "2024-09", "value": 90.8, "unit": "%", "business_unit": "Generation"},
        {"period": "2024-10", "value": 92.5, "unit": "%", "business_unit": "Generation"},
        {"period": "2024-11", "value": 93.1, "unit": "%", "business_unit": "Generation"},
        {"period": "2024-12", "value": 93.5, "unit": "%", "business_unit": "Generation"},
    ],
    "Retail Churn Rate": [
        {"period": "2024-07", "value": 17.2, "unit": "%", "business_unit": "Retail"},
        {"period": "2024-08", "value": 17.8, "unit": "%", "business_unit": "Retail"},
        {"period": "2024-09", "value": 18.1, "unit": "%", "business_unit": "Retail"},
        {"period": "2024-10", "value": 18.6, "unit": "%", "business_unit": "Retail"},
        {"period": "2024-11", "value": 19.2, "unit": "%", "business_unit": "Retail"},
        {"period": "2024-12", "value": 19.8, "unit": "%", "business_unit": "Retail"},
    ],
}


@router.get("/api/kpi/trends")
async def kpi_trends():
    """Returns monthly KPI values for the last 6 periods per KPI."""
    rows = _run_sql(f"""
        SELECT kpi_name, business_unit, period, ROUND(CAST(value AS DOUBLE), 2) as value, unit
        FROM {CATALOG}.eds_synthetic.kpi_timeseries
        WHERE kpi_name IN ('Group EBITDA Margin','Retail Customer NPS','LYB Plant Availability','Retail Churn Rate')
        ORDER BY kpi_name, period DESC
    """)

    if not rows:
        return {"data": DEMO_TRENDS, "demo": True}

    # Group by kpi_name, take last 6 periods each
    grouped: dict[str, list] = {}
    for r in rows:
        name = r["kpi_name"]
        if name not in grouped:
            grouped[name] = []
        if len(grouped[name]) < 6:
            grouped[name].append({
                "period": r["period"],
                "value": float(r["value"]),
                "unit": r.get("unit", ""),
                "business_unit": r.get("business_unit", ""),
            })

    # Reverse so oldest first for chart
    for name in grouped:
        grouped[name] = list(reversed(grouped[name]))

    return {"data": grouped, "demo": False}


# ── Financial Highlights ──────────────────────────────────────────────────────

DEMO_FINANCIALS = [
    {"business_unit": "Generation", "actual": 412.5, "budget": 395.0},
    {"business_unit": "Retail", "actual": 285.3, "budget": 310.0},
    {"business_unit": "Trading", "actual": 178.2, "budget": 165.0},
    {"business_unit": "Corporate", "actual": -42.1, "budget": -38.0},
]


@router.get("/api/financials")
async def get_financials():
    """Revenue vs Budget by Business Unit for FY2025 1H."""
    rows = _run_sql(f"""
        SELECT business_unit, metric_type,
               ROUND(SUM(CAST(value AS DOUBLE))/1e6, 1) as value_millions
        FROM {CATALOG}.eds_synthetic.financial_data
        WHERE fiscal_year = 'FY2025' AND quarter IN ('Q1','Q2')
        GROUP BY business_unit, metric_type
        ORDER BY business_unit
    """)

    if not rows:
        return {"data": DEMO_FINANCIALS, "demo": True}

    # Pivot: one row per BU with actual + budget
    bu_map: dict[str, dict] = {}
    for r in rows:
        bu = r["business_unit"]
        if bu not in bu_map:
            bu_map[bu] = {"business_unit": bu, "actual": 0, "budget": 0}
        mt = (r.get("metric_type") or "").lower()
        val = float(r.get("value_millions", 0))
        if "actual" in mt or "revenue" in mt:
            bu_map[bu]["actual"] = val
        elif "budget" in mt or "plan" in mt:
            bu_map[bu]["budget"] = val

    return {"data": list(bu_map.values()), "demo": False}


# ── AI Insights ───────────────────────────────────────────────────────────────

DEMO_KPI_INSIGHT = (
    "Generation assets are outperforming targets with LYB Availability at 93.5% and Yandin Capacity "
    "Factor at 40.1%, driven by favourable wind conditions and successful planned maintenance. "
    "Retail metrics are the primary concern: NPS at 22 (target 25, -12%) and Churn at 19.8% (target 18%) "
    "are trending adversely, and Customer Acquisition Cost has triggered an anomaly at $185 vs $170 target. "
    "**Priority actions:** (1) ELT to review Retail NPS recovery plan with fortnightly tracking dashboard; "
    "(2) CMO to present CAC reduction strategy to CFO by end of week."
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
        print(f"[SQL/KPI slow] {e}")
        return []


@router.get("/api/kpi/ai_insights")
async def kpi_ai_insights():
    """AI narrative for current KPI performance via ai_query."""
    rows = _run_sql(f"""
        SELECT kpi_name, business_unit,
               ROUND(CAST(value AS DOUBLE), 2) as v, unit,
               ROUND(CAST(target AS DOUBLE), 2) as t,
               ROUND((CAST(value AS DOUBLE) - CAST(target AS DOUBLE))
                 / NULLIF(ABS(CAST(target AS DOUBLE)), 0) * 100, 1) as pct,
               is_anomaly
        FROM {CATALOG}.eds_synthetic.kpi_timeseries
        WHERE period = (SELECT MAX(period) FROM {CATALOG}.eds_synthetic.kpi_timeseries)
        ORDER BY business_unit, kpi_name
    """)

    use_demo = not rows
    kpis = DEMO_KPIS if use_demo else [
        {
            "kpi_name": r["kpi_name"], "business_unit": r.get("business_unit", ""),
            "value": float(r.get("v", 0)), "unit": r.get("unit", ""),
            "target": float(r.get("t", 0)),
            "pct_vs_target": float(r.get("pct") or 0),
            "is_anomaly": str(r.get("is_anomaly", "")).lower() in ("true", "1"),
        }
        for r in rows
    ]

    below = [k for k in kpis if k["pct_vs_target"] < 0]
    anomalies = [k["kpi_name"] for k in kpis if k.get("is_anomaly")]
    above = [k for k in kpis if k["pct_vs_target"] >= 0]

    below_summary = [(k["kpi_name"], f"{k['pct_vs_target']:+.1f}%") for k in below[:5]]
    prompt = (
        f"You are Alinta Energy's KPI Intelligence Agent. Analysing {len(kpis)} KPIs: "
        f"{len(above)} meeting or exceeding target, {len(below)} below target. "
        f"Below-target KPIs: {below_summary}. "
        f"Anomalies detected: {anomalies or ['none']}. "
        "Provide a 3-sentence executive narrative covering the dominant performance theme, "
        "the most critical concern, and the single most important leadership action. "
        "Be commercially direct and avoid generic statements."
    ).replace("'", "''")

    result = _run_sql_slow(f"SELECT ai_query('databricks-claude-sonnet-4-6', '{prompt}') as insight")
    if result and result[0].get("insight"):
        return {"insight": str(result[0]["insight"]), "demo": False}

    return {"insight": DEMO_KPI_INSIGHT, "demo": True}
