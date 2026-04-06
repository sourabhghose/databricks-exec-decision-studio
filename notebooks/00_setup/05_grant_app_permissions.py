# Databricks notebook source

# MAGIC %md
# MAGIC ## EDS — Grant App Service Principal Permissions
# MAGIC
# MAGIC Run this notebook **after** the `exec-decision-studio` Databricks App has been
# MAGIC deployed at least once.  It discovers the app's auto-created service principal
# MAGIC and grants every permission the app needs to operate:
# MAGIC
# MAGIC | Resource | Permission |
# MAGIC |---|---|
# MAGIC | Unity Catalog | USE CATALOG |
# MAGIC | All 7 EDS schemas | USE SCHEMA |
# MAGIC | 10 read tables | SELECT |
# MAGIC | 2 write tables | MODIFY |
# MAGIC | documents volume | READ VOLUME + WRITE VOLUME |
# MAGIC | VS index | SELECT |
# MAGIC | SQL Warehouse | CAN_USE |
# MAGIC | Ingestion Job | CAN_MANAGE_RUN |
# MAGIC
# MAGIC Safe to re-run — grants are idempotent.

# COMMAND ----------

import requests

# Parameters — injected by DABs via base_parameters; fall back to hardcoded defaults
# for manual notebook runs.
dbutils.widgets.text("warehouse_id", "33baaa9523773520")
dbutils.widgets.text("ingestion_job_id", "950647315295103")

CATALOG = "ausnet_process_intel_catalog"
APP_NAME = "exec-decision-studio"
WAREHOUSE_ID = dbutils.widgets.get("warehouse_id")
INGESTION_JOB_ID = int(dbutils.widgets.get("ingestion_job_id"))

SCHEMAS = [
    "eds_raw",
    "eds_synthetic",
    "eds_processed",
    "eds_actions",
    "eds_audit",
    "eds_evaluation",
    "eds_vectors",
]

TABLES = [
    f"{CATALOG}.eds_synthetic.kpi_timeseries",
    f"{CATALOG}.eds_synthetic.risk_register",
    f"{CATALOG}.eds_synthetic.financial_data",
    f"{CATALOG}.eds_synthetic.documents",
    f"{CATALOG}.eds_synthetic.asset_register",
    f"{CATALOG}.eds_processed.document_chunks",
    f"{CATALOG}.eds_actions.action_items",
    f"{CATALOG}.eds_actions.decision_register",
    f"{CATALOG}.eds_audit.agent_interactions",
    f"{CATALOG}.eds_evaluation.qa_pairs",
]

MODIFY_TABLES = [
    f"{CATALOG}.eds_audit.agent_interactions",
    f"{CATALOG}.eds_actions.action_items",
]

# COMMAND ----------

# Resolve workspace host and caller token from Databricks context
host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
headers = {"Authorization": f"Bearer {token}"}

# COMMAND ----------

# Discover the app's service principal UUID via Apps API + SCIM
sp_uuid = None
sp_name = None

try:
    r = requests.get(f"{host}/api/2.0/apps/{APP_NAME}", headers=headers, timeout=15)
    if r.ok:
        app_data = r.json()
        sp_name = app_data.get("service_principal_name", "")
        sp_id = app_data.get("service_principal_id")
        if sp_id:
            scim = requests.get(
                f"{host}/api/2.0/preview/scim/v2/ServicePrincipals/{sp_id}",
                headers=headers,
                timeout=15,
            )
            if scim.ok:
                sp_uuid = scim.json().get("applicationId")
                print(f"[OK] App SP discovered: {sp_name} → UUID {sp_uuid}")
            else:
                print(f"[ERROR] SCIM lookup failed: {scim.status_code} — {scim.text[:200]}")
        else:
            print(f"[ERROR] App found but service_principal_id is missing in response")
    elif r.status_code == 404:
        print(f"[ERROR] App '{APP_NAME}' not found (404).")
        print()
        print("  Deploy the app first:")
        print("    databricks apps deploy exec-decision-studio \\")
        print("      --source-code-path /Workspace/Users/<you>/eds-app \\")
        print("      -p fe-vm-ausnet-process-intel")
        print()
        print("  Then re-run this notebook.")
        dbutils.notebook.exit("App not deployed — no grants applied.")
    else:
        print(f"[ERROR] Apps API returned {r.status_code}: {r.text[:200]}")
        dbutils.notebook.exit(f"Apps API error {r.status_code} — no grants applied.")
except Exception as e:
    print(f"[ERROR] SP discovery exception: {e}")
    dbutils.notebook.exit("Exception during SP discovery — no grants applied.")

if not sp_uuid:
    print("[ERROR] Could not determine SP UUID — no grants applied.")
    dbutils.notebook.exit("SP UUID not resolved.")

# COMMAND ----------

# Apply all Unity Catalog grants
sp_ref = f"`{sp_uuid}`"
granted = 0
failed = 0


def _grant(stmt: str) -> None:
    global granted, failed
    try:
        spark.sql(stmt)
        granted += 1
    except Exception as ex:
        print(f"  [WARN] {stmt[:90]}: {str(ex)[:100]}")
        failed += 1


print("Applying Unity Catalog grants...")

_grant(f"GRANT USE CATALOG ON CATALOG {CATALOG} TO {sp_ref}")

for schema in SCHEMAS:
    _grant(f"GRANT USE SCHEMA ON SCHEMA {CATALOG}.{schema} TO {sp_ref}")

for tbl in TABLES:
    _grant(f"GRANT SELECT ON TABLE {tbl} TO {sp_ref}")

for tbl in MODIFY_TABLES:
    _grant(f"GRANT MODIFY ON TABLE {tbl} TO {sp_ref}")

_grant(f"GRANT READ VOLUME ON VOLUME {CATALOG}.eds_raw.documents TO {sp_ref}")
_grant(f"GRANT WRITE VOLUME ON VOLUME {CATALOG}.eds_raw.documents TO {sp_ref}")

# Vector Search index — must be granted separately from the backing table
_grant(f"GRANT SELECT ON TABLE {CATALOG}.eds_vectors.document_chunks_index TO {sp_ref}")

print(f"  Unity Catalog: {granted} grants applied so far, {failed} failed")

# COMMAND ----------

# SQL Warehouse: CAN_USE
print(f"Granting CAN_USE on SQL Warehouse {WAREHOUSE_ID}...")
try:
    rw = requests.patch(
        f"{host}/api/2.0/permissions/sql/warehouses/{WAREHOUSE_ID}",
        headers={**headers, "Content-Type": "application/json"},
        json={"access_control_list": [{"user_name": sp_uuid, "permission_level": "CAN_USE"}]},
        timeout=15,
    )
    if rw.ok:
        granted += 1
        print(f"  [OK] CAN_USE on warehouse {WAREHOUSE_ID}")
    else:
        failed += 1
        print(f"  [WARN] Warehouse permission: {rw.status_code} — {rw.text[:200]}")
except Exception as ex:
    failed += 1
    print(f"  [WARN] Warehouse permission exception: {ex}")

# COMMAND ----------

# Ingestion Job: CAN_MANAGE_RUN (allows the SP to call jobs/run-now)
print(f"Granting CAN_MANAGE_RUN on ingestion job {INGESTION_JOB_ID}...")
try:
    rj = requests.patch(
        f"{host}/api/2.0/permissions/jobs/{INGESTION_JOB_ID}",
        headers={**headers, "Content-Type": "application/json"},
        json={"access_control_list": [{"user_name": sp_uuid, "permission_level": "CAN_MANAGE_RUN"}]},
        timeout=15,
    )
    if rj.ok:
        granted += 1
        print(f"  [OK] CAN_MANAGE_RUN on job {INGESTION_JOB_ID}")
    else:
        failed += 1
        print(f"  [WARN] Job permission {INGESTION_JOB_ID}: {rj.status_code} — {rj.text[:200]}")
except Exception as ex:
    failed += 1
    print(f"  [WARN] Job permission exception: {ex}")

# COMMAND ----------

# Summary
print()
print("=" * 60)
if failed == 0:
    print("  ALL GRANTS APPLIED SUCCESSFULLY")
else:
    print(f"  GRANTS COMPLETE WITH WARNINGS")
print("=" * 60)
print(f"  Succeeded : {granted}")
print(f"  Failed    : {failed}")
print(f"  SP        : {sp_name}")
print(f"  UUID      : {sp_uuid}")
print("=" * 60)
if failed > 0:
    print()
    print("  Review [WARN] lines above. Common causes:")
    print("  - Table/schema does not exist yet (run 00_init_schemas first)")
    print("  - Caller does not have MANAGE privilege on the resource")
    print("  - VS index not yet created (run ingestion pipeline first)")
