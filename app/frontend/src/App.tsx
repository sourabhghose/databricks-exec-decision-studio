import { useState, useEffect, useRef } from "react";
import {
  MessageSquareText,
  BarChart3,
  Shield,
  Info,
  ClipboardList,
  AlertTriangle,
  Gavel,
  Library,
  Sparkles,
  LayoutDashboard,
  Sun,
  Moon,
  User,
  Globe,
  GitBranch,
  ChevronDown,
  Bot,
  Database,
} from "lucide-react";
import Overview from "./components/Overview";
import Chat from "./components/Chat";
import KPIDashboard from "./components/KPIDashboard";
import AuditLog from "./components/AuditLog";
import About from "./components/About";
import ActionItems from "./components/ActionItems";
import RiskRegister from "./components/RiskRegister";
import DecisionRegister from "./components/DecisionRegister";
import DocumentLibrary from "./components/DocumentLibrary";
import Briefing from "./components/Briefing";
import MarketIntelligence from "./components/MarketIntelligence";
import ScenarioSimulator from "./components/ScenarioSimulator";
import GenieInsights from "./components/GenieInsights";

type Tab =
  | "overview"
  | "chat"
  | "kpi"
  | "risks"
  | "decisions"
  | "actions"
  | "audit"
  | "documents"
  | "briefing"
  | "market"
  | "simulate"
  | "genie"
  | "about";

const AI_ASSISTANT_TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: "chat",     label: "Strategic Chat", icon: <MessageSquareText size={13} /> },
  { id: "briefing", label: "AI Briefing",    icon: <Sparkles size={13} /> },
  { id: "simulate", label: "Simulation",     icon: <GitBranch size={13} /> },
  { id: "genie",    label: "Data Insights",  icon: <Database size={13} /> },
];

const MAIN_TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: "overview",   label: "Overview",        icon: <LayoutDashboard size={14} /> },
  // "ai-assistant" handled separately as a dropdown
  { id: "market",     label: "Market Intel",    icon: <Globe size={14} /> },
  { id: "kpi",        label: "KPI Dashboard",   icon: <BarChart3 size={14} /> },
  { id: "risks",      label: "Risk Register",   icon: <AlertTriangle size={14} /> },
  { id: "decisions",  label: "Decisions",       icon: <Gavel size={14} /> },
  { id: "actions",    label: "Action Items",    icon: <ClipboardList size={14} /> },
  { id: "documents",  label: "Document Library",icon: <Library size={14} /> },
  { id: "audit",      label: "Audit Log",       icon: <Shield size={14} /> },
  { id: "about",      label: "About",           icon: <Info size={14} /> },
];

const AI_ASSISTANT_IDS = new Set<Tab>(["chat", "briefing", "simulate", "genie"]);

/* ── Alinta Energy logo ──────────────────────────────────────────────────── */
function AlintaIcon({ size = 36 }: { size?: number }) {
  const r = size / 2;
  const cx = r, cy = r;
  const petalColors = ["#F47920", "#D4500A", "#F5A623", "#F47920", "#D4500A", "#F5A623"];
  const petalRx = size * 0.115;
  const petalRy = size * 0.26;
  const offset = size * 0.19;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} fill="none">
      {petalColors.map((color, i) => {
        const angleDeg = i * 60 - 90;
        const angleRad = (angleDeg * Math.PI) / 180;
        const px = cx + Math.cos(angleRad) * offset;
        const py = cy + Math.sin(angleRad) * offset;
        return (
          <ellipse
            key={i}
            cx={px}
            cy={py}
            rx={petalRx}
            ry={petalRy}
            fill={color}
            opacity={0.9}
            transform={`rotate(${angleDeg + 90} ${px} ${py})`}
          />
        );
      })}
      <circle cx={cx} cy={cy} r={size * 0.14} fill="#F47920" />
    </svg>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [genieQuestion, setGenieQuestion] = useState<string>("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  function askGenie(question: string) {
    setGenieQuestion(question);
    selectTab("genie");
  }

  const isAiActive = AI_ASSISTANT_IDS.has(activeTab);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // ── Dark mode ────────────────────────────────────────────────────────────
  const [dark, setDark] = useState<boolean>(() => {
    const stored = localStorage.getItem("eds-theme");
    if (stored) return stored === "dark";
    return true;
  });

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("eds-theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("eds-theme", "light");
    }
  }, [dark]);

  function selectTab(id: Tab) {
    setActiveTab(id);
    setDropdownOpen(false);
  }

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "var(--bg)" }}>
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <header className="header-gradient sticky top-0 z-40">
        <div className="max-w-[1440px] mx-auto px-6">
          {/* Top bar */}
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-2.5">
              <AlintaIcon size={34} />
              <span
                className="text-[22px] font-bold tracking-tight select-none"
                style={{ color: "var(--accent)" }}
              >
                alinta<span style={{ color: "var(--accent)", fontWeight: 400 }}>energy</span>
              </span>
              <span
                className="hidden sm:block ml-3 pl-3 text-[12px] font-medium"
                style={{
                  borderLeft: "1px solid var(--border-strong)",
                  color: "var(--text-3)",
                  letterSpacing: "0.04em",
                }}
              >
                Executive Decision Studio
              </span>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setDark(!dark)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-colors"
                style={{
                  background: "var(--surface-2)",
                  border: "1px solid var(--border)",
                  color: "var(--text-3)",
                }}
                title={dark ? "Switch to light mode" : "Switch to dark mode"}
              >
                {dark ? <Sun size={14} /> : <Moon size={14} />}
                <span className="hidden sm:inline">{dark ? "Light" : "Dark"}</span>
              </button>

              <div
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
                style={{
                  background: "var(--surface-2)",
                  border: "1px solid var(--border)",
                }}
              >
                <User size={13} style={{ color: "var(--text-3)" }} />
                <span className="text-[12px]" style={{ color: "var(--text-3)" }}>
                  sourabh.ghose@alintaenergy.com.au
                </span>
              </div>
            </div>
          </div>

          {/* Tab navigation */}
          <nav
            className="flex gap-0.5 -mb-[1px]"
            style={{ borderBottom: "1px solid var(--border)" }}
          >
            {/* Overview */}
            {MAIN_TABS.slice(0, 1).map((tab) => (
              <button
                key={tab.id}
                onClick={() => selectTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-2.5 text-[12px] font-medium rounded-t-lg
                  transition-all duration-150 cursor-pointer whitespace-nowrap
                  ${activeTab === tab.id ? "tab-active" : ""}`}
                style={
                  activeTab === tab.id
                    ? { color: "var(--tab-active-text)", background: "var(--surface-2)" }
                    : { color: "var(--tab-inactive-text)" }
                }
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}

            {/* AI Assistant dropdown */}
            <div ref={dropdownRef} className="relative">
              <button
                onClick={() => setDropdownOpen((o) => !o)}
                className={`flex items-center gap-1.5 px-3 py-2.5 text-[12px] font-medium rounded-t-lg
                  transition-all duration-150 cursor-pointer whitespace-nowrap
                  ${isAiActive ? "tab-active" : ""}`}
                style={
                  isAiActive
                    ? { color: "var(--tab-active-text)", background: "var(--surface-2)" }
                    : { color: "var(--tab-inactive-text)" }
                }
              >
                <Bot size={14} />
                AI Assistant
                {isAiActive && (
                  <span
                    className="ml-0.5 text-[10px] font-normal opacity-70"
                    style={{ color: "var(--tab-active-text)" }}
                  >
                    · {AI_ASSISTANT_TABS.find((t) => t.id === activeTab)?.label}
                  </span>
                )}
                <ChevronDown
                  size={12}
                  className={`ml-0.5 transition-transform duration-150 ${dropdownOpen ? "rotate-180" : ""}`}
                />
              </button>

              {/* Dropdown panel */}
              {dropdownOpen && (
                <div
                  className="absolute top-full left-0 mt-1 rounded-xl py-1 z-50 min-w-[170px]"
                  style={{
                    background: "var(--surface-2)",
                    border: "1px solid var(--border-strong)",
                    boxShadow: "0 8px 24px rgba(0,0,0,0.35)",
                  }}
                >
                  {AI_ASSISTANT_TABS.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => selectTab(tab.id)}
                      className="flex items-center gap-2 w-full px-4 py-2.5 text-[12px] font-medium text-left transition-colors"
                      style={
                        activeTab === tab.id
                          ? { color: "var(--accent)", background: "rgba(244,121,32,0.10)" }
                          : { color: "var(--text-2)" }
                      }
                    >
                      {tab.icon}
                      {tab.label}
                      {activeTab === tab.id && (
                        <span
                          className="ml-auto w-1.5 h-1.5 rounded-full"
                          style={{ background: "var(--accent)" }}
                        />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Remaining tabs: Market Intel first, then the rest */}
            {MAIN_TABS.slice(1).map((tab) => (
              <button
                key={tab.id}
                onClick={() => selectTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-2.5 text-[12px] font-medium rounded-t-lg
                  transition-all duration-150 cursor-pointer whitespace-nowrap
                  ${activeTab === tab.id ? "tab-active" : ""}`}
                style={
                  activeTab === tab.id
                    ? { color: "var(--tab-active-text)", background: "var(--surface-2)" }
                    : { color: "var(--tab-inactive-text)" }
                }
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* ── Page content ─────────────────────────────────────────────────── */}
      <main className="flex-1 max-w-[1440px] w-full mx-auto p-6">
        <div className="animate-fade-in">
          {activeTab === "overview"   && <Overview onAskGenie={askGenie} />}
          {activeTab === "chat"       && <Chat />}
          {activeTab === "kpi"        && <KPIDashboard />}
          {activeTab === "risks"      && <RiskRegister />}
          {activeTab === "decisions"  && <DecisionRegister />}
          {activeTab === "actions"    && <ActionItems />}
          {activeTab === "documents"  && <DocumentLibrary />}
          {activeTab === "briefing"   && <Briefing />}
          {activeTab === "market"     && <MarketIntelligence />}
          {activeTab === "simulate"   && <ScenarioSimulator />}
          {activeTab === "genie"      && <GenieInsights initialQuestion={genieQuestion} onQuestionConsumed={() => setGenieQuestion("")} />}
          {activeTab === "audit"      && <AuditLog />}
          {activeTab === "about"      && <About />}
        </div>
      </main>
    </div>
  );
}
