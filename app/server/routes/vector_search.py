"""
GET  /api/vector-search/status — Index row count, sync state, and last sync time.
POST /api/vector-search/sync   — Trigger a manual delta sync of the VS index.
"""

import requests
from fastapi import APIRouter
from server.config import CATALOG, VS_INDEX, get_token, get_workspace_url

router = APIRouter()

_INDEX_NAME = VS_INDEX  # ausnet_process_intel_catalog.eds_vectors.document_chunks_index


def _vs_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@router.get("/api/vector-search/status")
async def vs_status():
    """Return current state of the Vector Search index."""
    tok = get_token()
    url = get_workspace_url()

    if not tok:
        return {"ready": False, "message": "Auth unavailable", "num_rows": None, "sync_state": "unknown"}

    try:
        r = requests.get(
            f"{url}/api/2.0/vector-search/indexes/{_INDEX_NAME}",
            headers=_vs_headers(tok),
            timeout=15,
        )
        if not r.ok:
            return {"ready": False, "message": f"VS API {r.status_code}: {r.text[:200]}", "num_rows": None, "sync_state": "unknown"}

        data = r.json()
        status = data.get("status", {})
        ready = status.get("ready", False)
        message = status.get("message", "")
        num_rows = data.get("status", {}).get("indexed_row_count")
        delta_sync = data.get("delta_sync_index_spec", {})
        sync_state = status.get("index_url", "")

        print(f"[VS] status ready={ready} rows={num_rows} message={message!r}")
        return {
            "ready": ready,
            "message": message,
            "num_rows": num_rows,
            "sync_state": "ready" if ready else "not_ready",
            "source_table": delta_sync.get("source_table", ""),
        }
    except Exception as e:
        print(f"[VS/status] {e}")
        return {"ready": False, "message": str(e)[:200], "num_rows": None, "sync_state": "error"}


@router.post("/api/vector-search/sync")
async def vs_sync():
    """Trigger a delta sync of the Vector Search index."""
    tok = get_token()
    url = get_workspace_url()

    if not tok:
        return {"triggered": False, "message": "Auth unavailable — sync not triggered."}

    try:
        r = requests.post(
            f"{url}/api/2.0/vector-search/indexes/{_INDEX_NAME}/sync",
            headers=_vs_headers(tok),
            timeout=15,
        )
        print(f"[VS/sync] HTTP {r.status_code}: {r.text[:200]}")
        if r.ok:
            return {"triggered": True, "message": "Vector Search sync triggered. Index will refresh in 1–3 minutes."}
        return {"triggered": False, "message": f"Sync request failed: HTTP {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        print(f"[VS/sync] {e}")
        return {"triggered": False, "message": str(e)[:200]}
