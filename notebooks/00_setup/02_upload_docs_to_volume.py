# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Upload Documents to Volume
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC Reads document content from `eds_synthetic.documents` and writes each document
# MAGIC as a plain-text file to the Unity Catalog volume at:
# MAGIC
# MAGIC ```
# MAGIC /Volumes/ausnet_process_intel_catalog/eds_raw/documents/
# MAGIC   tier1/   ← Board / C-Suite (RESTRICTED & CONFIDENTIAL tier-1 docs)
# MAGIC   tier2/   ← Executive Leadership Team
# MAGIC   tier3/   ← Senior Management
# MAGIC   tier4/   ← All Staff
# MAGIC ```
# MAGIC
# MAGIC Each file is named `{doc_id}.txt` and prefixed with a YAML-style header block
# MAGIC so the ingestion notebook can recover metadata without a separate lookup.

# COMMAND ----------

import os
from datetime import datetime

CATALOG = "ausnet_process_intel_catalog"
VOLUME_ROOT = f"/Volumes/{CATALOG}/eds_raw/documents"

spark.sql(f"USE CATALOG {CATALOG}")

print("="*60)
print("EDS — Upload Documents to Volume")
print("="*60)
print(f"Target volume: {VOLUME_ROOT}")
print(f"Started:       {datetime.utcnow().isoformat()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Create tier subdirectories

# COMMAND ----------

for tier in ["tier1", "tier2", "tier3", "tier4"]:
    path = f"{VOLUME_ROOT}/{tier}"
    dbutils.fs.mkdirs(path)
    print(f"[OK] {path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Read all documents from the synthetic registry

# COMMAND ----------

docs_df = spark.table(f"{CATALOG}.eds_synthetic.documents").select(
    "doc_id", "title", "doc_type", "classification",
    "access_tier_level", "business_area", "effective_date",
    "author", "version", "source_system", "content"
)

docs = docs_df.collect()
print(f"Found {len(docs)} documents in eds_synthetic.documents")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Write each document as a .txt file with YAML frontmatter

# COMMAND ----------

TIER_LABELS = {1: "Board / C-Suite", 2: "Executive Leadership Team", 3: "Senior Management", 4: "All Staff"}

uploaded = []
skipped = []

for row in docs:
    tier = row["access_tier_level"] or 4
    folder = f"{VOLUME_ROOT}/tier{tier}"
    file_path = f"{folder}/{row['doc_id']}.txt"

    # Build YAML-style frontmatter header
    header = f"""---
doc_id: {row["doc_id"]}
title: {row["title"]}
doc_type: {row["doc_type"]}
classification: {row["classification"]}
access_tier_level: {tier}
access_tier_label: {TIER_LABELS.get(tier, "Unknown")}
business_area: {row["business_area"] or ""}
effective_date: {row["effective_date"]}
author: {row["author"] or ""}
version: {row["version"] or "v1.0"}
source_system: {row["source_system"] or "Manual"}
is_synthetic: true
uploaded_at: {datetime.utcnow().isoformat()}
---

"""
    full_content = header + (row["content"] or "")

    try:
        dbutils.fs.put(file_path, full_content, overwrite=True)
        uploaded.append(row["doc_id"])
    except Exception as e:
        print(f"[ERROR] {row['doc_id']}: {e}")
        skipped.append(row["doc_id"])

print(f"\n[OK] Uploaded: {len(uploaded)} files")
if skipped:
    print(f"[WARN] Skipped:  {len(skipped)} files: {skipped}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Verify — list all uploaded files

# COMMAND ----------

print("\nVolume contents:")
total = 0
for tier in ["tier1", "tier2", "tier3", "tier4"]:
    path = f"{VOLUME_ROOT}/{tier}"
    try:
        files = dbutils.fs.ls(path)
        count = len(files)
        total += count
        print(f"\n  {path}/ ({count} files)")
        for f in files:
            size_kb = f.size / 1024
            print(f"    {f.name:25s}  {size_kb:6.1f} KB")
    except Exception:
        print(f"\n  {path}/ (empty or not found)")

print(f"\nTotal files in volume: {total}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("\n" + "="*60)
print("DOCUMENT UPLOAD — Complete")
print("="*60)
print(f"  Volume:    {VOLUME_ROOT}")
print(f"  Uploaded:  {len(uploaded)} documents")
print(f"  Format:    YAML frontmatter + plain text content")
print(f"  Structure: tier1/ tier2/ tier3/ tier4/")
print("="*60)
print("\nNext step: Run eds_ingestion_job to ingest from volume.")
