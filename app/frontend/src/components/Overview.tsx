import { useEffect, useState } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, PieChart, Pie, Legend,
} from "recharts";
import {
  TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle2,
  Clock, FileText, Users, Activity, Zap, ShieldAlert, RefreshCw,
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

export default function Overview() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
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
    (acc, k) => { acc[k.status] = (acc[k.status] || 0) + 1; return acc; },
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

  return (
    <div className="space-y-5">
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

      {/* Stat cards row */}
      <div className="grid grid-cols-4 gap-4">
        {[
          {
            label: "Active KPIs",
            value: data.kpis.length,
            sub: `${kpiStatusCounts["Red"] || 0} critical`,
            icon: <Activity size={18} />,
            color: "#f59e0b",
          },
          {
            label: "Open Risks",
            value: totalRisks,
            sub: `${criticalRisks} critical`,
            icon: <ShieldAlert size={18} />,
            color: criticalRisks > 0 ? "#ef4444" : "#22c55e",
          },
          {
            label: "Action Items",
            value: totalActions,
            sub: `${overdueActions} overdue`,
            icon: <CheckCircle2 size={18} />,
            color: overdueActions > 0 ? "#f97316" : "#22c55e",
          },
          {
            label: "AI Queries (7d)",
            value: data.audit_stats.total_queries,
            sub: `${(data.audit_stats.avg_confidence * 100).toFixed(0)}% avg confidence`,
            icon: <Zap size={18} />,
            color: "#a78bfa",
          },
        ].map((s) => (
          <div key={s.label} className="glass-card p-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-[11px] text-slate-400 uppercase tracking-wider">{s.label}</p>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${s.color}20`, color: s.color }}>
                {s.icon}
              </div>
            </div>
            <p className="text-3xl font-bold text-white">{s.value.toLocaleString()}</p>
            <p className="text-[11px] text-slate-500 mt-1">{s.sub}</p>
          </div>
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
