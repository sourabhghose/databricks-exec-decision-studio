# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — RAG Chain
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC Builds, logs, and evaluates the LangChain-based RAG chain that powers the
# MAGIC Executive Decision Studio. Uses Databricks Vector Search for retrieval and
# MAGIC `databricks-meta-llama-3-3-70b-instruct` for answer generation.

# COMMAND ----------

# MAGIC %pip install databricks-langchain langchain-core mlflow databricks-sdk --upgrade --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import mlflow
import json
from datetime import datetime
from databricks_langchain import DatabricksVectorSearch, ChatDatabricks
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, SystemMessage

CATALOG = "ausnet_process_intel_catalog"
WORKSPACE_URL = "https://fevm-ausnet-process-intel.cloud.databricks.com"

VS_ENDPOINT = "eds-vector-search"
VS_INDEX = f"{CATALOG}.eds_vectors.document_chunks_index"
LLM_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"
EMBEDDING_MODEL = "databricks-gte-large-en"

try:
    _username = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
except Exception:
    _username = "sourabh.ghose@databricks.com"
MLFLOW_EXPERIMENT = f"/Users/{_username}/EDS_rag_chain_experiment"
MODEL_NAME = f"{CATALOG}.eds_agents.rag_chain"

spark.sql(f"USE CATALOG {CATALOG}")

print("="*60)
print("EXECUTIVE DECISION STUDIO — RAG Chain Builder")
print("="*60)
print(f"  LLM:              {LLM_ENDPOINT}")
print(f"  Vector Search:    {VS_ENDPOINT}")
print(f"  Index:            {VS_INDEX}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Configure MLflow experiment

# COMMAND ----------

mlflow.set_experiment(MLFLOW_EXPERIMENT)
mlflow.langchain.autolog()
print(f"[OK] MLflow experiment: {MLFLOW_EXPERIMENT}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Initialise Vector Search retriever

# COMMAND ----------

def build_retriever(access_tier_level: int = 4, k: int = 6):
    """
    Build a DatabricksVectorSearch retriever filtered by access_tier_level.
    Users only see documents at or below their access tier
    (lower number = higher clearance, so users see docs where
     access_tier_level >= user_tier is NOT correct — we filter
     docs where access_tier_level >= user_access_tier,
     meaning the user can see all docs from their tier down to public).

    access_tier_level filter: retrieve docs where access_tier_level >= user_tier
    Tier 1 = Board (sees everything), Tier 4 = All staff (sees only tier 4)
    """
    vectorstore = DatabricksVectorSearch(
        endpoint=VS_ENDPOINT,
        index_name=VS_INDEX,
        columns=["chunk_id", "doc_id", "doc_title", "classification", "access_tier_level", "chunk_text", "section_title"],
    )

    # Build filter: user at access_tier_level X can see docs with access_tier_level >= X
    # (higher tier number = less restricted; tier 1 = most restricted/board only)
    filters = {"access_tier_level": {"$gte": access_tier_level}}

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
            "filter": filters,
        },
    )
    return retriever

# Test retriever build
print("Building retriever for tier 1 (Board)...")
try:
    retriever_test = build_retriever(access_tier_level=1, k=3)
    test_docs = retriever_test.invoke("Loy Yang B strategic options")
    print(f"[OK] Retriever working. Retrieved {len(test_docs)} documents for test query.")
    if test_docs:
        print(f"  First result: '{test_docs[0].metadata.get('doc_title', 'N/A')[:60]}'")
except Exception as e:
    print(f"[WARN] Retriever test: {e}")
    print("(Vector Search index may still be syncing — chain will work once index is ready)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Initialise the LLM

# COMMAND ----------

llm = ChatDatabricks(
    endpoint=LLM_ENDPOINT,
    max_tokens=2048,
    temperature=0.1,
)

# Quick LLM test
test_response = llm.invoke("In one sentence, what is Alinta Energy?")
print(f"[OK] LLM connected: {test_response.content[:120]}...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Build the RAG chain

# COMMAND ----------

SYSTEM_PROMPT = """You are the Alinta Energy Executive Decision Studio AI — a confidential strategic intelligence assistant for C-suite executives and Board members.

Your role is to provide concise, evidence-based answers drawing exclusively from the retrieved document context provided below. You support executive decision-making for one of Australia's leading energy companies, with assets across the National Electricity Market (NEM) and Western Australian Electricity Market (WEM).

## Instructions:
1. **Answer only from the context**: Do not use information outside the provided document excerpts. If the context does not contain sufficient information to answer, state this clearly.
2. **Cite your sources**: For every substantive claim, include an inline citation using the format [DOC-XXX] or [Document Title]. Multiple citations are encouraged.
3. **Be executive-grade**: Responses should be structured, precise, and suitable for C-suite consumption. Use bullet points, headers, and numbered lists where appropriate.
4. **Maintain confidentiality**: Do not reveal document classification levels or access tier information in your response.
5. **Quantify where possible**: Include specific numbers, dates, and financial figures from the context.
6. **Flag gaps**: If important information is missing from the retrieved context, explicitly note what additional documents or data sources would be needed for a complete answer.

## Context classification:
You are operating at access tier {access_tier} ({tier_label}). All retrieved documents are within your authorised access level.

## Retrieved context:
{context}

## User query:
{question}

## Response:"""

def format_docs(docs) -> str:
    """Format retrieved documents into a context string with source attribution."""
    if not docs:
        return "No relevant documents retrieved."

    formatted = []
    for i, doc in enumerate(docs, 1):
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        doc_title = metadata.get('doc_title', 'Unknown Document')
        doc_id = metadata.get('doc_id', f'DOC-{i:03d}')
        classification = metadata.get('classification', 'INTERNAL')
        section = metadata.get('section_title', '')

        section_str = f"\n  Section: {section}" if section else ""
        formatted.append(
            f"[{doc_id}] {doc_title} ({classification}){section_str}\n"
            f"---\n{doc.page_content}\n"
        )
    return "\n\n".join(formatted)

def build_rag_chain(access_tier_level: int = 4, tier_label: str = "All Staff"):
    """Build a complete RAG chain for the given access tier."""
    retriever = build_retriever(access_tier_level=access_tier_level, k=6)

    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

    chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
            "access_tier": RunnableLambda(lambda _: str(access_tier_level)),
            "tier_label": RunnableLambda(lambda _: tier_label),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

# Build chains for each tier
TIER_LABELS = {
    1: "Board / C-Suite",
    2: "Executive Leadership Team",
    3: "Senior Management",
    4: "All Staff",
}

print("Building RAG chains for all access tiers...")
chains = {}
for tier in [1, 2, 3, 4]:
    chains[tier] = build_rag_chain(access_tier_level=tier, tier_label=TIER_LABELS[tier])
    print(f"  [OK] Tier {tier} ({TIER_LABELS[tier]}) chain ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Test the chains

# COMMAND ----------

test_questions = [
    (1, "What are the strategic options for Loy Yang B and what does management recommend?"),
    (1, "What was Alinta's 1H FY25 EBITDA and how did it compare to the prior period?"),
    (2, "What is the status of the Yandin Wind Farm Stage 2 investment decision?"),
    (2, "How is the retail transformation programme tracking against plan?"),
    (3, "What is Alinta's current NPS score and the target?"),
]

print("\n" + "="*60)
print("RAG CHAIN TESTS")
print("="*60)

test_results = []
for tier, question in test_questions:
    print(f"\n[Tier {tier}] Q: {question}")
    try:
        answer = chains[tier].invoke(question)
        print(f"A: {answer[:300]}...")
        test_results.append({
            "tier": tier,
            "question": question,
            "answer": answer,
            "success": True,
        })
    except Exception as e:
        print(f"ERROR: {e}")
        test_results.append({
            "tier": tier,
            "question": question,
            "answer": str(e),
            "success": False,
        })

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Log the RAG chain with MLflow

# COMMAND ----------

# MLflow LangChain v1+ requires "models-from-code": the chain must be defined
# in a standalone Python file and the file path passed to log_model.

import os
import tempfile

# Write the chain definition to a temp file
CHAIN_CODE = f'''
import mlflow
from databricks_langchain import DatabricksVectorSearch, ChatDatabricks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

CATALOG = "{CATALOG}"
VS_ENDPOINT = "{VS_ENDPOINT}"
VS_INDEX = "{VS_INDEX}"
LLM_ENDPOINT = "{LLM_ENDPOINT}"

def build_chain():
    vectorstore = DatabricksVectorSearch(
        endpoint=VS_ENDPOINT,
        index_name=VS_INDEX,
        columns=["chunk_id", "doc_id", "doc_title", "classification", "access_tier_level", "chunk_text", "section_title"],
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={{"k": 6, "filter": {{"access_tier_level": {{"$gte": 1}}}}}},
    )

    prompt = ChatPromptTemplate.from_template(
        "You are the Alinta Energy Executive Decision Studio AI.\\n\\n"
        "Answer based on the context provided. Be concise and commercially direct.\\n\\n"
        "Context:\\n{{context}}\\n\\n"
        "Question: {{question}}"
    )
    llm = ChatDatabricks(endpoint=LLM_ENDPOINT, max_tokens=2048, temperature=0.1)

    def format_docs(docs):
        return "\\n\\n".join(
            f"[{{d.metadata.get('doc_id', 'N/A')}}] {{d.metadata.get('doc_title', '')}}\\n{{d.page_content}}"
            for d in docs
        )

    return (
        {{"context": retriever | format_docs, "question": RunnablePassthrough()}}
        | prompt
        | llm
        | StrOutputParser()
    )

chain = build_chain()
mlflow.models.set_model(chain)
'''

chain_file = tempfile.NamedTemporaryFile(mode="w", suffix="_rag_chain.py", delete=False)
chain_file.write(CHAIN_CODE)
chain_file.close()

from mlflow.models.signature import infer_signature

input_example = {"messages": [{"role": "user", "content": "What is Alinta's strategy for Loy Yang B?"}]}
sample_output = "Alinta Energy's strategy for Loy Yang B focuses on optimising asset performance while evaluating long-term transition options."
signature = infer_signature(input_example, sample_output)

print(f"\nLogging RAG chain to MLflow Unity Catalog model registry (models-from-code)...")

with mlflow.start_run(run_name="eds_rag_chain_v1") as run:
    mlflow.set_tags({
        "team": "Alinta Energy EDS",
        "model_type": "RAG Chain",
        "llm": LLM_ENDPOINT,
        "embedding_model": EMBEDDING_MODEL,
        "vector_search_index": VS_INDEX,
        "catalog": CATALOG,
    })
    mlflow.log_params({
        "chunk_size": 500,
        "chunk_overlap": 50,
        "retriever_k": 6,
        "llm_max_tokens": 2048,
        "llm_temperature": 0.1,
    })
    successful = sum(1 for r in test_results if r["success"])
    mlflow.log_metrics({
        "test_queries_total": len(test_results),
        "test_queries_successful": successful,
        "test_success_rate": successful / len(test_results) if test_results else 0,
    })

    model_info = mlflow.langchain.log_model(
        lc_model=chain_file.name,
        artifact_path="rag_chain",
        input_example=input_example,
        signature=signature,
        registered_model_name=MODEL_NAME,
    )
    print(f"[OK] Model logged. Run ID: {run.info.run_id}")
    print(f"[OK] Model URI: {model_info.model_uri}")
    run_id = run.info.run_id

os.unlink(chain_file.name)
print(f"\nMLflow run ID: {run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Sample evaluation with groundedness scoring

# COMMAND ----------

eval_qa_pairs = [
    {
        "question": "What was Alinta Energy's EBITDA guidance for FY25?",
        "expected": "$590-620 million",
        "tier": 1,
    },
    {
        "question": "How many MW is Yandin Wind Farm Stage 2?",
        "expected": "200 MW",
        "tier": 1,
    },
    {
        "question": "What is Alinta Energy's retail customer NPS?",
        "expected": "+18 or +22",
        "tier": 2,
    },
]

print("\n" + "="*60)
print("EVALUATION SAMPLE")
print("="*60)

eval_prompt = ChatPromptTemplate.from_template("""
You are evaluating whether a RAG system's answer is grounded in the retrieved context.

Question: {question}
Expected answer contains: {expected}
System answer: {answer}

Rate on a 0.0 to 1.0 scale whether the system answer:
1. Contains the key information expected (0-0.5 points)
2. Provides accurate citations or references (0-0.25 points)
3. Does not hallucinate beyond the expected content (0-0.25 points)

Respond with ONLY a JSON object: {{"score": 0.0, "reason": "brief explanation"}}
""")

eval_chain = eval_prompt | llm | StrOutputParser()

for qa in eval_qa_pairs:
    try:
        answer = chains[qa["tier"]].invoke(qa["question"])
        eval_input = {
            "question": qa["question"],
            "expected": qa["expected"],
            "answer": answer[:1000],
        }
        eval_response = eval_chain.invoke(eval_input)
        try:
            eval_json = json.loads(eval_response.strip())
            score = eval_json.get("score", 0)
            reason = eval_json.get("reason", "")
        except Exception:
            score = 0.0
            reason = eval_response[:100]

        print(f"\nQ: {qa['question']}")
        print(f"Expected: {qa['expected']}")
        print(f"Score: {score:.2f} | {reason}")
    except Exception as e:
        print(f"\nQ: {qa['question']} — EVAL ERROR: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("\n" + "="*65)
print("RAG CHAIN SETUP — Complete")
print("="*65)
print(f"  LLM endpoint:       {LLM_ENDPOINT}")
print(f"  Vector Search:      {VS_ENDPOINT}")
print(f"  Index:              {VS_INDEX}")
print(f"  Access tiers:       1 (Board) through 4 (All Staff)")
print(f"  MLflow model:       {MODEL_NAME}")
print(f"  MLflow run ID:      {run_id}")
print("="*65)
print("\nNext step: Run notebooks/03_agents/ to deploy specialist agents.")

dbutils.notebook.exit(f"model_uri={MODEL_NAME}")
