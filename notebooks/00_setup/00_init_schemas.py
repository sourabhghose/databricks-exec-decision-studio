# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Schema Initialisation
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC This notebook creates all required Delta Lake tables across the EDS schemas.
# MAGIC Run once during initial setup. Tables are created with `IF NOT EXISTS` so re-running is safe.

# COMMAND ----------

CATALOG = "ausnet_process_intel_catalog"

print(f"Initialising schemas under catalog: {CATALOG}")
spark.sql(f"USE CATALOG {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Unity Catalog Volume — Raw document files

# COMMAND ----------

spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.eds_raw.documents")
print(f"[OK] Volume: {CATALOG}.eds_raw.documents")
print(f"     Path:   /Volumes/{CATALOG}/eds_raw/documents/")

# COMMAND ----------

# MAGIC %md
# MAGIC ## eds_processed — Document Chunks (post-embedding)

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_processed.document_chunks (
    chunk_id            STRING          NOT NULL COMMENT 'Unique identifier for each chunk',
    doc_id              STRING          NOT NULL COMMENT 'Parent document identifier',
    doc_title           STRING          COMMENT 'Title of the source document',
    classification      STRING          COMMENT 'Security classification: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED',
    access_tier_level   INT             COMMENT '1=Board/C-suite, 2=ELT, 3=Senior Mgmt, 4=All staff',
    chunk_text          STRING          COMMENT 'Raw text of this chunk (used for embedding)',
    section_title       STRING          COMMENT 'Section heading under which this chunk falls',
    page_number         INT             COMMENT 'Source page number (1-indexed)',
    chunk_index         INT             COMMENT 'Position of this chunk within the document',
    metadata            STRING          COMMENT 'JSON blob of additional metadata',
    embedding_model     STRING          COMMENT 'Model used to produce the embedding vector',
    created_at          TIMESTAMP       COMMENT 'Row creation timestamp'
)
USING DELTA
COMMENT 'Chunked and embedded document segments for Vector Search indexing'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_processed.document_chunks")

# COMMAND ----------

# MAGIC %md
# MAGIC ## eds_synthetic — Core synthetic data tables

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_synthetic.documents (
    doc_id              STRING          NOT NULL COMMENT 'Unique document identifier (UUID)',
    title               STRING          NOT NULL COMMENT 'Document title',
    doc_type            STRING          COMMENT 'Type: board_paper, strategy, financial_report, risk_register, regulatory, competitive_intel',
    classification      STRING          COMMENT 'Security classification: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED',
    access_tier_level   INT             COMMENT '1=Board/C-suite, 2=ELT, 3=Senior Mgmt, 4=All staff',
    business_area       STRING          COMMENT 'Business unit: Generation, Retail, Trading, Corporate, Group',
    effective_date      DATE            COMMENT 'Date the document came into effect',
    author              STRING          COMMENT 'Document author or committee',
    version             STRING          COMMENT 'Document version string e.g. v1.0',
    content             STRING          COMMENT 'Full document text content',
    is_synthetic        BOOLEAN         COMMENT 'True for AI-generated synthetic content',
    source_system       STRING          COMMENT 'Origin system: SharePoint, BoardVantage, SAP, Manual',
    created_at          TIMESTAMP       COMMENT 'Row creation timestamp'
)
USING DELTA
COMMENT 'Synthetic board and strategy documents for EDS demonstration'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_synthetic.documents")

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_synthetic.financial_data (
    id              STRING      NOT NULL COMMENT 'Unique row identifier',
    business_unit   STRING      NOT NULL COMMENT 'Business unit name',
    period          DATE        NOT NULL COMMENT 'Month start date for this record',
    fiscal_year     INT         COMMENT 'Alinta fiscal year (July-June)',
    fiscal_quarter  INT         COMMENT 'Fiscal quarter within the year (1-4)',
    revenue         DOUBLE      COMMENT 'Monthly revenue in AUD millions',
    ebitda          DOUBLE      COMMENT 'Monthly EBITDA in AUD millions',
    capex           DOUBLE      COMMENT 'Monthly capital expenditure in AUD millions',
    opex            DOUBLE      COMMENT 'Monthly operating expenditure in AUD millions',
    net_debt        DOUBLE      COMMENT 'Net debt balance at period end in AUD millions',
    cash_flow       DOUBLE      COMMENT 'Operating cash flow in AUD millions',
    data_type       STRING      COMMENT 'Record type: budget, actuals, forecast',
    currency        STRING      COMMENT 'Currency code (AUD)',
    created_at      TIMESTAMP   COMMENT 'Row creation timestamp'
)
USING DELTA
COMMENT 'Monthly financial data (actuals, budget, forecast) across business units'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_synthetic.financial_data")

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_synthetic.kpi_timeseries (
    kpi_id              STRING      NOT NULL COMMENT 'Unique KPI series identifier',
    kpi_name            STRING      NOT NULL COMMENT 'Human-readable KPI name',
    category            STRING      COMMENT 'Category: operational, financial, safety, customer, ESG',
    business_unit       STRING      COMMENT 'Owning business unit',
    asset_name          STRING      COMMENT 'Asset name if asset-level KPI, else NULL',
    period              DATE        NOT NULL COMMENT 'Month start date',
    value               DOUBLE      COMMENT 'Observed KPI value',
    unit                STRING      COMMENT 'Unit of measure e.g. %, MW, AUD_M, TIFR',
    target              DOUBLE      COMMENT 'Target value for the period',
    lower_threshold     DOUBLE      COMMENT 'Lower alert threshold',
    upper_threshold     DOUBLE      COMMENT 'Upper alert threshold',
    is_anomaly          BOOLEAN     COMMENT 'Flagged as anomalous by z-score detection',
    created_at          TIMESTAMP   COMMENT 'Row creation timestamp'
)
USING DELTA
COMMENT 'Monthly KPI time-series for operational, financial, safety and ESG metrics'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_synthetic.kpi_timeseries")

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_synthetic.asset_register (
    asset_id            STRING      NOT NULL COMMENT 'Unique asset identifier',
    asset_name          STRING      NOT NULL COMMENT 'Asset name',
    asset_type          STRING      COMMENT 'Type: thermal, wind, solar, gas_peaker',
    capacity_mw         DOUBLE      COMMENT 'Nameplate capacity in MW',
    fuel                STRING      COMMENT 'Fuel type: brown_coal, wind, gas, solar',
    location            STRING      COMMENT 'Physical location / town',
    state               STRING      COMMENT 'Australian state code e.g. VIC, WA',
    market              STRING      COMMENT 'Electricity market: NEM, WEM',
    commissioning_year  INT         COMMENT 'Year asset was commissioned',
    status              STRING      COMMENT 'Asset status: operating, mothballed, development, decommissioned',
    owner_bu            STRING      COMMENT 'Owning business unit'
)
USING DELTA
COMMENT 'Alinta Energy generation asset register'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_synthetic.asset_register")

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_synthetic.risk_register (
    risk_id         STRING      NOT NULL COMMENT 'Unique risk identifier',
    category        STRING      COMMENT 'Risk category: regulatory, market, operational, ESG, cyber, financial',
    description     STRING      COMMENT 'Detailed risk description',
    likelihood      STRING      COMMENT 'Likelihood rating: Almost Certain, Likely, Possible, Unlikely, Rare',
    consequence     STRING      COMMENT 'Consequence rating: Catastrophic, Major, Moderate, Minor, Insignificant',
    rating          STRING      COMMENT 'Residual risk rating: Critical, High, Medium, Low',
    risk_score      INT         COMMENT 'Numeric risk score (1-25)',
    owner           STRING      COMMENT 'Risk owner name / role',
    mitigation      STRING      COMMENT 'Mitigation actions in place',
    status          STRING      COMMENT 'Status: open, in_progress, closed, accepted',
    review_date     DATE        COMMENT 'Next scheduled review date',
    created_at      TIMESTAMP   COMMENT 'Row creation timestamp'
)
USING DELTA
COMMENT 'Enterprise risk register for Alinta Energy'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_synthetic.risk_register")

# COMMAND ----------

# MAGIC %md
# MAGIC ## eds_actions — Decision & action tracking

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_actions.action_items (
    action_id       STRING      NOT NULL COMMENT 'Unique action identifier',
    description     STRING      NOT NULL COMMENT 'Description of the action item',
    owner           STRING      COMMENT 'Person or role responsible',
    due_date        DATE        COMMENT 'Target completion date',
    source_meeting  STRING      COMMENT 'Meeting or forum that generated this action',
    status          STRING      COMMENT 'Status: open, in_progress, complete, overdue, deferred',
    priority        STRING      COMMENT 'Priority: critical, high, medium, low',
    created_at      TIMESTAMP   COMMENT 'Row creation timestamp',
    updated_at      TIMESTAMP   COMMENT 'Last update timestamp'
)
USING DELTA
COMMENT 'Action items from board, ELT and committee meetings'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_actions.action_items")

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_actions.decision_register (
    decision_id             STRING          NOT NULL COMMENT 'Unique decision identifier',
    decision_date           DATE            COMMENT 'Date the decision was made',
    committee               STRING          COMMENT 'Decision-making body: Board, ELT, IC, RC',
    description             STRING          COMMENT 'Full decision description',
    decision_type           STRING          COMMENT 'Type: strategic, financial, operational, risk, governance',
    outcome                 STRING          COMMENT 'Decision outcome/resolution',
    owner                   STRING          COMMENT 'Accountable executive',
    implementation_status   STRING          COMMENT 'Implementation status: pending, in_progress, complete, deferred',
    supporting_docs         ARRAY<STRING>   COMMENT 'Array of related document IDs',
    created_at              TIMESTAMP       COMMENT 'Row creation timestamp'
)
USING DELTA
COMMENT 'Register of formal decisions made by Board and executive committees'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_actions.decision_register")

# COMMAND ----------

# MAGIC %md
# MAGIC ## eds_audit — Agent interaction audit trail

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_audit.agent_interactions (
    interaction_id              STRING      NOT NULL COMMENT 'Unique interaction UUID',
    timestamp                   TIMESTAMP   NOT NULL COMMENT 'UTC timestamp of the interaction',
    user_id                     STRING      COMMENT 'User identifier (anonymised)',
    user_tier                   STRING      COMMENT 'User role tier: board, ceo, cfo, coo, exco, senior_mgmt',
    access_tier_level           INT         COMMENT 'Numeric access tier: 1=highest (Board), 4=lowest',
    agent_name                  STRING      COMMENT 'Agent that handled the query',
    query                       STRING      COMMENT 'User query text',
    response_preview            STRING      COMMENT 'First 500 chars of agent response',
    source_doc_ids              ARRAY<STRING> COMMENT 'Document IDs referenced in response',
    confidence_score            DOUBLE      COMMENT 'Agent confidence 0-1',
    groundedness_score          DOUBLE      COMMENT 'Groundedness score 0-1 from evaluation agent',
    classification_tier_accessed STRING     COMMENT 'Highest document classification accessed',
    is_policy_compliant         BOOLEAN     COMMENT 'Access policy compliance check result',
    latency_ms                  LONG        COMMENT 'End-to-end query latency in milliseconds'
)
USING DELTA
COMMENT 'Immutable audit log of all agent queries and responses'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'false',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_audit.agent_interactions")

# COMMAND ----------

# MAGIC %md
# MAGIC ## eds_evaluation — RAG quality evaluation

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_evaluation.qa_pairs (
    qa_id                   STRING      NOT NULL COMMENT 'Unique QA pair identifier',
    source_doc_id           STRING      COMMENT 'Source document used to generate this pair',
    question                STRING      COMMENT 'Evaluation question',
    expected_answer         STRING      COMMENT 'Ground-truth expected answer',
    difficulty              STRING      COMMENT 'Question difficulty: easy, medium, hard',
    agent_answer            STRING      COMMENT 'Answer produced by the agent under test',
    groundedness_score      DOUBLE      COMMENT 'Groundedness: answer supported by retrieved context (0-1)',
    citation_quality_score  DOUBLE      COMMENT 'Citation quality: specific and correct references (0-1)',
    completeness_score      DOUBLE      COMMENT 'Completeness: all relevant points covered (0-1)',
    composite_confidence    STRING      COMMENT 'Composite label: HIGH, MEDIUM, LOW, UNSATISFACTORY',
    created_at              TIMESTAMP   COMMENT 'Row creation timestamp'
)
USING DELTA
COMMENT 'RAG evaluation QA pairs with LLM-judge scores'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
""")

print(f"[OK] {CATALOG}.eds_evaluation.qa_pairs")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

tables = [
    f"{CATALOG}.eds_processed.document_chunks",
    f"{CATALOG}.eds_synthetic.documents",
    f"{CATALOG}.eds_synthetic.financial_data",
    f"{CATALOG}.eds_synthetic.kpi_timeseries",
    f"{CATALOG}.eds_synthetic.asset_register",
    f"{CATALOG}.eds_synthetic.risk_register",
    f"{CATALOG}.eds_actions.action_items",
    f"{CATALOG}.eds_actions.decision_register",
    f"{CATALOG}.eds_audit.agent_interactions",
    f"{CATALOG}.eds_evaluation.qa_pairs",
]

print("\n" + "="*60)
print("EXECUTIVE DECISION STUDIO — Schema Initialisation Complete")
print("="*60)
for t in tables:
    row_count = spark.table(t).count()
    print(f"  {t:65s} [{row_count:>6} rows]")
print(f"\n  Volume: /Volumes/{CATALOG}/eds_raw/documents/")
print("="*60)
print(f"\nAll tables and volumes created successfully under catalog: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Grant App Service Principal Access to Unity Catalog
# MAGIC Dynamically discovers the EDS Databricks App's service principal and grants
# MAGIC it the required Unity Catalog permissions. Safe to re-run — uses IF EXISTS patterns.

# COMMAND ----------

import requests

APP_NAME = "exec-decision-studio"
SCHEMAS = ["eds_synthetic", "eds_processed", "eds_actions", "eds_audit", "eds_evaluation"]
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

# Get workspace host + token from Databricks context
host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
headers = {"Authorization": f"Bearer {token}"}

# Discover the app's service principal UUID
sp_uuid = None
try:
    r = requests.get(f"{host}/api/2.0/apps/{APP_NAME}", headers=headers, timeout=15)
    if r.ok:
        app_data = r.json()
        sp_name = app_data.get("service_principal_name", "")
        # Extract UUID from display name via SCIM lookup
        sp_id = app_data.get("service_principal_id")
        scim = requests.get(
            f"{host}/api/2.0/preview/scim/v2/ServicePrincipals/{sp_id}",
            headers=headers, timeout=15
        )
        if scim.ok:
            sp_uuid = scim.json().get("applicationId")
            print(f"[OK] App SP discovered: {sp_name} → UUID {sp_uuid}")
        else:
            print(f"[WARN] SCIM lookup failed: {scim.status_code}")
    else:
        print(f"[WARN] App '{APP_NAME}' not found ({r.status_code}) — skipping SP grants")
except Exception as e:
    print(f"[WARN] SP discovery failed: {e}")

if sp_uuid:
    sp_ref = f"`{sp_uuid}`"
    granted, failed = 0, 0

    def grant(stmt):
        global granted, failed
        try:
            spark.sql(stmt)
            granted += 1
        except Exception as ex:
            print(f"  [WARN] {stmt[:80]}: {str(ex)[:80]}")
            failed += 1

    # Catalog + schema access
    grant(f"GRANT USE CATALOG ON CATALOG {CATALOG} TO {sp_ref}")
    for schema in SCHEMAS:
        grant(f"GRANT USE SCHEMA ON SCHEMA {CATALOG}.{schema} TO {sp_ref}")

    # Table SELECT
    for tbl in TABLES:
        grant(f"GRANT SELECT ON TABLE {tbl} TO {sp_ref}")

    # Table MODIFY (audit writes)
    for tbl in MODIFY_TABLES:
        grant(f"GRANT MODIFY ON TABLE {tbl} TO {sp_ref}")

    # Volume access: read for ingestion, write for document upload via Files API
    grant(f"GRANT READ VOLUME ON VOLUME {CATALOG}.eds_raw.documents TO {sp_ref}")
    grant(f"GRANT WRITE VOLUME ON VOLUME {CATALOG}.eds_raw.documents TO {sp_ref}")

    print(f"\n[OK] SP grants complete: {granted} succeeded, {failed} failed")
else:
    print("[INFO] No SP grants applied (app not found or SP not discovered)")
