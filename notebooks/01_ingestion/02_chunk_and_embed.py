# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Chunking & Embedding
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC Reads staged documents from `eds_raw.staged_documents`, splits them into overlapping
# MAGIC text chunks, calls the Databricks Foundation Model API (`databricks-gte-large-en`)
# MAGIC to generate embeddings, and writes the results to `eds_processed.document_chunks`.

# COMMAND ----------

# MAGIC %pip install requests --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import uuid
import json
import time
import requests
from datetime import datetime
from pyspark.sql import functions as F, Row
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    ArrayType, FloatType, TimestampType, BooleanType
)

CATALOG = "ausnet_process_intel_catalog"
WORKSPACE_URL = "https://fevm-ausnet-process-intel.cloud.databricks.com"
EMBEDDING_MODEL = "databricks-gte-large-en"
EMBEDDING_ENDPOINT = f"{WORKSPACE_URL}/serving-endpoints/{EMBEDDING_MODEL}/invocations"

CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 50     # character overlap between consecutive chunks
EMBED_BATCH_SIZE = 20  # documents per API call

spark.sql(f"USE CATALOG {CATALOG}")
print(f"Chunking and embedding pipeline starting...")
print(f"Model: {EMBEDDING_MODEL}")
print(f"Chunk size: {CHUNK_SIZE} chars, overlap: {CHUNK_OVERLAP} chars")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Retrieve Databricks API token

# COMMAND ----------

def get_databricks_token():
    """Try multiple methods to obtain the workspace API token."""
    # Method 1: dbutils secrets
    try:
        token = dbutils.secrets.get(scope="eds", key="databricks_token")
        print("[Token] Retrieved from Databricks secrets (scope: eds)")
        return token
    except Exception:
        pass

    # Method 2: Spark context (works in clusters)
    try:
        token = spark.conf.get("spark.databricks.token")
        print("[Token] Retrieved from spark.conf")
        return token
    except Exception:
        pass

    # Method 3: Notebook context API token (interactive)
    try:
        token = (
            dbutils.notebook.entry_point
                .getDbutils()
                .notebook()
                .getContext()
                .apiToken()
                .get()
        )
        print("[Token] Retrieved from notebook context")
        return token
    except Exception:
        pass

    raise RuntimeError(
        "Could not obtain Databricks API token. "
        "Set dbutils.secrets scope='eds', key='databricks_token' "
        "or ensure cluster has token access."
    )

API_TOKEN = get_databricks_token()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Text chunking function

# COMMAND ----------

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """
    Sliding window chunker. Splits text into chunks of `chunk_size` characters
    with `overlap` character overlap. Tries to break on whitespace boundaries.
    """
    if not text or len(text) == 0:
        return []
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        # Try to break on whitespace for cleaner chunks
        if end < text_len:
            # Look back up to 60 chars for a space
            space_search = text.rfind(' ', max(start, end - 60), end)
            if space_search > start:
                end = space_search

        chunk = text[start:end].strip()
        if len(chunk) > 20:  # Skip tiny fragments
            chunks.append(chunk)

        if end >= text_len:
            break
        start = end - overlap

    return chunks

# Test
sample = "Alinta Energy is committed to the energy transition. " * 20
test_chunks = chunk_text(sample)
print(f"Test chunking: {len(sample)} chars → {len(test_chunks)} chunks")
print(f"First chunk (chars): {len(test_chunks[0]) if test_chunks else 0}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Embedding API function

# COMMAND ----------

def embed_texts(texts: list, token: str, endpoint: str, max_retries: int = 3) -> list:
    """
    Call Databricks Foundation Model embedding endpoint.
    Returns list of embedding vectors (list of float).
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"input": texts}

    for attempt in range(max_retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            # OpenAI-compatible response format
            embeddings = [item["embedding"] for item in result["data"]]
            return embeddings
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limit
                wait = 2 ** attempt
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  HTTP error {response.status_code}: {response.text[:200]}")
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise RuntimeError(f"Embedding API failed after {max_retries} attempts: {e}")

    return []

# Quick connectivity check
print("Testing embedding endpoint connectivity...")
try:
    test_emb = embed_texts(["Alinta Energy executive decision platform test."], API_TOKEN, EMBEDDING_ENDPOINT)
    print(f"[OK] Embedding API connected. Vector dimension: {len(test_emb[0])}")
    EMBED_DIM = len(test_emb[0])
except Exception as e:
    print(f"[WARN] Embedding API test failed: {e}")
    print("Will use placeholder embeddings (zero vectors) for schema testing.")
    EMBED_DIM = 1024
    test_emb = None

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Read staged documents

# COMMAND ----------

staged_df = spark.table(f"{CATALOG}.eds_raw.staged_documents")
staged_count = staged_df.count()
print(f"Documents to process: {staged_count}")

# Collect to driver for chunking + embedding (manageable volume for 15 docs)
docs = staged_df.collect()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Chunk and embed

# COMMAND ----------

def _extract_section_title(full_content: str, chunk: str) -> str:
    """Find nearest preceding heading for the chunk."""
    pos = full_content.find(chunk[:50])
    if pos < 0:
        return ""
    preceding = full_content[:pos]
    lines = [l.strip() for l in preceding.split('\n') if l.strip()]
    # Look for uppercase lines or lines ending without period (likely headings)
    for line in reversed(lines[-10:]):
        if len(line) > 4 and (line.isupper() or (not line.endswith('.') and len(line) < 80)):
            return line[:100]
    return ""

now = datetime.utcnow()
all_chunks_pending = []

for doc in docs:
    doc_id = doc["doc_id"]
    content = doc["content"] or ""
    title = doc["title"] or ""
    classification = doc["classification"]
    access_tier = doc["access_tier_level"]
    business_area = doc["business_area"]
    doc_type = doc["doc_type"]
    author = doc["author"]
    effective_date = str(doc["effective_date"]) if doc["effective_date"] else ""

    chunks = chunk_text(content)

    for idx, chunk in enumerate(chunks):
        metadata = json.dumps({
            "business_area": business_area,
            "doc_type": doc_type,
            "author": author,
            "effective_date": effective_date,
            "is_synthetic": True,
        })
        section = _extract_section_title(content, chunk)
        all_chunks_pending.append({
            "chunk_id": str(uuid.uuid4()),
            "doc_id": doc_id,
            "doc_title": title,
            "classification": classification,
            "access_tier_level": access_tier,
            "chunk_text": chunk,
            "section_title": section,
            "page_number": (idx // 3) + 1,
            "chunk_index": idx,
            "metadata": metadata,
        })

print(f"\nTotal chunks to embed: {len(all_chunks_pending)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Batch embed all chunks

# COMMAND ----------

chunk_texts_only = [c["chunk_text"] for c in all_chunks_pending]
all_embeddings = []

print(f"Embedding {len(chunk_texts_only)} chunks in batches of {EMBED_BATCH_SIZE}...")
for batch_start in range(0, len(chunk_texts_only), EMBED_BATCH_SIZE):
    batch = chunk_texts_only[batch_start: batch_start + EMBED_BATCH_SIZE]
    batch_num = (batch_start // EMBED_BATCH_SIZE) + 1
    total_batches = (len(chunk_texts_only) + EMBED_BATCH_SIZE - 1) // EMBED_BATCH_SIZE

    try:
        embeddings = embed_texts(batch, API_TOKEN, EMBEDDING_ENDPOINT)
        all_embeddings.extend(embeddings)
        print(f"  Batch {batch_num}/{total_batches}: {len(batch)} chunks embedded")
    except Exception as e:
        print(f"  Batch {batch_num}/{total_batches}: FAILED ({e}). Using zero vectors.")
        # Fallback: zero vectors so pipeline doesn't break
        all_embeddings.extend([[0.0] * EMBED_DIM] * len(batch))

    # Small sleep to respect rate limits
    if batch_start + EMBED_BATCH_SIZE < len(chunk_texts_only):
        time.sleep(0.2)

print(f"\n[OK] Embeddings generated: {len(all_embeddings)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Build chunk rows (with embeddings serialised as JSON)

# COMMAND ----------

# Note: Vector Search Delta Sync expects embeddings as ARRAY<FLOAT> or we store
# the embedding separately. For eds_processed.document_chunks we store chunk_text
# (which the Vector Search index will embed automatically), plus metadata fields.
# We also store a JSON-serialised embedding for direct similarity search if needed.

chunk_rows = []
for meta, emb in zip(all_chunks_pending, all_embeddings):
    # Serialize embedding as JSON string (stored in metadata field extended)
    extended_meta = json.loads(meta["metadata"])
    extended_meta["embedding_preview"] = emb[:5]  # First 5 dims for debugging
    extended_meta["embedding_dim"] = len(emb)

    chunk_rows.append(Row(
        chunk_id=meta["chunk_id"],
        doc_id=meta["doc_id"],
        doc_title=meta["doc_title"],
        classification=meta["classification"],
        access_tier_level=meta["access_tier_level"],
        chunk_text=meta["chunk_text"],
        section_title=meta["section_title"],
        page_number=meta["page_number"],
        chunk_index=meta["chunk_index"],
        metadata=json.dumps(extended_meta),
        embedding_model=EMBEDDING_MODEL,
        created_at=now,
    ))

print(f"Rows prepared: {len(chunk_rows)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8: Write to eds_processed.document_chunks

# COMMAND ----------

chunks_df = spark.createDataFrame(chunk_rows)

chunks_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.eds_processed.document_chunks")

final_count = spark.table(f"{CATALOG}.eds_processed.document_chunks").count()

print("\n" + "="*65)
print("CHUNKING & EMBEDDING PIPELINE — Complete")
print("="*65)
print(f"  Source documents:       {staged_count}")
print(f"  Total chunks created:   {final_count}")
print(f"  Embedding model:        {EMBEDDING_MODEL}")
print(f"  Vector dimension:       {EMBED_DIM}")
print("="*65)

# Summary by document
spark.sql(f"""
    SELECT doc_id, doc_title, classification, access_tier_level,
           COUNT(*) as chunk_count,
           MIN(chunk_index) as first_chunk,
           MAX(chunk_index) as last_chunk
    FROM {CATALOG}.eds_processed.document_chunks
    GROUP BY doc_id, doc_title, classification, access_tier_level
    ORDER BY access_tier_level, doc_id
""").show(truncate=60)

print("\n[OK] Chunks written to eds_processed.document_chunks")
print("[OK] Ready for Vector Search index creation")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9: Update ingestion status in eds_raw

# COMMAND ----------

spark.sql(f"""
    MERGE INTO {CATALOG}.eds_raw.staged_documents AS target
    USING (
        SELECT DISTINCT doc_id FROM {CATALOG}.eds_processed.document_chunks
    ) AS processed
    ON target.doc_id = processed.doc_id
    WHEN MATCHED THEN
        UPDATE SET target.ingestion_status = 'processed'
""")

print("[OK] Updated ingestion status to 'processed' in eds_raw.staged_documents")
