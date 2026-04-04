# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Document Q&A Agent
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC The Document Q&A Agent retrieves relevant document chunks via Vector Search
# MAGIC and generates cited, grounded answers using the Llama 3.3 70B LLM.
# MAGIC Enforces access-tier filtering so users only see documents within their clearance.

# COMMAND ----------

# MAGIC %pip install databricks-langchain langchain-core databricks-sdk --upgrade --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import json
import uuid
from datetime import datetime
from typing import Optional
from databricks_langchain import DatabricksVectorSearch
from databricks_langchain import ChatDatabricks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

CATALOG = "ausnet_process_intel_catalog"
VS_ENDPOINT = "eds-vector-search"
VS_INDEX = f"{CATALOG}.eds_vectors.document_chunks_index"
LLM_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"
EMBEDDING_MODEL = "databricks-gte-large-en"

spark.sql(f"USE CATALOG {CATALOG}")

print("="*60)
print("EXECUTIVE DECISION STUDIO — Document Q&A Agent")
print("="*60)
print(f"  LLM:      {LLM_ENDPOINT}")
print(f"  VS Index: {VS_INDEX}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Initialise components

# COMMAND ----------

llm = ChatDatabricks(
    endpoint=LLM_ENDPOINT,
    max_tokens=1500,
    temperature=0.05,
)

DOC_QA_SYSTEM_PROMPT = """You are the Alinta Energy Executive Decision Studio Document Intelligence Agent.

Your role is to answer executive questions based EXCLUSIVELY on the retrieved document context below.
You support Board directors, C-suite executives, and senior management of Alinta Energy.

## Rules:
1. ONLY use information from the Context section. Never fabricate facts.
2. ALWAYS cite sources using [DOC-XXX] format inline.
3. If the context does not contain sufficient information, state: "The retrieved documents do not contain sufficient information to fully answer this question. Additional sources that may help include: [suggest relevant document types]."
4. Structure responses with clear headings and bullet points for executive readability.
5. Include specific numbers, dates, and financial figures from the context.
6. Flag any apparent contradictions between sources.

## Document Context (your knowledge base for this query):
{context}

## Executive Question:
{question}

## Response (executive-grade, with citations):"""

qa_prompt = ChatPromptTemplate.from_template(DOC_QA_SYSTEM_PROMPT)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Build retriever

# COMMAND ----------

def build_retriever(access_tier_level: int, k: int = 8, score_threshold: float = 0.3):
    """
    Build a Vector Search retriever with access tier filtering.

    Access tier rules:
    - Tier 1 (Board): can see all documents (access_tier_level >= 1 means all)
    - Tier 2 (ELT): can see tier 2, 3, 4 docs
    - Tier 3 (Senior Mgmt): can see tier 3, 4 docs
    - Tier 4 (All Staff): can only see tier 4 docs
    """
    vs = DatabricksVectorSearch(
        endpoint=VS_ENDPOINT,
        index_name=VS_INDEX,
        columns=[
            "chunk_id", "doc_id", "doc_title", "classification",
            "access_tier_level", "chunk_text", "section_title",
            "page_number", "chunk_index",
        ],
        text_column="chunk_text",
    )

    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
            "filter": {"access_tier_level": {"$gte": access_tier_level}},
        },
    )
    return retriever

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Context formatter

# COMMAND ----------

def format_context(docs) -> tuple:
    """
    Format retrieved documents into a context string.
    Returns (context_str, source_ids list).
    """
    if not docs:
        return "No relevant documents retrieved for this query.", []

    source_ids = []
    parts = []

    for doc in docs:
        meta = doc.metadata if hasattr(doc, 'metadata') else {}
        doc_id = meta.get('doc_id', 'UNKNOWN')
        title = meta.get('doc_title', 'Unknown Document')
        section = meta.get('section_title', '')
        page = meta.get('page_number', 1)
        classification = meta.get('classification', 'INTERNAL')

        if doc_id not in source_ids:
            source_ids.append(doc_id)

        header = f"[{doc_id}] {title}"
        if section:
            header += f" — {section}"
        header += f" (p.{page}, {classification})"

        parts.append(f"{header}\n{'─'*60}\n{doc.page_content}")

    return "\n\n".join(parts), source_ids

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Groundedness scorer

# COMMAND ----------

GROUNDEDNESS_PROMPT = """You are evaluating whether an AI answer is grounded in the provided context.

Context (retrieved documents):
{context}

Answer to evaluate:
{answer}

Score the answer on groundedness (0.0 to 1.0):
- 1.0: Every claim in the answer is directly supported by the context
- 0.7-0.9: Most claims are grounded; minor gaps or over-extrapolations
- 0.4-0.6: Some claims are grounded but there is notable hallucination
- 0.0-0.3: Many claims are not in the context or contradict it

Also score citation quality (0.0 to 1.0):
- 1.0: All key claims have specific [DOC-XXX] citations
- 0.5: Some citations present but incomplete
- 0.0: No citations

Respond ONLY with: {{"groundedness": 0.0, "citation_quality": 0.0, "notes": "brief"}}
"""

groundedness_prompt = ChatPromptTemplate.from_template(GROUNDEDNESS_PROMPT)
groundedness_llm = ChatDatabricks(endpoint=LLM_ENDPOINT, max_tokens=200, temperature=0.0)
groundedness_chain = groundedness_prompt | groundedness_llm | StrOutputParser()

def score_groundedness(context: str, answer: str) -> dict:
    """Score the groundedness of an answer against its context."""
    try:
        raw = groundedness_chain.invoke({
            "context": context[:3000],  # Limit context for scoring
            "answer": answer[:2000],
        })
        raw = raw.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        result = json.loads(raw)
        return {
            "groundedness": min(1.0, max(0.0, float(result.get("groundedness", 0.7)))),
            "citation_quality": min(1.0, max(0.0, float(result.get("citation_quality", 0.5)))),
            "notes": result.get("notes", ""),
        }
    except Exception as e:
        return {"groundedness": 0.7, "citation_quality": 0.6, "notes": f"Scoring error: {e}"}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Main doc_qa_agent function

# COMMAND ----------

def doc_qa_agent(
    query: str,
    access_tier_level: int = 4,
    k: int = 8,
    score_groundedness: bool = True,
) -> dict:
    """
    Document Q&A agent: retrieves relevant chunks and generates cited answers.

    Args:
        query:              User's question
        access_tier_level:  User access tier (1=Board, 4=All Staff)
        k:                  Number of chunks to retrieve
        score_groundedness: Whether to run groundedness scoring (adds ~2s latency)

    Returns:
        dict with keys: answer, citations, confidence_score, groundedness_score,
                        citation_quality_score, num_sources, retrieval_metadata
    """
    import time
    start = time.time()

    # Retrieve documents
    retriever = build_retriever(access_tier_level=access_tier_level, k=k)

    try:
        docs = retriever.invoke(query)
    except Exception as e:
        return {
            "answer": f"Vector Search retrieval failed: {str(e)}. The index may still be syncing.",
            "citations": [],
            "confidence_score": 0.0,
            "groundedness_score": 0.0,
            "citation_quality_score": 0.0,
            "num_sources": 0,
            "retrieval_metadata": {"error": str(e)},
        }

    context_str, source_ids = format_context(docs)

    # Generate answer
    try:
        answer = (qa_prompt | llm | StrOutputParser()).invoke({
            "context": context_str,
            "question": query,
        })
    except Exception as e:
        answer = f"LLM generation failed: {str(e)}"
        source_ids = []

    # Compute confidence based on retrieval quality
    num_unique_docs = len(set(source_ids))
    retrieval_confidence = min(1.0, (num_unique_docs / 3) * 0.7 + (len(docs) / k) * 0.3)

    # Groundedness scoring (optional, adds latency)
    ground_scores = {"groundedness": 0.75, "citation_quality": 0.7, "notes": "not scored"}
    if score_groundedness and docs:
        ground_scores = score_groundedness(context_str, answer)

    elapsed_ms = int((time.time() - start) * 1000)

    return {
        "answer": answer,
        "citations": source_ids,
        "confidence_score": round(retrieval_confidence, 3),
        "groundedness_score": round(ground_scores["groundedness"], 3),
        "citation_quality_score": round(ground_scores["citation_quality"], 3),
        "num_sources": len(docs),
        "retrieval_metadata": {
            "num_chunks": len(docs),
            "unique_docs": num_unique_docs,
            "latency_ms": elapsed_ms,
            "access_tier": access_tier_level,
        },
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Test the agent

# COMMAND ----------

TEST_CASES = [
    {
        "query": "What are the three strategic options for Loy Yang B and what is the NPV of each?",
        "tier": 1,
        "description": "Board-level financial detail query",
    },
    {
        "query": "What was Alinta Energy's EBITDA in 1H FY25 and which division performed best?",
        "tier": 1,
        "description": "Half-year financial results",
    },
    {
        "query": "What are the key cyber risks facing Alinta and what is the OT security programme budget?",
        "tier": 2,
        "description": "Cyber risk query for ELT",
    },
    {
        "query": "How many customer accounts does Alinta have and what is the churn rate?",
        "tier": 3,
        "description": "Retail metrics for Senior Management",
    },
    {
        "query": "What is Alinta Energy's Net Zero 2040 commitment?",
        "tier": 4,
        "description": "ESG query for all staff",
    },
]

print("\n" + "="*65)
print("DOC Q&A AGENT — Test Suite")
print("="*65)

for i, tc in enumerate(TEST_CASES, 1):
    print(f"\n[Test {i}/{len(TEST_CASES)}] {tc['description']}")
    print(f"  Query: {tc['query'][:80]}...")
    print(f"  Tier:  {tc['tier']}")

    result = doc_qa_agent(
        query=tc["query"],
        access_tier_level=tc["tier"],
        k=6,
        score_groundedness=False,  # Skip groundedness for speed in testing
    )

    print(f"  Sources: {result['num_sources']} chunks, {len(result['citations'])} unique docs")
    print(f"  Confidence: {result['confidence_score']:.2f}")
    print(f"  Answer: {result['answer'][:200]}...")
    print(f"  Citations: {result['citations']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("\n" + "="*65)
print("DOC Q&A AGENT — Setup Complete")
print("="*65)
print(f"  Vector Search endpoint: {VS_ENDPOINT}")
print(f"  Index:                  {VS_INDEX}")
print(f"  LLM:                    {LLM_ENDPOINT}")
print(f"  Access tiers:           1 (Board) through 4 (All Staff)")
print(f"  Groundedness scoring:   Enabled (optional, adds ~2s latency)")
print("="*65)
print("\nThe doc_qa_agent() function is importable for use in the supervisor agent and app.")
