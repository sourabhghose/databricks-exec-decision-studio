import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, PieChart, Pie, Legend,
} from "recharts";
import {
  TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle2,
  Clock, FileText, Users, Activity, Zap, ShieldAlert, RefreshCw,
  X, ChevronRight, Sparkles,
} from "lucide-react";

interface KPI {
  kpi_name: string;
  business_unit: string;
  category: string;
  value: number;
  unit: string;
  target: number;
  pct_vs_target: number;
  status: "Green" | "Yellow" | "Red";
  is_anomaly: boolean;
}

interface Risk {
  risk_id: string;
  category: string;
  description: string;
  likelihood: string;
  consequence: string;
  rating: string;
  risk_score: number | string;
  owner: string;
  status: string;
}

interface Decision {
  decision_id: string;
  decision_date: string;
  committee: string;
  description: string;
  decision_type: string;
  implementation_status: string;
}

interface OverviewData {
  demo: boolean;
  kpis: KPI[];
  risk_summary: Record<string, number>;
  top_risks: Risk[];
  recent_decisions: Decision[];
  action_summary: Record<string, number>;
  audit_stats: { total_queries: number; avg_confidence: number; avg_latency_ms: number };
  doc_stats: { total_documents: number; total_chunks: number };
}

interface DrilldownData {
  metric: string;
  items: any[];
  analysis: string;
  kpi_name?: string;
  filter?: string;
}

const STATUS_COLORS: Record<string, string> = {
  Green: "#22c55e",
  Yellow: "#eab308",
  Red: "#ef4444",
};

const RISK_COLORS: Record<string, string> = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};

const ACTION_COLORS: Record<string, string> = {
  open: "#64748b",
  in_progress: "#3b82f6",
  complete: "#22c55e",
  overdue: "#ef4444",
};

const METRIC_LABELS: Record<string, string> = {
  kpis: "KPI Performance",
  risks: "Open Risk Register",
  actions: "Action Items",
  queries: "AI Query Activity",
  kpi_detail: "KPI Deep Dive",
};

function KPICard({ kpi, onClick }: { kpi: KPI; onClick?: () => void }) {
  const up = kpi.pct_vs_target >= 0;
  const Icon = up ? TrendingUp : TrendingDown;
  const borderColor = STATUS_COLORS[kpi.status] || "#64748b";

  return (
    <div
      className="glass-card p-4 flex flex-col gap-2 border-l-4 cursor-pointer group transition-all hover:shadow-lg"
      style={{ borderLeftColor: borderColor }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-[11px] text-slate-400 uppercase tracking-wider">{kpi.business_unit}</p>
          <p className="text-[13px] font-semibold text-slate-200 mt-0.5 leading-tight">{kpi.kpi_name}</p>
        </div>
        {kpi.is_anomaly && (
          <span className="text-[10px] bg-red-500/20 text-red-400 border border-red-500/30 px-1.5 py-0.5 rounded font-medium whitespace-nowrap">
            ANOMALY
          </span>
        )}
      </div>
      <div className="flex items-end justify-between">
        <div>
          <span className="text-xl font-bold text-white">
            {kpi.value?.toLocaleString()}
          </span>
          <span className="text-xs text-slate-400 ml-1">{kpi.unit}</span>
        </div>
        <div className="flex items-center gap-1" style={{ color: borderColor }}>
          <Icon size={14} />
          <span className="text-[12px] font-semibold">
            {up ? "+" : ""}{kpi.pct_vs_target?.toFixed(1)}%
          </span>
        </div>
      </div>
      <div className="flex items-center gap-1.5">
        <div className="flex-1 bg-slate-700/50 rounded-full h-1.5">
          <div
            className="h-1.5 rounded-full transition-all"
            style={{
              width: `${Math.min(100, Math.max(0, (kpi.value / (kpi.target || 1)) * 100))}%`,
              backgroundColor: borderColor,
            }}
          />
        </div>
        <span className="text-[10px] text-slate-500">
          Target: {kpi.target?.toLocaleString()} {kpi.unit}
        </span>
      </div>
      <div className="flex justify-end mt-0.5">
        <span className="text-[10px] text-slate-600 group-hover:text-slate-400 flex items-center gap-0.5 transition-colors">
          AI Analysis <ChevronRight size={10} />
        </span>
      </div>
    </div>
  );
}

function useTooltipStyle() {
  const dark = document.documentElement.classList.contains("dark");
  return dark
    ? { backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#e2e8f0", fontSize: "12px" }
    : { backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", color: "#0f172a", fontSize: "12px", boxShadow: "0 2px 8px rgba(0,0,0,0.12)" };
}

function useChartColors() {
  const dark = document.documentElement.classList.contains("dark");
  return { grid: dark ? "#1e293b" : "#f1f5f9", tick: dark ? "#94a3b8" : "#64748b" };
}

/** Render AI analysis text with basic markdown-like formatting. */
function AnalysisText({ text }: { text: string }) {
  return (
    <ul className="space-y-0.5 list-none p-0">
      {text.split("\n").map((line, idx) => {
        if (line.startsWith("## ") || line.startsWith("# "))
          return <p key={idx} className="text-[12px] font-bold text-amber-300 mt-3 mb-1 uppercase tracking-wide">{line.replace(/^#+\s*/, "")}</p>;
        if (line.startsWith("- "))
          return <li key={idx} className="text-[12px] text-slate-300 leading-relaxed ml-3 list-disc">{line.slice(2)}</li>;
        if (line.trim() === "")
          return <div key={idx} className="h-1" />;
        return <p key={idx} className="text-[12px] text-slate-300 leading-relaxed">{line}</p>;
      })}
    </ul>
  );
}

/** Drilldown items for KPIs: table view. */
function KpiItems({ items }: { items: any[] }) {
  const thCls = "py-2 px-2 text-slate-400 font-medium";
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[11px]">
        <thead>
          <tr className="border-b border-slate-700/50">
            <th className={`text-left ${thCls}`}>KPI Name</th>
            <th className={`text-left ${thCls}`}>Business Unit</th>
            <th className={`text-right ${thCls}`}>Value</th>
            <th className={`text-right ${thCls}`}>Target</th>
            <th className={`text-right ${thCls}`}>Δ%</th>
            <th className={`text-center ${thCls}`}>Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((kpi, i) => {
            const pct = kpi.pct_vs_target ?? 0;
            const c = STATUS_COLORS[kpi.status] || "#64748b";
            const badge = { backgroundColor: `${c}20`, color: c, border: `1px solid ${c}40` };
            return (
              <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                <td className="py-2 px-2 text-slate-200 font-medium">
                  {kpi.kpi_name}
                  {kpi.is_anomaly && <span className="ml-1 text-[9px] bg-red-500/20 text-red-400 border border-red-500/30 px-1 py-0.5 rounded">ANOMALY</span>}
                </td>
                <td className="py-2 px-2 text-slate-400">{kpi.business_unit}</td>
                <td className="py-2 px-2 text-right text-white font-semibold">{Number(kpi.value).toLocaleString()} <span className="text-slate-500 font-normal">{kpi.unit}</span></td>
                <td className="py-2 px-2 text-right text-slate-400">{Number(kpi.target).toLocaleString()} <span className="text-slate-600">{kpi.unit}</span></td>
                <td className="py-2 px-2 text-right font-semibold" style={{ color: c }}>{pct >= 0 ? "+" : ""}{Number(pct).toFixed(1)}%</td>
                <td className="py-2 px-2 text-center"><span className="text-[10px] font-bold px-2 py-0.5 rounded" style={badge}>{kpi.status}</span></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/** Drilldown items for Risks: card view. */
function RiskItems({ items }: { items: any[] }) {
  return (
    <div className="space-y-2">
      {items.map((risk, i) => {
        const c = RISK_COLORS[risk.rating] || "#64748b";
        return (
          <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/40 border border-slate-700/30">
            <span className="text-[10px] font-bold px-2 py-1 rounded mt-0.5 flex-shrink-0" style={{ backgroundColor: `${c}20`, color: c, border: `1px solid ${c}40` }}>{risk.rating}</span>
            <div className="min-w-0 flex-1">
              <p className="text-[12px] text-slate-200 leading-snug">{risk.description}</p>
              <p className="text-[10px] text-slate-500 mt-1">{risk.category} · Owner: {risk.owner}</p>
            </div>
            <span className="text-[13px] font-bold flex-shrink-0" style={{ color: c }}>{risk.risk_score}</span>
          </div>
        );
      })}
    </div>
  );
}

/** Drilldown items for Actions: list view. */
function ActionItems({ items }: { items: any[] }) {
  return (
    <div className="space-y-2">
      {items.map((action, i) => {
        const c = ACTION_COLORS[action.status] || "#64748b";
        return (
          <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/40 border border-slate-700/30">
            <span className="text-[10px] font-bold px-2 py-1 rounded mt-0.5 flex-shrink-0 capitalize" style={{ backgroundColor: `${c}20`, color: c, border: `1px solid ${c}40` }}>{(action.status || "").replace("_", " ")}</span>
            <div className="min-w-0 flex-1">
              <p className="text-[12px] text-slate-200 leading-snug font-medium">{action.title || action.description || "Untitled"}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">
                Owner: {action.owner || "Unassigned"}{action.due_date ? ` · Due: ${String(action.due_date).slice(0, 10)}` : ""}{action.priority ? ` · Priority: ${action.priority}` : ""}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/** Drilldown items for Queries: list view. */
function QueryItems({ items }: { items: any[] }) {
  return (
    <div className="space-y-2">
      {items.map((q, i) => {
        const conf = q.confidence_score ? `${(Number(q.confidence_score) * 100).toFixed(0)}%` : "N/A";
        const raw = String(q.query_text || "");
        const queryText = raw.slice(0, 80) + (raw.length > 80 ? "…" : "");
        const ts = q.timestamp ? String(q.timestamp).slice(0, 16).replace("T", " ") : "";
        return (
          <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/40 border border-slate-700/30">
            <span className="text-[10px] font-bold px-2 py-1 rounded mt-0.5 flex-shrink-0 bg-violet-500/20 text-violet-300 border border-violet-500/30 whitespace-nowrap">{q.agent_name || "Agent"}</span>
            <div className="min-w-0 flex-1">
              <p className="text-[12px] text-slate-200 leading-snug">{queryText}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Confidence: {conf}{ts ? ` · ${ts}` : ""}{q.user_role ? ` · ${q.user_role}` : ""}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/** KPI time-series history table for kpi_detail drill-down. */
function KpiDetailItems({ items }: { items: any[] }) {
  const unit = items[0]?.unit || "";
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #1e293b" }}>
            {["Period", "Value", "Target", "Δ%", "Anomaly"].map((h) => (
              <th key={h} style={{ padding: "6px 8px", color: "#64748b", fontWeight: 500, textAlign: h === "Period" ? "left" : "center" }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[...items].reverse().map((row, i) => {
            const pct = Number(row.pct ?? 0);
            const c = Math.abs(pct) < 5 ? "#22c55e" : pct < -10 ? "#ef4444" : "#eab308";
            const isAnom = String(row.is_anomaly || "").toLowerCase() === "true";
            return (
              <tr key={i} style={{ borderBottom: "1px solid #0f172a", background: i % 2 === 0 ? "rgba(255,255,255,0.02)" : "transparent" }}>
                <td style={{ padding: "5px 8px", color: "#e2e8f0" }}>{row.period}</td>
                <td style={{ padding: "5px 8px", color: "#fff", textAlign: "center", fontWeight: 600 }}>{Number(row.value).toLocaleString()} <span style={{ color: "#64748b", fontWeight: 400 }}>{unit}</span></td>
                <td style={{ padding: "5px 8px", color: "#94a3b8", textAlign: "center" }}>{Number(row.target).toLocaleString()} {unit}</td>
                <td style={{ padding: "5px 8px", textAlign: "center", color: c, fontWeight: 700 }}>{pct >= 0 ? "+" : ""}{pct.toFixed(1)}%</td>
                <td style={{ padding: "5px 8px", textAlign: "center" }}>{isAnom ? <span style={{ fontSize: 9, background: "rgba(239,68,68,0.2)", color: "#f87171", border: "1px solid rgba(239,68,68,0.3)", padding: "2px 5px", borderRadius: 4 }}>ANOMALY</span> : <span style={{ color: "#334155" }}>—</span>}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/** Right-side drawer — rendered via portal at document.body to escape stacking contexts. */
function DrilldownDrawer({
  metric,
  data,
  loading,
  onClose,
}: {
  metric: string;
  data: DrilldownData | null;
  loading: boolean;
  onClose: () => void;
}) {
  const title = metric === "kpi_detail" && data?.kpi_name
    ? data.kpi_name
    : (METRIC_LABELS[metric] || metric);

  const count = data?.items?.length ?? 0;
  const countLabel =
    metric === "kpis" ? "KPIs"
    : metric === "risks" ? "Risks"
    : metric === "actions" ? "Actions"
    : metric === "kpi_detail" ? "Periods"
    : "Queries";

  return createPortal(
    <>
      {/* Overlay */}
      <div
        onClick={onClose}
        style={{ position: "fixed", inset: 0, zIndex: 9998, background: "rgba(0,0,0,0.6)", backdropFilter: "blur(2px)" }}
      />

      {/* Drawer */}
      <div style={{
        position: "fixed", top: 0, right: 0, bottom: 0, width: 540,
        zIndex: 9999, background: "#0f172a", borderLeft: "1px solid #1e293b",
        display: "flex", flexDirection: "column", boxShadow: "-8px 0 32px rgba(0,0,0,0.5)",
      }}>
        {/* Header */}
        <div style={{ padding: "16px 20px", borderBottom: "1px solid #1e293b", display: "flex", alignItems: "center", justifyContent: "space-between", flexShrink: 0 }}>
          <div>
            <p style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 2 }}>Drill-Down</p>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: "#f1f5f9", margin: 0 }}>{title}</h3>
          </div>
          <button
            onClick={onClose}
            style={{ width: 32, height: 32, borderRadius: 8, border: "1px solid #1e293b", background: "transparent", color: "#64748b", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Scrollable body */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px 20px", display: "flex", flexDirection: "column", gap: 16 }}>

          {/* AI Analysis */}
          <div style={{ borderRadius: 12, border: "1px solid rgba(245,158,11,0.2)", background: "rgba(245,158,11,0.05)", padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <Sparkles size={14} color="#f59e0b" />
              <span style={{ fontSize: 11, fontWeight: 700, color: "#f59e0b", textTransform: "uppercase", letterSpacing: "0.08em" }}>AI Analysis · Claude Sonnet 4.6</span>
            </div>
            {loading ? (
              <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "16px 0", justifyContent: "center" }}>
                <RefreshCw size={16} color="#f59e0b" className="animate-spin" />
                <span style={{ fontSize: 12, color: "#94a3b8" }}>Generating executive analysis…</span>
              </div>
            ) : data?.analysis ? (
              <AnalysisText text={data.analysis} />
            ) : (
              <span style={{ fontSize: 12, color: "#64748b", fontStyle: "italic" }}>No analysis available.</span>
            )}
          </div>

          {/* Items list */}
          {!loading && count > 0 && (
            <div>
              <p style={{ fontSize: 11, fontWeight: 600, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>
                {count} {countLabel}
              </p>
              {metric === "kpis"       && <KpiItems       items={data!.items} />}
              {metric === "risks"      && <RiskItems      items={data!.items} />}
              {metric === "actions"    && <ActionItems    items={data!.items} />}
              {metric === "queries"    && <QueryItems     items={data!.items} />}
              {metric === "kpi_detail" && <KpiDetailItems items={data!.items} />}
            </div>
          )}

          {!loading && count === 0 && data && (
            <p style={{ fontSize: 12, color: "#64748b", fontStyle: "italic", textAlign: "center", padding: "16px 0" }}>No items to display.</p>
          )}
        </div>
      </div>
    </>,
    document.body
  );
}

export default function Overview() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [drilldown, setDrilldown] = useState<string | null>(null);
  const [drilldownData, setDrilldownData] = useState<DrilldownData | null>(null);
  const [drilldownLoading, setDrilldownLoading] = useState(false);
  const tooltipStyle = useTooltipStyle();
  const chartColors = useChartColors();

  async function fetchData() {
    setLoading(true);
    try {
      const r = await fetch("/api/overview");
      if (r.ok) setData(await r.json());
    } catch (e) {
      console.error("Overview fetch failed", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchData(); }, []);

  function handleRefresh() {
    setLastRefresh(new Date());
    fetchData();
  }

  async function openDrilldown(metric: string, filterKey = "", filterVal = "") {
    setDrilldown(metric);
    setDrilldownLoading(true);
    setDrilldownData(null);
    try {
      const params = new URLSearchParams({ metric });
      if (filterKey) params.set("filter_key", filterKey);
      if (filterVal) params.set("filter_val", filterVal);
      const r = await fetch(`/api/overview/drilldown?${params}`);
      if (r.ok) setDrilldownData(await r.json());
    } catch (e) {
      console.error("Drilldown fetch failed", e);
    } finally {
      setDrilldownLoading(false);
    }
  }

  function closeDrilldown() {
    setDrilldown(null);
    setDrilldownData(null);
    setDrilldownLoading(false);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw size={28} className="text-gold animate-spin mx-auto mb-3" />
          <p className="text-slate-400 text-sm">Loading executive overview…</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Failed to load overview data.</p>
      </div>
    );
  }

  // ── Derived data for charts ──────────────────────────────────────────────────
  const riskChartData = Object.entries(data.risk_summary).map(([rating, cnt]) => ({
    rating,
    count: cnt,
    fill: RISK_COLORS[rating] || "#64748b",
  }));

  const actionChartData = Object.entries(data.action_summary).map(([status, cnt]) => ({
    status: status.replace("_", " "),
    statusKey: status,
    count: cnt,
    fill: ACTION_COLORS[status] || "#64748b",
  }));

  const kpiStatusCounts = data.kpis.reduce(
    (acc, k) => ({ ...acc, [k.status]: (acc[k.status] || 0) + 1 }),
    {} as Record<string, number>
  );
  const kpiPieData = Object.entries(kpiStatusCounts).map(([s, v]) => ({
    name: s,
    value: v,
    fill: STATUS_COLORS[s],
  }));

  const totalActions = Object.values(data.action_summary).reduce((a, b) => a + b, 0);
  const totalRisks = Object.values(data.risk_summary).reduce((a, b) => a + b, 0);
  const criticalRisks = data.risk_summary["Critical"] || 0;
  const overdueActions = data.action_summary["overdue"] || 0;

  const statusColor =
    criticalRisks > 3 || overdueActions > 5 ? "#ef4444"
    : criticalRisks > 1 || overdueActions > 2 ? "#eab308"
    : "#22c55e";
  const statusLabel =
    criticalRisks > 3 || overdueActions > 5 ? "Elevated Risk"
    : criticalRisks > 1 || overdueActions > 2 ? "Monitor"
    : "On Track";

  // Hero stat card definitions
  const heroCards = [
    {
      label: "Active KPIs",
      metric: "kpis",
      value: data.kpis.length,
      sub: `${kpiStatusCounts["Red"] || 0} critical`,
      icon: <Activity size={18} />,
      color: "#f59e0b",
    },
    {
      label: "Open Risks",
      metric: "risks",
      value: totalRisks,
      sub: `${criticalRisks} critical`,
      icon: <ShieldAlert size={18} />,
      color: criticalRisks > 0 ? "#ef4444" : "#22c55e",
    },
    {
      label: "Action Items",
      metric: "actions",
      value: totalActions,
      sub: `${overdueActions} overdue`,
      icon: <CheckCircle2 size={18} />,
      color: overdueActions > 0 ? "#f97316" : "#22c55e",
    },
    {
      label: "AI Queries (7d)",
      metric: "queries",
      value: data.audit_stats.total_queries,
      sub: `${(data.audit_stats.avg_confidence * 100).toFixed(0)}% avg confidence`,
      icon: <Zap size={18} />,
      color: "#a78bfa",
    },
  ];

  return (
    <div className="space-y-5">
      {/* Drilldown drawer */}
      {drilldown && (
        <DrilldownDrawer
          metric={drilldown}
          data={drilldownData}
          loading={drilldownLoading}
          onClose={closeDrilldown}
        />
      )}

      {/* Header row */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Executive Overview</h2>
          <p className="text-[12px] text-slate-400 mt-0.5">
            Real-time strategic intelligence · Last refreshed {lastRefresh.toLocaleTimeString()}
            {data.demo && (
              <span className="ml-2 text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded text-[10px] font-medium border border-amber-400/20">
                DEMO DATA
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-[12px] font-semibold"
            style={{ borderColor: statusColor, color: statusColor, backgroundColor: `${statusColor}15` }}
          >
            <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: statusColor }} />
            {statusLabel}
          </div>
          <button
            onClick={handleRefresh}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] transition-colors"
            style={{ background: "var(--surface-2)", border: "1px solid var(--border)", color: "var(--text-3)" }}
          >
            <RefreshCw size={13} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stat cards row — clickable */}
      <div className="grid grid-cols-4 gap-4">
        {heroCards.map((s) => (
          <button
            key={s.label}
            onClick={() => openDrilldown(s.metric)}
            className="glass-card p-4 text-left w-full cursor-pointer transition-all hover:border-amber-400/30 group"
          >
            <div className="flex items-center justify-between mb-3">
              <p className="text-[11px] text-slate-400 uppercase tracking-wider">{s.label}</p>
              <div className="flex items-center gap-1">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${s.color}20`, color: s.color }}>
                  {s.icon}
                </div>
              </div>
            </div>
            <div className="flex items-end justify-between">
              <p className="text-3xl font-bold text-white">{s.value.toLocaleString()}</p>
              <ChevronRight size={14} className="text-slate-600 group-hover:text-slate-400 transition-colors mb-1" />
            </div>
            <p className="text-[11px] text-slate-500 mt-1">{s.sub}</p>
          </button>
        ))}
      </div>

      {/* KPI Hero Cards */}
      <div>
        <h3 className="text-[13px] font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
          <TrendingUp size={14} className="text-gold" />
          KPI Performance
        </h3>
        <div className="grid grid-cols-3 gap-3">
          {data.kpis.slice(0, 6).map((kpi) => (
            <KPICard key={kpi.kpi_name} kpi={kpi} onClick={() => openDrilldown("kpi_detail", "", kpi.kpi_name)} />
          ))}
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-3 gap-4">
        {/* Risk distribution */}
        <div className="glass-card p-4">
          <h3 className="text-[12px] font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
            <AlertTriangle size={13} className="text-amber-400" />
            Risk Distribution
          </h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={riskChartData} barSize={36}>
              <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
              <XAxis dataKey="rating" tick={{ fill: chartColors.tick, fontSize: 11 }} />
              <YAxis tick={{ fill: chartColors.tick, fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]} onClick={(d: any) => openDrilldown("risks", "rating", d.rating)} style={{ cursor: "pointer" }}>
                {riskChartData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* KPI status pie */}
        <div className="glass-card p-4">
          <h3 className="text-[12px] font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Activity size={13} className="text-gold" />
            KPI Health Status
          </h3>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={kpiPieData}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={72}
                paddingAngle={3}
                dataKey="value"
                onClick={(d: any) => openDrilldown("kpis", "status", d.name)}
                style={{ cursor: "pointer" }}
              >
                {kpiPieData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend
                formatter={(v) => <span style={{ color: chartColors.tick, fontSize: 11 }}>{v}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Action items status */}
        <div className="glass-card p-4">
          <h3 className="text-[12px] font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
            <CheckCircle2 size={13} className="text-blue-400" />
            Action Items
          </h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={actionChartData} barSize={36} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
              <XAxis type="number" tick={{ fill: chartColors.tick, fontSize: 11 }} />
              <YAxis dataKey="status" type="category" tick={{ fill: chartColors.tick, fontSize: 10 }} width={72} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" radius={[0, 4, 4, 0]} onClick={(d: any) => openDrilldown("actions", "status", d.statusKey)} style={{ cursor: "pointer" }}>
                {actionChartData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom row: top risks + recent decisions */}
      <div className="grid grid-cols-2 gap-4">
        {/* Top risks */}
        <div className="glass-card p-4">
          <h3 className="text-[12px] font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
            <ShieldAlert size={13} className="text-red-400" />
            Top Open Risks
          </h3>
          <div className="space-y-2">
            {data.top_risks.slice(0, 5).map((risk, i) => (
              <div key={i} className="flex items-start gap-3 p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/30">
                <span
                  className="text-[10px] font-bold px-1.5 py-0.5 rounded mt-0.5 flex-shrink-0"
                  style={{
                    backgroundColor: `${RISK_COLORS[risk.rating] || "#64748b"}20`,
                    color: RISK_COLORS[risk.rating] || "#94a3b8",
                    border: `1px solid ${RISK_COLORS[risk.rating] || "#64748b"}40`,
                  }}
                >
                  {risk.rating}
                </span>
                <div className="min-w-0">
                  <p className="text-[12px] text-slate-200 leading-snug truncate">{risk.description}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">{risk.category} · Owner: {risk.owner}</p>
                </div>
                <span className="text-[11px] font-bold text-slate-400 flex-shrink-0 ml-auto">
                  {risk.risk_score}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent decisions */}
        <div className="glass-card p-4">
          <h3 className="text-[12px] font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
            <FileText size={13} className="text-purple-400" />
            Recent Decisions
          </h3>
          <div className="space-y-2">
            {data.recent_decisions.slice(0, 4).map((dec, i) => {
              const statusColors: Record<string, string> = {
                "Approved": "#22c55e",
                "In Progress": "#3b82f6",
                "Pending": "#eab308",
                "Implemented": "#a78bfa",
              };
              const sc = statusColors[dec.implementation_status] || "#64748b";
              return (
                <div key={i} className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/30">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-[10px] text-slate-500">{dec.committee}</span>
                    <span
                      className="text-[10px] font-medium px-1.5 py-0.5 rounded"
                      style={{ backgroundColor: `${sc}15`, color: sc, border: `1px solid ${sc}30` }}
                    >
                      {dec.implementation_status}
                    </span>
                  </div>
                  <p className="text-[12px] text-slate-200 leading-snug">{dec.description}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">
                    {dec.decision_date?.slice(0, 10)} · {dec.decision_type}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* System status footer */}
      <div className="glass-card p-4">
        <h3 className="text-[12px] font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
          <Zap size={13} className="text-gold" />
          System Intelligence Summary
        </h3>
        <div className="grid grid-cols-4 gap-4">
          {[
            {
              label: "Document Corpus",
              value: `${data.doc_stats.total_documents} docs`,
              sub: `${data.doc_stats.total_chunks.toLocaleString()} chunks indexed`,
              icon: <FileText size={15} />,
              color: "#64748b",
            },
            {
              label: "AI Response Latency",
              value: `${(data.audit_stats.avg_latency_ms / 1000).toFixed(1)}s avg`,
              sub: "7-day rolling average",
              icon: <Clock size={15} />,
              color: data.audit_stats.avg_latency_ms < 3000 ? "#22c55e" : "#eab308",
            },
            {
              label: "Agent Confidence",
              value: `${(data.audit_stats.avg_confidence * 100).toFixed(0)}%`,
              sub: "Avg confidence score",
              icon: <Activity size={15} />,
              color: data.audit_stats.avg_confidence > 0.8 ? "#22c55e" : "#eab308",
            },
            {
              label: "Intelligence Queries",
              value: data.audit_stats.total_queries.toLocaleString(),
              sub: "Last 7 days",
              icon: <Users size={15} />,
              color: "#a78bfa",
            },
          ].map((s) => (
            <div key={s.label} className="flex items-start gap-3">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style={{ backgroundColor: `${s.color}20`, color: s.color }}
              >
                {s.icon}
              </div>
              <div>
                <p className="text-[11px] text-slate-400">{s.label}</p>
                <p className="text-[15px] font-bold text-white">{s.value}</p>
                <p className="text-[10px] text-slate-500">{s.sub}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
