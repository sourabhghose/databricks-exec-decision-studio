"""POST /api/briefing — AI-generated executive briefing using LLM."""

import json
import time
import requests
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

from server.config import CATALOG, LLM_ENDPOINT, get_token, get_warehouse_id, get_workspace_url
from server.routes.kpi import DEMO_KPIS
from server.routes.risks import DEMO_RISKS
from server.routes.decisions import DEMO_DECISIONS  # type: ignore


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
        print(f"[SQL/briefing] {e}")
        return []


def _get_live_kpis() -> list:
    rows = _run_sql(f"""
        SELECT kpi_name, business_unit,
               ROUND(CAST(value AS DOUBLE), 2) as value, unit,
               ROUND(CAST(target AS DOUBLE), 2) as target,
               ROUND((CAST(value AS DOUBLE) - CAST(target AS DOUBLE))
                 / NULLIF(ABS(CAST(target AS DOUBLE)), 0) * 100, 1) as pct,
               is_anomaly
        FROM {CATALOG}.eds_synthetic.kpi_timeseries
        WHERE period = (SELECT MAX(period) FROM {CATALOG}.eds_synthetic.kpi_timeseries)
        ORDER BY business_unit, kpi_name LIMIT 20
    """)
    if not rows:
        return []
    out = []
    for r in rows:
        pct = float(r.get("pct") or 0)
        status = "Green" if abs(pct) < 5 else ("Red" if pct < -10 else "Yellow")
        out.append({
            "kpi_name": r["kpi_name"],
            "business_unit": r.get("business_unit", ""),
            "value": float(r.get("value", 0)),
            "unit": r.get("unit", ""),
            "target": float(r.get("target", 0)),
            "pct_vs_target": pct,
            "status": status,
            "is_anomaly": str(r.get("is_anomaly", "")).lower() in ("true", "1"),
        })
    return out


def _get_live_risks() -> list:
    return _run_sql(f"""
        SELECT risk_id, category, description, likelihood, consequence,
               rating, risk_score, owner, mitigation, status
        FROM {CATALOG}.eds_synthetic.risk_register
        ORDER BY risk_score DESC LIMIT 10
    """)

router = APIRouter()


class BriefingRequest(BaseModel):
    role: str = "Board Director / CEO"
    focus_areas: List[str] = ["kpis", "risks", "decisions", "strategy"]
    briefing_type: str = "weekly"  # weekly | board | investor | crisis


BRIEFING_TYPES = {
    "weekly": "Weekly Management Briefing",
    "board": "Board Meeting Pre-Read",
    "investor": "Investor Relations Briefing",
    "crisis": "Crisis / Issues Management Brief",
}


def _build_context(focus_areas: list) -> str:
    """Assemble structured data context for the LLM. Tries live SQL, falls back to demo."""
    sections = []

    if "kpis" in focus_areas:
        live_kpis = _get_live_kpis()
        kpis_to_use = live_kpis if live_kpis else DEMO_KPIS
        kpi_lines = []
        for k in kpis_to_use:
            status_emoji = "✅" if k["status"] == "Green" else ("⚠️" if k["status"] == "Yellow" else "🔴")
            anomaly = " [ANOMALY]" if k.get("is_anomaly") else ""
            pct = k.get("pct_vs_target", 0)
            kpi_lines.append(
                f"  {status_emoji} {k['kpi_name']} ({k['business_unit']}): "
                f"{k['value']} {k['unit']} vs target {k['target']} {k['unit']} "
                f"({pct:+.1f}%){anomaly}"
            )
        sections.append("## KPI SNAPSHOT (Latest Period)\n" + "\n".join(kpi_lines))

    if "risks" in focus_areas:
        live_risks = _get_live_risks()
        risks_to_use = live_risks if live_risks else DEMO_RISKS
        top_risks = sorted(risks_to_use, key=lambda r: float(r.get("risk_score", 0) or 0), reverse=True)[:5]
        risk_lines = []
        for r in top_risks:
            risk_lines.append(
                f"  [{r['rating']}] {r['risk_id']} — {r['category'].upper()}: "
                f"{r['description'][:120]}... Owner: {r['owner']}"
            )
        sections.append("## TOP ENTERPRISE RISKS\n" + "\n".join(risk_lines))

    if "decisions" in focus_areas:
        recent = DEMO_DECISIONS[:4]
        dec_lines = []
        for d in recent:
            dec_lines.append(
                f"  {d['decision_id']} [{d['committee']}] {d['decision_date']}: "
                f"{d['description'][:100]}... Status: {d['implementation_status']}"
            )
        sections.append("## RECENT DECISIONS\n" + "\n".join(dec_lines))

    return "\n\n".join(sections)


def _stream_llm(prompt: str, role: str, briefing_label: str):
    """Stream SSE tokens from the Databricks LLM endpoint."""
    tok = get_token()
    url = get_workspace_url()
    start = time.time()

    system_prompt = (
        f"You are Alinta Energy's Executive Intelligence Assistant, producing a {briefing_label} "
        f"for a {role}. Write in a precise, executive-grade style. Use clear headings (##), "
        "bullet points, and bold key numbers. Include a 3-sentence executive summary at the top, "
        "then detailed sections, and end with 3 recommended actions for leadership. "
        "Do NOT include boilerplate disclaimers. Be commercially candid."
    )

    if not tok:
        # Fallback — no token available
        def demo_stream():
            demo = (
                f"## {briefing_label}\n\n"
                "**Executive Summary**\n\n"
                "Alinta Energy delivered a mixed performance in the current period. "
                "Generation assets continue to outperform availability targets, while "
                "retail metrics show concerning churn trends requiring urgent management attention. "
                "The enterprise risk profile remains elevated, with regulatory and cyber risks at Critical.\n\n"
                "## KPI Highlights\n\n"
                "- **LYB Plant Availability**: 93.5% vs 93.0% target (+0.5%) ✅\n"
                "- **Retail Customer NPS**: 22 vs 25 target (-12%) ⚠️\n"
                "- **Group EBITDA Margin**: 18.2% vs 18.0% target (+1.1%) ✅\n"
                "- **Customer Acquisition Cost**: $185 vs $170 target (-8.8%) 🔴 ANOMALY\n\n"
                "## Top Risks\n\n"
                "1. **WEM Capacity Mechanism** [Critical] — Policy uncertainty threatening generation economics\n"
                "2. **Loy Yang B Plant Risk** [Critical] — Ageing asset, outage probability rising\n"
                "3. **Cyber / OT Security** [High] — ISO 27001 uplift programme underway\n\n"
                "## Recommended Actions\n\n"
                "1. Accelerate Yandin Stage 2 FID to secure renewable pipeline before FY26\n"
                "2. Retail NPS recovery plan to be escalated to ELT with fortnightly tracking\n"
                "3. CFO to present FY26 debt refinancing options at next Board meeting\n"
            )
            for chunk in demo.split(" "):
                data = json.dumps({"type": "token", "content": chunk + " "})
                yield f"data: {data}\n\n"
            latency = int((time.time() - start) * 1000)
            yield f"data: {json.dumps({'type': 'done', 'latency_ms': latency})}\n\n"

        return StreamingResponse(demo_stream(), media_type="text/event-stream")

    payload = {
        "model": LLM_ENDPOINT,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1800,
        "temperature": 0.3,
        "stream": True,
    }

    def token_stream():
        try:
            with requests.post(
                f"{url}/serving-endpoints/{LLM_ENDPOINT}/invocations",
                headers={
                    "Authorization": f"Bearer {tok}",
                    "Content-Type": "application/json",
                },
                json=payload,
                stream=True,
                timeout=120,
            ) as resp:
                if not resp.ok:
                    err = json.dumps({"type": "token", "content": f"[LLM error {resp.status_code}]"})
                    yield f"data: {err}\n\n"
                    return

                for line in resp.iter_lines():
                    if not line:
                        continue
                    text = line.decode("utf-8") if isinstance(line, bytes) else line
                    if text.startswith("data: "):
                        chunk_str = text[6:]
                        if chunk_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(chunk_str)
                            content = (
                                chunk.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content", "")
                            )
                            if content:
                                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                        except Exception:
                            pass

        except Exception as e:
            yield f"data: {json.dumps({'type': 'token', 'content': f'[Error: {e}]'})}\n\n"

        latency = int((time.time() - start) * 1000)
        yield f"data: {json.dumps({'type': 'done', 'latency_ms': latency})}\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")


@router.post("/api/briefing/stream")
async def generate_briefing(req: BriefingRequest):
    briefing_label = BRIEFING_TYPES.get(req.briefing_type, "Executive Briefing")
    context = _build_context(req.focus_areas)

    prompt = (
        f"Generate a comprehensive {briefing_label} for an Alinta Energy {req.role}.\n\n"
        f"Focus areas requested: {', '.join(req.focus_areas)}\n\n"
        f"Current data context:\n{context}\n\n"
        "Produce the full briefing now."
    )

    return _stream_llm(prompt, req.role, briefing_label)
