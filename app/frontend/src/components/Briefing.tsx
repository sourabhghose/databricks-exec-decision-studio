import { useState } from "react";
import {
  Zap,
  FileText,
  BarChart3,
  Shield,
  Gavel,
  RefreshCw,
  Download,
  Clock,
  Sparkles,
  Bot,
} from "lucide-react";

const ROLES = [
  "Board Director / CEO",
  "CFO / C-Suite",
  "Executive Leadership Team",
  "Senior Management",
  "All Staff",
];

const BRIEFING_TYPES = [
  { id: "weekly", label: "Weekly Management Briefing", icon: <BarChart3 size={14} />, desc: "Concise weekly summary for leadership" },
  { id: "board", label: "Board Meeting Pre-Read", icon: <Gavel size={14} />, desc: "Structured Board paper format" },
  { id: "investor", label: "Investor Relations Briefing", icon: <FileText size={14} />, desc: "Investor-ready narrative & metrics" },
  { id: "crisis", label: "Crisis / Issues Brief", icon: <Shield size={14} />, desc: "Issues management & response" },
];

const FOCUS_AREAS = [
  { id: "kpis", label: "KPI Performance", icon: <BarChart3 size={13} />, desc: "Latest KPI scorecard" },
  { id: "risks", label: "Enterprise Risks", icon: <Shield size={13} />, desc: "Top risks & mitigations" },
  { id: "decisions", label: "Recent Decisions", icon: <Gavel size={13} />, desc: "Board & ELT decisions" },
  { id: "strategy", label: "Strategic Context", icon: <Zap size={13} />, desc: "Strategic priorities & outlook" },
];

function renderMarkdown(text: string): string {
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Process markdown tables before block/inline replacements
  html = html.replace(/((?:^\|[^\n]+\|\n?)+)/gm, (tableBlock) => {
    const rows = tableBlock.trim().split("\n").filter((r) => r.trim());
    const isSeparator = (row: string) => /^\|[\s\-|:]+\|$/.test(row.trim());
    const parseRow = (row: string) =>
      row.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());

    const dataRows = rows.filter((r) => !isSeparator(r));
    if (dataRows.length < 1) return tableBlock;

    const [headerRow, ...bodyRows] = dataRows;
    const headers = parseRow(headerRow);

    const headerCells = headers
      .map(
        (h) =>
          `<th class="text-xs font-semibold text-slate-200 px-3 py-2 text-left border-b border-slate-700 whitespace-nowrap">${h}</th>`
      )
      .join("");

    const bodyHTML = bodyRows
      .map((row, i) => {
        const cells = parseRow(row);
        const bg = i % 2 === 0 ? "" : ' class="bg-slate-800/30"';
        const tds = cells
          .map(
            (c) =>
              `<td class="text-xs text-slate-300 px-3 py-1.5 border-b border-slate-700/40">${c}</td>`
          )
          .join("");
        return `<tr${bg}>${tds}</tr>`;
      })
      .join("");

    return (
      `<div class="overflow-x-auto my-4 rounded-lg border border-slate-700">` +
      `<table class="w-full border-collapse text-sm">` +
      `<thead><tr class="bg-slate-800/60">${headerCells}</tr></thead>` +
      `<tbody>${bodyHTML}</tbody>` +
      `</table></div>`
    );
  });

  html = html.replace(/^### (.+)$/gm, '<h3 class="text-sm font-semibold text-slate-200 mt-4 mb-1.5">$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2 class="text-base font-bold text-gold mt-5 mb-2 pb-1 border-b border-dark-border">$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1 class="text-lg font-bold text-slate-100 mb-3">$1</h1>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="text-slate-100 font-semibold">$1</strong>');
  html = html.replace(/`([^`]+)`/g, '<code class="text-xs bg-dark-bg px-1.5 py-0.5 rounded text-gold font-mono">$1</code>');
  html = html.replace(/^[-*] (.+)$/gm, '<li class="text-slate-300 text-sm leading-relaxed ml-4 list-disc">$1</li>');
  html = html.replace(/((?:<li[^>]*>.*<\/li>\n?)+)/g, '<ul class="my-2 space-y-0.5">$1</ul>');
  html = html.replace(/^\d+\. (.+)$/gm, '<li class="text-slate-300 text-sm leading-relaxed ml-4 list-decimal">$1</li>');
  html = html.replace(/\n\n/g, '</p><p class="text-slate-300 text-sm leading-relaxed my-2">');
  html = '<p class="text-slate-300 text-sm leading-relaxed my-2">' + html + "</p>";
  html = html.replace(/\n/g, "<br/>");
  html = html.replace(/<p[^>]*><\/p>/g, "");
  html = html.replace(/<p[^>]*><br\/>/g, (m) => m.replace(/<br\/>/, ""));

  // Highlight ✅ ⚠️ 🔴 markers
  html = html.replace(/✅/g, '<span class="text-green-400">✅</span>');
  html = html.replace(/⚠️/g, '<span class="text-amber-400">⚠️</span>');
  html = html.replace(/🔴/g, '<span class="text-red-400">🔴</span>');

  return html;
}

export default function Briefing() {
  const [role, setRole] = useState(ROLES[0]);
  const [briefingType, setBriefingType] = useState("weekly");
  const [focusAreas, setFocusAreas] = useState(["kpis", "risks", "decisions"]);
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState("");
  const [latency, setLatency] = useState(0);
  const [generated, setGenerated] = useState(false);
  const [reportingPeriod, setReportingPeriod] = useState("");

  const toggleFocus = (id: string) => {
    setFocusAreas((prev) =>
      prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]
    );
  };

  const generate = async () => {
    if (loading || focusAreas.length === 0) return;
    setLoading(true);
    setContent("");
    setGenerated(false);
    setReportingPeriod("");

    try {
      const res = await fetch("/api/briefing/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role, briefing_type: briefingType, focus_areas: focusAreas }),
      });

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "meta") {
                if (data.reporting_period) setReportingPeriod(data.reporting_period);
              } else if (data.type === "token") {
                setContent((prev) => prev + data.content);
              } else if (data.type === "done") {
                setLatency(data.latency_ms || 0);
                setGenerated(true);
              }
            } catch {
              // ignore
            }
          }
        }
      }
    } catch (err) {
      setContent(`Error generating briefing: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setLoading(false);
      setGenerated(true);
    }
  };

  const typeLabel = BRIEFING_TYPES.find((t) => t.id === briefingType)?.label || "Briefing";
  const dateSlug = new Date().toISOString().slice(0, 10);

  const handleDownloadMd = () => {
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Alinta_Energy_${typeLabel.replace(/\s+/g, "_")}_${dateSlug}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = () => {
    const dateStr = new Date().toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" });
    const periodStr = reportingPeriod ? ` · Reporting Period: ${reportingPeriod}` : "";
    const win = window.open("", "_blank", "width=900,height=700");
    if (!win) return;
    win.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>${typeLabel}</title><style>
      @page{margin:20mm}body{font-family:Arial,sans-serif;font-size:12pt;color:#1e293b;line-height:1.6}
      .header{border-bottom:3px solid #F47920;padding-bottom:12px;margin-bottom:20px}
      .brand{color:#F47920;font-size:11pt;font-weight:700;letter-spacing:.05em}
      .meta{font-size:10pt;color:#64748b;margin-top:4px}
      h1,h2,h3{color:#F47920}h2{font-size:14pt;margin-top:20pt}h3{font-size:12pt}
      p{margin:8pt 0}strong{color:#0f172a}
      code{background:#f1f5f9;padding:1px 4px;border-radius:3px;font-family:monospace;font-size:10pt}
      table{width:100%;border-collapse:collapse;font-size:11pt;margin:12pt 0}
      th{background:#fff3e8;color:#c4611a;border:1px solid #e2e8f0;padding:8px 10px;text-align:left;font-weight:600}
      td{border:1px solid #e2e8f0;padding:7px 10px}
      tr:nth-child(even) td{background:#f8fafc}
      ul{padding-left:18px;margin:8pt 0}li{margin:3pt 0}
    </style></head><body>
      <div class="header">
        <div class="brand">ALINTA ENERGY · EXECUTIVE DECISION STUDIO</div>
        <div class="meta">${typeLabel} · Prepared for: ${role}${periodStr} · ${dateStr}</div>
      </div>
      <div class="content">${renderMarkdown(content)}</div>
      <script>window.onload=function(){window.print();setTimeout(()=>window.close(),1500)}<\/script>
    </body></html>`);
    win.document.close();
  };

  const handleDownloadPPTX = async () => {
    const res = await fetch("/api/export/pptx", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content,
        agent: typeLabel,
        sources: [],
        title: `${typeLabel} — ${role}`,
      }),
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Alinta_Energy_${typeLabel.replace(/\s+/g, "_")}_${dateSlug}.pptx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex gap-5 h-[calc(100vh-160px)]">
      {/* Sidebar */}
      <div className="w-72 flex-shrink-0 flex flex-col gap-4 overflow-visible">

        {/* Role selector */}
        <div className="glass-card p-4">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
            Recipient Role
          </label>
          <div className="flex flex-col gap-1.5">
            {ROLES.map((r) => (
              <button
                key={r}
                onClick={() => setRole(r)}
                className={`text-left px-3 py-2 rounded-lg border text-xs transition-all cursor-pointer
                  ${role === r
                    ? "bg-gold/10 border-gold/30 text-gold font-medium"
                    : "border-dark-border text-slate-400 hover:text-slate-200 hover:border-slate-600"
                  }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        {/* Briefing type */}
        <div className="glass-card p-4">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
            Briefing Type
          </label>
          <div className="flex flex-col gap-2">
            {BRIEFING_TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setBriefingType(t.id)}
                className={`text-left px-3 py-2.5 rounded-lg border transition-all cursor-pointer
                  ${briefingType === t.id
                    ? "bg-gold/10 border-gold/30 text-gold"
                    : "border-dark-border text-slate-400 hover:text-slate-200 hover:border-slate-600"
                  }`}
              >
                <div className="flex items-center gap-2 mb-0.5">
                  {t.icon}
                  <span className="text-xs font-medium">{t.label}</span>
                </div>
                <p className="text-[11px] text-slate-500 ml-5">{t.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Focus areas */}
        <div className="glass-card p-4">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
            Include Sections
          </label>
          <div className="flex flex-col gap-2">
            {FOCUS_AREAS.map((f) => {
              const active = focusAreas.includes(f.id);
              return (
                <button
                  key={f.id}
                  onClick={() => toggleFocus(f.id)}
                  className={`text-left px-3 py-2 rounded-lg border transition-all cursor-pointer flex items-center gap-2
                    ${active
                      ? "bg-gold/10 border-gold/30 text-gold"
                      : "border-dark-border text-slate-400 hover:text-slate-200 hover:border-slate-600"
                    }`}
                >
                  <div className={`w-4 h-4 rounded flex items-center justify-center flex-shrink-0 border ${active ? "bg-gold border-gold" : "border-slate-600"}`}>
                    {active && <span className="text-navy-900 text-[9px] font-bold">✓</span>}
                  </div>
                  {f.icon}
                  <div>
                    <p className="text-xs font-medium">{f.label}</p>
                    <p className="text-[10px] text-slate-500">{f.desc}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Generate button */}
        <button
          onClick={generate}
          disabled={loading || focusAreas.length === 0}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-gold-dark to-gold
            text-navy-900 font-bold text-sm flex items-center justify-center gap-2
            hover:shadow-lg hover:shadow-gold/20 disabled:opacity-40 disabled:cursor-not-allowed
            transition-all duration-200 cursor-pointer"
        >
          {loading ? (
            <><RefreshCw size={15} className="animate-spin" /> Generating...</>
          ) : (
            <><Sparkles size={15} /> Generate Briefing</>
          )}
        </button>
      </div>

      {/* Briefing output */}
      <div className="flex-1 flex flex-col glass-card overflow-hidden">
        {/* Toolbar */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-dark-border">
          <div className="flex items-center gap-2">
            <Bot size={16} className="text-gold" />
            <span className="text-sm font-medium text-slate-300">
              {BRIEFING_TYPES.find((t) => t.id === briefingType)?.label}
            </span>
            {generated && latency > 0 && (
              <span className="flex items-center gap-1 text-[11px] text-slate-500 ml-2">
                <Clock size={11} />
                {(latency / 1000).toFixed(1)}s
              </span>
            )}
          </div>
          {generated && content && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleDownloadPDF}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400
                  border border-dark-border hover:text-gold hover:border-gold/30 transition-colors cursor-pointer"
                title="Export as PDF (print dialog)"
              >
                <Download size={12} />
                PDF
              </button>
              <button
                onClick={handleDownloadPPTX}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400
                  border border-dark-border hover:text-gold hover:border-gold/30 transition-colors cursor-pointer"
                title="Export as PowerPoint"
              >
                <Download size={12} />
                PPTX
              </button>
              <button
                onClick={handleDownloadMd}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400
                  border border-dark-border hover:text-gold hover:border-gold/30 transition-colors cursor-pointer"
                title="Export as Markdown"
              >
                <Download size={12} />
                MD
              </button>
            </div>
          )}
        </div>

        {/* Content area */}
        <div className="flex-1 overflow-y-auto p-6">
          {!content && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center opacity-60">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-navy-800 to-navy-900 flex items-center justify-center mb-4 border border-dark-border">
                <Sparkles size={28} className="text-gold" />
              </div>
              <h3 className="text-lg font-semibold text-slate-300 mb-1">
                AI Executive Briefing
              </h3>
              <p className="text-sm text-slate-500 max-w-md leading-relaxed">
                Configure the briefing type and select focus areas, then click{" "}
                <span className="text-gold">Generate Briefing</span> to produce a
                structured executive briefing powered by Databricks Mosaic AI.
              </p>
              <div className="mt-4 flex flex-wrap gap-2 justify-center">
                {["KPI Scorecard", "Risk Heatmap", "Decision Log", "Strategic Context"].map((label) => (
                  <span key={label} className="text-xs px-2.5 py-1 rounded-full bg-dark-bg border border-dark-border text-slate-500">
                    {label}
                  </span>
                ))}
              </div>
            </div>
          )}

          {(content || loading) && (
            <div className="max-w-2xl mx-auto">
              {/* Briefing header */}
              <div className="mb-6 pb-4 border-b border-dark-border">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-gold/15 text-gold border border-gold/20 uppercase tracking-wider">
                    Alinta Energy
                  </span>
                  <span className="text-[11px] text-slate-500">·</span>
                  <span className="text-[11px] text-slate-500">
                    {BRIEFING_TYPES.find((t) => t.id === briefingType)?.label}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-slate-500">
                    Prepared for: <span className="text-slate-300">{role}</span>
                  </p>
                  <p className="text-xs text-slate-500">
                    {reportingPeriod
                      ? `Reporting Period: ${reportingPeriod}`
                      : new Date().toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" })}
                  </p>
                </div>
              </div>

              {/* Rendered markdown */}
              <div
                className="briefing-content"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
              />

              {/* Streaming indicator */}
              {loading && (
                <div className="flex gap-1.5 mt-3">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              )}

              {/* Export buttons — visible at bottom after generation */}
              {generated && !loading && content && (
                <div className="mt-8 pt-4 border-t border-dark-border/50 flex items-center gap-2">
                  <span className="text-xs text-slate-600 mr-2">Export as:</span>
                  <button
                    onClick={handleDownloadPDF}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400
                      border border-dark-border hover:text-gold hover:border-gold/30 transition-colors cursor-pointer"
                  >
                    <Download size={12} />
                    PDF
                  </button>
                  <button
                    onClick={handleDownloadPPTX}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400
                      border border-dark-border hover:text-gold hover:border-gold/30 transition-colors cursor-pointer"
                  >
                    <Download size={12} />
                    PPTX
                  </button>
                  <button
                    onClick={handleDownloadMd}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400
                      border border-dark-border hover:text-gold hover:border-gold/30 transition-colors cursor-pointer"
                  >
                    <Download size={12} />
                    Markdown
                  </button>
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
