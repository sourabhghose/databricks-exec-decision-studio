import {
  Cpu,
  Database,
  Search,
  Shield,
  BarChart3,
  FileText,
  Brain,
  Layers,
  BookOpen,
  GitBranch,
  CheckCircle,
  Server,
  Lock,
  Globe,
  Zap,
  MessageSquare,
  Eye,
  TrendingUp,
} from "lucide-react";

const HERO_METRICS = [
  { value: "28", label: "Capabilities" },
  { value: "22", label: "Agents" },
  { value: "22", label: "Docs Indexed" },
  { value: "12", label: "Live KPIs" },
];

const CAPABILITIES = [
  {
    icon: <FileText size={18} />,
    name: "Document Intelligence",
    desc: "RAG over 22 board documents covering strategy, financials, ESG, risk, and governance. Full citation chain with [DOC-XXX] references.",
    cap: "Capabilities 1–4",
    color: "#F47920",
  },
  {
    icon: <Search size={18} />,
    name: "Strategic Gap Analysis",
    desc: "Identifies blind spots, risks, and gaps in strategy documents against AEMO ISP projections and market benchmarks.",
    cap: "Capabilities 5–8",
    color: "#8b5cf6",
  },
  {
    icon: <Brain size={18} />,
    name: "Competitive Intelligence",
    desc: "Market position analysis vs Origin Energy, AGL, Energy Australia across retail, generation, and trading.",
    cap: "Capabilities 9–12",
    color: "#3b82f6",
  },
  {
    icon: <BookOpen size={18} />,
    name: "Executive Briefing",
    desc: "Board-ready briefing generation with structured headings, executive summaries, and full document citations.",
    cap: "Capabilities 13–16",
    color: "#22c55e",
  },
  {
    icon: <BarChart3 size={18} />,
    name: "KPI Monitoring & Anomaly Detection",
    desc: "Z-score anomaly detection across 12 KPI metrics over 36 months. Automated trend analysis and alert generation.",
    cap: "Capabilities 17–22",
    color: "#eab308",
  },
  {
    icon: <Shield size={18} />,
    name: "Governance & Evaluation",
    desc: "Groundedness scoring, citation quality verification, tiered access control, and immutable audit logging.",
    cap: "Capabilities 23–28",
    color: "#ef4444",
  },
];

const DATA_SCHEMAS = [
  { schema: "eds_synthetic", contents: "22 strategic docs + financial data FY24–27 + 12 KPIs × 36 months", status: "active" },
  { schema: "eds_processed", contents: "Document chunks with embeddings (databricks-gte-large-en)", status: "active" },
  { schema: "eds_vectors", contents: "Databricks Vector Search Delta Sync Index", status: "active" },
  { schema: "eds_audit", contents: "Immutable audit trail — every agent interaction logged", status: "active" },
  { schema: "eds_actions", contents: "Board action items and decision register", status: "active" },
  { schema: "eds_evaluation", contents: "RAG evaluation QA pairs + groundedness scores", status: "active" },
];

const TECH_STACK = [
  { icon: <Cpu size={15} />, label: "LLM", value: "Claude Sonnet 4.6", detail: "Databricks Foundation Model API" },
  { icon: <Database size={15} />, label: "Embeddings", value: "GTE-Large-EN", detail: "1024-dim dense vectors" },
  { icon: <Search size={15} />, label: "Vector Search", value: "Delta Sync Index", detail: "Managed Databricks VS" },
  { icon: <Globe size={15} />, label: "Frontend", value: "React + Vite + Tailwind", detail: "TypeScript, light/dark theme" },
  { icon: <Server size={15} />, label: "Backend", value: "FastAPI + Uvicorn", detail: "Async Python, SSE streaming" },
  { icon: <Lock size={15} />, label: "Auth", value: "Tiered RBAC", detail: "5 access tiers, OAuth2 SP" },
];

/* ── Architecture Diagram ──────────────────────────────────────────────────── */
function ArchDiagram() {
  const accent = "var(--accent)";
  const surface = "var(--surface)";
  const border = "var(--border)";
  const text1 = "var(--text-1)";
  const text3 = "var(--text-3)";

  const agents = [
    { name: "Document\nQA Agent", color: "#F47920", icon: "📄" },
    { name: "Strategic\nGap Advisor", color: "#8b5cf6", icon: "🔍" },
    { name: "Competitive\nIntel Agent", color: "#3b82f6", icon: "📊" },
    { name: "Briefing\nAgent", color: "#22c55e", icon: "📋" },
    { name: "KPI\nMonitor", color: "#eab308", icon: "📈" },
  ];

  return (
    <svg
      viewBox="0 0 860 380"
      width="100%"
      style={{ maxHeight: 380, display: "block" }}
      fontFamily="Inter, -apple-system, sans-serif"
    >
      {/* ── Background grid ── */}
      <defs>
        <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
          <path d="M 24 0 L 0 0 0 24" fill="none" stroke="currentColor" strokeOpacity="0.04" strokeWidth="1" />
        </pattern>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
          <path d="M0,0 L0,6 L8,3 z" fill="#94a3b8" opacity="0.5" />
        </marker>
        <marker id="arrowAccent" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
          <path d="M0,0 L0,6 L8,3 z" fill={accent} />
        </marker>
      </defs>

      {/* ── User Query box ── */}
      <rect x="20" y="160" width="130" height="60" rx="10"
        fill={surface} stroke={border} strokeWidth="1.5" />
      <text x="85" y="184" textAnchor="middle" fontSize="11" fill={text3} fontWeight="500">User Query</text>
      <text x="85" y="200" textAnchor="middle" fontSize="9.5" fill={text3}>(Exec / Board)</text>
      <rect x="30" y="170" width="4" height="40" rx="2" fill={accent} />

      {/* Arrow: User → Supervisor */}
      <line x1="152" y1="190" x2="218" y2="190"
        stroke={accent} strokeWidth="1.5" markerEnd="url(#arrowAccent)" />
      <text x="185" y="183" textAnchor="middle" fontSize="9" fill={accent}>classify</text>

      {/* ── Supervisor Agent (centre) ── */}
      <rect x="220" y="130" width="170" height="120" rx="12"
        fill={surface} stroke={accent} strokeWidth="2" />
      <rect x="220" y="130" width="170" height="32" rx="12" fill={accent} />
      <rect x="220" y="150" width="170" height="12" rx="0" fill={accent} />
      <text x="305" y="151" textAnchor="middle" fontSize="11" fill="white" fontWeight="700">Supervisor Agent</text>
      <text x="305" y="172" textAnchor="middle" fontSize="9.5" fill={text3}>Intent Classifier</text>
      <text x="305" y="187" textAnchor="middle" fontSize="9.5" fill={text3}>Access Control (Tier 1–4)</text>
      <text x="305" y="202" textAnchor="middle" fontSize="9.5" fill={text3}>Agent Router</text>
      <text x="305" y="217" textAnchor="middle" fontSize="9.5" fill={text3}>Confidence Scorer</text>
      <text x="305" y="232" textAnchor="middle" fontSize="9.5" fill={text3}>Audit Logger</text>

      {/* Arrows: Supervisor → each agent */}
      {agents.map((agent, i) => {
        const agentX = 460;
        const agentY = 32 + i * 66;
        const agentCY = agentY + 28;
        const supervisorCY = 190;
        const supervisorRX = 390;
        // Bezier from supervisor right edge to agent left edge
        const cx1 = supervisorRX + 30;
        const cx2 = agentX - 25;
        return (
          <path key={i}
            d={`M ${supervisorRX} ${supervisorCY} C ${cx1} ${supervisorCY}, ${cx2} ${agentCY}, ${agentX} ${agentCY}`}
            fill="none" stroke={agent.color} strokeWidth="1.5" opacity="0.7"
            markerEnd="url(#arrow)"
          />
        );
      })}

      {/* ── Specialist Agent boxes ── */}
      {agents.map((agent, i) => {
        const x = 460, y = 32 + i * 66;
        const lines = agent.name.split("\n");
        return (
          <g key={i}>
            <rect x={x} y={y} width="148" height="54" rx="8"
              fill={surface} stroke={agent.color} strokeWidth="1.5" />
            <rect x={x} y={y} width="4" height="54" rx="2 0 0 2" fill={agent.color} />
            <text x={x + 14} y={y + 18} fontSize="10" fill={agent.color} fontWeight="600">{agent.icon}</text>
            {lines.map((line, li) => (
              <text key={li} x={x + 30} y={y + 19 + li * 15} fontSize="10" fill={text1} fontWeight="500">{line}</text>
            ))}
          </g>
        );
      })}

      {/* Arrow: agents → Response */}
      <line x1="609" y1="190" x2="668" y2="190"
        stroke={accent} strokeWidth="1.5" markerEnd="url(#arrowAccent)" />

      {/* ── Response box ── */}
      <rect x="670" y="160" width="130" height="60" rx="10"
        fill={surface} stroke={border} strokeWidth="1.5" />
      <rect x="794" y="170" width="4" height="40" rx="2" fill={accent} />
      <text x="736" y="184" textAnchor="middle" fontSize="11" fill={text3} fontWeight="500">Response</text>
      <text x="736" y="200" textAnchor="middle" fontSize="9.5" fill={text3}>Streamed + Cited</text>

      {/* ── Data layer (bottom) ── */}
      {/* VS box */}
      <rect x="220" y="290" width="110" height="50" rx="8"
        fill={surface} stroke="#8b5cf6" strokeWidth="1.5" />
      <text x="275" y="311" textAnchor="middle" fontSize="10" fill="#8b5cf6" fontWeight="600">Vector Search</text>
      <text x="275" y="327" textAnchor="middle" fontSize="9" fill={text3}>22 docs indexed</text>
      {/* Arrow up */}
      <line x1="275" y1="290" x2="275" y2="252" stroke="#8b5cf6" strokeWidth="1.2"
        strokeDasharray="4 3" markerEnd="url(#arrow)" />

      {/* UC box */}
      <rect x="345" y="290" width="110" height="50" rx="8"
        fill={surface} stroke="#22c55e" strokeWidth="1.5" />
      <text x="400" y="311" textAnchor="middle" fontSize="10" fill="#22c55e" fontWeight="600">Unity Catalog</text>
      <text x="400" y="327" textAnchor="middle" fontSize="9" fill={text3}>6 eds_ schemas</text>
      {/* Arrow up */}
      <line x1="370" y1="290" x2="345" y2="252" stroke="#22c55e" strokeWidth="1.2"
        strokeDasharray="4 3" markerEnd="url(#arrow)" />

      {/* Audit box */}
      <rect x="470" y="290" width="110" height="50" rx="8"
        fill={surface} stroke="#ef4444" strokeWidth="1.5" />
      <text x="525" y="311" textAnchor="middle" fontSize="10" fill="#ef4444" fontWeight="600">Audit Trail</text>
      <text x="525" y="327" textAnchor="middle" fontSize="9" fill={text3}>eds_audit schema</text>
      {/* Arrow up */}
      <line x1="480" y1="290" x2="380" y2="252" stroke="#ef4444" strokeWidth="1.2"
        strokeDasharray="4 3" markerEnd="url(#arrow)" />

      {/* ── LLM label (top) ── */}
      <rect x="220" y="18" width="170" height="34" rx="8"
        fill={surface} stroke={accent} strokeWidth="1" strokeDasharray="5 3" />
      <text x="305" y="33" textAnchor="middle" fontSize="10" fill={accent} fontWeight="600">Claude Sonnet 4.6</text>
      <text x="305" y="46" textAnchor="middle" fontSize="9" fill={text3}>Databricks Foundation Model API</text>
      <line x1="305" y1="52" x2="305" y2="128" stroke={accent} strokeWidth="1.2"
        strokeDasharray="4 3" markerEnd="url(#arrowAccent)" />
    </svg>
  );
}

export default function About() {
  return (
    <div className="max-w-5xl mx-auto space-y-7">
      {/* ── Hero ── */}
      <div className="glass-card p-8">
        <div className="flex items-center gap-3 mb-5">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center"
            style={{ background: "var(--accent-light)" }}
          >
            <Zap size={24} style={{ color: "var(--accent)" }} />
          </div>
          <div>
            <h2 className="text-2xl font-bold" style={{ color: "var(--text-1)" }}>
              Agentic AI Strategic Intelligence Platform
            </h2>
            <p className="text-[13px]" style={{ color: "var(--text-3)" }}>
              Built on Databricks Mosaic AI · Alinta Energy Board & C-Suite
            </p>
          </div>
        </div>
        <p className="text-sm leading-relaxed mb-6" style={{ color: "var(--text-3)" }}>
          Transforms how senior leaders access, synthesise, and act on strategic information.
          Multi-agent architecture with RAG, Vector Search, MLflow tracing, and real-time KPI intelligence.
        </p>
        <div className="grid grid-cols-4 gap-3">
          {HERO_METRICS.map((m) => (
            <div
              key={m.label}
              className="text-center py-4 rounded-xl"
              style={{ background: "var(--accent-light)", border: "1px solid var(--border)" }}
            >
              <div className="text-3xl font-bold mb-1" style={{ color: "var(--accent)" }}>{m.value}</div>
              <div className="text-[11px] uppercase tracking-wider font-medium" style={{ color: "var(--text-3)" }}>
                {m.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Architecture Diagram ── */}
      <div className="glass-card p-6">
        <h3 className="text-base font-bold mb-1 flex items-center gap-2" style={{ color: "var(--text-1)" }}>
          <GitBranch size={16} style={{ color: "var(--accent)" }} />
          Multi-Agent Architecture
        </h3>
        <p className="text-[12px] mb-4" style={{ color: "var(--text-3)" }}>
          Supervisor pattern — intent classification routes queries to specialist agents with tier-based access control
        </p>
        <div
          className="rounded-xl p-4"
          style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
        >
          <ArchDiagram />
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-4 mt-4">
          {[
            { label: "Document QA", color: "#F47920" },
            { label: "Strategic Gap", color: "#8b5cf6" },
            { label: "Competitive Intel", color: "#3b82f6" },
            { label: "Executive Briefing", color: "#22c55e" },
            { label: "KPI Monitor", color: "#eab308" },
          ].map((a) => (
            <div key={a.label} className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: a.color }} />
              <span className="text-[11px]" style={{ color: "var(--text-3)" }}>{a.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Capabilities Grid ── */}
      <div>
        <h3 className="text-base font-bold mb-4 flex items-center gap-2" style={{ color: "var(--text-1)" }}>
          <Cpu size={16} style={{ color: "var(--accent)" }} />
          Platform Capabilities
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {CAPABILITIES.map((cap) => (
            <div
              key={cap.name}
              className="glass-card p-4"
              style={{ borderLeft: `3px solid ${cap.color}` }}
            >
              <div className="flex gap-3">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: `${cap.color}15`, color: cap.color }}
                >
                  {cap.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-[13px] font-semibold" style={{ color: "var(--text-1)" }}>{cap.name}</div>
                    <span className="text-[10px] font-mono" style={{ color: "var(--text-4)" }}>{cap.cap}</span>
                  </div>
                  <div className="text-[11px] leading-relaxed" style={{ color: "var(--text-3)" }}>{cap.desc}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Data Architecture ── */}
      <div>
        <h3 className="text-base font-bold mb-4 flex items-center gap-2" style={{ color: "var(--text-1)" }}>
          <Database size={16} style={{ color: "var(--accent)" }} />
          Data Architecture
        </h3>
        <div className="glass-card overflow-hidden">
          <div
            className="px-5 py-2.5 flex items-center justify-between"
            style={{ borderBottom: "1px solid var(--border)", background: "var(--surface-2)" }}
          >
            <div className="flex items-center gap-2">
              <span className="text-[11px]" style={{ color: "var(--text-3)" }}>Unity Catalog:</span>
              <code className="text-[11px] font-mono px-1.5 py-0.5 rounded" style={{ background: "var(--accent-light)", color: "var(--accent)" }}>
                ausnet_process_intel_catalog
              </code>
            </div>
            <span className="text-[11px] text-emerald-600 flex items-center gap-1">
              <CheckCircle size={11} /> All schemas active
            </span>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                {["Schema", "Contents", "Status"].map((h, i) => (
                  <th key={h} className={`py-2.5 text-[11px] font-semibold uppercase tracking-wider ${i === 2 ? "text-center px-4 w-20" : "text-left px-5"}`}
                    style={{ color: "var(--text-3)" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {DATA_SCHEMAS.map((s, i) => (
                <tr key={s.schema} style={{ borderBottom: "1px solid var(--border)", background: i % 2 === 1 ? "var(--surface-2)" : undefined }}>
                  <td className="px-5 py-2.5 font-mono text-[11px]" style={{ color: "var(--accent)" }}>{s.schema}</td>
                  <td className="px-4 py-2.5 text-[11px]" style={{ color: "var(--text-3)" }}>{s.contents}</td>
                  <td className="px-4 py-2.5 text-center">
                    <span className="inline-flex items-center gap-1 text-[10px] text-emerald-600">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      Live
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Technology Stack ── */}
      <div className="glass-card p-5">
        <h3 className="text-base font-bold mb-4 flex items-center gap-2" style={{ color: "var(--text-1)" }}>
          <Layers size={16} style={{ color: "var(--accent)" }} />
          Technology Stack
        </h3>
        <div className="grid grid-cols-3 gap-3">
          {TECH_STACK.map((tech) => (
            <div
              key={tech.label}
              className="p-3.5 rounded-xl"
              style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span style={{ color: "var(--accent)" }}>{tech.icon}</span>
                <span className="text-[10px] uppercase tracking-wider font-semibold" style={{ color: "var(--text-3)" }}>
                  {tech.label}
                </span>
              </div>
              <div className="text-[13px] font-semibold mb-0.5" style={{ color: "var(--text-1)" }}>{tech.value}</div>
              <div className="text-[11px]" style={{ color: "var(--text-4)" }}>{tech.detail}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── AI Agents detail ── */}
      <div className="glass-card p-5">
        <h3 className="text-base font-bold mb-4 flex items-center gap-2" style={{ color: "var(--text-1)" }}>
          <Brain size={16} style={{ color: "var(--accent)" }} />
          Agent Details
        </h3>
        <div className="grid grid-cols-3 gap-2">
          {[
            { name: "Supervisor Agent", role: "Intent classification, routing, access control, audit", icon: <MessageSquare size={13} />, color: "#F47920" },
            { name: "Document QA Agent", role: "RAG retrieval over 22 indexed board documents with citations", icon: <FileText size={13} />, color: "#F47920" },
            { name: "Strategic Gap Advisor", role: "Identifies blind spots vs AEMO ISP and market benchmarks", icon: <Search size={13} />, color: "#8b5cf6" },
            { name: "Competitive Intel Agent", role: "Market share, NPS, and positioning vs Origin, AGL, EA", icon: <Eye size={13} />, color: "#3b82f6" },
            { name: "Briefing Agent", role: "Board-ready briefing with headings, bullets, citations", icon: <BookOpen size={13} />, color: "#22c55e" },
            { name: "KPI Monitor Agent", role: "Z-score anomaly detection, trend analysis on 12 live KPIs", icon: <TrendingUp size={13} />, color: "#eab308" },
            { name: "Evaluation Agent", role: "Groundedness scoring, citation quality verification", icon: <CheckCircle size={13} />, color: "#ef4444" },
            { name: "MLflow Tracing", role: "End-to-end trace logging for every agent invocation", icon: <GitBranch size={13} />, color: "#64748b" },
            { name: "Audit Logger", role: "Immutable interaction log: query, response, tier, confidence", icon: <Shield size={13} />, color: "#64748b" },
          ].map((a) => (
            <div
              key={a.name}
              className="p-3 rounded-lg flex gap-2.5"
              style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
            >
              <div
                className="w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5"
                style={{ backgroundColor: `${a.color}18`, color: a.color }}
              >
                {a.icon}
              </div>
              <div>
                <div className="text-[12px] font-semibold" style={{ color: "var(--text-1)" }}>{a.name}</div>
                <div className="text-[10px] leading-snug mt-0.5" style={{ color: "var(--text-3)" }}>{a.role}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <p className="text-center text-[11px] pb-4" style={{ color: "var(--text-4)" }}>
        All content is AI-generated synthetic data for demonstration purposes.
        Built with Databricks Mosaic AI · Executive Decision Studio v2.1.0
      </p>
    </div>
  );
}
