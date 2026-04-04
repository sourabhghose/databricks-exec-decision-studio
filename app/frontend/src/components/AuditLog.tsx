import { useState, useEffect } from "react";
import {
  RefreshCw,
  ShieldCheck,
  ShieldAlert,
  Clock,
  Cpu,
} from "lucide-react";

interface AuditEntry {
  timestamp: string;
  user_tier: string;
  agent_name: string;
  query_preview: string;
  confidence: number;
  latency_ms: number;
  compliant: boolean;
}

function agentBadgeColor(agent: string): string {
  const map: Record<string, string> = {
    doc_qa: "bg-blue-500/15 text-blue-400 border-blue-500/20",
    strategic_gap: "bg-purple-500/15 text-purple-400 border-purple-500/20",
    competitive: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    briefing: "bg-gold/15 text-gold border-gold/20",
    kpi_monitor: "bg-cyan-500/15 text-cyan-400 border-cyan-500/20",
  };
  return map[agent] || "bg-slate-500/15 text-slate-400 border-slate-500/20";
}

function agentLabel(agent: string): string {
  return agent
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function AuditLog() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [demo, setDemo] = useState(false);

  const fetchAudit = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/audit");
      const data = await res.json();
      setEntries(data.data || []);
      setDemo(data.demo || false);
    } catch {
      setEntries([]);
      setDemo(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit();
  }, []);

  return (
    <div className="space-y-6">
      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">
            Agent Interaction Audit Trail
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            {demo ? (
              <span className="text-gold/70">Demo data - connect SQL warehouse for live audit log</span>
            ) : (
              <>Live from <code className="text-xs text-slate-400">eds.eds_audit.agent_interactions</code></>
            )}
          </p>
        </div>
        <button
          onClick={fetchAudit}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg glass-card
            text-sm text-slate-300 hover:text-gold hover:border-gold/30
            transition-all disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* ── Table ───────────────────────────────────────────────── */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Tier
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Agent
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Query Preview
                </th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Latency
                </th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Compliant
                </th>
              </tr>
            </thead>
            <tbody>
              {loading && entries.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500">
                    <RefreshCw size={20} className="animate-spin mx-auto mb-2" />
                    Loading audit data...
                  </td>
                </tr>
              ) : entries.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500">
                    No audit entries
                  </td>
                </tr>
              ) : (
                entries.map((entry, i) => (
                  <tr
                    key={i}
                    className={`border-b border-dark-border/50 transition-colors hover:bg-white/[0.02] ${
                      i % 2 === 0 ? "bg-transparent" : "bg-white/[0.01]"
                    }`}
                  >
                    <td className="px-5 py-3 text-slate-400 font-mono text-xs whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <Clock size={12} className="text-slate-500" />
                        {entry.timestamp}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-300 text-xs">
                      {entry.user_tier}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full border ${agentBadgeColor(
                          entry.agent_name
                        )}`}
                      >
                        <Cpu size={10} />
                        {agentLabel(entry.agent_name)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300 text-xs max-w-[300px] truncate">
                      {entry.query_preview}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`font-mono text-xs font-medium ${
                          entry.confidence >= 0.85
                            ? "text-emerald-400"
                            : entry.confidence >= 0.7
                            ? "text-amber-400"
                            : "text-red-400"
                        }`}
                      >
                        {(entry.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-slate-400 font-mono text-xs">
                      {(entry.latency_ms / 1000).toFixed(1)}s
                    </td>
                    <td className="px-4 py-3 text-center">
                      {entry.compliant ? (
                        <ShieldCheck
                          size={16}
                          className="text-emerald-400 mx-auto"
                        />
                      ) : (
                        <ShieldAlert
                          size={16}
                          className="text-red-400 mx-auto"
                        />
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
