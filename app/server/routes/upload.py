"""
POST /api/documents/upload — Upload a document to the UC Volume and trigger ingestion.
"""

import os
import uuid
from datetime import datetime

import requests
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from server.config import CATALOG, get_token, get_warehouse_id, get_workspace_url

router = APIRouter()

VOLUME_ROOT = f"/Volumes/{CATALOG}/eds_raw/documents"
INGESTION_JOB_ID = 950647315295103  # [EDS] 01 - Document Ingestion & Embedding


def _files_api_upload(token: str, workspace_url: str, volume_path: str, content: bytes) -> tuple[bool, str]:
    """Upload bytes to a UC Volume via the Databricks Files API. Returns (ok, error_detail)."""
    url = f"{workspace_url}/api/2.0/fs/files{volume_path}"
    try:
        r = requests.put(
            url,
            headers={"Authorization": f"Bearer {token}"},
            data=content,
            timeout=60,
        )
        if r.ok:
            return True, ""
        detail = f"HTTP {r.status_code}: {r.text[:300]}"
        print(f"[upload] Files API {detail}")
        return False, detail
    except Exception as e:
        print(f"[upload] Files API error: {e}")
        return False, str(e)[:200]


def _trigger_ingestion(token: str, workspace_url: str) -> tuple[str | None, str]:
    """Trigger the ingestion job. Returns (run_id, error_detail)."""
    try:
        r = requests.post(
            f"{workspace_url}/api/2.1/jobs/run-now",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"job_id": INGESTION_JOB_ID},
            timeout=15,
        )
        print(f"[upload] Job trigger HTTP {r.status_code}: {r.text[:300]}")
        if r.ok:
            run_id = r.json().get("run_id")
            print(f"[upload] Triggered ingestion job, run_id={run_id}")
            return str(run_id), ""
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        print(f"[upload] Job trigger error: {e}")
        return None, str(e)[:200]


@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tier: int = Form(default=4),
    classification: str = Form(default="INTERNAL"),
):
    """
    Accept a document upload, write it to the Unity Catalog Volume,
    then trigger the ingestion job so it becomes searchable in ~2 min.
    """
    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "No filename provided."})

    tok = get_token()
    url = get_workspace_url()

    if not tok:
        return JSONResponse(
            status_code=503,
            content={"error": "No Databricks auth token available. Upload requires live backend."},
        )

    # Read file content
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50 MB limit
        return JSONResponse(status_code=413, content={"error": "File too large (max 50 MB)."})

    # Normalise filename: strip spaces, ensure safe chars
    safe_name = file.filename.replace(" ", "_")
    volume_path = f"{VOLUME_ROOT}/tier{tier}/{safe_name}"

    # Upload to volume
    ok, upload_err = _files_api_upload(tok, url, volume_path, content)
    if not ok:
        return JSONResponse(
            status_code=502,
            content={"error": f"Failed to upload to Unity Catalog Volume. {upload_err}"},
        )

    # Trigger ingestion job (async — doesn't block response)
    run_id, trigger_err = _trigger_ingestion(tok, url)

    return {
        "success": True,
        "filename": safe_name,
        "volume_path": volume_path,
        "tier": tier,
        "size_kb": round(len(content) / 1024, 1),
        "run_id": run_id,
        "trigger_error": trigger_err,
        "message": (
            f"'{safe_name}' uploaded to Tier {tier} volume. "
            "Ingestion job triggered — document will be available for querying in approximately 2–3 minutes."
            if run_id
            else f"'{safe_name}' uploaded to Tier {tier} volume. Job trigger failed: {trigger_err}"
        ),
    }


@router.get("/api/documents/upload/status")
async def upload_status(run_id: str):
    """Poll the Databricks ingestion job run status."""
    tok = get_token()
    workspace_url = get_workspace_url()
    if not tok:
        return {"state": "unknown", "message": "Auth unavailable — check status manually."}
    try:
        r = requests.get(
            f"{workspace_url}/api/2.1/jobs/runs/get",
            headers={"Authorization": f"Bearer {tok}"},
            params={"run_id": run_id},
            timeout=10,
        )
        if not r.ok:
            return {"state": "unknown", "message": f"Status unavailable ({r.status_code})"}
        data = r.json()
        state = data.get("state", {})
        life = state.get("life_cycle_state", "PENDING")
        result_state = state.get("result_state", "")
        msg = state.get("state_message", "")

        tasks = data.get("tasks", [])
        running_task = next((t for t in tasks if t.get("state", {}).get("life_cycle_state") == "RUNNING"), None)

        if life in ("PENDING", "WAITING_FOR_RETRY"):
            return {"state": "queued", "message": "Job queued — waiting for compute…"}
        if life == "RUNNING":
            label = running_task.get("task_key", "processing").replace("_", " ") if running_task else "processing"
            return {"state": "running", "message": f"Running: {label}…"}
        if life == "TERMINATING":
            return {"state": "running", "message": "Finalising index…"}
        if life == "TERMINATED":
            if result_state == "SUCCESS":
                return {"state": "success", "message": "Document ingested and indexed — ready to query."}
            return {"state": "error", "message": msg or "Ingestion job failed."}
        return {"state": "running", "message": "Processing…"}
    except Exception as e:
        print(f"[upload/status] {e}")
        return {"state": "error", "message": str(e)[:120]}
