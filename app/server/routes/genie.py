"""
POST /api/genie/query  — AI/BI Genie Conversation API wrapper

Translates natural-language questions into SQL via a Genie Space,
then returns the generated SQL, narrative, and result rows.

Demo fallback: if GENIE_SPACE_ID is not set (or Genie call fails),
returns realistic hardcoded data so the tab is always functional.
"""

import os
import time

import requests
from fastapi import APIRouter
from pydantic import BaseModel

from server.config import get_token, get_workspace_url

router = APIRouter()

POLL_INTERVAL = 2   # seconds between status checks
POLL_MAX = 30       # max attempts (60s timeout)


# ── Request / Response models ────────────────────────────────────────────────

class GenieRequest(BaseModel):
    question: str
    conversation_id: str | None = None


class GenieResponse(BaseModel):
    conversation_id: str
    message_id: str
    narrative: str
    sql: str
    columns: list[str]
    rows: list[list]
    demo: bool = False


# ── Demo fallback data ────────────────────────────────────────────────────────

_DEMO_BY_KEYWORD: list[tuple[list[str], GenieResponse]] = [
    (
        ["kpi", "below target", "target", "generation", "anomal", "churn", "trend"],
        GenieResponse(
            conversation_id="demo-conv-kpi",
            message_id="demo-msg-kpi",
            narrative=(
                "Three KPIs are currently below target. Generation Availability is at 91.2% "
                "against a 93.0% target, Retail Churn Rate is 18.4% against a 15.0% target, "
                "and Solar Yield at Yandin is 94.1% against a 95.0% target."
            ),
            sql=(
                "SELECT kpi_name, business_unit, current_value, target_value, unit, status\n"
                "FROM ausnet_process_intel_catalog.eds_synthetic.kpi_timeseries\n"
                "WHERE status = 'Below Target'\n"
                "ORDER BY (current_value - target_value) ASC\n"
                "LIMIT 10"
            ),
            columns=["kpi_name", "business_unit", "current_value", "target_value", "unit", "status"],
            rows=[
                ["Generation Availability", "Generation", 91.2, 93.0, "%", "Below Target"],
                ["Retail Churn Rate", "Retail", 18.4, 15.0, "%", "Below Target"],
                ["Solar Yield — Yandin", "Renewables", 94.1, 95.0, "%", "Below Target"],
            ],
            demo=True,
        ),
    ),
    (
        ["risk", "score", "top", "critical", "high", "cro", "owner"],
        GenieResponse(
            conversation_id="demo-conv-risk",
            message_id="demo-msg-risk",
            narrative=(
                "The five highest-scoring enterprise risks are Energy Transition Risk (score 24), "
                "Cybersecurity & OT Risk (score 20), Regulatory & Policy Risk (score 20), "
                "Wholesale Price Volatility (score 16), and Climate Physical Risk (score 15). "
                "Two are rated Critical and three are High."
            ),
            sql=(
                "SELECT risk_name, category, likelihood, consequence, risk_score, rating, owner\n"
                "FROM ausnet_process_intel_catalog.eds_synthetic.risk_register\n"
                "ORDER BY risk_score DESC\n"
                "LIMIT 5"
            ),
            columns=["risk_name", "category", "likelihood", "consequence", "risk_score", "rating", "owner"],
            rows=[
                ["Energy Transition Risk", "Strategic", 4, 6, 24, "Critical", "CEO"],
                ["Cybersecurity & OT Risk", "Operational", 4, 5, 20, "Critical", "CIO"],
                ["Regulatory & Policy Risk", "Compliance", 4, 5, 20, "High", "General Counsel"],
                ["Wholesale Price Volatility", "Financial", 4, 4, 16, "High", "CFO"],
                ["Climate Physical Risk", "Environmental", 3, 5, 15, "High", "CRO"],
            ],
            demo=True,
        ),
    ),
    (
        ["ebitda", "financial", "revenue", "profit", "business unit", "fy2025", "fy25"],
        GenieResponse(
            conversation_id="demo-conv-fin",
            message_id="demo-msg-fin",
            narrative=(
                "FY2025 EBITDA totals $1.42B across all business units. Generation leads at $680M, "
                "followed by Renewables at $390M, Retail at $210M, and Corporate & Other at $140M. "
                "Renewables EBITDA is 18% above the FY2025 budget."
            ),
            sql=(
                "SELECT business_unit, SUM(ebitda_m) AS total_ebitda_m,\n"
                "       SUM(revenue_m) AS total_revenue_m, fiscal_year\n"
                "FROM ausnet_process_intel_catalog.eds_synthetic.financial_data\n"
                "WHERE fiscal_year = 'FY2025'\n"
                "GROUP BY business_unit, fiscal_year\n"
                "ORDER BY total_ebitda_m DESC"
            ),
            columns=["business_unit", "total_ebitda_m", "total_revenue_m", "fiscal_year"],
            rows=[
                ["Generation", 680, 1420, "FY2025"],
                ["Renewables", 390, 820, "FY2025"],
                ["Retail", 210, 1650, "FY2025"],
                ["Corporate & Other", 140, 95, "FY2025"],
            ],
            demo=True,
        ),
    ),
    (
        ["action", "overdue", "due", "owner"],
        GenieResponse(
            conversation_id="demo-conv-action",
            message_id="demo-msg-action",
            narrative=(
                "There are 4 overdue action items. The highest-priority is the Cybersecurity OT Audit "
                "owned by the CIO (due 2025-03-31). Three others relate to the Retail Transformation "
                "program and ESG reporting deadlines."
            ),
            sql=(
                "SELECT title, owner, due_date, priority, status\n"
                "FROM ausnet_process_intel_catalog.eds_actions.action_items\n"
                "WHERE due_date < current_date() AND status != 'Completed'\n"
                "ORDER BY due_date ASC\n"
                "LIMIT 10"
            ),
            columns=["title", "owner", "due_date", "priority", "status"],
            rows=[
                ["Cybersecurity OT Audit", "CIO", "2025-03-31", "Critical", "In Progress"],
                ["Retail Pricing Model Review", "CCO", "2025-03-28", "High", "Not Started"],
                ["ESG Reporting — CER Submission", "CRO", "2025-03-25", "High", "In Progress"],
                ["LYB Transition Plan Sign-off", "CEO", "2025-03-15", "Critical", "In Progress"],
            ],
            demo=True,
        ),
    ),
    (
        ["decision", "board", "progress", "status", "last 6", "register"],
        GenieResponse(
            conversation_id="demo-conv-dec",
            message_id="demo-msg-dec",
            narrative=(
                "There are 3 decisions currently In Progress. The Yandin Stage 2 investment decision "
                "is tracking on schedule, the Loy Yang B retirement timeline is under board review, "
                "and the FY2026 capital allocation framework is pending CFO sign-off."
            ),
            sql=(
                "SELECT title, decision_type, decision_date, status, owner, implementation_progress\n"
                "FROM ausnet_process_intel_catalog.eds_actions.decision_register\n"
                "WHERE status = 'In Progress'\n"
                "ORDER BY decision_date DESC\n"
                "LIMIT 10"
            ),
            columns=["title", "decision_type", "decision_date", "status", "owner", "implementation_progress"],
            rows=[
                ["Yandin Stage 2 Investment", "Strategic", "2025-02-14", "In Progress", "Board", 45],
                ["Loy Yang B Retirement Timeline", "Operational", "2025-01-20", "In Progress", "CEO", 30],
                ["FY2026 Capital Allocation", "Financial", "2025-03-05", "In Progress", "CFO", 60],
            ],
            demo=True,
        ),
    ),
]


def _demo_response(question: str) -> GenieResponse:
    """Return the best-matching demo response for the given question."""
    q_lower = question.lower()
    for keywords, response in _DEMO_BY_KEYWORD:
        if any(kw in q_lower for kw in keywords):
            return response
    # Default: return KPI demo
    return _DEMO_BY_KEYWORD[0][1]


# ── Genie Conversation API helpers ────────────────────────────────────────────

def _headers(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


def _start_conversation(tok: str, url: str, space_id: str, question: str) -> tuple[str, str]:
    """Start a new Genie conversation. Returns (conversation_id, message_id)."""
    resp = requests.post(
        f"{url}/api/2.0/genie/spaces/{space_id}/start-conversation",
        headers=_headers(tok),
        json={"content": question},
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"start-conversation failed: {resp.status_code} {resp.text[:300]}")
    data = resp.json()
    return data["conversation_id"], data["message_id"]


def _continue_conversation(
    tok: str, url: str, space_id: str, conversation_id: str, question: str
) -> str:
    """Send a follow-up message. Returns message_id."""
    resp = requests.post(
        f"{url}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages",
        headers=_headers(tok),
        json={"content": question},
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"send-message failed: {resp.status_code} {resp.text[:300]}")
    return resp.json()["message_id"]


def _poll_message(
    tok: str, url: str, space_id: str, conversation_id: str, message_id: str
) -> dict:
    """Poll until message status is COMPLETED or FAILED. Returns the message dict."""
    for attempt in range(POLL_MAX):
        resp = requests.get(
            f"{url}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}",
            headers=_headers(tok),
            timeout=30,
        )
        if not resp.ok:
            raise RuntimeError(f"poll-message failed: {resp.status_code} {resp.text[:300]}")
        msg = resp.json()
        status = msg.get("status", "")
        if status == "COMPLETED":
            return msg
        if status == "FAILED":
            raise RuntimeError(f"Genie message failed: {msg.get('error', 'unknown error')}")
        time.sleep(POLL_INTERVAL)
    raise RuntimeError("Genie message timed out after 60s")


def _get_query_result(
    tok: str, url: str, space_id: str, conversation_id: str, message_id: str
) -> tuple[list[str], list[list]]:
    """Fetch query result rows. Returns (columns, rows)."""
    resp = requests.get(
        f"{url}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/query-result",
        headers=_headers(tok),
        timeout=30,
    )
    if not resp.ok:
        return [], []
    data = resp.json()
    try:
        sr = data["statement_response"]
        schema = sr["manifest"]["schema"]["columns"]
        columns = [c["name"] for c in schema]
        rows = sr.get("result", {}).get("data_array", [])
        return columns, rows
    except (KeyError, TypeError):
        return [], []


def _extract_narrative_and_sql(msg: dict) -> tuple[str, str]:
    """Extract narrative text and SQL query from Genie message attachments."""
    narrative = ""
    sql = ""
    for attachment in msg.get("attachments", []):
        if not narrative:
            text_block = attachment.get("text", {})
            if isinstance(text_block, dict):
                narrative = text_block.get("content", "")
            elif isinstance(text_block, str):
                narrative = text_block
        if not sql:
            query_block = attachment.get("query", {})
            if isinstance(query_block, dict):
                sql = query_block.get("query", "")
    return narrative, sql


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/api/genie/query", response_model=GenieResponse)
async def genie_query(req: GenieRequest) -> GenieResponse:
    """
    Send a natural-language question to the Genie Space and return results.

    Maintains conversation context when conversation_id is provided (follow-ups).
    Falls back to demo data if GENIE_SPACE_ID is not configured.
    """
    space_id = os.getenv("GENIE_SPACE_ID", "")
    tok = get_token()
    url = get_workspace_url()

    if not space_id or not tok:
        print(f"[genie] demo mode — space_id={'set' if space_id else 'missing'} tok={'set' if tok else 'missing'}")
        return _demo_response(req.question)

    try:
        # Start or continue conversation
        if req.conversation_id:
            conversation_id = req.conversation_id
            message_id = _continue_conversation(tok, url, space_id, conversation_id, req.question)
        else:
            conversation_id, message_id = _start_conversation(tok, url, space_id, req.question)

        # Poll for completion
        msg = _poll_message(tok, url, space_id, conversation_id, message_id)

        # Extract narrative + SQL
        narrative, sql = _extract_narrative_and_sql(msg)

        # Fetch result rows
        columns, rows = _get_query_result(tok, url, space_id, conversation_id, message_id)

        return GenieResponse(
            conversation_id=conversation_id,
            message_id=message_id,
            narrative=narrative or "Query completed successfully.",
            sql=sql,
            columns=columns,
            rows=rows[:50],  # cap at 50 rows
            demo=False,
        )

    except Exception as e:
        print(f"[genie] error: {e} — falling back to demo")
        demo = _demo_response(req.question)
        return GenieResponse(
            conversation_id=req.conversation_id or "demo-fallback",
            message_id="demo-fallback",
            narrative=f"[Live Genie unavailable: {e}]\n\n{demo.narrative}",
            sql=demo.sql,
            columns=demo.columns,
            rows=demo.rows,
            demo=True,
        )
