# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # [EDS] 06 — Create Genie Space
# MAGIC
# MAGIC Fully automated, idempotent setup for the Data Insights tab:
# MAGIC
# MAGIC 1. Create (or find) the AI/BI Genie Space over 5 EDS Unity Catalog tables
# MAGIC 2. Add 10 curated sample questions
# MAGIC 3. Discover the app service principal from the Databricks Apps API
# MAGIC 4. Grant the SP `CAN_RUN` on the Genie Space
# MAGIC 5. Update `app/app.yaml` in the workspace — sets `GENIE_SPACE_ID` as a plain `value`
# MAGIC
# MAGIC **Idempotent:** re-running does not create duplicate spaces or duplicate questions.
# MAGIC After this notebook completes, re-run `./scripts/deploy.sh` to activate.

# COMMAND ----------

import base64
import time

import requests

# COMMAND ----------
# MAGIC %md ## Parameters

# COMMAND ----------

dbutils.widgets.text("warehouse_id", "33baaa9523773520", "SQL Warehouse ID")
dbutils.widgets.text("app_name", "exec-decision-studio", "Databricks App name")

WAREHOUSE_ID = dbutils.widgets.get("warehouse_id")
APP_NAME     = dbutils.widgets.get("app_name")

CATALOG      = "ausnet_process_intel_catalog"
SPACE_NAME   = "EDS — Executive Data Explorer"
WORKSPACE_PATH = "/Workspace/Users/sourabh.ghose@databricks.com/eds-app/app/app.yaml"

TABLES = [
    f"{CATALOG}.eds_synthetic.kpi_timeseries",
    f"{CATALOG}.eds_synthetic.risk_register",
    f"{CATALOG}.eds_synthetic.financial_data",
    f"{CATALOG}.eds_actions.action_items",
    f"{CATALOG}.eds_actions.decision_register",
]

SAMPLE_QUESTIONS = [
    "Which KPIs are below target in the Generation business unit?",
    "What are the top 5 risks by risk score?",
    "Show me all Critical and High rated risks",
    "Which action items are overdue?",
    "What decisions are currently in progress?",
    "Show EBITDA by business unit for FY2025",
    "Which KPIs have been flagged as anomalies?",
    "List all board decisions from the last 6 months",
    "Show risks owned by the CRO",
    "What is the retail customer churn rate trend?",
]

# COMMAND ----------
# MAGIC %md ## Auth helpers

# COMMAND ----------

def _tok() -> str:
    return dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

def _url() -> str:
    return dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

def _h(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}

# COMMAND ----------
# MAGIC %md ## 1 — Create or find Genie Space

# COMMAND ----------

def find_existing_space(tok: str, url: str) -> str | None:
    resp = requests.get(f"{url}/api/2.0/data-rooms", headers=_h(tok), timeout=30)
    if not resp.ok:
        print(f"[EDS] Could not list Genie spaces: {resp.status_code} {resp.text[:200]}")
        return None
    for room in resp.json().get("data_rooms", []):
        if room.get("display_name") == SPACE_NAME:
            sid = room.get("space_id") or room.get("id")
            print(f"[EDS] Found existing Genie Space: {sid}")
            return sid
    return None


def create_space(tok: str, url: str) -> str:
    payload = {
        "display_name": SPACE_NAME,
        "warehouse_id": WAREHOUSE_ID,
        "table_identifiers": TABLES,
        "run_as_type": "VIEWER",
        "description": (
            "AI/BI Genie Space for Alinta Energy Executive Decision Studio. "
            "Supports natural-language queries over KPIs, risks, financials, "
            "action items, and the decision register."
        ),
    }
    resp = requests.post(f"{url}/api/2.0/data-rooms/", headers=_h(tok), json=payload, timeout=60)
    if not resp.ok:
        raise RuntimeError(f"Failed to create Genie Space: {resp.status_code} {resp.text[:500]}")
    sid = resp.json().get("space_id") or resp.json().get("id")
    print(f"[EDS] Created Genie Space: {sid}")
    return sid


def add_curated_questions(tok: str, url: str, space_id: str) -> None:
    # Fetch existing questions to stay idempotent
    existing_resp = requests.get(
        f"{url}/api/2.0/data-rooms/{space_id}/curated-questions",
        headers=_h(tok), timeout=30,
    )
    existing = set()
    if existing_resp.ok:
        for q in existing_resp.json().get("curated_questions", []):
            existing.add(q.get("question", ""))

    added = 0
    for question in SAMPLE_QUESTIONS:
        if question in existing:
            print(f"[EDS]   ✓ already exists: {question[:60]}")
            continue
        resp = requests.post(
            f"{url}/api/2.0/data-rooms/{space_id}/curated-questions",
            headers=_h(tok), json={"question": question}, timeout=30,
        )
        if resp.ok:
            print(f"[EDS]   + added: {question[:60]}")
            added += 1
        else:
            print(f"[EDS]   ! failed ({resp.status_code}): {question[:60]}")
    print(f"[EDS] Questions: {added} added, {len(existing)} already present")


def create_or_find_space(tok: str, url: str) -> str:
    existing = find_existing_space(tok, url)
    if existing:
        add_curated_questions(tok, url, existing)
        return existing
    sid = create_space(tok, url)
    add_curated_questions(tok, url, sid)
    return sid

# COMMAND ----------
# MAGIC %md ## 2 — Discover app service principal

# COMMAND ----------

def get_app_sp_name(tok: str, url: str) -> str | None:
    """Return the service_principal_name (client_id UUID) of the Databricks App SP."""
    resp = requests.get(f"{url}/api/2.0/apps/{APP_NAME}", headers=_h(tok), timeout=30)
    if not resp.ok:
        print(f"[EDS] Could not fetch app details: {resp.status_code} {resp.text[:200]}")
        return None
    sp_name = resp.json().get("service_principal_name")
    print(f"[EDS] App SP name: {sp_name}")
    return sp_name

# COMMAND ----------
# MAGIC %md ## 3 — Grant SP CAN_RUN on Genie Space

# COMMAND ----------

def grant_sp_can_run(tok: str, url: str, space_id: str, sp_name: str) -> None:
    """Grant the app SP CAN_RUN on the Genie Space (idempotent — PUT replaces ACL)."""
    payload = {
        "access_control_list": [
            {"service_principal_name": sp_name, "permission_level": "CAN_RUN"}
        ]
    }
    resp = requests.put(
        f"{url}/api/2.0/permissions/genie/{space_id}",
        headers=_h(tok), json=payload, timeout=30,
    )
    if resp.ok:
        print(f"[EDS] Granted CAN_RUN to SP '{sp_name}' on Genie Space {space_id}")
    else:
        print(f"[EDS] WARNING: Could not grant permission: {resp.status_code} {resp.text[:300]}")
        print("[EDS] Grant manually: PUT /api/2.0/permissions/genie/{space_id}")

# COMMAND ----------
# MAGIC %md ## 4 — Patch app.yaml with GENIE_SPACE_ID

# COMMAND ----------

def _read_workspace_file(tok: str, url: str, path: str) -> str:
    resp = requests.get(
        f"{url}/api/2.0/workspace/export",
        headers=_h(tok),
        params={"path": path, "format": "SOURCE"},
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Could not read {path}: {resp.status_code} {resp.text[:300]}")
    return base64.b64decode(resp.json().get("content", "")).decode("utf-8")


def _write_workspace_file(tok: str, url: str, path: str, content: str) -> None:
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    resp = requests.post(
        f"{url}/api/2.0/workspace/import",
        headers=_h(tok),
        json={"path": path, "content": encoded, "overwrite": True, "format": "AUTO"},
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Could not write {path}: {resp.status_code} {resp.text[:300]}")
    print(f"[EDS] Wrote {path}")


def patch_app_yaml(tok: str, url: str, space_id: str) -> None:
    """
    Ensure app.yaml contains exactly one GENIE_SPACE_ID env var with the correct value.
    Strategy: read → remove all existing GENIE_SPACE_ID lines → append clean entry.
    This avoids brittle YAML parsing and handles both first-run and re-run.
    """
    try:
        content = _read_workspace_file(tok, url, WORKSPACE_PATH)
    except RuntimeError as e:
        print(f"[EDS] WARNING: {e}")
        print("[EDS] Skipping app.yaml patch — set GENIE_SPACE_ID manually in app.yaml env section.")
        return

    lines = content.splitlines()

    # Remove any existing GENIE_SPACE_ID block (name + value/valueFrom lines)
    cleaned = []
    skip_next = False
    for line in lines:
        if skip_next:
            # Skip the value/valueFrom line that follows the name: GENIE_SPACE_ID line
            if line.strip().startswith("value"):
                skip_next = False
                continue
            skip_next = False
        if "GENIE_SPACE_ID" in line and line.strip().startswith("- name:"):
            skip_next = True   # skip this line and the next value line
            continue
        if "GENIE_SPACE_ID" in line:
            continue           # stray GENIE_SPACE_ID line (e.g. orphan valueFrom)
        cleaned.append(line)

    # Remove any duplicate blank lines at end
    content = "\n".join(cleaned).rstrip()

    # Ensure there is an env: section; if not, append one
    if "env:" not in content:
        content += "\n\nenv:"

    # Append GENIE_SPACE_ID as the last env entry
    content += f"\n  - name: GENIE_SPACE_ID\n    value: \"{space_id}\"\n"

    _write_workspace_file(tok, url, WORKSPACE_PATH, content)
    print(f"[EDS] GENIE_SPACE_ID set to {space_id} in app.yaml")

# COMMAND ----------
# MAGIC %md ## Main

# COMMAND ----------

tok = _tok()
url = _url()

print(f"[EDS] Workspace: {url}")
print(f"[EDS] Warehouse: {WAREHOUSE_ID}")
print(f"[EDS] App:       {APP_NAME}")
print()

# Step 1: Create or find Genie Space
space_id = create_or_find_space(tok, url)
print(f"\n[EDS] Genie Space ID: {space_id}")

# Step 2: Discover app SP
sp_name = get_app_sp_name(tok, url)

# Step 3: Grant CAN_RUN
if sp_name:
    grant_sp_can_run(tok, url, space_id, sp_name)
else:
    print("[EDS] WARNING: Could not discover app SP — grant CAN_RUN manually.")

# Step 4: Patch app.yaml
patch_app_yaml(tok, url, space_id)

print("\n[EDS] ✅ Done.")
print("[EDS] Next step: run ./scripts/deploy.sh to activate the Data Insights tab.")
