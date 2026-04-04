import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  Leaf,
  Newspaper,
  BarChart2,
} from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface NewsArticle {
  title: string;
  source: string;
  date: string;
  url: string;
  sentiment: "positive" | "risk" | "neutral";
  tags: string[];
}

interface StockData {
  symbol: string;
  name: string;
  color: string;
  price: number;
  change: number;
  change_pct: number;
  week52_high: number;
  week52_low: number;
  market_cap_b: number | null;
  sparkline: number[];
}

interface CarbonTrend {
  period: string;
  price: number;
}

interface CarbonInstrument {
  name: string;
  full_name: string;
  price: number;
  unit: string;
  change_qoq: number;
  change_pct: number;
  context: string;
  trend: CarbonTrend[];
}

interface CarbonData {
  as_of: string;
  source: string;
  source_url: string;
  accu: CarbonInstrument;
  lgc: CarbonInstrument;
  strategic_notes: string[];
}

// ── Sentiment badge ───────────────────────────────────────────────────────────

function SentimentBadge({ sentiment }: { sentiment: string }) {
  const map: Record<string, { label: string; bg: string; color: string }> = {
    positive: { label: "Opportunity", bg: "rgba(34,197,94,0.12)", color: "#16a34a" },
    risk:     { label: "Risk",        bg: "rgba(239,68,68,0.12)",  color: "#dc2626" },
    neutral:  { label: "Monitor",     bg: "rgba(156,163,175,0.15)", color: "var(--text-3)" },
  };
  const s = map[sentiment] ?? map.neutral;
  return (
    <span
      className="inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded-full uppercase tracking-wide"
      style={{ background: s.bg, color: s.color }}
    >
      {s.label}
    </span>
  );
}

// ── Tag pill ──────────────────────────────────────────────────────────────────

function TagPill({ tag }: { tag: string }) {
  return (
    <span
      className="inline-block text-[10px] px-1.5 py-0.5 rounded"
      style={{ background: "var(--surface-2)", color: "var(--text-3)", border: "1px solid var(--border)" }}
    >
      {tag}
    </span>
  );
}

// ── Sparkline ─────────────────────────────────────────────────────────────────

function Sparkline({ data, color }: { data: number[]; color: string }) {
  const pts = data.map((v, i) => ({ i, v }));
  return (
    <ResponsiveContainer width="100%" height={40}>
      <LineChart data={pts} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
        <Line
          type="monotone"
          dataKey="v"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ── Carbon trend mini chart ───────────────────────────────────────────────────

function CarbonTrendChart({ trend, color }: { trend: CarbonTrend[]; color: string }) {
  const isDark = document.documentElement.classList.contains("dark");
  const tickColor = isDark ? "#9ca3af" : "#6b7280";
  return (
    <ResponsiveContainer width="100%" height={80}>
      <LineChart data={trend} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
        <XAxis
          dataKey="period"
          tick={{ fontSize: 9, fill: tickColor }}
          axisLine={false}
          tickLine={false}
          interval={1}
        />
        <YAxis hide domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{
            background: isDark ? "#1f2937" : "#fff",
            border: `1px solid ${isDark ? "#374151" : "#e5e7eb"}`,
            borderRadius: 6,
            fontSize: 11,
          }}
          formatter={(v: unknown) => [`$${Number(v).toFixed(2)}`, ""]}
        />
        <ReferenceLine y={trend[trend.length - 1]?.price} stroke={color} strokeDasharray="3 3" strokeOpacity={0.3} />
        <Line type="monotone" dataKey="price" stroke={color} strokeWidth={2} dot={{ r: 2, fill: color }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ── Section header ────────────────────────────────────────────────────────────

function SectionHeader({ icon, title, badge, badgeColor }: {
  icon: React.ReactNode;
  title: string;
  badge?: string;
  badgeColor?: string;
}) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <div
        className="w-7 h-7 rounded-lg flex items-center justify-center"
        style={{ background: "rgba(244,121,32,0.12)" }}
      >
        <span style={{ color: "var(--accent)" }}>{icon}</span>
      </div>
      <h2 className="text-[15px] font-semibold" style={{ color: "var(--text-1)" }}>
        {title}
      </h2>
      {badge && (
        <span
          className="text-[10px] font-semibold px-2 py-0.5 rounded-full ml-1"
          style={{ background: badgeColor ?? "var(--surface-2)", color: "var(--text-3)", border: "1px solid var(--border)" }}
        >
          {badge}
        </span>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function MarketIntelligence() {
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [newsDemo, setNewsDemo] = useState(false);
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [stocksDemo, setStocksDemo] = useState(false);
  const [carbon, setCarbon] = useState<CarbonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  async function fetchAll() {
    setLoading(true);
    try {
      const [newsRes, stocksRes, carbonRes] = await Promise.all([
        fetch("/api/market/news"),
        fetch("/api/market/stocks"),
        fetch("/api/market/carbon"),
      ]);
      const newsJson = await newsRes.json();
      const stocksJson = await stocksRes.json();
      const carbonJson = await carbonRes.json();

      setNews(newsJson.data ?? []);
      setNewsDemo(newsJson.demo ?? false);
      setStocks(stocksJson.data ?? []);
      setStocksDemo(stocksJson.demo ?? false);
      setCarbon(carbonJson.data ?? null);
      setLastRefresh(new Date());
    } catch (e) {
      console.error("[MarketIntelligence] fetch error", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAll();
  }, []);

  const posCount = news.filter((n) => n.sentiment === "positive").length;
  const riskCount = news.filter((n) => n.sentiment === "risk").length;

  return (
    <div className="space-y-6">
      {/* ── Page header ──────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: "var(--text-1)" }}>
            Market Intelligence
          </h1>
          <p className="text-[13px] mt-0.5" style={{ color: "var(--text-3)" }}>
            Competitor news, ASX peer stocks &amp; Australian carbon market
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[11px]" style={{ color: "var(--text-4)" }}>
            Refreshed {lastRefresh.toLocaleTimeString()}
          </span>
          <button
            onClick={fetchAll}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-colors"
            style={{
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
              color: "var(--text-2)",
            }}
          >
            <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
        </div>
      </div>

      {/* ── Summary stat row ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "News Articles", value: news.length, sub: "Last 7 days", color: "#3b82f6" },
          { label: "Risk Signals", value: riskCount, sub: "Competitor / regulatory", color: "#ef4444" },
          { label: "Opportunities", value: posCount, sub: "Positive developments", color: "#22c55e" },
          { label: "Peers Tracked", value: stocks.length, sub: "ASX-listed competitors", color: "#F47920" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="glass-card rounded-xl p-4"
          >
            <p className="text-[11px] font-medium mb-1" style={{ color: "var(--text-3)" }}>
              {stat.label}
            </p>
            <p className="text-2xl font-bold" style={{ color: stat.color }}>
              {loading ? "—" : stat.value}
            </p>
            <p className="text-[11px] mt-0.5" style={{ color: "var(--text-4)" }}>
              {stat.sub}
            </p>
          </div>
        ))}
      </div>

      {/* ── Two-column layout: News + Stocks/Carbon ───────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* ── News feed ──────────────────────────────────────────────────── */}
        <div className="glass-card rounded-xl p-5">
          <SectionHeader
            icon={<Newspaper size={15} />}
            title="Competitor & Regulatory News"
            badge={newsDemo ? "Demo" : "GDELT Live"}
            badgeColor={newsDemo ? "rgba(234,179,8,0.15)" : "rgba(34,197,94,0.15)"}
          />
          {loading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 rounded-lg animate-pulse" style={{ background: "var(--surface-2)" }} />
              ))}
            </div>
          ) : (
            <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
              {news.map((article, i) => (
                <div
                  key={i}
                  className="rounded-lg p-3 transition-colors"
                  style={{
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <a
                      href={article.url === "#" ? undefined : article.url}
                      target={article.url === "#" ? undefined : "_blank"}
                      rel="noreferrer"
                      className="text-[13px] font-medium leading-snug hover:underline"
                      style={{ color: "var(--text-1)" }}
                    >
                      {article.title}
                      {article.url !== "#" && (
                        <ExternalLink size={10} className="inline ml-1 opacity-50" />
                      )}
                    </a>
                    <SentimentBadge sentiment={article.sentiment} />
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[11px]" style={{ color: "var(--text-3)" }}>
                      {article.source}
                    </span>
                    <span className="text-[11px]" style={{ color: "var(--text-4)" }}>
                      {article.date}
                    </span>
                    {article.tags.map((t) => (
                      <TagPill key={t} tag={t} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Right column: Stocks + Carbon ──────────────────────────────── */}
        <div className="space-y-5">

          {/* ── ASX Peer Stocks ──────────────────────────────────────────── */}
          <div className="glass-card rounded-xl p-5">
            <SectionHeader
              icon={<BarChart2 size={15} />}
              title="ASX Peer Comparison"
              badge={stocksDemo ? "Demo" : "Yahoo Finance Live"}
              badgeColor={stocksDemo ? "rgba(234,179,8,0.15)" : "rgba(34,197,94,0.15)"}
            />
            {loading ? (
              <div className="space-y-3">
                {[...Array(2)].map((_, i) => (
                  <div key={i} className="h-20 rounded-lg animate-pulse" style={{ background: "var(--surface-2)" }} />
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {stocks.map((stock) => {
                  const up = stock.change_pct >= 0;
                  const TrendIcon = up ? TrendingUp : stock.change_pct === 0 ? Minus : TrendingDown;
                  const trendColor = up ? "#22c55e" : stock.change_pct === 0 ? "var(--text-3)" : "#ef4444";
                  const rangePos = stock.week52_low < stock.week52_high
                    ? ((stock.price - stock.week52_low) / (stock.week52_high - stock.week52_low)) * 100
                    : 50;

                  return (
                    <div
                      key={stock.symbol}
                      className="rounded-lg p-3"
                      style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
                    >
                      <div className="flex items-start gap-3">
                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-2 h-2 rounded-full flex-shrink-0"
                              style={{ background: stock.color }}
                            />
                            <span className="text-[13px] font-semibold" style={{ color: "var(--text-1)" }}>
                              {stock.name}
                            </span>
                            <span className="text-[11px]" style={{ color: "var(--text-4)" }}>
                              {stock.symbol}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 mt-1">
                            <span className="text-xl font-bold" style={{ color: "var(--text-1)" }}>
                              ${stock.price.toFixed(2)}
                            </span>
                            <span
                              className="flex items-center gap-1 text-[12px] font-medium"
                              style={{ color: trendColor }}
                            >
                              <TrendIcon size={12} />
                              {up ? "+" : ""}
                              {stock.change_pct.toFixed(2)}%
                            </span>
                          </div>
                          {/* 52-week range bar */}
                          <div className="mt-2">
                            <div className="flex justify-between text-[10px] mb-1" style={{ color: "var(--text-4)" }}>
                              <span>52wk L: ${stock.week52_low.toFixed(2)}</span>
                              <span>52wk H: ${stock.week52_high.toFixed(2)}</span>
                            </div>
                            <div
                              className="h-1 rounded-full relative"
                              style={{ background: "var(--border-strong)" }}
                            >
                              <div
                                className="absolute top-0 h-full w-1.5 rounded-full -translate-x-1/2"
                                style={{
                                  left: `${Math.max(2, Math.min(98, rangePos))}%`,
                                  background: stock.color,
                                }}
                              />
                            </div>
                          </div>
                        </div>
                        {/* Sparkline */}
                        <div className="w-28 flex-shrink-0">
                          <Sparkline data={stock.sparkline} color={stock.color} />
                          <p className="text-[9px] text-center mt-0.5" style={{ color: "var(--text-4)" }}>
                            8-week trend
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* ── Carbon Market ──────────────────────────────────────────────── */}
          {carbon && (
            <div className="glass-card rounded-xl p-5">
              <SectionHeader
                icon={<Leaf size={15} />}
                title="Australian Carbon Market"
                badge={carbon.as_of}
              />

              <div className="grid grid-cols-2 gap-3 mb-4">
                {[carbon.accu, carbon.lgc].map((inst) => {
                  const up = inst.change_qoq >= 0;
                  const trendColor = up ? "#22c55e" : "#ef4444";
                  const TrendIcon = up ? TrendingUp : TrendingDown;
                  const chartColor = inst.name === "ACCU" ? "#F47920" : "#3b82f6";

                  return (
                    <div
                      key={inst.name}
                      className="rounded-lg p-3"
                      style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] font-semibold" style={{ color: "var(--text-3)" }}>
                          {inst.name}
                        </span>
                        <span
                          className="flex items-center gap-0.5 text-[10px] font-medium"
                          style={{ color: trendColor }}
                        >
                          <TrendIcon size={10} />
                          {up ? "+" : ""}{inst.change_pct.toFixed(1)}% QoQ
                        </span>
                      </div>
                      <p className="text-xl font-bold mb-0.5" style={{ color: "var(--text-1)" }}>
                        ${inst.price.toFixed(2)}
                      </p>
                      <p className="text-[10px] mb-2" style={{ color: "var(--text-4)" }}>
                        {inst.unit}
                      </p>
                      <CarbonTrendChart trend={inst.trend} color={chartColor} />
                      <p className="text-[10px] mt-1 leading-snug" style={{ color: "var(--text-3)" }}>
                        {inst.context}
                      </p>
                    </div>
                  );
                })}
              </div>

              {/* Strategic notes */}
              <div
                className="rounded-lg p-3 space-y-2"
                style={{ background: "rgba(244,121,32,0.06)", border: "1px solid rgba(244,121,32,0.2)" }}
              >
                <p className="text-[11px] font-semibold flex items-center gap-1.5" style={{ color: "var(--accent)" }}>
                  <AlertTriangle size={12} />
                  Strategic Implications
                </p>
                {carbon.strategic_notes.map((note, i) => (
                  <p key={i} className="text-[11px] leading-relaxed" style={{ color: "var(--text-2)" }}>
                    • {note}
                  </p>
                ))}
              </div>

              <a
                href={carbon.source_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-[10px] mt-2 hover:underline"
                style={{ color: "var(--text-4)" }}
              >
                <ExternalLink size={10} />
                Source: {carbon.source}
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
