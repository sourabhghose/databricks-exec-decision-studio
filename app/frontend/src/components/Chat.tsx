import { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  FileText,
  Clock,
  Cpu,
  Gauge,
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
}

const ROLES = [
  "Board Director / CEO",
  "CFO / C-Suite",
  "Executive Leadership Team",
  "Senior Management",
  "All Staff",
];

const QUICK_QUERIES = [
  { label: "Loy Yang B Options", query: "What are the strategic options and timeline for the Loy Yang B transition and retirement?" },
  { label: "KPI Performance", query: "Summarise the latest KPI performance across all business units, highlighting any anomalies" },
  { label: "Competitive Position", query: "How does Alinta's market position compare to Origin Energy, AGL, and Energy Australia?" },
  { label: "1H FY25 Results", query: "What were the key financial results, variances from budget, and management commentary for 1H FY25?" },
  { label: "Enterprise Risks", query: "What are the top enterprise risks this quarter and what mitigations are in place?" },
  { label: "WA Renewables Brief", query: "Prepare an executive briefing on the WA renewables pipeline and Yandin Stage 2 investment case" },
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

function renderMarkdown(text: string): string {
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
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

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [role, setRole] = useState(ROLES[0]);
  const [loading, setLoading] = useState(false);
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
          role,
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex gap-5 h-[calc(100vh-160px)]">
      {/* -- Left Sidebar -- */}
      <div className="w-72 flex-shrink-0 flex flex-col gap-4">
        {/* Role selector */}
        <div className="glass-card p-4">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
            Access Tier
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

        {/* Quick queries */}
        <div className="glass-card p-4 flex-1 overflow-y-auto">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 block">
            Quick Queries
          </label>
          <div className="flex flex-col gap-2">
            {QUICK_QUERIES.map((q) => (
              <button
                key={q.label}
                onClick={() => sendMessage(q.query)}
                disabled={loading}
                className="text-left text-sm px-3 py-2 rounded-lg border border-dark-border
                  text-slate-300 hover:text-gold hover:border-gold/30 hover:bg-gold/5
                  transition-all duration-200 disabled:opacity-40 cursor-pointer"
              >
                {q.label}
              </button>
            ))}
          </div>
        </div>

        {/* Session stats */}
        <div className="glass-card p-4">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
            Session
          </label>
          <div className="text-sm text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Messages</span>
              <span className="text-slate-200">{messages.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Role</span>
              <span className="text-gold text-xs">{role.split(" / ")[0]}</span>
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
