# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Vector Search Setup
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC Creates the Databricks Vector Search endpoint and Delta Sync Index on
# MAGIC `eds_processed.document_chunks`. The index is used by all EDS agents for
# MAGIC semantic retrieval with access-tier filtering.

# COMMAND ----------

# MAGIC %pip install databricks-sdk --upgrade --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.vectorsearch import (
    EndpointType,
    VectorIndexType,
    DeltaSyncVectorIndexSpecRequest,
    EmbeddingSourceColumn,
    PipelineType,
)

CATALOG = "ausnet_process_intel_catalog"
WORKSPACE_URL = "https://fevm-ausnet-process-intel.cloud.databricks.com"

VS_ENDPOINT_NAME = "eds-vector-search"
SOURCE_TABLE = f"{CATALOG}.eds_processed.document_chunks"
INDEX_NAME = f"{CATALOG}.eds_vectors.document_chunks_index"
EMBEDDING_MODEL = "databricks-gte-large-en"
PRIMARY_KEY = "chunk_id"
EMBEDDING_SOURCE_COLUMN = "chunk_text"

print("="*60)
print("EXECUTIVE DECISION STUDIO — Vector Search Setup")
print("="*60)
print(f"  Endpoint:      {VS_ENDPOINT_NAME}")
print(f"  Source table:  {SOURCE_TABLE}")
print(f"  Index:         {INDEX_NAME}")
print(f"  Embedding:     {EMBEDDING_MODEL}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Initialise Databricks SDK client

# COMMAND ----------

# SDK auto-discovers credentials from the running cluster context
w = WorkspaceClient()
print(f"[OK] Workspace client connected: {w.config.host}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Create Vector Search endpoint (if not exists)

# COMMAND ----------

def get_or_create_endpoint(client: WorkspaceClient, endpoint_name: str) -> str:
    """
    Returns the endpoint name after ensuring it exists and is ready.
    """
    try:
        existing = client.vector_search_endpoints.get_endpoint(endpoint_name)
        state = existing.endpoint_status.state.value if existing.endpoint_status else "UNKNOWN"
        print(f"[OK] Endpoint '{endpoint_name}' already exists. State: {state}")
        return endpoint_name
    except Exception as e:
        if "does not exist" in str(e).lower() or "not found" in str(e).lower() or "404" in str(e):
            print(f"Creating endpoint '{endpoint_name}'...")
        else:
            raise

    # Create the endpoint
    client.vector_search_endpoints.create_endpoint(
        name=endpoint_name,
        endpoint_type=EndpointType.STANDARD,
    )
    print(f"Endpoint creation initiated. Waiting for ONLINE state...")

    # Poll until ready
    max_wait = 600  # 10 minutes
    elapsed = 0
    while elapsed < max_wait:
        ep = client.vector_search_endpoints.get_endpoint(endpoint_name)
        state = ep.endpoint_status.state.value if ep.endpoint_status else "UNKNOWN"
        print(f"  ... endpoint state: {state} ({elapsed}s elapsed)")
        if state == "ONLINE":
            break
        if state in ("FAILED", "DELETED"):
            raise RuntimeError(f"Endpoint creation failed. State: {state}")
        time.sleep(30)
        elapsed += 30

    if elapsed >= max_wait:
        raise TimeoutError(f"Endpoint did not reach ONLINE state within {max_wait}s")

    print(f"[OK] Endpoint '{endpoint_name}' is ONLINE.")
    return endpoint_name

endpoint = get_or_create_endpoint(w, VS_ENDPOINT_NAME)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Ensure eds_vectors schema exists

# COMMAND ----------

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.eds_vectors COMMENT 'Vector Search indices for EDS'")
print(f"[OK] Schema {CATALOG}.eds_vectors ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Ensure source table has Change Data Feed enabled

# COMMAND ----------

spark.sql(f"""
    ALTER TABLE {SOURCE_TABLE}
    SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
""")
print(f"[OK] Change Data Feed enabled on {SOURCE_TABLE}")

# Verify chunk count
chunk_count = spark.table(SOURCE_TABLE).count()
print(f"[OK] Source table row count: {chunk_count:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Create Delta Sync Vector Search index

# COMMAND ----------

def get_or_create_index(client: WorkspaceClient, endpoint_name: str, index_name: str, source_table: str):
    """
    Creates a Delta Sync Vector Search index if it doesn't already exist.
    """
    try:
        existing = client.vector_search_indexes.get_index(index_name)
        status = existing.status.ready if existing.status else False
        print(f"[OK] Index '{index_name}' already exists. Ready: {status}")
        return existing
    except Exception as e:
        if "does not exist" in str(e).lower() or "not found" in str(e).lower() or "404" in str(e):
            print(f"Creating index '{index_name}'...")
        else:
            raise

    index = client.vector_search_indexes.create_index(
        name=index_name,
        endpoint_name=endpoint_name,
        primary_key=PRIMARY_KEY,
        index_type=VectorIndexType.DELTA_SYNC,
        delta_sync_index_spec=DeltaSyncVectorIndexSpecRequest(
            source_table=source_table,
            pipeline_type=PipelineType.TRIGGERED,
            embedding_source_columns=[
                EmbeddingSourceColumn(
                    name=EMBEDDING_SOURCE_COLUMN,
                    embedding_model_endpoint_name=EMBEDDING_MODEL,
                )
            ],
        ),
    )

    print(f"Index creation initiated. Index name: {index_name}")
    return index

index = get_or_create_index(w, VS_ENDPOINT_NAME, INDEX_NAME, SOURCE_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Wait for index to be ready and trigger sync

# COMMAND ----------

def wait_for_index(client: WorkspaceClient, index_name: str, timeout: int = 900):
    """Poll until index is ready or timeout."""
    elapsed = 0
    while elapsed < timeout:
        idx = client.vector_search_indexes.get_index(index_name)
        ready = idx.status.ready if idx.status else False
        message = idx.status.message if idx.status else "no status"
        print(f"  Index status: ready={ready}, message={message} ({elapsed}s)")
        if ready:
            return True
        time.sleep(30)
        elapsed += 30
    return False

print("Waiting for index to become ready...")
is_ready = wait_for_index(w, INDEX_NAME)

if is_ready:
    print(f"\n[OK] Index '{INDEX_NAME}' is ready for querying.")

    # Trigger a sync to ensure all documents are indexed
    try:
        w.vector_search_indexes.sync_index(INDEX_NAME)
        print("[OK] Index sync triggered successfully.")
    except Exception as e:
        print(f"[WARN] Index sync trigger: {e}")
else:
    print(f"[WARN] Index may not be fully ready yet. Check Databricks UI.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Test the index with a sample query

# COMMAND ----------

import json

print("\nTesting Vector Search index with sample queries...")

def test_vector_search(client: WorkspaceClient, index_name: str, query: str, num_results: int = 3):
    """Run a test similarity search against the index."""
    try:
        results = client.vector_search_indexes.query_index(
            index_name=index_name,
            columns=["chunk_id", "doc_id", "doc_title", "classification", "access_tier_level", "chunk_text"],
            query_text=query,
            num_results=num_results,
        )
        print(f"\nQuery: '{query}'")
        print(f"Results: {len(results.result.data_array) if results.result and results.result.data_array else 0}")
        if results.result and results.result.data_array:
            for i, row in enumerate(results.result.data_array[:3]):
                print(f"  [{i+1}] {row}")
        return results
    except Exception as e:
        print(f"  Query test failed: {e}")
        return None

test_queries = [
    "Loy Yang B transition strategy and closure options",
    "Yandin Wind Farm Stage 2 capital investment decision",
    "retail customer churn and NPS improvement",
]

for q in test_queries:
    test_vector_search(w, INDEX_NAME, q)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("\n" + "="*65)
print("VECTOR SEARCH SETUP — Complete")
print("="*65)
print(f"  Endpoint:        {VS_ENDPOINT_NAME}")
print(f"  Index:           {INDEX_NAME}")
print(f"  Source table:    {SOURCE_TABLE}")
print(f"  Embedding model: {EMBEDDING_MODEL}")
print(f"  Primary key:     {PRIMARY_KEY}")
print(f"  Source column:   {EMBEDDING_SOURCE_COLUMN}")
print("="*65)
print("\nNext step: Run 02_rag_chain.py to build and log the RAG chain.")
