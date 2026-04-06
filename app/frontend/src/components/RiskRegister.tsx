import { useState, useEffect } from "react";
import { RefreshCw, ShieldAlert, AlertTriangle, Info, Sparkles } from "lucide-react";

interface Risk {
  risk_id: string;
  category: string;
  description: string;
  likelihood: string;
  consequence: string;
  rating: string;
  risk_score: number;
  owner: string;
  mitigation: string;
  status: string;
}

const LIKELIHOOD_ORDER = ["Almost Certain", "Likely", "Possible", "Unlikely", "Rare"];
const CONSEQUENCE_ORDER = ["Catastrophic", "Major", "Moderate", "Minor", "Insignificant"];

const CATEGORY_COLORS: Record<string, string> = {
  regulatory: "bg-purple-500/15 text-purple-300 border-purple-500/20",
  market: "bg-blue-500/15 text-blue-300 border-blue-500/20",
  operational: "bg-orange-500/15 text-orange-300 border-orange-500/20",
  ESG: "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
  cyber: "bg-red-500/15 text-red-300 border-red-500/20",
  financial: "bg-yellow-500/15 text-yellow-300 border-yellow-500/20",
};

const STATUS_COLORS: Record<string, string> = {
  open: "bg-red-500/10 text-red-400 border-red-500/20",
  in_progress: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  closed: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  accepted: "bg-slate-500/10 text-slate-400 border-slate-500/20",
};

function ratingClass(rating: string) {
  const r = rating.toLowerCase();
  if (r === "critical") return "status-red";
  if (r === "high") return "bg-amber-500/15 text-amber-400 border border-amber-500/20 text-[11px] font-medium px-2.5 py-1 rounded-full";
  if (r === "medium") return "bg-blue-500/15 text-blue-400 border border-blue-500/20 text-[11px] font-medium px-2.5 py-1 rounded-full";
  return "bg-slate-500/15 text-slate-400 border border-slate-500/20 text-[11px] font-medium px-2.5 py-1 rounded-full";
}

// Risk score heat map colours (5x5 matrix)
function matrixColor(row: number, col: number): string {
  const score = (row + 1) * (col + 1); // rough proxy
  if (score >= 15) return "bg-red-600/80 text-white";
  if (score >= 9) return "bg-amber-500/80 text-white";
  if (score >= 4) return "bg-yellow-400/80 text-navy-900";
  return "bg-emerald-500/80 text-navy-900";
}

function RiskMatrix({ risks }: { risks: Risk[] }) {
  return (
    <div className="glass-card p-5">
      <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider">
        Risk Heat Map
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr>
              <th className="text-left text-slate-500 pb-2 pr-3 font-normal">Consequence →</th>
              {CONSEQUENCE_ORDER.map((c) => (
                <th key={c} className="text-center pb-2 px-1 font-medium text-slate-400 w-24">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {LIKELIHOOD_ORDER.map((lik, row) => (
              <tr key={lik}>
                <td className="text-slate-400 pr-3 py-1 font-medium whitespace-nowrap">{lik}</td>
                {CONSEQUENCE_ORDER.map((con, col) => {
                  const cellRisks = risks.filter(
                    (r) => r.likelihood === lik && r.consequence === con
                  );
                  return (
                    <td key={con} className="px-1 py-1">
                      <div
                        className={`rounded-md h-10 flex items-center justify-center cursor-default transition-opacity ${matrixColor(4 - row, 4 - col)} ${cellRisks.length > 0 ? "opacity-100" : "opacity-20"}`}
                        title={cellRisks.map((r) => `${r.risk_id}: ${r.description.slice(0, 60)}...`).join("\n")}
                      >
                        {cellRisks.length > 0 && (
                          <span className="font-bold text-sm">{cellRisks.length}</span>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
        <div className="flex gap-4 mt-3 text-xs text-slate-500">
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-red-600/80 inline-block" /> Critical</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-amber-500/80 inline-block" /> High</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-yellow-400/80 inline-block" /> Medium</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-emerald-500/80 inline-block" /> Low</span>
        </div>
      </div>
    </div>
  );
}

export default function RiskRegister() {
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);
  const [demo, setDemo] = useState(false);
  const [filter, setFilter] = useState<string>("all");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<Record<string, string>>({});
  const [aiLoading, setAiLoading] = useState<Record<string, boolean>>({});

  const fetchRisks = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/risks");
      const data = await res.json();
      setRisks(data.data || []);
      setDemo(data.demo || false);
    } catch {
      setRisks([]);
      setDemo(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRisks(); }, []);

  async function fetchRiskAnalysis(riskId: string) {
    if (aiAnalysis[riskId] || aiLoading[riskId]) return;
    setAiLoading((prev) => ({ ...prev, [riskId]: true }));
    try {
      const r = await fetch(`/api/risks/ai_insights?risk_id=${riskId}`);
      const d = await r.json();
      setAiAnalysis((prev) => ({ ...prev, [riskId]: d.insight || "No analysis available." }));
    } catch {
      setAiAnalysis((prev) => ({ ...prev, [riskId]: "Analysis failed — check connection." }));
    } finally {
      setAiLoading((prev) => ({ ...prev, [riskId]: false }));
    }
  }

  const categories = ["all", ...Array.from(new Set(risks.map((r) => r.category)))];
  const filtered = filter === "all" ? risks : risks.filter((r) => r.category === filter);

  const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
  risks.forEach((r) => { if (r.rating in counts) counts[r.rating as keyof typeof counts]++; });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Enterprise Risk Register</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            {demo ? (
              <span className="text-gold/70">Demo data — connect SQL warehouse for live risk data</span>
            ) : (
              <code className="text-xs text-slate-400">eds.eds_synthetic.risk_register</code>
            )}
          </p>
        </div>
        <button
          onClick={fetchRisks}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg glass-card text-sm text-slate-300 hover:text-gold hover:border-gold/30 transition-all disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Critical", count: counts.Critical, icon: <ShieldAlert size={18} />, color: "from-red-600/20 to-red-700/10", iconColor: "text-red-400" },
          { label: "High", count: counts.High, icon: <AlertTriangle size={18} />, color: "from-amber-500/20 to-amber-600/10", iconColor: "text-amber-400" },
          { label: "Medium", count: counts.Medium, icon: <AlertTriangle size={18} />, color: "from-blue-500/20 to-blue-600/10", iconColor: "text-blue-400" },
          { label: "Low", count: counts.Low, icon: <Info size={18} />, color: "from-emerald-500/20 to-emerald-600/10", iconColor: "text-emerald-400" },
        ].map((card) => (
          <div key={card.label} className={`glass-card p-5 bg-gradient-to-br ${card.color}`}>
            <div className={`mb-2 ${card.iconColor}`}>{card.icon}</div>
            <div className="text-3xl font-bold text-slate-100">{card.count}</div>
            <div className="text-xs text-slate-400 mt-0.5">{card.label} Risks</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-[1fr_340px] gap-5">
        {/* Risk table */}
        <div className="space-y-4">
          {/* Category filter */}
          <div className="flex gap-2 flex-wrap">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer ${
                  filter === cat
                    ? "bg-gold/20 text-gold border border-gold/30"
                    : "bg-dark-card border border-dark-border text-slate-400 hover:text-slate-200"
                }`}
              >
                {cat === "all" ? "All Categories" : cat}
              </button>
            ))}
          </div>

          <div className="glass-card overflow-hidden">
            {loading && risks.length === 0 ? (
              <div className="flex items-center justify-center py-16 text-slate-500">
                <RefreshCw size={20} className="animate-spin mr-3" /> Loading risk register...
              </div>
            ) : (
              <div className="divide-y divide-dark-border/50">
                {filtered.map((risk) => (
                  <div key={risk.risk_id} className="p-4 hover:bg-white/[0.02] transition-colors">
                    <div
                      className="flex items-start gap-3 cursor-pointer"
                      onClick={() => setExpanded(expanded === risk.risk_id ? null : risk.risk_id)}
                    >
                      <div className="flex-shrink-0 mt-0.5">
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded ${ratingClass(risk.rating)}`}>
                          {risk.rating}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-mono text-slate-500">{risk.risk_id}</span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${CATEGORY_COLORS[risk.category] || "bg-slate-500/10 text-slate-400 border-slate-500/20"}`}>
                            {risk.category}
                          </span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${STATUS_COLORS[risk.status] || ""}`}>
                            {risk.status.replace("_", " ")}
                          </span>
                          <span className="ml-auto text-xs font-bold text-slate-300">
                            Score: {risk.risk_score}/25
                          </span>
                        </div>
                        <p className="text-sm text-slate-200 leading-snug">{risk.description}</p>
                        <div className="flex items-center gap-4 mt-1.5 text-xs text-slate-500">
                          <span>Owner: <span className="text-slate-400">{risk.owner}</span></span>
                          <span>Likelihood: <span className="text-slate-400">{risk.likelihood}</span></span>
                          <span>Consequence: <span className="text-slate-400">{risk.consequence}</span></span>
                        </div>
                        {expanded === risk.risk_id && (
                          <div className="mt-3 space-y-2">
                            <div className="p-3 rounded-lg bg-dark-bg border border-dark-border text-xs text-slate-400 leading-relaxed">
                              <span className="text-gold font-medium">Mitigation: </span>{risk.mitigation}
                            </div>
                            {aiAnalysis[risk.risk_id] ? (
                              <div className="p-3 rounded-lg bg-amber-400/5 border border-amber-400/20 text-xs text-slate-300 leading-relaxed">
                                <div className="flex items-center gap-1.5 mb-1.5">
                                  <Sparkles size={11} className="text-amber-400" />
                                  <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">AI Risk Analysis</span>
                                </div>
                                <div className="space-y-1.5">
                                  {aiAnalysis[risk.risk_id]
                                    .split(/\n+/)
                                    .map(s => s.trim())
                                    .filter(Boolean)
                                    .map((line, i) => (
                                      <p key={i} dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g, '<strong class="text-slate-100">$1</strong>') }} />
                                    ))
                                  }
                                </div>
                              </div>
                            ) : (
                              <button
                                onClick={(e) => { e.stopPropagation(); fetchRiskAnalysis(risk.risk_id); }}
                                disabled={aiLoading[risk.risk_id]}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] border border-amber-400/20 text-amber-400 hover:bg-amber-400/10 transition-colors cursor-pointer disabled:opacity-50"
                              >
                                {aiLoading[risk.risk_id] ? <RefreshCw size={11} className="animate-spin" /> : <Sparkles size={11} />}
                                {aiLoading[risk.risk_id] ? "Analysing…" : "Get AI Analysis"}
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Heat map */}
        <div>
          <RiskMatrix risks={risks} />
        </div>
      </div>
    </div>
  );
}
