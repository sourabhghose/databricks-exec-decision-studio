import { useState, useEffect } from "react";
import {
  RefreshCw,
  User,
  Calendar,
  FileText,
  AlertCircle,
} from "lucide-react";

interface Action {
  action_id: string;
  title: string;
  owner: string;
  due_date: string;
  priority: "Critical" | "High" | "Medium" | "Low";
  status: "Open" | "In Progress" | "Completed";
  business_unit: string;
  source_doc_id: string;
}

const PRIORITY_STYLES: Record<string, string> = {
  Critical: "bg-red-500/15 text-red-400 border-red-500/30",
  High: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  Medium: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  Low: "bg-slate-500/15 text-slate-400 border-slate-500/30",
};

const BU_STYLES: Record<string, string> = {
  Generation: "bg-gold/10 text-gold border-gold/20",
  Retail: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  Trading: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  Group: "bg-slate-500/10 text-slate-300 border-slate-500/20",
};

const COLUMN_HEADERS: Record<string, { label: string; color: string }> = {
  Open: { label: "Open", color: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
  "In Progress": { label: "In Progress", color: "bg-blue-500/20 text-blue-400 border-blue-500/30" },
  Completed: { label: "Completed", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
};

function dueDateClass(dateStr: string): string {
  const due = new Date(dateStr);
  const now = new Date();
  const diffDays = (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);

  if (diffDays < 0) return "text-red-400";
  if (diffDays <= 7) return "text-amber-400";
  return "text-slate-400";
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-AU", { day: "numeric", month: "short", year: "numeric" });
}

export default function ActionItems() {
  const [actions, setActions] = useState<Action[]>([]);
  const [loading, setLoading] = useState(true);
  const [demo, setDemo] = useState(false);

  const fetchActions = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/actions");
      const data = await res.json();
      setActions(data.data || []);
      setDemo(data.demo || false);
    } catch {
      setActions([]);
      setDemo(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
  }, []);

  const columns: ("Open" | "In Progress" | "Completed")[] = ["Open", "In Progress", "Completed"];

  const grouped = {
    Open: actions.filter((a) => a.status === "Open"),
    "In Progress": actions.filter((a) => a.status === "In Progress"),
    Completed: actions.filter((a) => a.status === "Completed"),
  };

  return (
    <div className="space-y-6">
      {/* -- Header -- */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">
            Board Action Tracker
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            {demo ? (
              <span className="text-gold/70">Demo data - connect SQL warehouse for live actions</span>
            ) : (
              <>
                Live from{" "}
                <code className="text-xs text-slate-400">
                  eds.eds_actions.action_items
                </code>
              </>
            )}
          </p>
        </div>
        <button
          onClick={fetchActions}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg glass-card
            text-sm text-slate-300 hover:text-gold hover:border-gold/30
            transition-all disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* -- Kanban Board -- */}
      {loading && actions.length === 0 ? (
        <div className="flex items-center justify-center py-20">
          <RefreshCw size={24} className="animate-spin text-gold mr-3" />
          <span className="text-slate-400">Loading action items...</span>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-5">
          {columns.map((col) => (
            <div key={col} className="flex flex-col">
              {/* Column header */}
              <div className="flex items-center gap-2 mb-3">
                <span
                  className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${COLUMN_HEADERS[col].color}`}
                >
                  {COLUMN_HEADERS[col].label}
                </span>
                <span className="text-xs text-slate-500">
                  ({grouped[col].length})
                </span>
              </div>

              {/* Cards */}
              <div className="flex flex-col gap-3 flex-1">
                {grouped[col].length === 0 ? (
                  <div className="glass-card p-6 text-center text-sm text-slate-600">
                    No items
                  </div>
                ) : (
                  grouped[col].map((action) => (
                    <div
                      key={action.action_id}
                      className="glass-card p-4 hover:border-gold/20 transition-colors"
                    >
                      {/* Priority + ID */}
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${
                            PRIORITY_STYLES[action.priority] || PRIORITY_STYLES.Medium
                          }`}
                        >
                          {action.priority}
                        </span>
                        <span className="text-[11px] text-slate-600 font-mono">
                          {action.action_id}
                        </span>
                      </div>

                      {/* Title */}
                      <h4 className="text-sm font-semibold text-slate-200 leading-snug line-clamp-2 mb-3">
                        {action.title}
                      </h4>

                      {/* Owner */}
                      <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1.5">
                        <User size={12} />
                        <span>{action.owner}</span>
                      </div>

                      {/* Due date */}
                      <div className={`flex items-center gap-1.5 text-xs mb-3 ${dueDateClass(action.due_date)}`}>
                        <Calendar size={12} />
                        <span>{formatDate(action.due_date)}</span>
                        {new Date(action.due_date) < new Date() && action.status !== "Completed" && (
                          <AlertCircle size={12} className="text-red-400" />
                        )}
                      </div>

                      {/* Bottom row: BU badge + Source doc */}
                      <div className="flex items-center gap-2 flex-wrap">
                        <span
                          className={`text-[11px] px-2 py-0.5 rounded-full border ${
                            BU_STYLES[action.business_unit] || BU_STYLES.Group
                          }`}
                        >
                          {action.business_unit}
                        </span>
                        {action.source_doc_id && (
                          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-navy-800 border border-dark-border text-slate-400">
                            <FileText size={10} />
                            {action.source_doc_id}
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
