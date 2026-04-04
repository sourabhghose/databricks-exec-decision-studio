import { useState, useEffect } from "react";
import { RefreshCw, Gavel, CheckCircle, Clock, XCircle, ArrowRight } from "lucide-react";

interface Decision {
  decision_id: string;
  decision_date: string;
  committee: string;
  description: string;
  decision_type: string;
  outcome: string;
  owner: string;
  implementation_status: string;
}

const COMMITTEE_COLORS: Record<string, string> = {
  Board: "bg-gold/15 text-gold border-gold/25",
  ELT: "bg-blue-500/15 text-blue-300 border-blue-500/25",
  IC: "bg-purple-500/15 text-purple-300 border-purple-500/25",
  RC: "bg-red-500/15 text-red-300 border-red-500/25",
};

const TYPE_COLORS: Record<string, string> = {
  strategic: "bg-indigo-500/15 text-indigo-300 border-indigo-500/20",
  financial: "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
  operational: "bg-orange-500/15 text-orange-300 border-orange-500/20",
  risk: "bg-red-500/15 text-red-300 border-red-500/20",
  governance: "bg-slate-500/15 text-slate-300 border-slate-500/20",
};

const STATUS_CONFIG: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  complete: { icon: <CheckCircle size={14} />, color: "text-emerald-400", label: "Complete" },
  in_progress: { icon: <Clock size={14} />, color: "text-amber-400", label: "In Progress" },
  pending: { icon: <ArrowRight size={14} />, color: "text-blue-400", label: "Pending" },
  deferred: { icon: <XCircle size={14} />, color: "text-slate-400", label: "Deferred" },
};

export default function DecisionRegister() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [demo, setDemo] = useState(false);
  const [filter, setFilter] = useState<string>("all");

  const fetchDecisions = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/decisions");
      const data = await res.json();
      setDecisions(data.data || []);
      setDemo(data.demo || false);
    } catch {
      setDecisions([]);
      setDemo(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDecisions(); }, []);

  const committees = ["all", ...Array.from(new Set(decisions.map((d) => d.committee)))];
  const filtered = filter === "all" ? decisions : decisions.filter((d) => d.committee === filter);

  const counts = {
    Board: decisions.filter((d) => d.committee === "Board").length,
    ELT: decisions.filter((d) => d.committee === "ELT").length,
    complete: decisions.filter((d) => d.implementation_status === "complete").length,
    in_progress: decisions.filter((d) => d.implementation_status === "in_progress").length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Board Decision Register</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            {demo ? (
              <span className="text-gold/70">Demo data — connect SQL warehouse for live decisions</span>
            ) : (
              <code className="text-xs text-slate-400">eds.eds_actions.decision_register</code>
            )}
          </p>
        </div>
        <button
          onClick={fetchDecisions}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg glass-card text-sm text-slate-300 hover:text-gold hover:border-gold/30 transition-all disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Board Decisions", value: counts.Board, color: "from-gold/20 to-gold-dark/10", icon: <Gavel size={18} className="text-gold" /> },
          { label: "ELT Decisions", value: counts.ELT, color: "from-blue-500/20 to-blue-600/10", icon: <Gavel size={18} className="text-blue-400" /> },
          { label: "Implemented", value: counts.complete, color: "from-emerald-500/20 to-emerald-600/10", icon: <CheckCircle size={18} className="text-emerald-400" /> },
          { label: "In Progress", value: counts.in_progress, color: "from-amber-500/20 to-amber-600/10", icon: <Clock size={18} className="text-amber-400" /> },
        ].map((card) => (
          <div key={card.label} className={`glass-card p-5 bg-gradient-to-br ${card.color}`}>
            <div className="mb-2">{card.icon}</div>
            <div className="text-3xl font-bold text-slate-100">{card.value}</div>
            <div className="text-xs text-slate-400 mt-0.5">{card.label}</div>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {committees.map((c) => (
          <button
            key={c}
            onClick={() => setFilter(c)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer ${
              filter === c
                ? "bg-gold/20 text-gold border border-gold/30"
                : "bg-dark-card border border-dark-border text-slate-400 hover:text-slate-200"
            }`}
          >
            {c === "all" ? "All Committees" : c}
          </button>
        ))}
      </div>

      {/* Decision list */}
      <div className="glass-card overflow-hidden">
        {loading && decisions.length === 0 ? (
          <div className="flex items-center justify-center py-16 text-slate-500">
            <RefreshCw size={20} className="animate-spin mr-3" /> Loading decisions...
          </div>
        ) : (
          <div className="divide-y divide-dark-border/50">
            {filtered.map((dec) => {
              const statusCfg = STATUS_CONFIG[dec.implementation_status] || STATUS_CONFIG.pending;
              return (
                <div key={dec.decision_id} className="p-5 hover:bg-white/[0.02] transition-colors">
                  <div className="flex items-start gap-4">
                    {/* Date column */}
                    <div className="flex-shrink-0 text-center w-14">
                      <div className="text-gold font-bold text-sm">
                        {dec.decision_date?.slice(0, 7)}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <span className="text-xs font-mono text-slate-500">{dec.decision_id}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${COMMITTEE_COLORS[dec.committee] || ""}`}>
                          {dec.committee}
                        </span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full border ${TYPE_COLORS[dec.decision_type] || ""}`}>
                          {dec.decision_type}
                        </span>
                        <span className={`ml-auto flex items-center gap-1 text-xs ${statusCfg.color}`}>
                          {statusCfg.icon}
                          {statusCfg.label}
                        </span>
                      </div>

                      <p className="text-sm text-slate-200 leading-relaxed mb-2">
                        {dec.description}
                      </p>

                      <div className="p-3 rounded-lg bg-dark-bg border border-dark-border text-xs text-slate-400">
                        <span className="text-gold font-medium">Resolution: </span>
                        {dec.outcome}
                      </div>

                      <div className="mt-2 text-xs text-slate-500">
                        Owner: <span className="text-slate-400">{dec.owner}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
