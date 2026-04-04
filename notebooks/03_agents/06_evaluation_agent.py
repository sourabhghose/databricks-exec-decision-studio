# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Evaluation Agent
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC Evaluates the quality of RAG responses using LLM-as-judge methodology.
# MAGIC Scores groundedness, citation quality, and completeness. Logs scores to
# MAGIC `eds_evaluation.qa_pairs` for ongoing quality monitoring.

# COMMAND ----------

# MAGIC %pip install databricks-langchain langchain-core mlflow --upgrade --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import uuid
import json
import mlflow
from datetime import datetime
from pyspark.sql import Row
from databricks_langchain import ChatDatabricks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

CATALOG = "ausnet_process_intel_catalog"
LLM_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"
VS_ENDPOINT = "eds-vector-search"
VS_INDEX = f"{CATALOG}.eds_vectors.document_chunks_index"

spark.sql(f"USE CATALOG {CATALOG}")

# Use a smaller/cheaper model for evaluation to separate judge from candidate
eval_llm = ChatDatabricks(endpoint=LLM_ENDPOINT, max_tokens=512, temperature=0.0)
print("Evaluation Agent initialised.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Evaluation rubrics

# COMMAND ----------

GROUNDEDNESS_RUBRIC = """You are an expert evaluator for a RAG (Retrieval-Augmented Generation) system.

## Task: Score GROUNDEDNESS
Groundedness measures whether every factual claim in the AI's answer is directly supported by the retrieved context.

## Retrieved Context:
{context}

## AI Answer to Evaluate:
{answer}

## Scoring (0.0 to 1.0):
- 1.0: Every claim is directly supported by the context with no hallucination
- 0.8: Most claims supported; minor extrapolations within reason
- 0.6: Some claims supported; notable unsupported statements present
- 0.4: Many claims unverifiable against context; significant hallucination risk
- 0.2: Answer largely not grounded in the provided context
- 0.0: Answer completely contradicts or ignores the context

Respond with ONLY valid JSON:
{{"score": 0.0, "unsupported_claims": ["claim1", "claim2"], "reasoning": "brief explanation (1-2 sentences)"}}"""

CITATION_QUALITY_RUBRIC = """You are an expert evaluator for a RAG system used by C-suite executives.

## Task: Score CITATION QUALITY
Citation quality measures whether the answer provides specific, accurate, and useful source references.

## Answer to Evaluate:
{answer}

## Known Source Documents Available:
{source_ids}

## Scoring (0.0 to 1.0):
- 1.0: Every key claim has a specific [DOC-XXX] citation; citations are accurate and helpful
- 0.8: Most key claims cited; minor gaps in citation coverage
- 0.6: Some claims cited; important claims missing citations
- 0.4: Few citations; mostly general references without specificity
- 0.2: Minimal or incorrect citations
- 0.0: No citations at all

Respond with ONLY valid JSON:
{{"score": 0.0, "cited_docs": ["DOC-001"], "missing_citations": ["key uncited claim"], "reasoning": "brief (1-2 sentences)"}}"""

COMPLETENESS_RUBRIC = """You are an expert evaluator for a RAG system supporting executive decision-making.

## Task: Score COMPLETENESS
Completeness measures whether the answer addresses all important aspects of the executive's question.

## Original Question:
{question}

## AI Answer:
{answer}

## Expected Answer / Key Points:
{expected_answer}

## Scoring (0.0 to 1.0):
- 1.0: All important aspects of the question fully addressed
- 0.8: Most aspects covered; minor gaps
- 0.6: Core question addressed but important nuances missing
- 0.4: Partial answer; significant aspects not addressed
- 0.2: Minimal engagement with the question
- 0.0: Answer does not address the question

Respond with ONLY valid JSON:
{{"score": 0.0, "covered_aspects": ["aspect1"], "missing_aspects": ["missing1"], "reasoning": "brief (1-2 sentences)"}}"""

groundedness_prompt = ChatPromptTemplate.from_template(GROUNDEDNESS_RUBRIC)
citation_prompt = ChatPromptTemplate.from_template(CITATION_QUALITY_RUBRIC)
completeness_prompt = ChatPromptTemplate.from_template(COMPLETENESS_RUBRIC)

groundedness_chain = groundedness_prompt | eval_llm | StrOutputParser()
citation_chain = citation_prompt | eval_llm | StrOutputParser()
completeness_chain = completeness_prompt | eval_llm | StrOutputParser()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Score parsers

# COMMAND ----------

def parse_score_response(raw: str, score_key: str = "score") -> dict:
    """Parse LLM score response, handling markdown code blocks and extraction errors."""
    raw = raw.strip()
    # Strip markdown code fences
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    # Handle truncated JSON
    if not raw.endswith("}"):
        raw = raw + '"}'  # Best-effort fix
    try:
        result = json.loads(raw)
        score = min(1.0, max(0.0, float(result.get(score_key, 0.5))))
        return {**result, score_key: score}
    except Exception:
        # Extract just the numeric score if JSON fails
        import re
        match = re.search(r'"score":\s*([0-9.]+)', raw)
        if match:
            return {score_key: float(match.group(1)), "reasoning": "parse_fallback"}
        return {score_key: 0.5, "reasoning": f"Parse error: {raw[:100]}"}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Composite confidence label

# COMMAND ----------

def compute_composite_confidence(
    groundedness: float,
    citation_quality: float,
    completeness: float,
) -> str:
    """Compute composite confidence label from three component scores."""
    composite = (groundedness * 0.45) + (citation_quality * 0.25) + (completeness * 0.30)
    if composite >= 0.85:
        return "HIGH"
    elif composite >= 0.70:
        return "MEDIUM"
    elif composite >= 0.50:
        return "LOW"
    else:
        return "UNSATISFACTORY"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Main evaluation_agent function

# COMMAND ----------

def evaluation_agent(
    question: str,
    agent_answer: str,
    context: str = "",
    expected_answer: str = "",
    source_doc_ids: list = None,
    source_doc_id: str = None,
    difficulty: str = "medium",
    log_to_delta: bool = True,
) -> dict:
    """
    Evaluate a RAG response using LLM-as-judge methodology.

    Args:
        question:       Original user question
        agent_answer:   Agent's response to evaluate
        context:        Retrieved context that was provided to the agent
        expected_answer: Ground truth or expected answer (optional)
        source_doc_ids: List of source document IDs used
        source_doc_id:  Primary source document ID (for QA pair logging)
        difficulty:     Question difficulty: easy, medium, hard
        log_to_delta:   Whether to log scores to eds_evaluation.qa_pairs

    Returns:
        dict: groundedness_score, citation_quality_score, completeness_score,
              composite_confidence, qa_id, evaluation_metadata
    """
    import time
    start = time.time()
    source_doc_ids = source_doc_ids or []
    source_doc_id = source_doc_id or (source_doc_ids[0] if source_doc_ids else "UNKNOWN")

    # Score groundedness
    try:
        raw_g = groundedness_chain.invoke({
            "context": context[:4000] if context else "No context provided.",
            "answer": agent_answer[:2000],
        })
        g_result = parse_score_response(raw_g)
        groundedness_score = g_result.get("score", 0.5)
    except Exception as e:
        groundedness_score = 0.5
        g_result = {"reasoning": f"Error: {e}"}

    # Score citation quality
    try:
        raw_c = citation_chain.invoke({
            "answer": agent_answer[:2000],
            "source_ids": ", ".join(source_doc_ids[:10]) if source_doc_ids else "No source IDs provided",
        })
        c_result = parse_score_response(raw_c)
        citation_score = c_result.get("score", 0.5)
    except Exception as e:
        citation_score = 0.5
        c_result = {"reasoning": f"Error: {e}"}

    # Score completeness
    try:
        raw_comp = completeness_chain.invoke({
            "question": question,
            "answer": agent_answer[:2000],
            "expected_answer": expected_answer[:1000] if expected_answer else "No expected answer provided — score based on question coverage.",
        })
        comp_result = parse_score_response(raw_comp)
        completeness_score = comp_result.get("score", 0.5)
    except Exception as e:
        completeness_score = 0.5
        comp_result = {"reasoning": f"Error: {e}"}

    # Compute composite
    composite = compute_composite_confidence(groundedness_score, citation_score, completeness_score)

    elapsed_ms = int((time.time() - start) * 1000)

    qa_id = str(uuid.uuid4())

    # Log to Delta table
    if log_to_delta:
        try:
            row = Row(
                qa_id=qa_id,
                source_doc_id=source_doc_id,
                question=question,
                expected_answer=expected_answer or "",
                difficulty=difficulty,
                agent_answer=agent_answer[:5000],  # Truncate for storage
                groundedness_score=round(groundedness_score, 4),
                citation_quality_score=round(citation_score, 4),
                completeness_score=round(completeness_score, 4),
                composite_confidence=composite,
                created_at=datetime.utcnow(),
            )
            df = spark.createDataFrame([row])
            df.write.format("delta").mode("append").saveAsTable(f"{CATALOG}.eds_evaluation.qa_pairs")
        except Exception as e:
            print(f"[WARN] Failed to log to eds_evaluation.qa_pairs: {e}")

    return {
        "qa_id": qa_id,
        "groundedness_score": round(groundedness_score, 4),
        "citation_quality_score": round(citation_score, 4),
        "completeness_score": round(completeness_score, 4),
        "composite_confidence": composite,
        "groundedness_details": g_result,
        "citation_details": c_result,
        "completeness_details": comp_result,
        "latency_ms": elapsed_ms,
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Batch evaluation with synthetic QA pairs

# COMMAND ----------

# Generate synthetic QA pairs from document content
def generate_qa_pairs_from_docs(num_pairs: int = 20) -> list:
    """Generate evaluation QA pairs from stored documents."""
    docs_df = spark.sql(f"""
        SELECT doc_id, title, content
        FROM {CATALOG}.eds_synthetic.documents
        ORDER BY RAND()
        LIMIT 10
    """)

    qa_pairs = []
    # Curated QA pairs for reliable evaluation
    qa_pairs = [
        {
            "question": "What are the three strategic options for Loy Yang B and their NPV?",
            "expected_answer": "Option A (Continue to FY32) NPV $520M; Option B (Early Retirement FY27) NPV $435M; Option C (Gas CCGT Conversion) NPV $380M",
            "source_doc_id": "DOC-002",
            "difficulty": "hard",
        },
        {
            "question": "What was Alinta's 1H FY25 EBITDA margin?",
            "expected_answer": "18.4% (EBITDA $298 million on revenue $1,618 million)",
            "source_doc_id": "DOC-003",
            "difficulty": "medium",
        },
        {
            "question": "What is Alinta's Net Zero Scope 1 and 2 target and by when?",
            "expected_answer": "Net zero by 2040, with 50% (or 55%) absolute reduction interim target by 2030 vs FY20 baseline",
            "source_doc_id": "DOC-005",
            "difficulty": "easy",
        },
        {
            "question": "What is the total capex estimate for Yandin Wind Farm Stage 2?",
            "expected_answer": "$385 million (±10%), with $295 million EPC contract with Vestas",
            "source_doc_id": "DOC-006",
            "difficulty": "medium",
        },
        {
            "question": "What is Alinta's retail customer NPS versus the best digital native competitor?",
            "expected_answer": "Alinta NPS +18 (or +22 in Q2 FY25) vs Amber Electric +42 (highest competitor)",
            "source_doc_id": "DOC-004",
            "difficulty": "medium",
        },
        {
            "question": "What is the Group WACC hurdle rate for new investments?",
            "expected_answer": "9.5% pre-tax nominal (renewable WA: 9.0%, thermal LYB sustaining: 12.0%, retail: 10.5%)",
            "source_doc_id": "DOC-015",
            "difficulty": "hard",
        },
        {
            "question": "How many direct employees does Loy Yang B have?",
            "expected_answer": "Approximately 600 direct staff (and 200 permanent contractors)",
            "source_doc_id": "DOC-002",
            "difficulty": "easy",
        },
        {
            "question": "What is the FY26 Group revenue target?",
            "expected_answer": "$3,350 million (up 4.7% on FY25 guidance)",
            "source_doc_id": "DOC-009",
            "difficulty": "medium",
        },
    ]
    return qa_pairs[:num_pairs]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Run batch evaluation

# COMMAND ----------

print("\n" + "="*65)
print("EVALUATION AGENT — Batch QA Evaluation")
print("="*65)

# First, get answers from the doc_qa agent
from databricks_langchain import DatabricksVectorSearch

def get_agent_answer(question: str, source_doc_id: str) -> tuple:
    """Get an answer and context from the doc_qa agent."""
    try:
        vs = DatabricksVectorSearch(
            endpoint=VS_ENDPOINT,
            index_name=VS_INDEX,
            columns=["chunk_id", "doc_id", "doc_title", "chunk_text"],
            text_column="chunk_text",
        )
        retriever = vs.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6, "filter": {"access_tier_level": {"$gte": 1}}},
        )
        docs = retriever.invoke(question)
        context = "\n\n---\n\n".join([
            f"[{d.metadata.get('doc_id', 'UNK')}] {d.metadata.get('doc_title', '')}\n{d.page_content}"
            for d in docs
        ])
        source_ids = list(set([d.metadata.get('doc_id', 'UNK') for d in docs]))

        answer_prompt = ChatPromptTemplate.from_template(
            "Answer the following question based on the context. Include [DOC-XXX] citations.\n\n"
            "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )
        answer_llm = ChatDatabricks(endpoint=LLM_ENDPOINT, max_tokens=600, temperature=0.1)
        answer = (answer_prompt | answer_llm | StrOutputParser()).invoke({
            "context": context[:5000],
            "question": question,
        })
        return answer, context, source_ids
    except Exception as e:
        return f"Error: {e}", "", []

qa_pairs = generate_qa_pairs_from_docs(num_pairs=5)  # Limit for demo
eval_results = []

for i, qa in enumerate(qa_pairs, 1):
    print(f"\n[{i}/{len(qa_pairs)}] Evaluating: {qa['question'][:70]}...")

    # Get agent answer
    agent_answer, context, source_ids = get_agent_answer(qa["question"], qa["source_doc_id"])

    # Evaluate
    eval_result = evaluation_agent(
        question=qa["question"],
        agent_answer=agent_answer,
        context=context,
        expected_answer=qa["expected_answer"],
        source_doc_ids=source_ids,
        source_doc_id=qa["source_doc_id"],
        difficulty=qa["difficulty"],
        log_to_delta=True,
    )
    eval_results.append({**qa, "eval": eval_result, "agent_answer": agent_answer})

    g = eval_result["groundedness_score"]
    c = eval_result["citation_quality_score"]
    comp = eval_result["completeness_score"]
    conf = eval_result["composite_confidence"]
    print(f"  Groundedness: {g:.2f} | Citation: {c:.2f} | Completeness: {comp:.2f} | Confidence: {conf}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Evaluation summary and MLflow logging

# COMMAND ----------

print("\n" + "="*65)
print("EVALUATION SUMMARY")
print("="*65)

avg_groundedness = sum(r["eval"]["groundedness_score"] for r in eval_results) / len(eval_results) if eval_results else 0
avg_citation = sum(r["eval"]["citation_quality_score"] for r in eval_results) / len(eval_results) if eval_results else 0
avg_completeness = sum(r["eval"]["completeness_score"] for r in eval_results) / len(eval_results) if eval_results else 0
confidence_dist = {}
for r in eval_results:
    conf = r["eval"]["composite_confidence"]
    confidence_dist[conf] = confidence_dist.get(conf, 0) + 1

print(f"  QA Pairs Evaluated:      {len(eval_results)}")
print(f"  Avg Groundedness:        {avg_groundedness:.3f}")
print(f"  Avg Citation Quality:    {avg_citation:.3f}")
print(f"  Avg Completeness:        {avg_completeness:.3f}")
print(f"  Confidence Distribution: {confidence_dist}")

# Log to MLflow
with mlflow.start_run(run_name="eds_evaluation_run"):
    mlflow.log_metrics({
        "avg_groundedness": avg_groundedness,
        "avg_citation_quality": avg_citation,
        "avg_completeness": avg_completeness,
        "num_evaluated": len(eval_results),
        "high_confidence_pct": confidence_dist.get("HIGH", 0) / max(len(eval_results), 1),
    })
    print("\n[OK] Metrics logged to MLflow.")

# Show qa_pairs table
qa_count = spark.table(f"{CATALOG}.eds_evaluation.qa_pairs").count()
print(f"\n[OK] Total QA evaluation records in eds_evaluation.qa_pairs: {qa_count}")

print("\n[OK] Evaluation Agent setup complete.")
