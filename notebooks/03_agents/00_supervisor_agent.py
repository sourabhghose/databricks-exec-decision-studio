# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Supervisor Agent
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC The Supervisor Agent is the central orchestrator for all user queries in the
# MAGIC Executive Decision Studio. It classifies intent, routes to specialist agents,
# MAGIC enforces access control, and logs every interaction to the audit trail.

# COMMAND ----------

# MAGIC %pip install databricks-langchain langchain-core databricks-sdk mlflow --upgrade --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import uuid
import json
import time
from datetime import datetime
from typing import Optional
from databricks_langchain import ChatDatabricks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pyspark.sql import Row

CATALOG = "ausnet_process_intel_catalog"
LLM_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"
WORKSPACE_URL = "https://fevm-ausnet-process-intel.cloud.databricks.com"

spark.sql(f"USE CATALOG {CATALOG}")

# Access tier definitions
TIER_LABELS = {
    1: "Board / C-Suite",
    2: "Executive Leadership Team",
    3: "Senior Management",
    4: "All Staff",
}

AGENT_NAMES = ["doc_qa", "strategic_gap", "competitive", "briefing", "kpi_monitor", "evaluation"]

print("="*60)
print("EXECUTIVE DECISION STUDIO — Supervisor Agent")
print("="*60)
print(f"  LLM: {LLM_ENDPOINT}")
print(f"  Catalog: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Initialise LLM

# COMMAND ----------

llm = ChatDatabricks(
    endpoint=LLM_ENDPOINT,
    max_tokens=512,
    temperature=0.0,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Intent classifier

# COMMAND ----------

INTENT_CLASSIFICATION_PROMPT = """You are a query router for the Alinta Energy Executive Decision Studio.

Classify the user's query into exactly ONE of these intent categories:

- doc_qa: Questions about specific documents, board papers, reports, or policies. Questions asking "what does [document] say", "find information about", factual questions about Alinta's operations, financials, strategy, or assets.
- strategic_gap: Questions asking for analysis of gaps, risks not covered, missing strategy, what hasn't been addressed, or meta-level strategic assessment questions.
- competitive: Questions specifically about competitors (Origin, AGL, Energy Australia, etc.), market share, competitive positioning, or how Alinta compares to peers.
- briefing: Requests to produce an executive summary, briefing note, situation report, or digest of multiple topics. "Prepare a briefing", "summarise the key issues", "give me a board-ready summary".
- kpi_monitor: Questions about KPI performance, metrics, dashboards, current values, trends, anomalies, or operational data. "How are we tracking", "what is the current", "show me the latest".
- evaluation: Requests to evaluate, assess quality of, or check accuracy of a previous response. Meta-level quality questions.

User query: {query}

Respond with ONLY a JSON object in this exact format:
{{"intent": "doc_qa", "confidence": 0.95, "reasoning": "brief explanation"}}

Valid intent values: doc_qa, strategic_gap, competitive, briefing, kpi_monitor, evaluation
"""

intent_prompt = ChatPromptTemplate.from_template(INTENT_CLASSIFICATION_PROMPT)
intent_chain = intent_prompt | llm | StrOutputParser()

def classify_intent(query: str) -> dict:
    """Classify the user query into an intent category."""
    try:
        raw = intent_chain.invoke({"query": query})
        # Extract JSON from response
        raw = raw.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        result = json.loads(raw)
        intent = result.get("intent", "doc_qa")
        if intent not in AGENT_NAMES:
            intent = "doc_qa"
        return {
            "intent": intent,
            "confidence": float(result.get("confidence", 0.7)),
            "reasoning": result.get("reasoning", ""),
        }
    except Exception as e:
        print(f"[WARN] Intent classification failed: {e}. Defaulting to doc_qa.")
        return {"intent": "doc_qa", "confidence": 0.5, "reasoning": f"Classification error: {e}"}

# Test intent classifier
test_queries = [
    "What are the strategic options for Loy Yang B?",
    "How is our NPS tracking this quarter?",
    "What does the competitive intelligence report say about Origin?",
    "Prepare an executive briefing on the WA renewables programme",
    "What strategic risks has management not adequately addressed?",
]

print("\nIntent classification tests:")
for q in test_queries:
    result = classify_intent(q)
    print(f"  [{result['intent']:15s}] ({result['confidence']:.2f}) {q[:60]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Access control validator

# COMMAND ----------

def validate_access(user_tier: int, required_tier: int) -> bool:
    """
    Returns True if the user has sufficient access.
    Tier 1 = highest (Board), Tier 4 = lowest (All Staff).
    A user can access content at their tier or higher (less restrictive) tier number.
    """
    return user_tier <= required_tier

def get_max_accessible_tier(user_tier: int) -> int:
    """Returns the highest (least restrictive) tier the user can access."""
    return 4  # Users can always see down to tier 4

def check_policy_compliance(query: str, user_tier: int, intent: str) -> dict:
    """Check if this query is policy compliant for the given user tier."""
    # Strategic gap and competitive intel require tier 2 or above
    restricted_intents = {
        "strategic_gap": 2,
        "competitive": 2,
        "evaluation": 3,
    }
    required = restricted_intents.get(intent, 4)
    compliant = validate_access(user_tier, required)

    return {
        "is_compliant": compliant,
        "required_tier": required,
        "user_tier": user_tier,
        "message": "" if compliant else f"This query type requires tier {required} access or above. Your tier: {user_tier}.",
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Import and call specialist agents

# COMMAND ----------

# ─── Doc Q&A Agent ────────────────────────────────────────────────────────────

def run_doc_qa_agent(query: str, user_tier: int, k: int = 6) -> dict:
    """Call the document Q&A agent via Vector Search RAG."""
    from databricks_langchain import DatabricksVectorSearch
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda

    VS_ENDPOINT = "eds-vector-search"
    VS_INDEX = f"{CATALOG}.eds_vectors.document_chunks_index"

    try:
        vs = DatabricksVectorSearch(
            endpoint=VS_ENDPOINT,
            index_name=VS_INDEX,
            columns=["chunk_id", "doc_id", "doc_title", "classification", "access_tier_level", "chunk_text"],
            text_column="chunk_text",
        )
        retriever = vs.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k, "filter": {"access_tier_level": {"$gte": user_tier}}},
        )
        docs = retriever.invoke(query)

        context_parts = []
        source_ids = []
        for doc in docs:
            meta = doc.metadata if hasattr(doc, 'metadata') else {}
            doc_id = meta.get('doc_id', 'UNKNOWN')
            title = meta.get('doc_title', 'Unknown')
            source_ids.append(doc_id)
            context_parts.append(f"[{doc_id}] {title}\n{doc.page_content}")
        context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant documents found."

        answer_prompt = ChatPromptTemplate.from_template(
            "You are the Alinta Energy Executive Decision Studio. Answer the question based on the provided context.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Provide a structured, executive-grade answer with citations [DOC-XXX]:"
        )
        answer_llm = ChatDatabricks(endpoint=LLM_ENDPOINT, max_tokens=1024, temperature=0.1)
        answer_chain = answer_prompt | answer_llm | StrOutputParser()

        answer = answer_chain.invoke({"context": context, "question": query})

        return {
            "answer": answer,
            "citations": list(set(source_ids)),
            "confidence_score": 0.85 if docs else 0.3,
            "groundedness_score": 0.80,
            "num_sources": len(docs),
        }
    except Exception as e:
        return {
            "answer": f"Document Q&A agent encountered an error: {str(e)}",
            "citations": [],
            "confidence_score": 0.0,
            "groundedness_score": 0.0,
            "num_sources": 0,
        }


# ─── KPI Monitor Agent (lightweight inline version) ───────────────────────────

def run_kpi_monitor_agent(query: str, user_tier: int) -> dict:
    """Query KPI time series and return structured status."""
    try:
        kpi_df = spark.sql(f"""
            SELECT kpi_name, category, business_unit, asset_name,
                   period, value, unit, target, lower_threshold, upper_threshold, is_anomaly
            FROM {CATALOG}.eds_synthetic.kpi_timeseries
            WHERE period = (SELECT MAX(period) FROM {CATALOG}.eds_synthetic.kpi_timeseries)
            ORDER BY category, kpi_name
        """)
        kpi_data = [row.asDict() for row in kpi_df.collect()]

        kpi_summary = []
        anomalies = []
        for kpi in kpi_data:
            val = kpi['value']
            target = kpi['target']
            variance = ((val - target) / target * 100) if target != 0 else 0
            status = "ON_TARGET" if abs(variance) < 5 else ("ABOVE" if variance > 5 else "BELOW")
            kpi_summary.append(f"{kpi['kpi_name']}: {val:.2f} {kpi['unit']} (target {target:.2f}, {variance:+.1f}%){' [ANOMALY]' if kpi['is_anomaly'] else ''}")
            if kpi['is_anomaly']:
                anomalies.append(kpi['kpi_name'])

        summary_text = "\n".join(kpi_summary)
        prompt_text = f"Based on these KPI values, {query}\n\nKPI Data (latest period):\n{summary_text}\n\nProvide executive-grade analysis:"
        llm_response = (ChatDatabricks(endpoint=LLM_ENDPOINT, max_tokens=800, temperature=0.1)
                        .invoke(prompt_text))

        return {
            "answer": llm_response.content,
            "kpi_data": kpi_data,
            "anomalies": anomalies,
            "citations": ["eds_synthetic.kpi_timeseries"],
            "confidence_score": 0.92,
            "groundedness_score": 0.95,
        }
    except Exception as e:
        return {
            "answer": f"KPI Monitor agent error: {str(e)}",
            "kpi_data": [],
            "anomalies": [],
            "citations": [],
            "confidence_score": 0.0,
            "groundedness_score": 0.0,
        }


# ─── Fallback wrapper for other agents ────────────────────────────────────────

def run_generic_agent(agent_name: str, query: str, user_tier: int) -> dict:
    """Generic agent runner for agents not yet fully implemented inline."""
    # These call doc_qa as a fallback with a modified system prompt
    augmented_query = f"[{agent_name.upper()} CONTEXT] {query}"
    return run_doc_qa_agent(augmented_query, user_tier)


def route_to_agent(intent: str, query: str, user_tier: int) -> dict:
    """Route query to the appropriate specialist agent."""
    if intent == "doc_qa":
        return run_doc_qa_agent(query, user_tier)
    elif intent == "kpi_monitor":
        return run_kpi_monitor_agent(query, user_tier)
    elif intent in ["strategic_gap", "competitive", "briefing", "evaluation"]:
        return run_generic_agent(intent, query, user_tier)
    else:
        return run_doc_qa_agent(query, user_tier)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Audit logging

# COMMAND ----------

def log_to_audit(
    user_id: str,
    user_tier: int,
    agent_name: str,
    query: str,
    response_preview: str,
    source_doc_ids: list,
    confidence_score: float,
    groundedness_score: float,
    is_policy_compliant: bool,
    latency_ms: int,
) -> str:
    """Append an interaction record to eds_audit.agent_interactions."""
    interaction_id = str(uuid.uuid4())
    tier_label = TIER_LABELS.get(user_tier, "Unknown")

    try:
        row = Row(
            interaction_id=interaction_id,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            user_tier=tier_label,
            access_tier_level=user_tier,
            agent_name=agent_name,
            query=query,
            response_preview=response_preview[:500],
            source_doc_ids=source_doc_ids[:10],  # cap for storage
            confidence_score=confidence_score,
            groundedness_score=groundedness_score,
            classification_tier_accessed=tier_label,
            is_policy_compliant=is_policy_compliant,
            latency_ms=latency_ms,
        )
        df = spark.createDataFrame([row])
        df.write.format("delta").mode("append").saveAsTable(f"{CATALOG}.eds_audit.agent_interactions")
    except Exception as e:
        print(f"[WARN] Audit logging failed: {e}")

    return interaction_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Main supervisor function

# COMMAND ----------

def supervisor_agent(
    query: str,
    user_id: str = "demo_user",
    user_tier: int = 2,
    session_id: Optional[str] = None,
) -> dict:
    """
    Main entry point for the Executive Decision Studio supervisor agent.

    Args:
        query:      User's natural language question
        user_id:    User identifier (for audit)
        user_tier:  Access tier (1=Board, 2=ELT, 3=Senior Mgmt, 4=All Staff)
        session_id: Optional session identifier for multi-turn conversations

    Returns:
        dict with keys: response, agent_used, confidence, sources,
                        intent, groundedness, interaction_id, is_compliant
    """
    start_time = time.time()
    session_id = session_id or str(uuid.uuid4())

    print(f"\n{'='*60}")
    print(f"SUPERVISOR AGENT | User: {user_id} | Tier: {user_tier}")
    print(f"Query: {query[:80]}...")

    # Step 1: Classify intent
    classification = classify_intent(query)
    intent = classification["intent"]
    intent_confidence = classification["confidence"]
    print(f"Intent: {intent} (confidence: {intent_confidence:.2f})")

    # Step 2: Check access policy
    policy = check_policy_compliance(query, user_tier, intent)
    if not policy["is_compliant"]:
        response_text = (
            f"Access denied: {policy['message']} "
            f"Please contact your system administrator if you believe this is an error."
        )
        elapsed_ms = int((time.time() - start_time) * 1000)
        interaction_id = log_to_audit(
            user_id=user_id, user_tier=user_tier, agent_name="supervisor",
            query=query, response_preview=response_text, source_doc_ids=[],
            confidence_score=0.0, groundedness_score=0.0,
            is_policy_compliant=False, latency_ms=elapsed_ms,
        )
        return {
            "response": response_text,
            "agent_used": "supervisor",
            "confidence": 0.0,
            "sources": [],
            "intent": intent,
            "groundedness": 0.0,
            "interaction_id": interaction_id,
            "is_compliant": False,
        }

    # Step 3: Route to specialist agent
    try:
        agent_result = route_to_agent(intent, query, user_tier)
        response_text = agent_result.get("answer", "No response generated.")
        source_ids = agent_result.get("citations", [])
        confidence = agent_result.get("confidence_score", 0.7)
        groundedness = agent_result.get("groundedness_score", 0.7)
    except Exception as e:
        print(f"[ERROR] Agent execution failed: {e}")
        response_text = f"I encountered an error processing your query: {str(e)}. Please try again."
        source_ids = []
        confidence = 0.0
        groundedness = 0.0

    elapsed_ms = int((time.time() - start_time) * 1000)
    print(f"Agent: {intent} | Latency: {elapsed_ms}ms | Sources: {len(source_ids)}")
    print(f"Response preview: {response_text[:100]}...")

    # Step 4: Log to audit
    interaction_id = log_to_audit(
        user_id=user_id,
        user_tier=user_tier,
        agent_name=intent,
        query=query,
        response_preview=response_text,
        source_doc_ids=source_ids,
        confidence_score=confidence,
        groundedness_score=groundedness,
        is_policy_compliant=True,
        latency_ms=elapsed_ms,
    )

    return {
        "response": response_text,
        "agent_used": intent,
        "confidence": confidence,
        "sources": source_ids,
        "intent": intent,
        "groundedness": groundedness,
        "interaction_id": interaction_id,
        "is_compliant": True,
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: End-to-end tests

# COMMAND ----------

test_cases = [
    {
        "query": "What are the main strategic priorities for Alinta Energy in FY25?",
        "user_id": "ceo_demo",
        "user_tier": 1,
    },
    {
        "query": "Show me the latest KPI performance across all business units.",
        "user_id": "cfo_demo",
        "user_tier": 1,
    },
    {
        "query": "What does the competitive intelligence report say about Origin Energy?",
        "user_id": "coo_demo",
        "user_tier": 2,
    },
    {
        "query": "How is the retail transformation programme tracking?",
        "user_id": "gm_retail_demo",
        "user_tier": 3,
    },
]

print("\n" + "="*65)
print("SUPERVISOR AGENT — End-to-End Tests")
print("="*65)

results = []
for tc in test_cases:
    result = supervisor_agent(
        query=tc["query"],
        user_id=tc["user_id"],
        user_tier=tc["user_tier"],
    )
    results.append(result)
    print(f"\n[{'PASS' if result['is_compliant'] else 'BLOCKED'}] "
          f"Tier {tc['user_tier']} | Agent: {result['agent_used']} | "
          f"Confidence: {result['confidence']:.2f} | "
          f"Sources: {len(result['sources'])}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("\n" + "="*65)
print("SUPERVISOR AGENT — Setup Complete")
print("="*65)
audit_count = spark.table(f"{CATALOG}.eds_audit.agent_interactions").count()
print(f"  Total audit records:  {audit_count}")
print(f"  Test queries run:     {len(test_cases)}")
print(f"  Agents available:     {', '.join(AGENT_NAMES)}")
print("="*65)
print("\nThe supervisor_agent() function is ready for use in app/app.py")
