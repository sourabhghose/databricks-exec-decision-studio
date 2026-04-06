/**
 * GenieInsights — AI/BI Genie conversational data query tab.
 *
 * Lets executives ask natural-language questions over live EDS Unity Catalog
 * tables (KPIs, risks, financials, action items, decision register).
 *
 * Maintains multi-turn conversation context via conversation_id.
 * Falls back gracefully to demo data when GENIE_SPACE_ID is not configured.
 */

import { useState, useRef, useEffect } from "react";
import { Database, SendHorizontal, X, Loader2, AlertCircle } from "lucide-react";

// ── Types ──────────────────────────────────────────────────────────────────────

interface GenieResponse {
  conversation_id: string;
  message_id: string;
  narrative: string;
  sql: string;
  columns: string[];
  rows: unknown[][];
  demo: boolean;
}

interface ConversationTurn {
  question: string;
  response: GenieResponse;
}

// ── Constants ──────────────────────────────────────────────────────────────────

const QUICK_QUESTIONS = [
  "Which KPIs are below target?",
  "Top 5 risks by score",
  "Show Critical and High risks",
  "Overdue action items",
  "Decisions currently in progress",
  "EBITDA by business unit",
  "KPIs flagged as anomalies",
  "Board decisions last 6 months",
  "Risks owned by the CRO",
  "Retail churn rate trend",
  "Financial performance vs budget",
  "Highest likelihood risks",
  "Actions due this month",
  "KPI performance in Generation",
  "Risk mitigation actions pending",
  "Revenue by business unit FY2025",
  "Which decisions are completed?",
  "Show all strategic risks",
];

// ── Sub-components ─────────────────────────────────────────────────────────────

function DataTable({ columns, rows }: { columns: string[]; rows: unknown[][] }) {
  const [showAll, setShowAll] = useState(false);
  if (columns.length === 0) return null;

  const displayRows = showAll ? rows : rows.slice(0, 20);
  const hasMore = rows.length > 20;

  return (
    <div className="mt-3 overflow-x-auto rounded-xl" style={{ border: "1px solid var(--border)" }}>
      <table className="w-full text-[12px]">
        <thead>
          <tr style={{ background: "var(--surface-3)", borderBottom: "1px solid var(--border)" }}>
            {columns.map((col) => (
              <th
                key={col}
                className="px-3 py-2 text-left font-semibold whitespace-nowrap"
                style={{ color: "var(--text-2)" }}
              >
                {col.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayRows.map((row, ri) => (
            <tr
              key={ri}
              style={{
                background: ri % 2 === 0 ? "transparent" : "var(--surface-2)",
                borderBottom: ri < displayRows.length - 1 ? "1px solid var(--border)" : undefined,
              }}
            >
              {row.map((cell, ci) => {
                const isNum = typeof cell === "number";
                return (
                  <td
                    key={ci}
                    className={`px-3 py-2 whitespace-nowrap ${isNum ? "text-right tabular-nums" : ""}`}
                    style={{ color: "var(--text-1)" }}
                  >
                    {isNum ? Number(cell).toLocaleString() : String(cell ?? "")}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {hasMore && !showAll && (
        <button
          onClick={() => setShowAll(true)}
          className="w-full py-2 text-[12px] font-medium transition-colors"
          style={{ color: "var(--accent)", background: "var(--surface-2)", borderTop: "1px solid var(--border)" }}
        >
          Show all {rows.length} rows
        </button>
      )}
    </div>
  );
}

/** Render **bold** and bullet-list markdown in Genie narrative text. */
function NarrativeText({ text }: { text: string }) {
  // Split on " - " bullet separators (Genie uses " - item" pattern)
  const parts = text.split(/\s+-\s+/);
  const intro = parts[0].trim();
  const bullets = parts.slice(1);

  function renderInline(str: string) {
    // Replace **text** with <strong>
    const segments = str.split(/\*\*(.+?)\*\*/g);
    return segments.map((seg, i) =>
      i % 2 === 1 ? <strong key={i} style={{ color: "var(--text-1)", fontWeight: 600 }}>{seg}</strong> : seg
    );
  }

  if (bullets.length === 0) {
    return (
      <p className="text-[13px] leading-6" style={{ color: "var(--text-2)" }}>
        {renderInline(intro)}
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {intro && (
        <p className="text-[13px] leading-6" style={{ color: "var(--text-2)" }}>
          {renderInline(intro)}
        </p>
      )}
      <ul className="space-y-1 pl-1">
        {bullets.map((b, i) => (
          <li key={i} className="flex items-start gap-2 text-[13px] leading-6" style={{ color: "var(--text-2)" }}>
            <span className="mt-2 w-1.5 h-1.5 rounded-full shrink-0" style={{ background: "var(--accent)" }} />
            <span>{renderInline(b.trim())}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function TurnCard({ turn }: { turn: ConversationTurn }) {
  return (
    <div className="space-y-3">
      {/* User question */}
      <div className="flex justify-end">
        <div
          className="max-w-[80%] px-4 py-2.5 rounded-2xl rounded-br-sm text-[13px]"
          style={{ background: "var(--accent)", color: "#fff" }}
        >
          {turn.question}
        </div>
      </div>

      {/* Genie response */}
      <div
        className="rounded-2xl rounded-bl-sm p-4"
        style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
      >
        {/* Demo banner */}
        {turn.response.demo && (
          <div
            className="flex items-center gap-2 mb-3 px-3 py-1.5 rounded-lg text-[11px] font-medium"
            style={{ background: "rgba(251,191,36,0.12)", border: "1px solid rgba(251,191,36,0.3)", color: "#f59e0b" }}
          >
            <AlertCircle size={12} />
            Demo data — configure GENIE_SPACE_ID to enable live queries
          </div>
        )}

        {/* Narrative */}
        <NarrativeText text={turn.response.narrative} />

        {/* Data table */}
        {turn.response.columns.length > 0 && (
          <DataTable columns={turn.response.columns} rows={turn.response.rows} />
        )}
      </div>
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────

export default function GenieInsights() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom on new turns
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns]);

  async function submitQuestion(q: string) {
    const trimmed = q.trim();
    if (!trimmed || loading) return;

    setQuestion("");
    setLoading(true);
    setError(null);

    try {
      const body = { question: trimmed, conversation_id: conversationId };
      const resp = await fetch("/api/genie/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`${resp.status}: ${text.slice(0, 200)}`);
      }

      const data: GenieResponse = await resp.json();

      setConversationId(data.conversation_id);
      setTurns((prev) => [...prev, { question: trimmed, response: data }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function clearConversation() {
    setTurns([]);
    setConversationId(null);
    setError(null);
    setQuestion("");
  }

  const hasConversation = turns.length > 0;

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Database size={20} style={{ color: "var(--accent)" }} />
          <h1 className="text-[22px] font-bold" style={{ color: "var(--text-1)" }}>
            Data Insights
          </h1>
        </div>
        <p className="text-[13px]" style={{ color: "var(--text-3)" }}>
          Ask natural-language questions about KPIs, risks, financials, action items, and decisions.
          Powered by Databricks AI/BI Genie over live Unity Catalog data.
        </p>
      </div>

      {/* Quick question chips — always visible */}
      <div>
        <p className="text-[11px] font-semibold mb-2 uppercase tracking-wider" style={{ color: "var(--text-3)" }}>
          Quick questions
        </p>
        <div className="flex flex-wrap gap-2">
          {QUICK_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => submitQuestion(q)}
              disabled={loading}
              className="px-3 py-1.5 rounded-full text-[12px] font-medium transition-all disabled:opacity-40"
              style={{
                background: "var(--surface-2)",
                border: "1px solid var(--border)",
                color: "var(--text-2)",
              }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Conversation turns */}
      {hasConversation && (
        <div className="space-y-6">
          {turns.map((turn, i) => (
            <TurnCard key={i} turn={turn} />
          ))}
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="flex items-center gap-2" style={{ color: "var(--text-3)" }}>
          <Loader2 size={14} className="animate-spin" />
          <span className="text-[12px]">Genie is thinking...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-[12px]"
          style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#ef4444" }}
        >
          <AlertCircle size={13} />
          {error}
        </div>
      )}

      <div ref={bottomRef} />

      {/* Input area */}
      <div
        className="sticky bottom-4 rounded-2xl p-3"
        style={{
          background: "var(--surface-2)",
          border: "1px solid var(--border-strong)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
        }}
      >
        {/* Follow-up label */}
        {hasConversation && (
          <p className="text-[11px] mb-2 font-medium" style={{ color: "var(--text-3)" }}>
            Ask a follow-up question...
          </p>
        )}

        <div className="flex gap-2 items-center">
          <input
            ref={inputRef}
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submitQuestion(question); } }}
            placeholder={hasConversation ? "Ask a follow-up..." : "Ask a question about your data..."}
            className="flex-1 px-4 py-2.5 rounded-xl text-[13px] outline-none"
            style={{
              background: "var(--surface-3)",
              border: "1px solid var(--border)",
              color: "var(--text-1)",
            }}
          />

          <button
            onClick={() => submitQuestion(question)}
            disabled={!question.trim() || loading}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-[13px] font-semibold transition-all disabled:opacity-40"
            style={{ background: "var(--accent)", color: "#fff" }}
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <SendHorizontal size={14} />}
            Ask
          </button>

          {hasConversation && (
            <button
              onClick={clearConversation}
              className="flex items-center gap-1 px-3 py-2.5 rounded-xl text-[12px] transition-all"
              style={{ background: "var(--surface-3)", border: "1px solid var(--border)", color: "var(--text-3)" }}
              title="Clear conversation"
            >
              <X size={13} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
