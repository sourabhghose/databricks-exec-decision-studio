import { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  FileText,
  Clock,
  Cpu,
  Gauge,
  ThumbsUp,
  FileDown,
  Presentation,
} from "lucide-react";
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine,
} from "recharts";

interface ChartSeries {
  key: string;
  label: string;
  color: string;
}

interface ChartData {
  chart_type: string;
  title: string;
  data: Record<string, unknown>[];
  x_key: string;
  series: ChartSeries[];
  reference_lines?: { y: number; label: string; color: string }[];
}

interface Message {
  role: "user" | "assistant";
  content: string;
  agent?: string;
  confidence?: number;
  sources?: string[];
  latency_ms?: number;
  chartData?: ChartData;
  liked?: boolean;
}

const ROLE = "Board Director / CEO";

const SAMPLE_QUESTIONS: { category: string; color: string; questions: { label: string; query: string }[] }[] = [
  {
    category: "Strategy",
    color: "#F47920",
    questions: [
      { label: "Loy Yang B timeline & options", query: "What are the strategic options and final decision timeline for the Loy Yang B transition? What does the Board need to decide and by when?" },
      { label: "FY26 strategic priorities", query: "What are the top 3 strategic priorities for the Board to focus on in FY2026 and what key decisions are required?" },
      { label: "Strategy vs AEMO ISP gaps", query: "Where are the biggest gaps between Alinta's current strategy and AEMO's Integrated System Plan projections?" },
      { label: "Yandin Stage 2 status", query: "What is the current status, key milestones, and risk profile of the Yandin Stage 2 wind farm investment?" },
      { label: "Renewables pipeline overview", query: "What is Alinta's total committed renewables pipeline, capex schedule, and expected generation output by FY28?" },
      { label: "Battery storage strategy", query: "What is Alinta's battery storage strategy and how does it compare to the commitments made by Origin and AGL?" },
    ],
  },
  {
    category: "Financial Performance",
    color: "#3b82f6",
    questions: [
      { label: "1H FY25 results summary", query: "Summarise the key financial results for 1H FY25. Where did we beat or miss budget and what are the key drivers?" },
      { label: "EBITDA variance drivers", query: "What are the primary drivers of EBITDA variance from budget across Generation, Retail, and Trading in 1H FY25?" },
      { label: "Balance sheet & debt headroom", query: "What is our current Net Debt/EBITDA ratio, covenant headroom, and when is the $800M debt refinancing due?" },
      { label: "FY26 budget assumptions", query: "What are the key assumptions underpinning the FY26 budget and where are the main upside/downside sensitivities?" },
      { label: "Capital allocation priorities", query: "How is capital being allocated across Yandin Stage 2, LYB life extension, Retail Transformation, and dividends in FY26?" },
      { label: "Dividend sustainability", query: "Is the 60% dividend payout ratio sustainable given our capex commitments and debt refinancing schedule?" },
    ],
  },
  {
    category: "Risk & Governance",
    color: "#ef4444",
    questions: [
      { label: "Top enterprise risks", query: "What are the top enterprise risks this quarter, their ratings, and what mitigations are in place for each?" },
      { label: "Carbon liability exposure", query: "What is Alinta's total Scope 1 carbon liability at current ACCU prices and how does this change under forward price trajectories to 2035?" },
      { label: "WEM regulatory risk", query: "What is the financial impact of WEM capacity mechanism uncertainty on Alinta's generation revenue and how are we positioned?" },
      { label: "Cyber & OT security posture", query: "How prepared are we for an OT/SCADA cyber attack on Loy Yang B or Yandin? What is the status of the cybersecurity uplift program?" },
      { label: "LYB unplanned outage risk", query: "What is the probability and financial impact of an unplanned extended outage at Loy Yang B, and what contingency plans exist?" },
      { label: "Risks to FY26 budget", query: "What are the key risks that could prevent us achieving the FY26 EBITDA target of $290M and how are they being managed?" },
    ],
  },
  {
    category: "Competitive Intelligence",
    color: "#8b5cf6",
    questions: [
      { label: "NPS gap vs competitors", query: "What is Alinta's NPS gap versus Energy Australia and ERM Power, what is driving it, and what is the plan to close it within 18 months?" },
      { label: "National market share trend", query: "How is Alinta's national retail market share trending and what is driving the movement in customer acquisition and churn?" },
      { label: "AGL & Origin strategic moves", query: "What are AGL Energy and Origin Energy's key strategic moves in the last quarter and how should Alinta respond?" },
      { label: "Digital disruptor threat", query: "How significant is the threat from digital-native retailers like Amber Electric? What customer segments are most at risk?" },
      { label: "WA vs Eastern seaboard position", query: "How does Alinta's competitive position in WA compare to our Eastern seaboard penetration strategy and where should we prioritise?" },
      { label: "ASX peer comparison", query: "How does Alinta compare to Origin Energy and AGL on key financial and operational metrics? Where are we ahead and where are we behind?" },
    ],
  },
  {
    category: "ESG & Carbon",
    color: "#22c55e",
    questions: [
      { label: "Net Zero pathway status", query: "What is Alinta's current progress against the Net Zero by 2045 pathway? Are we on track and what are the critical decision points?" },
      { label: "Scope 1 intensity trajectory", query: "What is our current Scope 1 emissions intensity and what is the projected trajectory under each LYB retirement scenario?" },
      { label: "LGC revenue from Yandin 2", query: "How much LGC revenue will Yandin Stage 2 generate once commissioned and how does this improve our renewable certificate position?" },
      { label: "ESG ratings vs peers", query: "How does Alinta's ESG rating compare to Origin and AGL? What are the key areas where we need to improve our disclosure?" },
      { label: "Climate scenario analysis", query: "What does the climate scenario analysis show for Alinta's generation portfolio under 1.5°C and 2°C pathways?" },
    ],
  },
  {
    category: "Operations & People",
    color: "#f59e0b",
    questions: [
      { label: "LYB plant availability & risks", query: "How is Loy Yang B plant availability tracking against target and are there any near-term unplanned outage risks from the aging fleet?" },
      { label: "Retail churn & NPS recovery", query: "What is the current retail churn rate, what interventions are underway, and when do we expect to see NPS improvement?" },
      { label: "Retail Transformation milestones", query: "What are the key milestones for the $45M Retail Transformation Program and are we on track to deliver the NPS improvement by FY27?" },
      { label: "Safety performance", query: "How is our TRIFR safety metric performing, what is driving the improvement, and are there any serious injury or fatality risks?" },
      { label: "Executive talent & succession", query: "What are the key talent risks in the executive leadership team and what succession plans are in place for critical roles?" },
    ],
  },
];

const DOC_TITLES: Record<string, string> = {
  "DOC-001": "FY2025 Group Strategy Review",
  "DOC-002": "Loy Yang B Transition Options",
  "DOC-003": "1H FY25 Financial Results",
  "DOC-004": "Competitive Intelligence Report",
  "DOC-005": "ESG & Climate Risk Report",
  "DOC-006": "Yandin Stage 2 Investment Case",
  "DOC-007": "Enterprise Risk Management",
  "DOC-008": "WEM Capacity Mechanism Submission",
  "DOC-009": "FY2026 Budget Paper",
  "DOC-010": "Cybersecurity & OT Security Update",
  "DOC-011": "Retail Transformation Q2 FY25",
  "DOC-012": "People & Culture Strategy",
  "DOC-013": "Trading & Hedging Strategy",
  "DOC-014": "Board Skills & Governance",
  "DOC-015": "Capital Allocation Framework",
};

const CHART_COLORS = {
  green: "#22c55e",
  yellow: "#f59e0b",
  red: "#ef4444",
};

function InlineChart({ chart }: { chart: ChartData }) {
  const isLine = chart.chart_type === "line";

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: {name: string; value: number; color: string}[]; label?: string }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-navy-900 border border-dark-border rounded-lg px-3 py-2 text-xs shadow-xl">
        <p className="text-slate-300 font-medium mb-1">{label}</p>
        {payload.map((p) => (
          <div key={p.name} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: p.color }} />
            <span className="text-slate-400">{p.name}:</span>
            <span className="text-slate-100 font-medium">{typeof p.value === "number" ? p.value.toFixed(1) : p.value}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="mt-4 pt-3 border-t border-dark-border/50">
      <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-3">{chart.title}</p>
      <ResponsiveContainer width="100%" height={220}>
        {isLine ? (
          <LineChart data={chart.data} margin={{ top: 4, right: 8, left: -20, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey={chart.x_key} tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: "10px", color: "#94a3b8" }} />
            {chart.series.map((s) => (
              <Line key={s.key} type="monotone" dataKey={s.key} name={s.label}
                stroke={s.color} strokeWidth={2} dot={{ r: 3, fill: s.color }}
                activeDot={{ r: 4 }} />
            ))}
          </LineChart>
        ) : (
          <BarChart data={chart.data} margin={{ top: 4, right: 8, left: -20, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey={chart.x_key} tick={{ fill: "#64748b", fontSize: 9 }} axisLine={false} tickLine={false} angle={-20} textAnchor="end" height={40} />
            <YAxis tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: "10px", color: "#94a3b8" }} />
            {chart.series.map((s) => (
              <Bar key={s.key} dataKey={s.key} name={s.label} fill={s.color} radius={[3, 3, 0, 0]} maxBarSize={32} />
            ))}
            {chart.reference_lines?.map((rl) => (
              <ReferenceLine key={rl.label} y={rl.y} stroke={rl.color}
                strokeDasharray="4 2" label={{ value: rl.label, fill: rl.color, fontSize: 9 }} />
            ))}
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

function agentLabel(agent: string): string {
  return agent
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function buildHtmlTable(lines: string[]): string {
  const isSepRow = (l: string): boolean => {
    const inner = l.trim().replace(/^\|/, "").replace(/\|$/, "");
    return inner.split("|").every((c) => /^\s*[-:\s]+\s*$/.test(c));
  };
  const parseRow = (line: string): string[] => {
    const inner = line.trim().replace(/^\|/, "").replace(/\|$/, "");
    return inner.split("|").map((c) => c.trim());
  };
  const inlineFmt = (c: string) =>
    c.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");

  const rows = lines.filter((l) => l.trim());
  if (!rows.length) return "";

  const hasHeader = rows.length >= 2 && isSepRow(rows[1]);
  let html = '<div class="md-table-wrap"><table class="md-table">';

  if (hasHeader) {
    html += `<thead><tr>${parseRow(rows[0]).map((h) => `<th>${inlineFmt(h)}</th>`).join("")}</tr></thead><tbody>`;
    for (let i = 2; i < rows.length; i++) {
      if (!isSepRow(rows[i]))
        html += `<tr>${parseRow(rows[i]).map((c) => `<td>${inlineFmt(c)}</td>`).join("")}</tr>`;
    }
  } else {
    html += "<tbody>";
    for (const row of rows) {
      if (!isSepRow(row))
        html += `<tr>${parseRow(row).map((c) => `<td>${inlineFmt(c)}</td>`).join("")}</tr>`;
    }
  }
  return html + "</tbody></table></div>";
}

function processTextBlock(raw: string): string {
  let html = raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/^[-*] (.+)$/gm, "<li>$1</li>");
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, "<ul>$1</ul>");
  html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");
  html = html.replace(/\n\n/g, "</p><p>");
  html = "<p>" + html + "</p>";
  html = html.replace(/\n/g, "<br/>");
  html = html.replace(/<p><\/p>/g, "");
  html = html.replace(/<p><br\/>/g, "<p>");
  return html;
}

function renderMarkdown(text: string): string {
  const lines = text.split("\n");
  const parts: { kind: "text" | "table"; lines: string[] }[] = [];
  let i = 0;
  while (i < lines.length) {
    if (/^\s*\|.+\|/.test(lines[i])) {
      const tl: string[] = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) tl.push(lines[i++]);
      parts.push({ kind: "table", lines: tl });
    } else {
      const tl: string[] = [];
      while (i < lines.length && !/^\s*\|.+\|/.test(lines[i])) tl.push(lines[i++]);
      if (tl.length) parts.push({ kind: "text", lines: tl });
    }
  }
  return parts
    .map((p) =>
      p.kind === "table"
        ? buildHtmlTable(p.lines.map((l) => l.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")))
        : processTextBlock(p.lines.join("\n"))
    )
    .join("");
}

function downloadAsPDF(msg: Message) {
  const content = renderMarkdown(msg.content);
  const agentLabel = msg.agent ? msg.agent.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()) : "Strategic Intelligence";
  const dateStr = new Date().toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" });
  const win = window.open("", "_blank", "width=900,height=700");
  if (!win) return;
  win.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Executive Decision Studio</title><style>
    @page{margin:20mm}body{font-family:Arial,sans-serif;font-size:12pt;color:#1e293b;line-height:1.6}
    .header{border-bottom:3px solid #F47920;padding-bottom:12px;margin-bottom:20px}
    .brand{color:#F47920;font-size:11pt;font-weight:700;letter-spacing:.05em}
    .meta{font-size:10pt;color:#64748b;margin-top:4px}
    h1,h2,h3{color:#F47920}h2{font-size:14pt;margin-top:20pt}h3{font-size:12pt}
    p{margin:8pt 0}strong{color:#0f172a}
    code{background:#f1f5f9;padding:1px 4px;border-radius:3px;font-family:monospace;font-size:10pt}
    .md-table-wrap{overflow-x:auto;margin:12pt 0}
    table.md-table{width:100%;border-collapse:collapse;font-size:11pt}
    table.md-table th{background:#fff3e8;color:#c4611a;border:1px solid #e2e8f0;padding:8px 10px;text-align:left;font-weight:600}
    table.md-table td{border:1px solid #e2e8f0;padding:7px 10px}
    table.md-table tr:nth-child(even) td{background:#f8fafc}
    ul{padding-left:18px;margin:8pt 0}li{margin:3pt 0}
    .sources{margin-top:24pt;padding-top:12pt;border-top:1px solid #e2e8f0;font-size:10pt;color:#64748b}
    .footer{margin-top:24pt;padding-top:12pt;text-align:center;font-size:9pt;color:#94a3b8;border-top:1px solid #f1f5f9}
  </style></head><body>
    <div class="header"><div class="brand">ALINTA ENERGY · EXECUTIVE DECISION STUDIO</div>
    <div class="meta">${agentLabel} · ${dateStr}</div></div>
    <div class="content">${content}</div>
    ${msg.sources?.length ? `<div class="sources"><strong>Source Documents:</strong> ${msg.sources.join(" · ")}</div>` : ""}
    <div class="footer">Confidential · Executive Decision Studio · Alinta Energy</div>
    <script>window.onload=function(){window.print();setTimeout(()=>window.close(),1500)}<\/script>
  </body></html>`);
  win.document.close();
}

async function downloadAsPPTX(msg: Message) {
  const res = await fetch("/api/export/pptx", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      content: msg.content,
      agent: msg.agent || "Strategic Intelligence",
      sources: msg.sources || [],
    }),
  });
  if (!res.ok) return;
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `executive-briefing-${new Date().toISOString().split("T")[0]}.pptx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text?: string) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput("");

    const userMsg: Message = { role: "user", content: msg };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setLoading(true);

    // Add placeholder assistant message
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", agent: undefined, sources: [], confidence: 0, latency_ms: 0 },
    ]);

    try {
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          history: messages.slice(-6).map((m) => ({
            role: m.role,
            content: m.content,
          })),
          role: ROLE,
        }),
      });

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }

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
                setMessages((prev) =>
                  prev.map((m, i) =>
                    i === prev.length - 1
                      ? { ...m, agent: data.agent, sources: data.sources }
                      : m
                  )
                );
                setLoading(false);
              } else if (data.type === "token") {
                setMessages((prev) =>
                  prev.map((m, i) =>
                    i === prev.length - 1
                      ? { ...m, content: m.content + data.content }
                      : m
                  )
                );
              } else if (data.type === "chart") {
                const { type: _t, ...chartData } = data;
                setMessages((prev) =>
                  prev.map((m, i) =>
                    i === prev.length - 1
                      ? { ...m, chartData: chartData as ChartData }
                      : m
                  )
                );
              } else if (data.type === "done") {
                setMessages((prev) =>
                  prev.map((m, i) =>
                    i === prev.length - 1
                      ? { ...m, confidence: data.confidence, latency_ms: data.latency_ms }
                      : m
                  )
                );
              }
            } catch {
              // ignore parse errors
            }
          }
        }
      }
    } catch (err) {
      setMessages((prev) => {
        // Replace the placeholder with error
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: `Connection error: ${err instanceof Error ? err.message : "Unknown error"}. Please try again.`,
          agent: "system",
          confidence: 0,
          sources: [],
          latency_ms: 0,
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const likeMessage = (index: number) => {
    setMessages((prev) =>
      prev.map((m, i) => (i === index ? { ...m, liked: !m.liked } : m))
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex gap-5 h-[calc(100vh-160px)]">
      {/* -- Left Sidebar -- */}
      <div className="w-72 flex-shrink-0 flex flex-col gap-3">
        {/* Sample questions header */}
        <div className="glass-card p-4 flex-1 overflow-y-auto min-h-0">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 block">
            Sample Questions
          </label>

          <div className="space-y-1">
            {SAMPLE_QUESTIONS.map((cat) => {
              const isOpen = activeCategory === cat.category;
              return (
                <div key={cat.category}>
                  {/* Category header */}
                  <button
                    onClick={() => setActiveCategory(isOpen ? null : cat.category)}
                    className="w-full flex items-center justify-between px-2 py-1.5 rounded-lg
                      text-[11px] font-semibold uppercase tracking-wider transition-colors cursor-pointer
                      hover:bg-white/5"
                    style={{ color: cat.color }}
                  >
                    <span>{cat.category}</span>
                    <span className="text-slate-500 font-normal normal-case tracking-normal text-[10px]">
                      {isOpen ? "▲" : "▼"}
                    </span>
                  </button>

                  {/* Questions */}
                  {isOpen && (
                    <div className="flex flex-col gap-1 mt-1 mb-2 pl-1">
                      {cat.questions.map((q) => (
                        <button
                          key={q.label}
                          onClick={() => { sendMessage(q.query); setActiveCategory(null); }}
                          disabled={loading}
                          className="text-left text-[12px] px-3 py-2 rounded-lg border border-dark-border
                            text-slate-300 hover:border-opacity-50 hover:bg-white/5
                            transition-all duration-150 disabled:opacity-40 cursor-pointer leading-snug"
                          style={{ borderColor: "rgba(255,255,255,0.07)" }}
                          onMouseEnter={(e) => (e.currentTarget.style.borderColor = cat.color + "55")}
                          onMouseLeave={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.07)")}
                        >
                          {q.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Session stats */}
        <div className="glass-card p-4 flex-shrink-0">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
            Session
          </label>
          <div className="text-sm text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Messages</span>
              <span className="text-slate-200">{messages.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Access</span>
              <span className="text-[11px]" style={{ color: "#F47920" }}>Board / CEO</span>
            </div>
          </div>
        </div>
      </div>

      {/* -- Chat Area -- */}
      <div className="flex-1 flex flex-col glass-card overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center opacity-60">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-navy-800 to-navy-900 flex items-center justify-center mb-4 border border-dark-border">
                <Bot size={28} className="text-gold" />
              </div>
              <h3 className="text-lg font-semibold text-slate-300 mb-1">
                Executive Decision Studio
              </h3>
              <p className="text-sm text-slate-500 max-w-md leading-relaxed">
                Ask strategic questions about Alinta Energy&apos;s operations,
                financials, risks, and competitive positioning. Select a quick
                query or type your own.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 animate-slide-up ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-navy-800 border border-dark-border flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot size={16} className="text-gold" />
                </div>
              )}

              <div
                className={`${msg.role === "user" ? "max-w-[75%]" : "max-w-[85%] w-full"} ${
                  msg.role === "user"
                    ? "bg-blue-600/20 border border-blue-500/30 rounded-2xl rounded-br-md px-4 py-3"
                    : "bg-dark-card border-l-2 border-l-gold/60 border border-dark-border rounded-2xl rounded-bl-md px-4 py-3"
                }`}
              >
                {/* Agent / confidence badges */}
                {msg.role === "assistant" && msg.agent && msg.agent !== "system" && (
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-gold/15 text-gold border border-gold/20">
                      <Cpu size={10} />
                      {agentLabel(msg.agent)}
                    </span>
                    {msg.confidence !== undefined && msg.confidence > 0 && (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/20">
                        <Gauge size={10} />
                        {Math.round(msg.confidence * 100)}%
                      </span>
                    )}
                    {msg.latency_ms !== undefined && msg.latency_ms > 0 && (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-500/15 text-slate-400 border border-slate-500/20">
                        <Clock size={10} />
                        {(msg.latency_ms / 1000).toFixed(1)}s
                      </span>
                    )}
                  </div>
                )}

                {/* Message content */}
                {msg.role === "assistant" && !msg.content && !msg.agent ? (
                  /* Still waiting for meta — show nothing yet */
                  <div className="text-sm text-slate-500 italic">Routing query...</div>
                ) : (
                  <div
                    className={`msg-content text-sm leading-relaxed ${
                      msg.role === "user" ? "text-blue-100" : "text-slate-200"
                    }`}
                    dangerouslySetInnerHTML={{
                      __html: renderMarkdown(msg.content),
                    }}
                  />
                )}

                {/* Inline chart */}
                {msg.role === "assistant" && msg.chartData && (
                  <InlineChart chart={msg.chartData} />
                )}

                {/* Source citations */}
                {msg.role === "assistant" &&
                  msg.sources &&
                  msg.sources.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-dark-border/50">
                      <FileText size={12} className="text-slate-500 mt-0.5" />
                      {msg.sources.map((src) => (
                        <span
                          key={src}
                          className="text-[11px] px-2 py-0.5 rounded-full bg-navy-800 border border-dark-border
                            text-slate-300 hover:text-gold hover:border-gold/30 transition-colors cursor-default"
                          title={DOC_TITLES[src] || src}
                        >
                          {src}
                          {DOC_TITLES[src] && (
                            <span className="text-slate-500 ml-1">
                              {DOC_TITLES[src].length > 20
                                ? DOC_TITLES[src].slice(0, 20) + "..."
                                : DOC_TITLES[src]}
                            </span>
                          )}
                        </span>
                      ))}
                    </div>
                  )}

                {/* Like + Download actions */}
                {msg.role === "assistant" && msg.content && (
                  <div className="flex items-center gap-2 mt-2 pt-2 border-t border-dark-border/30">
                    <button
                      onClick={() => likeMessage(i)}
                      title={msg.liked ? "Unlike" : "Like this response"}
                      className={`flex items-center gap-1 text-[11px] px-2 py-1 rounded-lg border transition-all cursor-pointer
                        ${msg.liked
                          ? "bg-gold/15 border-gold/40 text-gold"
                          : "border-dark-border/50 text-slate-500 hover:text-gold hover:border-gold/30"}`}
                    >
                      <ThumbsUp size={11} />
                      {msg.liked ? "Liked" : "Like"}
                    </button>
                    {msg.liked && (
                      <>
                        <button
                          onClick={() => downloadAsPDF(msg)}
                          className="flex items-center gap-1 text-[11px] px-2 py-1 rounded-lg border border-dark-border/50 text-slate-400 hover:text-blue-400 hover:border-blue-400/40 transition-all cursor-pointer"
                          title="Download as PDF (print dialog)"
                        >
                          <FileDown size={11} />
                          PDF
                        </button>
                        <button
                          onClick={() => downloadAsPPTX(msg)}
                          className="flex items-center gap-1 text-[11px] px-2 py-1 rounded-lg border border-dark-border/50 text-slate-400 hover:text-orange-400 hover:border-orange-400/40 transition-all cursor-pointer"
                          title="Download as PowerPoint"
                        >
                          <Presentation size={11} />
                          PPTX
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>

              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-lg bg-blue-600/30 border border-blue-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <User size={16} className="text-blue-300" />
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="flex gap-3 animate-fade-in">
              <div className="w-8 h-8 rounded-lg bg-navy-800 border border-dark-border flex items-center justify-center flex-shrink-0">
                <Bot size={16} className="text-gold" />
              </div>
              <div className="bg-dark-card border-l-2 border-l-gold/60 border border-dark-border rounded-2xl rounded-bl-md px-5 py-4">
                <div className="flex gap-1.5">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input area */}
        <div className="p-4 border-t border-dark-border bg-dark-card/50">
          <div className="flex gap-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a strategic question..."
              rows={1}
              className="flex-1 bg-dark-bg border border-dark-border rounded-xl px-4 py-3
                text-sm text-slate-200 placeholder-slate-500
                focus:outline-none focus:border-gold/50 focus:ring-1 focus:ring-gold/20
                resize-none transition-colors"
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="px-4 rounded-xl bg-gradient-to-r from-gold-dark to-gold
                text-navy-900 font-semibold text-sm
                hover:shadow-lg hover:shadow-gold/20
                disabled:opacity-30 disabled:cursor-not-allowed
                transition-all duration-200 flex items-center gap-2 cursor-pointer"
            >
              <Send size={16} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
