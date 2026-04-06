# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # [EDS] 06 — Create Genie Space
# MAGIC
# MAGIC Creates (or finds) an AI/BI Genie Space over the five core EDS Unity Catalog tables,
# MAGIC adds 10 curated sample questions, then patches `app/app.yaml` in the workspace with:
# MAGIC - `genie_space` resource block (so Databricks Apps grants the SP `CAN_RUN`)
# MAGIC - `GENIE_SPACE_ID` env var (`valueFrom: genie_space`)
# MAGIC
# MAGIC **Idempotent:** re-running does not create a duplicate space.
# MAGIC After this notebook completes, re-run `./scripts/deploy.sh` to activate.

# COMMAND ----------

import json
import base64
import time

import requests

# COMMAND ----------
# MAGIC %md ## Parameters

# COMMAND ----------

dbutils.widgets.text("warehouse_id", "33baaa9523773520", "SQL Warehouse ID")

WAREHOUSE_ID = dbutils.widgets.get("warehouse_id")

CATALOG = "ausnet_process_intel_catalog"
SPACE_NAME = "EDS — Executive Data Explorer"
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

def _get_token() -> str:
    return dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()


def _get_workspace_url() -> str:
    return dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()


def _headers(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


# COMMAND ----------
# MAGIC %md ## Genie Space helpers

# COMMAND ----------

def find_existing_space(tok: str, url: str) -> str | None:
    """Return space_id if a space named SPACE_NAME already exists, else None."""
    resp = requests.get(f"{url}/api/2.0/data-rooms", headers=_headers(tok), timeout=30)
    if not resp.ok:
        print(f"[EDS] Could not list data-rooms: {resp.status_code} {resp.text[:200]}")
        return None
    rooms = resp.json().get("data_rooms", [])
    for room in rooms:
        if room.get("display_name") == SPACE_NAME:
            sid = room.get("space_id") or room.get("id")
            print(f"[EDS] Found existing Genie Space: {sid}")
            return sid
    return None


def create_space(tok: str, url: str) -> str:
    """Create a new Genie Space and return its space_id."""
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
    resp = requests.post(
        f"{url}/api/2.0/data-rooms/",
        headers=_headers(tok),
        json=payload,
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"Failed to create Genie Space: {resp.status_code} {resp.text[:500]}")
    data = resp.json()
    sid = data.get("space_id") or data.get("id")
    print(f"[EDS] Created Genie Space: {sid}")
    return sid


def add_curated_questions(tok: str, url: str, space_id: str) -> None:
    """Add sample questions to the Genie Space."""
    for question in SAMPLE_QUESTIONS:
        payload = {"question": question}
        resp = requests.post(
            f"{url}/api/2.0/data-rooms/{space_id}/curated-questions",
            headers=_headers(tok),
            json=payload,
            timeout=30,
        )
        if resp.ok:
            print(f"[EDS]   + question: {question[:60]}...")
        else:
            print(f"[EDS]   ! failed ({resp.status_code}): {question[:60]}")


def create_or_find_space(tok: str, url: str) -> str:
    """Idempotent: return existing space_id or create a new one."""
    existing = find_existing_space(tok, url)
    if existing:
        return existing
    sid = create_space(tok, url)
    print("[EDS] Adding curated questions...")
    add_curated_questions(tok, url, sid)
    return sid


# COMMAND ----------
# MAGIC %md ## app.yaml patch helpers

# COMMAND ----------

def _read_workspace_file(tok: str, url: str, path: str) -> str:
    """Read a file from the Databricks workspace and return its content as a string."""
    resp = requests.get(
        f"{url}/api/2.0/workspace/export",
        headers=_headers(tok),
        params={"path": path, "format": "SOURCE"},
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Could not read {path}: {resp.status_code} {resp.text[:300]}")
    encoded = resp.json().get("content", "")
    return base64.b64decode(encoded).decode("utf-8")


def _write_workspace_file(tok: str, url: str, path: str, content: str) -> None:
    """Write (overwrite) a file in the Databricks workspace."""
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    resp = requests.post(
        f"{url}/api/2.0/workspace/import",
        headers=_headers(tok),
        json={"path": path, "content": encoded, "overwrite": True, "format": "AUTO"},
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Could not write {path}: {resp.status_code} {resp.text[:300]}")
    print(f"[EDS] Wrote {path}")


def patch_app_yaml(tok: str, url: str, space_id: str) -> None:
    """
    Insert or update the genie_space resource and GENIE_SPACE_ID env var
    in the app.yaml stored in the workspace.

    Operates as line-level text manipulation to preserve all existing content.
    """
    try:
        content = _read_workspace_file(tok, url, WORKSPACE_PATH)
    except RuntimeError as e:
        print(f"[EDS] WARNING: {e}")
        print("[EDS] Skipping app.yaml patch — re-run deploy.sh manually and add genie_space resource via UI.")
        return

    lines = content.splitlines(keepends=True)

    # ── Check if genie_space block already exists ──────────────────────────────
    if "genie_space:" in content:
        # Update space_id in existing block
        new_lines = []
        in_genie = False
        for line in lines:
            if "genie_space:" in line:
                in_genie = True
            if in_genie and "space_id:" in line:
                indent = len(line) - len(line.lstrip())
                line = " " * indent + f"space_id: \"{space_id}\"\n"
                in_genie = False
            new_lines.append(line)
        content = "".join(new_lines)
        print(f"[EDS] Updated existing genie_space.space_id → {space_id}")
    else:
        # Append genie_space resource block under existing resources section
        genie_resource_block = (
            f"  - name: genie_space\n"
            f"    genie_space:\n"
            f"      space_id: \"{space_id}\"\n"
            f"      permission: CAN_RUN\n"
        )
        genie_env_block = (
            f"  - name: GENIE_SPACE_ID\n"
            f"    valueFrom: genie_space\n"
        )

        # Insert after last existing resource entry (before first blank line after resources)
        # Simple approach: append to end, then restructure
        # Find the resources: section and append our block
        if "resources:" in content:
            # Find the end of the resources section (first top-level key after it)
            new_lines = []
            in_resources = False
            resources_done = False
            in_env = False
            env_done = False

            for i, line in enumerate(lines):
                stripped = line.strip()

                # Detect top-level keys (not indented)
                is_top_level = line and not line[0].isspace() and stripped and not stripped.startswith("#")

                if line.rstrip() == "resources:":
                    in_resources = True
                    in_env = False
                elif line.rstrip() == "env:":
                    in_env = True
                    in_resources = False
                elif is_top_level and stripped.endswith(":") and in_resources and not resources_done:
                    # New top-level section — insert genie resource before it
                    new_lines.append(genie_resource_block)
                    resources_done = True
                    in_resources = False
                elif is_top_level and stripped.endswith(":") and in_env and not env_done:
                    new_lines.append(genie_env_block)
                    env_done = True
                    in_env = False

                new_lines.append(line)

            # If still inside resources or env at EOF
            if in_resources and not resources_done:
                new_lines.append(genie_resource_block)
            if in_env and not env_done:
                new_lines.append(genie_env_block)

            # If env section wasn't found at all, append it
            if not env_done:
                new_lines.append("\nenv:\n")
                new_lines.append(genie_env_block)

            content = "".join(new_lines)
        else:
            # No resources section at all — append both
            content += (
                f"\nresources:\n{genie_resource_block}"
                f"\nenv:\n{genie_env_block}"
            )

        print(f"[EDS] Added genie_space resource block (space_id={space_id})")

    _write_workspace_file(tok, url, WORKSPACE_PATH, content)


# COMMAND ----------
# MAGIC %md ## Main

# COMMAND ----------

tok = _get_token()
url = _get_workspace_url()

print(f"[EDS] Workspace: {url}")
print(f"[EDS] Warehouse: {WAREHOUSE_ID}")
print(f"[EDS] Tables: {len(TABLES)}")

space_id = create_or_find_space(tok, url)
print(f"\n[EDS] Genie Space ID: {space_id}")

patch_app_yaml(tok, url, space_id)

print("\n[EDS] ✅ Done.")
print(f"[EDS] Next step: run ./scripts/deploy.sh to activate the Genie integration.")
print(f"[EDS] The app will read GENIE_SPACE_ID from the Databricks Apps resource injection.")
