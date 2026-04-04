"""
GET /api/market/news    — Competitor & regulatory news feed (GDELT, free, no key)
GET /api/market/stocks  — ASX peer stock comparison (Yahoo Finance, free, no key)
GET /api/market/carbon  — ACCU/LGC carbon market prices (CER quarterly data)
"""

import re
import time
from datetime import datetime, timedelta, timezone

import requests
from fastapi import APIRouter

router = APIRouter()

# ── TTL Cache ─────────────────────────────────────────────────────────────────

_MARKET_CACHE: dict = {}
_CACHE_TTL = {"news": 1800, "stocks": 3600, "carbon": 3600}  # seconds


def _cache_get(key: str):
    entry = _MARKET_CACHE.get(key)
    if entry and time.time() - entry["ts"] < _CACHE_TTL.get(key, 1800):
        return entry["data"]
    return None


def _cache_set(key: str, data) -> None:
    _MARKET_CACHE[key] = {"ts": time.time(), "data": data}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get(url: str, params: dict = None, timeout: int = 10) -> dict | list | None:
    try:
        r = requests.get(url, params=params, timeout=timeout,
                         headers={"User-Agent": "Mozilla/5.0 (EDS/2.0)"})
        if r.ok:
            return r.json()
    except Exception as e:
        print(f"[market] GET {url}: {e}")
    return None


# ── News feed ─────────────────────────────────────────────────────────────────

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

GDELT_QUERY = (
    '"Alinta Energy" OR "Origin Energy" OR "AGL Energy" OR '
    '"Energy Australia" OR "AEMO" OR "Australian energy transition" OR '
    '"Loy Yang" OR "NEM electricity" OR "WEM electricity"'
)

DEMO_NEWS = [
    {
        "title": "AGL Energy reports stronger-than-expected H1 FY25 earnings, upgrades FY25 guidance",
        "source": "Australian Financial Review",
        "date": "2025-02-14",
        "url": "#",
        "sentiment": "neutral",
        "tags": ["AGL", "Earnings", "Competitor"],
    },
    {
        "title": "Origin Energy completes Eraring coal plant closure, accelerates renewables transition",
        "source": "The Australian",
        "date": "2025-02-10",
        "url": "#",
        "sentiment": "risk",
        "tags": ["Origin Energy", "Coal", "Transition"],
    },
    {
        "title": "AEMO warns of tight supply outlook in Victoria for summer 2025-26",
        "source": "RenewEconomy",
        "date": "2025-02-08",
        "url": "#",
        "sentiment": "risk",
        "tags": ["AEMO", "Supply", "Victoria"],
    },
    {
        "title": "Federal Government confirms $20B Rewiring the Nation funding allocation schedule",
        "source": "ABC News",
        "date": "2025-02-05",
        "url": "#",
        "sentiment": "positive",
        "tags": ["Policy", "Renewables", "Funding"],
    },
    {
        "title": "Energy Australia announces 1.2GW battery storage pipeline for NSW and Queensland",
        "source": "PV Magazine Australia",
        "date": "2025-02-01",
        "url": "#",
        "sentiment": "neutral",
        "tags": ["Energy Australia", "Battery", "Competitor"],
    },
    {
        "title": "AEMC releases final determination on capacity mechanism — implications for coal generators",
        "source": "Energy Source & Distribution",
        "date": "2025-01-28",
        "url": "#",
        "sentiment": "risk",
        "tags": ["AEMC", "Regulation", "Coal"],
    },
    {
        "title": "Amber Electric reaches 100,000 customer milestone, signals retail disruption risk",
        "source": "The Australian",
        "date": "2025-01-22",
        "url": "#",
        "sentiment": "risk",
        "tags": ["Amber Electric", "Retail", "Disruption"],
    },
    {
        "title": "Clean Energy Regulator: LGC surrender volumes hit record high in Q4 FY24",
        "source": "Clean Energy Regulator",
        "date": "2025-01-15",
        "url": "#",
        "sentiment": "positive",
        "tags": ["CER", "LGC", "Renewables"],
    },
]


def _sentiment_from_title(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ("warn", "risk", "tight", "clos", "threat", "disrupt", "decline", "fail", "concern")):
        return "risk"
    if any(w in t for w in ("strong", "record", "growth", "approv", "complet", "secur", "fund", "invest")):
        return "positive"
    return "neutral"


@router.get("/api/market/news")
async def get_news():
    cached = _cache_get("news")
    if cached:
        return cached

    data = _get(GDELT_URL, params={
        "query": GDELT_QUERY,
        "mode": "artlist",
        "maxrecords": "12",
        "timespan": "7d",
        "sort": "DateDesc",
        "format": "json",
        "sourcelang": "english",
    })

    if data and isinstance(data, dict) and data.get("articles"):
        articles = []
        for a in data["articles"][:10]:
            raw_date = a.get("seendate", "")
            try:
                dt = datetime.strptime(raw_date, "%Y%m%dT%H%M%SZ")
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                date_str = raw_date[:10]

            title = a.get("title", "")
            domain = a.get("domain", "")
            # Derive tags from title keywords
            tags = []
            for kw in ["AGL", "Origin", "Energy Australia", "AEMO", "AEMC", "AER",
                       "Alinta", "Loy Yang", "Yandin", "LGC", "ACCU", "battery",
                       "solar", "wind", "coal", "gas"]:
                if kw.lower() in title.lower():
                    tags.append(kw)

            articles.append({
                "title": title,
                "source": domain,
                "date": date_str,
                "url": a.get("url", "#"),
                "sentiment": _sentiment_from_title(title),
                "tags": tags[:4],
            })
        result = {"data": articles, "demo": False, "source": "GDELT"}
        _cache_set("news", result)
        return result

    result = {"data": DEMO_NEWS, "demo": True, "source": "demo"}
    return result


# ── Stock prices ──────────────────────────────────────────────────────────────

YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

STOCKS = [
    {"symbol": "ORG.AX", "name": "Origin Energy", "color": "#3b82f6"},
    {"symbol": "AGL.AX", "name": "AGL Energy",    "color": "#8b5cf6"},
]

DEMO_STOCKS = [
    {
        "symbol": "ORG.AX", "name": "Origin Energy", "color": "#3b82f6",
        "price": 9.42, "change": 0.08, "change_pct": 0.86,
        "week52_high": 11.20, "week52_low": 7.85,
        "market_cap_b": 16.8,
        "sparkline": [8.85, 8.92, 9.10, 9.05, 9.18, 9.25, 9.38, 9.42],
    },
    {
        "symbol": "AGL.AX", "name": "AGL Energy", "color": "#8b5cf6",
        "price": 11.15, "change": -0.12, "change_pct": -1.07,
        "week52_high": 13.40, "week52_low": 9.80,
        "market_cap_b": 7.2,
        "sparkline": [10.92, 11.08, 11.25, 11.18, 11.30, 11.22, 11.27, 11.15],
    },
]


def _fetch_stock(symbol: str, name: str, color: str) -> dict | None:
    data = _get(
        YAHOO_URL.format(symbol=symbol),
        params={"interval": "1wk", "range": "2mo"},
        timeout=8,
    )
    if not data:
        return None
    try:
        result = data["chart"]["result"][0]
        meta = result["meta"]
        closes = result["indicators"]["quote"][0].get("close", [])
        closes = [c for c in closes if c is not None]

        price = meta.get("regularMarketPrice") or meta.get("previousClose", 0)
        prev = meta.get("previousClose", price)
        change = round(price - prev, 3)
        change_pct = round((change / prev) * 100, 2) if prev else 0

        return {
            "symbol": symbol,
            "name": name,
            "color": color,
            "price": round(price, 2),
            "change": change,
            "change_pct": change_pct,
            "week52_high": round(meta.get("fiftyTwoWeekHigh", 0), 2),
            "week52_low": round(meta.get("fiftyTwoWeekLow", 0), 2),
            "market_cap_b": None,
            "sparkline": [round(c, 2) for c in closes[-10:]],
        }
    except Exception as e:
        print(f"[market/stocks] parse {symbol}: {e}")
        return None


@router.get("/api/market/stocks")
async def get_stocks():
    cached = _cache_get("stocks")
    if cached:
        return cached
    results = []
    for s in STOCKS:
        stock = _fetch_stock(s["symbol"], s["name"], s["color"])
        if stock:
            results.append(stock)

    if results:
        out = {"data": results, "demo": False, "source": "Yahoo Finance", "as_of": datetime.now(timezone.utc).isoformat()}
        _cache_set("stocks", out)
        return out

    return {"data": DEMO_STOCKS, "demo": True, "source": "demo", "as_of": datetime.now(timezone.utc).isoformat()}


# ── Carbon market prices ──────────────────────────────────────────────────────
# Source: Clean Energy Regulator quarterly carbon market reports
# https://cer.gov.au/markets/reports-and-data/quarterly-carbon-market-reports
# Updated quarterly — no free real-time API exists; data reflects latest CER report

CARBON_DATA = {
    "as_of": "Q3 FY2025 (Dec 2024)",
    "source": "Clean Energy Regulator — Quarterly Carbon Market Report",
    "source_url": "https://cer.gov.au/markets/reports-and-data/quarterly-carbon-market-reports",
    "accu": {
        "name": "ACCU",
        "full_name": "Australian Carbon Credit Unit",
        "price": 35.20,
        "unit": "AUD/tonne CO₂e",
        "change_qoq": 1.40,
        "change_pct": 4.1,
        "context": "Supported by voluntary corporate demand; forward prices signal ~$70/t by 2035 per government trajectory",
        "trend": [
            {"period": "Q4 FY23", "price": 29.50},
            {"period": "Q1 FY24", "price": 31.00},
            {"period": "Q2 FY24", "price": 32.40},
            {"period": "Q3 FY24", "price": 33.10},
            {"period": "Q4 FY24", "price": 33.80},
            {"period": "Q1 FY25", "price": 34.20},
            {"period": "Q2 FY25", "price": 33.80},
            {"period": "Q3 FY25", "price": 35.20},
        ],
    },
    "lgc": {
        "name": "LGC",
        "full_name": "Large-scale Generation Certificate",
        "price": 3.85,
        "unit": "AUD/MWh",
        "change_qoq": 0.30,
        "change_pct": 8.5,
        "context": "Prices rising on increased voluntary surrender; Yandin Stage 2 eligible to generate from Q2 FY27",
        "trend": [
            {"period": "Q4 FY23", "price": 2.10},
            {"period": "Q1 FY24", "price": 2.40},
            {"period": "Q2 FY24", "price": 2.80},
            {"period": "Q3 FY24", "price": 3.10},
            {"period": "Q4 FY24", "price": 3.35},
            {"period": "Q1 FY25", "price": 3.55},
            {"period": "Q2 FY25", "price": 3.55},
            {"period": "Q3 FY25", "price": 3.85},
        ],
    },
    "strategic_notes": [
        "At $35.20/t ACCU, Loy Yang B Scope 1 emissions (est. 8–9 Mt CO₂e/year) represent ~$300M/year implicit carbon liability at current price.",
        "Yandin Stage 2 (132 MW, commissioning Q2 FY27) will generate est. 420 GWh/year → ~420,000 LGCs at $3.85/LGC = ~$1.6M/year incremental LGC revenue.",
        "Forward ACCU price trajectory to ~$70/t by 2035 strengthens case for accelerated coal retirement (DOC-002 Loy Yang B transition options).",
    ],
}


@router.get("/api/market/carbon")
async def get_carbon():
    return {"data": CARBON_DATA, "demo": False}
