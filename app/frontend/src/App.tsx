import { useState, useEffect } from "react";
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
  | "about";

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: "overview",   label: "Overview",        icon: <LayoutDashboard size={14} /> },
  { id: "chat",       label: "Strategic Chat",  icon: <MessageSquareText size={14} /> },
  { id: "kpi",        label: "KPI Dashboard",   icon: <BarChart3 size={14} /> },
  { id: "risks",      label: "Risk Register",   icon: <AlertTriangle size={14} /> },
  { id: "decisions",  label: "Decisions",       icon: <Gavel size={14} /> },
  { id: "actions",    label: "Action Items",    icon: <ClipboardList size={14} /> },
  { id: "documents",  label: "Document Library",icon: <Library size={14} /> },
  { id: "briefing",   label: "AI Briefing",     icon: <Sparkles size={14} /> },
  { id: "market",     label: "Market Intel",      icon: <Globe size={14} /> },
  { id: "simulate",   label: "Scenario Sim",      icon: <GitBranch size={14} /> },
  { id: "audit",      label: "Audit Log",         icon: <Shield size={14} /> },
  { id: "about",      label: "About",             icon: <Info size={14} /> },
];

/* ── Alinta Energy logo ──────────────────────────────────────────────────── */
function AlintaIcon({ size = 36 }: { size?: number }) {
  const r = size / 2;
  const cx = r, cy = r;
  // 6 petals at 60° intervals, alternating orange / dark-orange / amber
  const petalColors = ["#F47920", "#D4500A", "#F5A623", "#F47920", "#D4500A", "#F5A623"];
  const petalRx = size * 0.115;
  const petalRy = size * 0.26;
  const offset = size * 0.19; // distance from center

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

  // ── Dark mode ────────────────────────────────────────────────────────────
  const [dark, setDark] = useState<boolean>(() => {
    const stored = localStorage.getItem("eds-theme");
    if (stored) return stored === "dark";
    return true; // default: dark
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

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "var(--bg)" }}>
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <header className="header-gradient sticky top-0 z-40">
        <div className="max-w-[1440px] mx-auto px-6">
          {/* Top bar: logo + user */}
          <div className="flex items-center justify-between h-14">
            {/* Logo */}
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

            {/* Right side: dark mode toggle + user */}
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
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
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
      <main
        className="flex-1 max-w-[1440px] w-full mx-auto p-6"
      >
        <div className="animate-fade-in">
          {activeTab === "overview"   && <Overview />}
          {activeTab === "chat"       && <Chat />}
          {activeTab === "kpi"        && <KPIDashboard />}
          {activeTab === "risks"      && <RiskRegister />}
          {activeTab === "decisions"  && <DecisionRegister />}
          {activeTab === "actions"    && <ActionItems />}
          {activeTab === "documents"  && <DocumentLibrary />}
          {activeTab === "briefing"   && <Briefing />}
          {activeTab === "market"     && <MarketIntelligence />}
          {activeTab === "simulate"   && <ScenarioSimulator />}
          {activeTab === "audit"      && <AuditLog />}
          {activeTab === "about"      && <About />}
        </div>
      </main>
    </div>
  );
}
