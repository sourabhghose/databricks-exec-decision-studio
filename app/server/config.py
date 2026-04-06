"""
Authentication and configuration helpers.
Dual-mode: service principal in Databricks Apps, SDK auth locally.
"""

import os

IS_DATABRICKS_APP = bool(os.environ.get("DATABRICKS_APP_NAME"))

CATALOG = "ausnet_process_intel_catalog"
LLM_ENDPOINT = "databricks-claude-sonnet-4-6"
VS_INDEX = f"{CATALOG}.eds_vectors.document_chunks_index"

TIER_MAP = {
    "Board Director / CEO": 1,
    "CFO / C-Suite": 1,
    "Executive Leadership Team": 2,
    "Senior Management": 3,
    "All Staff": 4,
}

DOC_TITLES = {
    "DOC-001": "FY2025 Group Strategy Review",
    "DOC-002": "Loy Yang B Transition Options",
    "DOC-003": "1H FY25 Financial Results",
    "DOC-004": "Competitive Intelligence Report",
    "DOC-005": "ESG & Climate Risk Report",
    "DOC-006": "Yandin Stage 2 Investment Case",
    "DOC-007": "Enterprise Risk Management",
    "DOC-008": "WEM Capacity Mechanism Submission",
    "DOC-009": "FY2026 Budget Paper",
    "DOC-010": "Cybersecurity & OT Security Update",
    "DOC-011": "Retail Transformation Q2 FY25",
    "DOC-012": "People & Culture Strategy",
    "DOC-013": "Trading & Hedging Strategy",
    "DOC-014": "Board Skills & Governance",
    "DOC-015": "Capital Allocation Framework",
}

_COMPLETION_RULE = (
    " CRITICAL: You have a limited output budget. "
    "Write concisely. Complete every sentence and every bullet point fully before moving to the next. "
    "If you are near the end of your budget, wrap up with a brief concluding sentence — "
    "never stop mid-sentence or mid-bullet."
)

AGENT_PROMPTS = {
    "doc_qa": (
        "You are Alinta Energy's Document Intelligence Agent. "
        "Answer precisely using the retrieved context. Cite sources as [DOC-XXX]. "
        "Be executive-grade and concise." + _COMPLETION_RULE
    ),
    "strategic_gap": (
        "You are Alinta Energy's Strategic Gap Advisor. "
        "Identify gaps, blind spots, and risks in the strategy. Be commercially candid. "
        "Cover 3–5 key gaps with concise commentary each." + _COMPLETION_RULE
    ),
    "competitive": (
        "You are Alinta Energy's Competitive Intelligence Advisor. "
        "Analyse market position vs Origin Energy, AGL, and others. "
        "Be concise — use a table or short bullets." + _COMPLETION_RULE
    ),
    "briefing": (
        "You are Alinta Energy's Executive Briefing Agent. "
        "Produce structured briefings with headings, bullets, and citations [DOC-XXX]. "
        "Keep each section to 3–4 bullets maximum." + _COMPLETION_RULE
    ),
    "kpi_monitor": (
        "You are Alinta Energy's KPI Monitor. "
        "Analyse KPI data and identify anomalies, trends, and recommended actions. "
        "Limit to top 5 insights." + _COMPLETION_RULE
    ),
    "scenario": (
        "You are Alinta Energy's Strategic Scenario Advisor.\n"
        "Given the decision below, generate exactly 3 scenarios: Bear, Base, Bull.\n"
        "Return ONLY valid JSON — no markdown fences, no prose outside the JSON object.\n\n"
        "Required schema:\n"
        '{\n  "decision": "<restate the decision concisely>",\n'
        '  "scenarios": [\n'
        '    {\n      "label": "Bear",\n      "probability": <float 0-1>,\n'
        '      "headline": "<one-sentence worst-case outcome>",\n'
        '      "key_assumptions": ["<assumption>"],\n'
        '      "kpi_impact": {\n'
        '        "<kpi_name>": {"baseline": <float>, "projected": <float>, "unit": "<$M|%|MW>"}\n'
        '      },\n      "risk_factors": ["<risk>"],\n'
        '      "strategic_rationale": "<2-3 sentences>"\n    },\n'
        '    { "label": "Base", ... },\n    { "label": "Bull", ... }\n  ],\n'
        '  "recommended": "Bear"|"Base"|"Bull",\n'
        '  "recommendation_rationale": "<2 sentences>"\n}\n\n'
        "Rules: probabilities must sum to 1.0. Include 3-4 key_assumptions, "
        "3-5 kpi_impact entries using KPI names from the data context, "
        "and 2-3 risk_factors per scenario. Be commercially specific to Alinta Energy."
    ),
    "scenario_drilldown": (
        "You are Alinta Energy's Strategic Scenario Advisor. "
        "The board has selected the {branch} scenario for the decision: {decision}. "
        "Produce a structured drill-down with these sections:\n\n"
        "## Implementation Roadmap\n"
        "List 5 concrete implementation steps with owners and timelines.\n\n"
        "## Risk Mitigations\n"
        "For each risk factor in this scenario, provide a specific mitigation action.\n\n"
        "## 90-Day Board Actions\n"
        "List exactly 3 actions the board must take in the next 90 days.\n\n"
        "## Key Metrics to Track\n"
        "List 3-4 leading indicators the board should monitor monthly.\n\n"
        "Be executive-grade, commercially specific, bullet points under each heading."
        + _COMPLETION_RULE
    ),
}

# ── Auth ─────────────────────────────────────────────────────────────────────
_wh_cache: dict = {}
_sdk_client = None  # WorkspaceClient singleton — SDK handles token refresh internally


def _get_sdk_client():
    global _sdk_client
    if _sdk_client is None:
        try:
            from databricks.sdk import WorkspaceClient
            _sdk_client = WorkspaceClient()
        except Exception as e:
            print(f"[EDS] SDK init failed: {e}")
    return _sdk_client


def get_token() -> str:
    """Get a valid bearer token for Databricks API calls.

    For PATs (DATABRICKS_TOKEN env var) — returned directly (long-lived).
    For M2M OAuth (Databricks Apps SP) — always fetched via SDK so the SDK
    can handle automatic refresh before the 1-hour expiry.
    """
    # PAT: long-lived, return directly
    pat = os.environ.get("DATABRICKS_TOKEN", "")
    if pat:
        return pat

    # M2M OAuth: ask SDK each time — it caches with proper TTL internally
    try:
        w = _get_sdk_client()
        if w is None:
            return ""
        auth = w.config.authenticate()
        if auth:
            tok = auth.get("Authorization", "").replace("Bearer ", "")
            if tok:
                return tok
    except Exception as e:
        print(f"[EDS] SDK auth failed: {e}")

    return ""


def get_workspace_url() -> str:
    """Return workspace URL with https:// prefix."""
    raw = os.environ.get(
        "DATABRICKS_HOST",
        "https://fevm-ausnet-process-intel.cloud.databricks.com",
    )
    return raw if raw.startswith("http") else f"https://{raw}"


FALLBACK_WAREHOUSE_ID = "33baaa9523773520"  # Process Intelligence Warehouse


def get_warehouse_id() -> str:
    """Discover or return cached SQL warehouse ID."""
    if _wh_cache.get("id"):
        return _wh_cache["id"]

    # 1. Explicit env var (set via app.yaml valueFrom or manually)
    wh = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
    if wh and wh != "auto":
        _wh_cache["id"] = wh
        return wh

    tok = get_token()
    if not tok:
        _wh_cache["id"] = FALLBACK_WAREHOUSE_ID
        return FALLBACK_WAREHOUSE_ID

    import requests

    try:
        r = requests.get(
            f"{get_workspace_url()}/api/2.0/sql/warehouses",
            headers={"Authorization": f"Bearer {tok}"},
            timeout=10,
        )
        if r.ok:
            whs = r.json().get("warehouses", [])
            # Prefer running, accept stopped (they start on first query)
            priority = ["RUNNING", "STARTING", "STOPPED"]
            for state in priority:
                match = [w for w in whs if w.get("state") == state]
                if match:
                    _wh_cache["id"] = match[0]["id"]
                    print(f"[EDS] Warehouse: {_wh_cache['id']} ({state})")
                    return _wh_cache["id"]
    except Exception as e:
        print(f"[EDS] Warehouse discovery: {e}")

    # 2. Hardcoded fallback
    _wh_cache["id"] = FALLBACK_WAREHOUSE_ID
    return FALLBACK_WAREHOUSE_ID
