import { useState, useEffect, useRef } from "react";
import { Play, ChevronDown, ChevronUp, BookmarkPlus, Loader2, AlertTriangle } from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface KpiImpact {
  baseline: number;
  projected: number;
  unit: string;
}

interface Scenario {
  label: "Bear" | "Base" | "Bull";
  probability: number;
  headline: string;
  key_assumptions: string[];
  kpi_impact: Record<string, KpiImpact>;
  risk_factors: string[];
  strategic_rationale: string;
}

interface ScenarioTree {
  decision: string;
  scenarios: Scenario[];
  recommended: string;
  recommendation_rationale: string;
}

interface Template {
  label: string;
  text: string;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const SCENARIO_META: Record<string, { emoji: string; color: string; border: string; badge: string }> = {
  Bear: {
    emoji: "↘",
    color: "var(--risk-high, #ef4444)",
    border: "rgba(239,68,68,0.25)",
    badge: "#7f1d1d",
  },
  Base: {
    emoji: "→",
    color: "var(--accent, #F47920)",
    border: "rgba(244,121,32,0.25)",
    badge: "#7c2d12",
  },
  Bull: {
    emoji: "↗",
    color: "var(--risk-low, #22c55e)",
    border: "rgba(34,197,94,0.25)",
    badge: "#14532d",
  },
};

function kpiDelta(impact: KpiImpact): number {
  if (impact.baseline === 0) return 0;
  return ((impact.projected - impact.baseline) / Math.abs(impact.baseline)) * 100;
}

function tryParseScenarioJson(raw: string): ScenarioTree | null {
  // Strip any markdown fences the LLM may have added
  const cleaned = raw.replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();
  try {
    return JSON.parse(cleaned) as ScenarioTree;
  } catch {
    return null;
  }
}

// ── Sub-components ────────────────────────────────────────────────────────────

function KpiRow({ name, impact }: { name: string; impact: KpiImpact }) {
  const delta = kpiDelta(impact);
  const positive = delta >= 0;
  return (
    <div className="flex items-center justify-between py-1 text-[11px]">
      <span style={{ color: "var(--text-2)" }}>{name}</span>
      <div className="flex items-center gap-2">
        <span style={{ color: "var(--text-3)" }}>
          {impact.baseline.toLocaleString()} {impact.unit}
        </span>
        <span style={{ color: "var(--text-3)" }}>→</span>
        <span style={{ color: "var(--text-1)", fontWeight: 600 }}>
          {impact.projected.toLocaleString()} {impact.unit}
        </span>
        <span
          className="px-1.5 py-0.5 rounded font-mono font-semibold"
          style={{
            background: positive ? "rgba(34,197,94,0.12)" : "rgba(239,68,68,0.12)",
            color: positive ? "#22c55e" : "#ef4444",
          }}
        >
          {positive ? "+" : ""}{delta.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}

function ScenarioCard({
  scenario,
  recommended,
  onDrilldown,
}: {
  scenario: Scenario;
  recommended: string;
  onDrilldown: (s: Scenario) => void;
}) {
  const meta = SCENARIO_META[scenario.label] ?? SCENARIO_META.Base;
  const isRecommended = scenario.label === recommended;

  return (
    <div
      className="flex flex-col rounded-xl p-4 gap-3"
      style={{
        border: `1.5px solid ${isRecommended ? meta.color : meta.border}`,
        background: "var(--surface-2)",
        flex: "1 1 0",
        minWidth: "260px",
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[18px]" style={{ color: meta.color }}>
            {meta.emoji}
          </span>
          <span className="text-[15px] font-bold" style={{ color: meta.color }}>
            {scenario.label}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          {isRecommended && (
            <span
              className="text-[10px] font-bold px-2 py-0.5 rounded-full"
              style={{ background: meta.color, color: "#fff" }}
            >
              RECOMMENDED
            </span>
          )}
          <span className="text-[12px] font-semibold" style={{ color: "var(--text-2)" }}>
            {Math.round(scenario.probability * 100)}%
          </span>
        </div>
      </div>

      {/* Probability bar */}
      <div
        className="h-1.5 rounded-full overflow-hidden"
        style={{ background: "var(--surface-3, rgba(255,255,255,0.06))" }}
      >
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${scenario.probability * 100}%`, background: meta.color }}
        />
      </div>

      {/* Headline */}
      <p className="text-[12px] leading-relaxed" style={{ color: "var(--text-1)" }}>
        {scenario.headline}
      </p>

      {/* KPI Impact */}
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-widest mb-1.5" style={{ color: "var(--text-3)" }}>
          KPI Impact
        </p>
        <div
          className="rounded-lg px-3 py-1 divide-y divide-white/10"
          style={{ background: "var(--surface-3, rgba(0,0,0,0.15))" }}
        >
          {Object.entries(scenario.kpi_impact).map(([name, impact]) => (
            <KpiRow key={name} name={name} impact={impact} />
          ))}
        </div>
      </div>

      {/* Key Assumptions */}
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-widest mb-1" style={{ color: "var(--text-3)" }}>
          Key Assumptions
        </p>
        <ul className="space-y-0.5">
          {scenario.key_assumptions.map((a, i) => (
            <li key={i} className="text-[11px] flex gap-1.5" style={{ color: "var(--text-2)" }}>
              <span style={{ color: meta.color, flexShrink: 0 }}>•</span>
              {a}
            </li>
          ))}
        </ul>
      </div>

      {/* Risk Factors */}
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-widest mb-1" style={{ color: "var(--text-3)" }}>
          Risk Factors
        </p>
        <ul className="space-y-0.5">
          {scenario.risk_factors.map((r, i) => (
            <li key={i} className="text-[11px] flex gap-1.5" style={{ color: "var(--text-2)" }}>
              <AlertTriangle size={10} className="mt-0.5 flex-shrink-0" style={{ color: "#ef4444" }} />
              {r}
            </li>
          ))}
        </ul>
      </div>

      {/* Rationale */}
      <p className="text-[11px] italic leading-relaxed" style={{ color: "var(--text-3)" }}>
        {scenario.strategic_rationale}
      </p>

      {/* Drill-down button */}
      <button
        onClick={() => onDrilldown(scenario)}
        className="mt-auto flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-medium transition-colors"
        style={{
          background: "var(--surface-3, rgba(255,255,255,0.06))",
          border: `1px solid ${meta.border}`,
          color: meta.color,
        }}
      >
        <ChevronDown size={13} />
        Drill Down
      </button>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function ScenarioSimulator() {
  const [decision, setDecision] = useState("");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [rawJson, setRawJson] = useState("");
  const [scenarioTree, setScenarioTree] = useState<ScenarioTree | null>(null);
  const [parseError, setParseError] = useState(false);

  const [drilldownScenario, setDrilldownScenario] = useState<Scenario | null>(null);
  const [drilldownText, setDrilldownText] = useState("");
  const [drilldownStreaming, setDrilldownStreaming] = useState(false);
  const [drilldownOpen, setDrilldownOpen] = useState(false);

  const [savedMsg, setSavedMsg] = useState("");

  const drilldownRef = useRef<HTMLDivElement>(null);

  // ── Load templates on mount ─────────────────────────────────────────────────
  useEffect(() => {
    fetch("/api/simulate/templates")
      .then((r) => r.json())
      .then((d) => setTemplates(d.templates ?? []))
      .catch(() => {});
  }, []);

  // ── Parse JSON as tokens arrive ─────────────────────────────────────────────
  useEffect(() => {
    if (!rawJson) return;
    const parsed = tryParseScenarioJson(rawJson);
    if (parsed) {
      setScenarioTree(parsed);
      setParseError(false);
    }
  }, [rawJson]);

  // ── Run simulation ──────────────────────────────────────────────────────────
  function runSimulation() {
    if (!decision.trim() || streaming) return;
    setStreaming(true);
    setRawJson("");
    setScenarioTree(null);
    setParseError(false);
    setDrilldownScenario(null);
    setDrilldownText("");
    setDrilldownOpen(false);

    fetch("/api/simulate/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    })
      .then((res) => {
        const reader = res.body!.getReader();
        const decoder = new TextDecoder();
        let accumulated = "";
        let lineBuffer = ""; // buffer for incomplete SSE lines across chunk boundaries

        function pump(): Promise<void> {
          return reader.read().then(({ done, value }) => {
            if (done) {
              setStreaming(false);
              // Fallback: if "result" event never arrived, try parsing accumulated tokens
              setScenarioTree((prev) => {
                if (prev) return prev; // already set by "result" event
                const parsed = tryParseScenarioJson(accumulated);
                if (parsed) {
                  setParseError(false);
                  return parsed;
                }
                setParseError(true);
                return null;
              });
              return;
            }
            const chunk = decoder.decode(value, { stream: true });
            // Prepend any buffered incomplete line from previous chunk
            const text = lineBuffer + chunk;
            const lines = text.split("\n");
            // Last element may be incomplete — buffer it
            lineBuffer = lines.pop() ?? "";
            lines.forEach((line) => {
              if (!line.startsWith("data: ")) return;
              try {
                const evt = JSON.parse(line.slice(6));
                if (evt.type === "token") {
                  accumulated += evt.content;
                  setRawJson(accumulated);
                }
                // "result" carries the complete assembled JSON — use this for parsing
                if (evt.type === "result") {
                  const parsed = tryParseScenarioJson(evt.content ?? "");
                  if (parsed) {
                    setScenarioTree(parsed);
                    setParseError(false);
                  }
                }
                if (evt.type === "done") {
                  setStreaming(false);
                }
                if (evt.type === "error") {
                  setStreaming(false);
                  setParseError(true);
                }
              } catch {
                // malformed SSE line — ignore
              }
            });
            return pump();
          });
        }
        return pump();
      })
      .catch(() => setStreaming(false));
  }

  // ── Drill-down ──────────────────────────────────────────────────────────────
  function runDrilldown(scenario: Scenario) {
    setDrilldownScenario(scenario);
    setDrilldownText("");
    setDrilldownStreaming(true);
    setDrilldownOpen(true);
    setTimeout(() => drilldownRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);

    fetch("/api/simulate/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision,
        drilldown_branch: scenario.label,
        drilldown_scenario: scenario,
      }),
    })
      .then((res) => {
        const reader = res.body!.getReader();
        const decoder = new TextDecoder();
        let text = "";

        function pump(): Promise<void> {
          return reader.read().then(({ done, value }) => {
            if (done) {
              setDrilldownStreaming(false);
              return;
            }
            const chunk = decoder.decode(value, { stream: true });
            chunk.split("\n").forEach((line) => {
              if (!line.startsWith("data: ")) return;
              try {
                const evt = JSON.parse(line.slice(6));
                if (evt.type === "token") {
                  text += evt.content;
                  setDrilldownText(text);
                }
                if (evt.type === "done") setDrilldownStreaming(false);
              } catch {
                // ignore
              }
            });
            return pump();
          });
        }
        return pump();
      })
      .catch(() => setDrilldownStreaming(false));
  }

  // ── Save to decision register ───────────────────────────────────────────────
  function saveToDecisionRegister() {
    if (!drilldownScenario || !scenarioTree) return;
    const payload = {
      decision_id: `SIM-${Date.now().toString(36).toUpperCase()}`,
      decision_date: new Date().toISOString().slice(0, 10),
      committee: "Board",
      description: `[Scenario Simulation] ${decision} — Selected: ${drilldownScenario.label}. ${drilldownScenario.headline}`,
      decision_type: "strategic",
      outcome: `${drilldownScenario.label} scenario selected (${Math.round(drilldownScenario.probability * 100)}% probability). ${scenarioTree.recommendation_rationale}`,
      owner: "CEO",
      implementation_status: "pending",
    };
    fetch("/api/decisions/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(() => setSavedMsg("Saved to Decision Register"))
      .catch(() => setSavedMsg("Save failed — register it manually"))
      .finally(() => setTimeout(() => setSavedMsg(""), 4000));
  }

  // ── Markdown-lite renderer ──────────────────────────────────────────────────
  function renderMarkdown(text: string) {
    return text.split("\n").map((line, i) => {
      if (line.startsWith("## ")) {
        return (
          <h3
            key={i}
            className="text-[13px] font-bold mt-4 mb-1.5"
            style={{ color: "var(--accent)" }}
          >
            {line.slice(3)}
          </h3>
        );
      }
      if (line.startsWith("- **") || line.startsWith("- ")) {
        const content = line.slice(2).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        return (
          <li
            key={i}
            className="text-[12px] leading-relaxed ml-3"
            style={{ color: "var(--text-2)" }}
            dangerouslySetInnerHTML={{ __html: content }}
          />
        );
      }
      if (line.trim() === "") return <div key={i} className="h-1" />;
      return (
        <p key={i} className="text-[12px] leading-relaxed" style={{ color: "var(--text-2)" }}>
          {line}
        </p>
      );
    });
  }

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-[22px] font-bold" style={{ color: "var(--text-1)" }}>
          Scenario Simulator
        </h1>
        <p className="text-[13px] mt-1" style={{ color: "var(--text-3)" }}>
          Define a strategic decision and simulate Bear, Base, and Bull outcomes grounded in Alinta's live data.
        </p>
      </div>

      {/* Decision input card */}
      <div
        className="rounded-xl p-5 space-y-4"
        style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
      >
        <div className="space-y-2">
          <label className="text-[12px] font-semibold uppercase tracking-widest" style={{ color: "var(--text-3)" }}>
            Decision Scenario
          </label>
          <textarea
            value={decision}
            onChange={(e) => setDecision(e.target.value)}
            placeholder="Describe the strategic decision the board needs to evaluate..."
            rows={4}
            className="w-full rounded-lg px-3 py-2.5 text-[13px] leading-relaxed resize-none focus:outline-none"
            style={{
              background: "var(--surface-3, rgba(0,0,0,0.2))",
              border: "1px solid var(--border)",
              color: "var(--text-1)",
            }}
          />
        </div>

        {/* Quick-start templates */}
        {templates.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-[11px]" style={{ color: "var(--text-3)" }}>
              Quick start:
            </p>
            <div className="flex flex-wrap gap-2">
              {templates.map((t) => (
                <button
                  key={t.label}
                  onClick={() => setDecision(t.text)}
                  className="px-2.5 py-1 rounded-lg text-[11px] font-medium transition-colors"
                  style={{
                    background: "var(--surface-3, rgba(255,255,255,0.06))",
                    border: "1px solid var(--border)",
                    color: "var(--accent)",
                  }}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Run button */}
        <div className="flex items-center justify-end gap-3">
          {streaming && (
            <span className="text-[12px] flex items-center gap-1.5" style={{ color: "var(--text-3)" }}>
              <Loader2 size={13} className="animate-spin" />
              Generating scenarios…
            </span>
          )}
          <button
            onClick={runSimulation}
            disabled={!decision.trim() || streaming}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-[13px] font-semibold transition-all"
            style={{
              background: decision.trim() && !streaming ? "var(--accent)" : "var(--surface-3, rgba(255,255,255,0.06))",
              color: decision.trim() && !streaming ? "#fff" : "var(--text-3)",
              cursor: decision.trim() && !streaming ? "pointer" : "not-allowed",
            }}
          >
            <Play size={14} />
            Run Simulation
          </button>
        </div>

        {/* Streaming progress bar */}
        {streaming && (
          <div
            className="h-1 rounded-full overflow-hidden"
            style={{ background: "var(--surface-3, rgba(255,255,255,0.06))" }}
          >
            <div
              className="h-full rounded-full animate-pulse"
              style={{ width: "60%", background: "var(--accent)" }}
            />
          </div>
        )}
      </div>

      {/* Parse error */}
      {parseError && !streaming && (
        <div
          className="rounded-lg px-4 py-3 text-[12px]"
          style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#ef4444" }}
        >
          Could not parse scenario response. Try rephrasing the decision or running again.
        </div>
      )}

      {/* Scenario cards */}
      {scenarioTree && (
        <div className="space-y-4">
          {/* Recommendation banner */}
          <div
            className="rounded-lg px-4 py-3 flex items-start gap-2"
            style={{ background: "rgba(244,121,32,0.1)", border: "1px solid rgba(244,121,32,0.25)" }}
          >
            <span className="text-[13px] font-bold" style={{ color: "var(--accent)" }}>
              Recommendation: {scenarioTree.recommended}
            </span>
            <span className="text-[12px] leading-relaxed" style={{ color: "var(--text-2)" }}>
              — {scenarioTree.recommendation_rationale}
            </span>
          </div>

          {/* Three scenario cards */}
          <div className="flex gap-4 flex-wrap">
            {scenarioTree.scenarios.map((s) => (
              <ScenarioCard
                key={s.label}
                scenario={s}
                recommended={scenarioTree.recommended}
                onDrilldown={runDrilldown}
              />
            ))}
          </div>
        </div>
      )}

      {/* Skeleton cards while streaming before first valid JSON */}
      {streaming && !scenarioTree && (
        <div className="flex gap-4 flex-wrap">
          {["Bear", "Base", "Bull"].map((label) => {
            const meta = SCENARIO_META[label];
            return (
              <div
                key={label}
                className="flex-1 min-w-[260px] rounded-xl p-4 animate-pulse"
                style={{ background: "var(--surface-2)", border: `1.5px solid ${meta.border}`, minHeight: "320px" }}
              >
                <div className="h-4 rounded w-1/3 mb-3" style={{ background: "var(--surface-3, rgba(255,255,255,0.06))" }} />
                <div className="h-2 rounded w-full mb-2" style={{ background: "var(--surface-3, rgba(255,255,255,0.06))" }} />
                <div className="h-2 rounded w-5/6" style={{ background: "var(--surface-3, rgba(255,255,255,0.06))" }} />
              </div>
            );
          })}
        </div>
      )}

      {/* Drill-down panel */}
      {drilldownScenario && (
        <div
          ref={drilldownRef}
          className="rounded-xl overflow-hidden"
          style={{ border: "1px solid var(--border)" }}
        >
          {/* Collapsible header */}
          <button
            className="w-full flex items-center justify-between px-5 py-3"
            style={{ background: "var(--surface-2)" }}
            onClick={() => setDrilldownOpen(!drilldownOpen)}
          >
            <div className="flex items-center gap-2">
              <span
                className="text-[13px] font-bold"
                style={{ color: SCENARIO_META[drilldownScenario.label]?.color ?? "var(--accent)" }}
              >
                {drilldownScenario.label} Scenario — Drill-Down
              </span>
              {drilldownStreaming && <Loader2 size={13} className="animate-spin" style={{ color: "var(--text-3)" }} />}
            </div>
            {drilldownOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>

          {drilldownOpen && (
            <div className="px-5 py-4 space-y-2" style={{ background: "var(--surface-1)" }}>
              {drilldownText ? (
                <div className="space-y-1">{renderMarkdown(drilldownText)}</div>
              ) : (
                <div className="flex items-center gap-2 text-[12px]" style={{ color: "var(--text-3)" }}>
                  <Loader2 size={13} className="animate-spin" />
                  Generating drill-down…
                </div>
              )}

              {/* Save button — shown once drill-down is complete */}
              {!drilldownStreaming && drilldownText && (
                <div className="flex items-center gap-3 pt-3 border-t" style={{ borderColor: "var(--border)" }}>
                  <button
                    onClick={saveToDecisionRegister}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-colors"
                    style={{
                      background: "var(--surface-2)",
                      border: "1px solid var(--border)",
                      color: "var(--accent)",
                    }}
                  >
                    <BookmarkPlus size={13} />
                    Save to Decision Register
                  </button>
                  {savedMsg && (
                    <span className="text-[12px]" style={{ color: "#22c55e" }}>
                      {savedMsg}
                    </span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
