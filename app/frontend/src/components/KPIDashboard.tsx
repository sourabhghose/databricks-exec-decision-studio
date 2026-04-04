import { useState, useEffect } from "react";
import {
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  DollarSign,
  Activity,
  Users,
  Leaf,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts";

interface KPI {
  kpi_name: string;
  business_unit: string;
  category: string;
  value: number;
  unit: string;
  target: number;
  pct_vs_target: number;
  status: string;
  is_anomaly: boolean;
}

interface TrendPoint {
  period: string;
  value: number;
  unit: string;
  business_unit: string;
}

interface FinancialRow {
  business_unit: string;
  actual: number;
  budget: number;
}

const SUMMARY_CARDS = [
  {
    key: "Group EBITDA Margin",
    icon: <DollarSign size={20} />,
    label: "Group EBITDA",
    color: "from-emerald-500/20 to-emerald-600/10",
    iconColor: "text-emerald-400",
  },
  {
    key: "Retail Customer NPS",
    icon: <Users size={20} />,
    label: "Customer NPS",
    color: "from-blue-500/20 to-blue-600/10",
    iconColor: "text-blue-400",
  },
  {
    key: "LYB Plant Availability",
    icon: <Activity size={20} />,
    label: "Plant Availability",
    color: "from-gold/20 to-gold-dark/10",
    iconColor: "text-gold",
  },
  {
    key: "Net Debt to EBITDA",
    icon: <Leaf size={20} />,
    label: "Net Debt/EBITDA",
    color: "from-purple-500/20 to-purple-600/10",
    iconColor: "text-purple-400",
  },
];

const KPI_COLORS: Record<string, string> = {
  "Group EBITDA Margin": "#c4962a",
  "Retail Customer NPS": "#60a5fa",
  "LYB Plant Availability": "#f59e0b",
  "Retail Churn Rate": "#f87171",
};

const BU_COLORS: Record<string, string> = {
  Generation: "#c4962a",
  Retail: "#60a5fa",
  Trading: "#a78bfa",
  Corporate: "#64748b",
};

function statusClass(status: string): string {
  const s = status.toLowerCase();
  if (s.includes("green")) return "status-green";
  if (s.includes("red")) return "status-red";
  return "status-yellow";
}

function trendIcon(pct: number) {
  if (pct > 2) return <TrendingUp size={14} className="text-emerald-400" />;
  if (pct < -2) return <TrendingDown size={14} className="text-red-400" />;
  return <Minus size={14} className="text-slate-500" />;
}

export default function KPIDashboard() {
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [trends, setTrends] = useState<Record<string, TrendPoint[]>>({});
  const [financials, setFinancials] = useState<FinancialRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [demo, setDemo] = useState(false);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [kpiRes, trendRes, finRes] = await Promise.all([
        fetch("/api/kpi"),
        fetch("/api/kpi/trends"),
        fetch("/api/financials"),
      ]);
      const kpiData = await kpiRes.json();
      const trendData = await trendRes.json();
      const finData = await finRes.json();

      setKpis(kpiData.data || []);
      setTrends(trendData.data || {});
      setFinancials(finData.data || []);
      setDemo(kpiData.demo || false);
    } catch {
      setKpis([]);
      setTrends({});
      setFinancials([]);
      setDemo(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const findKPI = (name: string): KPI | undefined =>
    kpis.find((k) => k.kpi_name === name);

  // Build chart data for trends: merge all KPIs into one array keyed by period
  const trendChartData = (() => {
    const kpiNames = Object.keys(trends);
    if (!kpiNames.length) return [];

    // Get all unique periods
    const periodsSet = new Set<string>();
    for (const name of kpiNames) {
      for (const pt of trends[name]) {
        periodsSet.add(pt.period);
      }
    }
    const periods = Array.from(periodsSet).sort();

    return periods.map((period) => {
      const row: Record<string, string | number> = { period: period.slice(0, 7) };
      for (const name of kpiNames) {
        const pt = trends[name]?.find((p) => p.period === period);
        if (pt) row[name] = pt.value;
      }
      return row;
    });
  })();

  const trendKPINames = Object.keys(trends);

  return (
    <div className="space-y-6">
      {/* -- Header -- */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">
            Strategic KPI Dashboard
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            {demo ? (
              <span className="text-gold/70">Demo data - connect SQL warehouse for live metrics</span>
            ) : (
              <>Live from <code className="text-xs text-slate-400">eds.eds_synthetic.kpi_timeseries</code></>
            )}
          </p>
        </div>
        <button
          onClick={fetchAll}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg glass-card
            text-sm text-slate-300 hover:text-gold hover:border-gold/30
            transition-all disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* -- Summary cards -- */}
      <div className="grid grid-cols-4 gap-4">
        {SUMMARY_CARDS.map((card) => {
          const kpi = findKPI(card.key);
          return (
            <div
              key={card.key}
              className={`glass-card p-5 bg-gradient-to-br ${card.color}`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className={`${card.iconColor}`}>{card.icon}</span>
                {kpi && trendIcon(kpi.pct_vs_target)}
              </div>
              <div className="text-2xl font-bold text-slate-100 mb-0.5">
                {kpi ? `${kpi.value} ${kpi.unit}` : "--"}
              </div>
              <div className="text-xs text-slate-400">{card.label}</div>
              {kpi && (
                <div
                  className={`text-xs mt-2 font-medium ${
                    kpi.pct_vs_target >= 0 ? "text-emerald-400" : "text-red-400"
                  }`}
                >
                  {kpi.pct_vs_target >= 0 ? "+" : ""}
                  {kpi.pct_vs_target.toFixed(1)}% vs target
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* -- KPI Trends Chart -- */}
      {trendChartData.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-base font-semibold text-slate-200 mb-4">
            KPI Trends (Last 6 Periods)
          </h3>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={trendChartData} margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4d" />
              <XAxis
                dataKey="period"
                stroke="#64748b"
                tick={{ fontSize: 12, fill: "#94a3b8" }}
              />
              <YAxis stroke="#64748b" tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#111827",
                  border: "1px solid #1e2d4d",
                  borderRadius: "8px",
                  fontSize: "13px",
                  color: "#e2e8f0",
                }}
                labelStyle={{ color: "#c4962a", fontWeight: 600 }}
              />
              <Legend
                wrapperStyle={{ fontSize: "12px", color: "#94a3b8" }}
              />
              {trendKPINames.map((name) => (
                <Line
                  key={name}
                  type="monotone"
                  dataKey={name}
                  stroke={KPI_COLORS[name] || "#94a3b8"}
                  strokeWidth={2}
                  dot={{ r: 4, fill: KPI_COLORS[name] || "#94a3b8" }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* -- Full KPI table -- */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  KPI Name
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Business Unit
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Category
                </th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Value
                </th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Target
                </th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  % vs Target
                </th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {loading && kpis.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500">
                    <RefreshCw size={20} className="animate-spin mx-auto mb-2" />
                    Loading KPI data...
                  </td>
                </tr>
              ) : kpis.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500">
                    No KPI data available
                  </td>
                </tr>
              ) : (
                kpis.map((kpi, i) => (
                  <tr
                    key={i}
                    className={`border-b border-dark-border/50 transition-colors hover:bg-white/[0.02] ${
                      i % 2 === 0 ? "bg-transparent" : "bg-white/[0.01]"
                    }`}
                  >
                    <td className="px-5 py-3 font-medium text-slate-200">
                      <div className="flex items-center gap-2">
                        {kpi.kpi_name}
                        {kpi.is_anomaly && (
                          <span title="Anomaly detected">
                            <AlertTriangle
                              size={13}
                              className="text-amber-400"
                            />
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-400">
                      {kpi.business_unit}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs px-2 py-0.5 rounded-full bg-navy-800 border border-dark-border text-slate-400">
                        {kpi.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-slate-200 font-mono text-xs">
                      {kpi.value} {kpi.unit}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-400 font-mono text-xs">
                      {kpi.target} {kpi.unit}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span
                        className={`inline-flex items-center gap-1 font-mono text-xs ${
                          kpi.pct_vs_target >= 0
                            ? "text-emerald-400"
                            : "text-red-400"
                        }`}
                      >
                        {trendIcon(kpi.pct_vs_target)}
                        {kpi.pct_vs_target >= 0 ? "+" : ""}
                        {kpi.pct_vs_target.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`text-[11px] font-medium px-2.5 py-1 rounded-full ${statusClass(
                          kpi.status
                        )}`}
                      >
                        {kpi.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* -- Financial Highlights FY25 -- */}
      {financials.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-base font-semibold text-slate-200 mb-1">
            Financial Highlights FY25
          </h3>
          <p className="text-xs text-slate-500 mb-4">Revenue vs Budget by Business Unit (1H FY25, $M)</p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={financials} margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4d" />
              <XAxis
                dataKey="business_unit"
                stroke="#64748b"
                tick={{ fontSize: 12, fill: "#94a3b8" }}
              />
              <YAxis stroke="#64748b" tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#111827",
                  border: "1px solid #1e2d4d",
                  borderRadius: "8px",
                  fontSize: "13px",
                  color: "#e2e8f0",
                }}
                formatter={(value) => [`$${value}M`, ""]}
                labelStyle={{ color: "#c4962a", fontWeight: 600 }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", color: "#94a3b8" }} />
              <Bar dataKey="actual" name="Actual" radius={[4, 4, 0, 0]}>
                {financials.map((entry) => (
                  <Cell key={entry.business_unit} fill={BU_COLORS[entry.business_unit] || "#64748b"} />
                ))}
              </Bar>
              <Bar dataKey="budget" name="Budget" radius={[4, 4, 0, 0]} fill="#334155" opacity={0.6} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
