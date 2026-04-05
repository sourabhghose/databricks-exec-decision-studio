"""GET /api/documents — Document library from eds_synthetic.documents with demo fallback."""

import requests
from fastapi import APIRouter
from server.config import CATALOG, get_token, get_warehouse_id, get_workspace_url

router = APIRouter()

# All 22 documents (15 txt + 7 binary rich docs)
DEMO_DOCUMENTS = [
    {"doc_id": "DOC-001", "title": "FY2025 Group Strategy Review", "doc_type": "strategy", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Group", "effective_date": "2024-07-01", "author": "Group Strategy", "format": "txt"},
    {"doc_id": "DOC-002", "title": "Board Paper: Loy Yang B Transition", "doc_type": "board_paper", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Generation", "effective_date": "2024-09-15", "author": "Board / COO", "format": "txt"},
    {"doc_id": "DOC-003", "title": "FY2025 Half Year Financial Results", "doc_type": "financial_report", "classification": "CONFIDENTIAL", "access_tier_level": 2, "business_area": "Group", "effective_date": "2025-02-28", "author": "CFO Office", "format": "txt"},
    {"doc_id": "DOC-004", "title": "Competitive Intelligence Report", "doc_type": "competitive_intel", "classification": "CONFIDENTIAL", "access_tier_level": 2, "business_area": "Group", "effective_date": "2025-01-10", "author": "Strategy Team", "format": "txt"},
    {"doc_id": "DOC-005", "title": "ESG & Climate Risk Report FY2024", "doc_type": "risk_register", "classification": "CONFIDENTIAL", "access_tier_level": 1, "business_area": "Group", "effective_date": "2024-10-01", "author": "Sustainability Office", "format": "txt"},
    {"doc_id": "DOC-006", "title": "WA Renewables — Yandin Stage 2", "doc_type": "board_paper", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Generation", "effective_date": "2024-11-01", "author": "COO / Projects", "format": "txt"},
    {"doc_id": "DOC-007", "title": "Enterprise Risk Management Framework", "doc_type": "risk_register", "classification": "CONFIDENTIAL", "access_tier_level": 2, "business_area": "Group", "effective_date": "2024-07-01", "author": "CRO Office", "format": "txt"},
    {"doc_id": "DOC-008", "title": "WEM Capacity Mechanism Submission", "doc_type": "regulatory", "classification": "INTERNAL", "access_tier_level": 3, "business_area": "Regulatory", "effective_date": "2024-08-15", "author": "Regulatory Affairs", "format": "txt"},
    {"doc_id": "DOC-009", "title": "FY2026 Budget Paper", "doc_type": "financial_report", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Group", "effective_date": "2025-03-01", "author": "CFO Office", "format": "txt"},
    {"doc_id": "DOC-010", "title": "Cybersecurity & OT Security Update", "doc_type": "board_paper", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Technology", "effective_date": "2024-12-01", "author": "CISO", "format": "txt"},
    {"doc_id": "DOC-011", "title": "Retail Transformation Q2 FY25", "doc_type": "strategy", "classification": "CONFIDENTIAL", "access_tier_level": 2, "business_area": "Retail", "effective_date": "2025-01-15", "author": "CMO / Retail", "format": "txt"},
    {"doc_id": "DOC-012", "title": "People & Culture Strategy FY25-27", "doc_type": "strategy", "classification": "INTERNAL", "access_tier_level": 3, "business_area": "Corporate", "effective_date": "2024-09-01", "author": "CHRO", "format": "txt"},
    {"doc_id": "DOC-013", "title": "Trading & Hedging Strategy Review", "doc_type": "strategy", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Trading", "effective_date": "2024-10-15", "author": "CRO / Trading", "format": "txt"},
    {"doc_id": "DOC-014", "title": "Board Skills Matrix & Governance", "doc_type": "board_paper", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Governance", "effective_date": "2024-07-30", "author": "Company Secretary", "format": "txt"},
    {"doc_id": "DOC-015", "title": "Capital Allocation Framework", "doc_type": "financial_report", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Group", "effective_date": "2024-11-15", "author": "CFO Office", "format": "txt"},
    {"doc_id": "DOC-016", "title": "Generation Asset Performance FY25", "doc_type": "financial_report", "classification": "CONFIDENTIAL", "access_tier_level": 2, "business_area": "Generation", "effective_date": "2025-01-31", "author": "COO / Generation", "format": "pdf"},
    {"doc_id": "DOC-017", "title": "Retail Portfolio Analytics Q2 FY25", "doc_type": "financial_report", "classification": "CONFIDENTIAL", "access_tier_level": 2, "business_area": "Retail", "effective_date": "2025-01-31", "author": "CMO / Retail Analytics", "format": "pdf"},
    {"doc_id": "DOC-018", "title": "ESG Metrics & Net Zero Roadmap FY25", "doc_type": "risk_register", "classification": "CONFIDENTIAL", "access_tier_level": 2, "business_area": "Sustainability", "effective_date": "2024-12-31", "author": "Sustainability Office", "format": "pdf"},
    {"doc_id": "DOC-019", "title": "FY2026 Strategic Plan Board Presentation", "doc_type": "board_paper", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Group", "effective_date": "2025-03-01", "author": "CEO / Group Strategy", "format": "pptx"},
    {"doc_id": "DOC-020", "title": "WA Renewables Investment Briefing", "doc_type": "board_paper", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Generation", "effective_date": "2025-02-15", "author": "COO / Projects", "format": "pptx"},
    {"doc_id": "DOC-021", "title": "FY2025 Half Year Financial Model", "doc_type": "financial_report", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Group", "effective_date": "2025-02-28", "author": "CFO Office", "format": "xlsx"},
    {"doc_id": "DOC-022", "title": "Trading & Hedging Portfolio Workbook", "doc_type": "financial_report", "classification": "RESTRICTED", "access_tier_level": 1, "business_area": "Trading", "effective_date": "2025-02-28", "author": "CRO / Trading", "format": "xlsx"},
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
        print(f"[SQL/docs] {e}")
        return []


@router.get("/api/documents")
async def get_documents():
    rows = _run_sql(f"""
        SELECT doc_id, title, doc_type, classification, access_tier_level,
               business_area, CAST(effective_date AS STRING) as effective_date, author
        FROM {CATALOG}.eds_synthetic.documents
        ORDER BY access_tier_level ASC, doc_id ASC
    """)

    if not rows:
        return {"data": DEMO_DOCUMENTS, "demo": True}

    # Merge with known format info (not stored in eds_synthetic.documents)
    FORMAT_MAP = {d["doc_id"]: d["format"] for d in DEMO_DOCUMENTS}
    out = []
    for r in rows:
        did = r.get("doc_id", "")
        out.append({
            "doc_id": did,
            "title": r.get("title", ""),
            "doc_type": r.get("doc_type", ""),
            "classification": r.get("classification", ""),
            "access_tier_level": int(r.get("access_tier_level") or 4),
            "business_area": r.get("business_area", ""),
            "effective_date": r.get("effective_date", ""),
            "author": r.get("author", ""),
            "format": FORMAT_MAP.get(did, "txt"),
        })

    return {"data": out, "demo": False}
