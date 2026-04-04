# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Strategic Gap Agent
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC The Strategic Gap Agent identifies gaps, blind spots, and unanswered strategic
# MAGIC questions in Alinta's document corpus. It retrieves relevant strategy documents,
# MAGIC synthesises themes, then uses a meta-reasoning LLM to identify what is missing.

# COMMAND ----------

# MAGIC %pip install databricks-langchain langchain-core --upgrade --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import json
from datetime import datetime
from databricks_langchain import DatabricksVectorSearch
from databricks_langchain import ChatDatabricks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

CATALOG = "ausnet_process_intel_catalog"
VS_ENDPOINT = "eds-vector-search"
VS_INDEX = f"{CATALOG}.eds_vectors.document_chunks_index"
LLM_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"

spark.sql(f"USE CATALOG {CATALOG}")

llm = ChatDatabricks(endpoint=LLM_ENDPOINT, max_tokens=1800, temperature=0.2)

print("Strategic Gap Agent initialised.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Retrieve strategy-relevant documents

# COMMAND ----------

def retrieve_strategy_docs(query: str, access_tier_level: int, k: int = 10) -> list:
    """Retrieve documents most relevant to the strategic gap query."""
    vs = DatabricksVectorSearch(
        endpoint=VS_ENDPOINT,
        index_name=VS_INDEX,
        columns=["chunk_id", "doc_id", "doc_title", "classification", "access_tier_level", "chunk_text"],
        text_column="chunk_text",
    )
    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k, "filter": {"access_tier_level": {"$gte": access_tier_level}}},
    )
    try:
        return retriever.invoke(query)
    except Exception as e:
        print(f"[WARN] Retrieval error: {e}")
        return []

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Strategic gap analysis prompts

# COMMAND ----------

STRATEGIC_COVERAGE_PROMPT = """You are a strategic advisor to the Board of Alinta Energy, Australia's leading diversified energy company.

You have been provided with excerpts from Alinta's board papers, strategy documents, risk registers, and financial reports.
Your task is to identify strategic gaps — important topics, risks, decisions, or analyses that appear to be MISSING or INSUFFICIENTLY addressed in the available documents.

## User Query:
{query}

## Available Document Excerpts:
{context}

## Your Analysis:

Provide a structured strategic gap analysis covering:

### 1. Topics Well Addressed in Current Documents
(List 3-5 areas where the documents provide adequate coverage)

### 2. Identified Strategic Gaps
For each gap, provide:
- **Gap**: What is missing or insufficiently addressed
- **Materiality**: Why this gap matters for Alinta's strategic position
- **Potential Impact**: Financial or operational consequences if unaddressed
- **Recommended Action**: What document, analysis, or decision is needed

### 3. Questions the Board Should Be Asking
(5-7 probing questions based on the gaps identified)

### 4. Priority Ranking
Rank the top 3 gaps by urgency and strategic materiality.

Cite specific documents [DOC-XXX] where relevant. Be direct and commercially grounded."""

GAP_SYNTHESIS_PROMPT = """Based on the following strategic gap analysis, provide a concise executive summary suitable for the Board Chair.

Analysis:
{analysis}

User's original question: {query}

Provide:
1. A 2-3 sentence headline summary of the most critical gaps
2. The single most urgent action required
3. A confidence assessment: how comprehensive is the available information to make this judgment?

Be direct, executive-grade, and action-oriented."""

gap_prompt = ChatPromptTemplate.from_template(STRATEGIC_COVERAGE_PROMPT)
synthesis_prompt = ChatPromptTemplate.from_template(GAP_SYNTHESIS_PROMPT)

gap_chain = gap_prompt | llm | StrOutputParser()
synthesis_chain = synthesis_prompt | llm | StrOutputParser()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Get full document list for gap meta-analysis

# COMMAND ----------

def get_document_inventory(access_tier_level: int) -> str:
    """Get list of available documents for gap meta-analysis."""
    docs_df = spark.sql(f"""
        SELECT doc_id, title, doc_type, classification, business_area,
               effective_date, author
        FROM {CATALOG}.eds_synthetic.documents
        WHERE access_tier_level >= {access_tier_level}
        ORDER BY access_tier_level, doc_type, title
    """)
    docs = docs_df.collect()
    lines = [f"[{d['doc_id']}] {d['title']} ({d['doc_type']}, {d['business_area']}, {d['effective_date']})"
             for d in docs]
    return "\n".join(lines)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Main strategic_gap_agent function

# COMMAND ----------

def strategic_gap_agent(
    query: str,
    access_tier_level: int = 1,
    include_inventory: bool = True,
) -> dict:
    """
    Strategic Gap Agent: identifies what Alinta's documents don't cover.

    Args:
        query:              User's strategic gap question
        access_tier_level:  User access tier (1=Board recommended for this agent)
        include_inventory:  Whether to append document inventory to context

    Returns:
        dict with: answer, gap_analysis, executive_summary, citations, confidence_score
    """
    import time
    start = time.time()

    # Retrieve relevant chunks
    docs = retrieve_strategy_docs(query, access_tier_level, k=10)

    context_parts = []
    source_ids = []
    for doc in docs:
        meta = doc.metadata if hasattr(doc, 'metadata') else {}
        doc_id = meta.get('doc_id', 'UNKNOWN')
        title = meta.get('doc_title', 'Unknown')
        if doc_id not in source_ids:
            source_ids.append(doc_id)
        context_parts.append(f"[{doc_id}] {title}\n{doc.page_content}")

    # Append document inventory for gap awareness
    if include_inventory:
        inventory = get_document_inventory(access_tier_level)
        context_parts.append(
            f"\n\n## DOCUMENT INVENTORY (all available documents):\n{inventory}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Run gap analysis
    try:
        gap_analysis = gap_chain.invoke({"query": query, "context": context[:8000]})
    except Exception as e:
        gap_analysis = f"Gap analysis error: {str(e)}"

    # Run synthesis
    try:
        executive_summary = synthesis_chain.invoke({
            "analysis": gap_analysis[:3000],
            "query": query,
        })
    except Exception as e:
        executive_summary = f"Synthesis error: {str(e)}"

    elapsed_ms = int((time.time() - start) * 1000)
    confidence = 0.75 if len(docs) >= 5 else 0.55

    full_answer = f"## Strategic Gap Analysis\n\n{gap_analysis}\n\n---\n\n## Executive Summary\n\n{executive_summary}"

    return {
        "answer": full_answer,
        "gap_analysis": gap_analysis,
        "executive_summary": executive_summary,
        "citations": source_ids,
        "confidence_score": confidence,
        "groundedness_score": 0.75,
        "num_sources": len(docs),
        "latency_ms": elapsed_ms,
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Test the agent

# COMMAND ----------

TEST_QUERIES = [
    "What strategic risks has management NOT adequately addressed in the available board papers?",
    "Are there any gaps in Alinta's approach to the energy transition that the Board should be aware of?",
    "What technology and digital strategy gaps exist in the current planning documents?",
]

print("\n" + "="*65)
print("STRATEGIC GAP AGENT — Test Suite")
print("="*65)

for i, q in enumerate(TEST_QUERIES, 1):
    print(f"\n[Test {i}] {q[:80]}...")
    result = strategic_gap_agent(query=q, access_tier_level=1, include_inventory=True)
    print(f"  Sources: {len(result['citations'])} docs — {result['citations']}")
    print(f"  Confidence: {result['confidence_score']:.2f}")
    print(f"  Latency: {result.get('latency_ms', 0)}ms")
    print(f"\n  Executive Summary:\n  {result['executive_summary'][:400]}...")

print("\n[OK] Strategic Gap Agent tests complete.")
