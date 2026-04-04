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

AGENT_PROMPTS = {
    "doc_qa": (
        "You are Alinta Energy's Document Intelligence Agent. "
        "Answer precisely using the retrieved context. Cite sources as [DOC-XXX]. "
        "Be executive-grade and concise."
    ),
    "strategic_gap": (
        "You are Alinta Energy's Strategic Gap Advisor. "
        "Identify gaps, blind spots, and risks in the strategy. Be commercially candid."
    ),
    "competitive": (
        "You are Alinta Energy's Competitive Intelligence Advisor. "
        "Analyse market position vs Origin Energy, AGL, and others."
    ),
    "briefing": (
        "You are Alinta Energy's Executive Briefing Agent. "
        "Produce structured briefings with headings, bullets, and citations [DOC-XXX]."
    ),
    "kpi_monitor": (
        "You are Alinta Energy's KPI Monitor. "
        "Analyse KPI data and identify anomalies, trends, and recommended actions."
    ),
}

# ── Token cache ──────────────────────────────────────────────────────────────
_token_cache: dict = {}
_wh_cache: dict = {}


def get_token() -> str:
    """Get bearer token for Databricks API calls."""
    if _token_cache.get("val") is not None:
        return _token_cache["val"]

    tok = os.environ.get("DATABRICKS_TOKEN", "")
    if not tok:
        try:
            from databricks.sdk import WorkspaceClient

            w = WorkspaceClient()
            # authenticate() returns a dict like {"Authorization": "Bearer ..."}
            auth = w.config.authenticate()
            if auth:
                tok = auth.get("Authorization", "").replace("Bearer ", "")
        except Exception as e:
            print(f"[EDS] SDK auth failed: {e}")

    _token_cache["val"] = tok or ""
    print(f"[EDS] Token ready: {bool(_token_cache['val'])}")
    return _token_cache["val"]


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
