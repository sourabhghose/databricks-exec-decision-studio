import { useEffect, useState } from "react";
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
};

function KPICard({ kpi }: { kpi: KPI }) {
  const up = kpi.pct_vs_target >= 0;
  const Icon = up ? TrendingUp : TrendingDown;
  const borderColor = STATUS_COLORS[kpi.status] || "#64748b";

  return (
    <div
      className="glass-card p-4 flex flex-col gap-2 border-l-4"
      style={{ borderLeftColor: borderColor }}
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

/** Right-side drawer for drilldown details. */
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
  const title = METRIC_LABELS[metric] || metric;

  return (
    <>
      {/* Dark overlay */}
      <div
        className="fixed inset-0 z-40 bg-black/50"
        onClick={onClose}
      />

      {/* Drawer panel */}
      <div className="fixed inset-y-0 right-0 z-50 w-[520px] flex flex-col bg-slate-900 border-l border-slate-700/50 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700/50 flex-shrink-0">
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-0.5">Drilldown</p>
            <h3 className="text-[15px] font-bold text-white">{title}</h3>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
          {/* AI Analysis section */}
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={14} className="text-amber-400" />
              <p className="text-[11px] font-bold text-amber-400 uppercase tracking-wider">AI Analysis</p>
            </div>

            {loading ? (
              <div className="flex items-center gap-2 py-4 justify-center">
                <RefreshCw size={16} className="text-amber-400 animate-spin" />
                <p className="text-[12px] text-slate-400">Generating executive analysis…</p>
              </div>
            ) : data?.analysis ? (
              <AnalysisText text={data.analysis} />
            ) : (
              <p className="text-[12px] text-slate-500 italic">No analysis available.</p>
            )}
          </div>

          {/* Items section */}
          {data && data.items.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-3">
                {data.items.length} {metric === "kpis" ? "KPIs" : metric === "risks" ? "Risks" : metric === "actions" ? "Actions" : "Queries"}
              </p>

              {metric === "kpis" && <KpiItems items={data.items} />}
              {metric === "risks" && <RiskItems items={data.items} />}
              {metric === "actions" && <ActionItems items={data.items} />}
              {metric === "queries" && <QueryItems items={data.items} />}
            </div>
          )}

          {data && data.items.length === 0 && !loading && (
            <p className="text-[12px] text-slate-500 italic text-center py-4">No items to display.</p>
          )}
        </div>
      </div>
    </>
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

  async function openDrilldown(metric: string) {
    setDrilldown(metric);
    setDrilldownLoading(true);
    setDrilldownData(null);
    try {
      const r = await fetch(`/api/overview/drilldown?metric=${metric}`);
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
            <KPICard key={kpi.kpi_name} kpi={kpi} />
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
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
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
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
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
