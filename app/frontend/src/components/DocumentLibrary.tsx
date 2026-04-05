import { useState, useEffect, useRef } from "react";
import {
  FileText,
  FileSpreadsheet,
  Presentation,
  File,
  Search,
  Filter,
  Lock,
  Eye,
  X,
  ChevronDown,
  Database,
  Upload,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

interface Document {
  doc_id: string;
  title: string;
  doc_type: string;
  classification: string;
  access_tier_level: number;
  business_area: string;
  effective_date: string;
  author: string;
  format: string;
}

const CLASSIFICATION_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  RESTRICTED:   { bg: "bg-red-500/15",    text: "text-red-400",    border: "border-red-500/30" },
  CONFIDENTIAL: { bg: "bg-amber-500/15",  text: "text-amber-400",  border: "border-amber-500/30" },
  INTERNAL:     { bg: "bg-blue-500/15",   text: "text-blue-400",   border: "border-blue-500/30" },
  PUBLIC:       { bg: "bg-green-500/15",  text: "text-green-400",  border: "border-green-500/30" },
};

const TIER_LABELS: Record<number, string> = {
  1: "Board / C-Suite",
  2: "ELT",
  3: "Senior Mgmt",
  4: "All Staff",
};

const DOC_TYPE_LABELS: Record<string, string> = {
  board_paper:      "Board Paper",
  strategy:         "Strategy",
  financial_report: "Financial Report",
  risk_register:    "Risk Register",
  regulatory:       "Regulatory",
  competitive_intel:"Competitive Intel",
};

const FORMAT_ICONS: Record<string, React.ReactNode> = {
  pdf:  <File size={18} className="text-red-400" />,
  pptx: <Presentation size={18} className="text-orange-400" />,
  xlsx: <FileSpreadsheet size={18} className="text-green-400" />,
  txt:  <FileText size={18} className="text-slate-400" />,
};

const FORMAT_LABELS: Record<string, string> = {
  pdf:  "PDF",
  pptx: "PowerPoint",
  xlsx: "Excel",
  txt:  "Text",
};

const ALL_FILTERS = {
  classification: ["RESTRICTED", "CONFIDENTIAL", "INTERNAL", "PUBLIC"],
  tier: [1, 2, 3, 4],
  format: ["pdf", "pptx", "xlsx", "txt"],
  doc_type: ["board_paper", "strategy", "financial_report", "risk_register", "regulatory", "competitive_intel"],
};

function classifyIcon(c: string) {
  const cls = CLASSIFICATION_COLORS[c] || CLASSIFICATION_COLORS["INTERNAL"];
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${cls.bg} ${cls.text} ${cls.border} uppercase tracking-wider`}>
      <Lock size={9} />
      {c}
    </span>
  );
}

function tierBadge(tier: number) {
  const colors = ["", "text-red-300 bg-red-500/10 border-red-500/20", "text-amber-300 bg-amber-500/10 border-amber-500/20", "text-blue-300 bg-blue-500/10 border-blue-500/20", "text-slate-300 bg-slate-500/10 border-slate-500/20"];
  return (
    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${colors[tier] || colors[4]}`}>
      Tier {tier} · {TIER_LABELS[tier] || "Staff"}
    </span>
  );
}

function DocModal({ doc, onClose }: { doc: Document; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="glass-card w-full max-w-xl mx-4 p-6 relative animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-200 cursor-pointer"
        >
          <X size={18} />
        </button>

        <div className="flex items-start gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-dark-bg border border-dark-border flex items-center justify-center flex-shrink-0">
            {FORMAT_ICONS[doc.format] || FORMAT_ICONS["txt"]}
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100 leading-snug">{doc.title}</h3>
            <p className="text-xs text-slate-400 mt-0.5">{doc.doc_id}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-5">
          {classifyIcon(doc.classification)}
          {tierBadge(doc.access_tier_level)}
          <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-dark-bg border border-dark-border text-slate-400 uppercase">
            {FORMAT_LABELS[doc.format] || doc.format}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          {[
            ["Document Type", DOC_TYPE_LABELS[doc.doc_type] || doc.doc_type],
            ["Business Area", doc.business_area],
            ["Author / Committee", doc.author],
            ["Effective Date", doc.effective_date],
          ].map(([label, val]) => (
            <div key={label} className="bg-dark-bg/60 rounded-lg p-3">
              <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-1">{label}</p>
              <p className="text-slate-200 font-medium text-xs">{val || "—"}</p>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 rounded-lg bg-gold/5 border border-gold/15">
          <p className="text-xs text-slate-400">
            This document is available via{" "}
            <span className="text-gold font-medium">Strategic Chat</span> — ask a question
            to retrieve content from this document.
          </p>
        </div>
      </div>
    </div>
  );
}

type UploadStatus = "idle" | "uploading" | "success" | "error";

export default function DocumentLibrary() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [demo, setDemo] = useState(false);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterClassification, setFilterClassification] = useState<string | null>(null);
  const [filterTier, setFilterTier] = useState<number | null>(null);
  const [filterFormat, setFilterFormat] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string | null>(null);
  const [selected, setSelected] = useState<Document | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [uploadMsg, setUploadMsg] = useState("");
  const [uploadRunId, setUploadRunId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function fetchDocuments() {
    fetch("/api/documents")
      .then((r) => r.json())
      .then((d) => {
        setDocuments(d.data || []);
        setDemo(d.demo);
      })
      .catch(() => {});
  }

  // Poll ingestion job status
  useEffect(() => {
    if (!uploadRunId) return;
    const interval = setInterval(async () => {
      try {
        const r = await fetch(`/api/documents/upload/status?run_id=${uploadRunId}`);
        const d = await r.json();
        setUploadMsg(d.message || "Processing…");
        if (d.state === "success") {
          setUploadStatus("success");
          setUploadRunId(null);
          // Refresh document list and notify Overview to update its tiles
          fetchDocuments();
          window.dispatchEvent(new CustomEvent("eds:docs-updated"));
          // Trigger VS index sync so new document is immediately searchable
          fetch("/api/vector-search/sync", { method: "POST" }).catch(() => {});
          setTimeout(() => setUploadStatus("idle"), 10000);
        } else if (d.state === "error") {
          setUploadStatus("error");
          setUploadRunId(null);
        }
      } catch { /* ignore polling errors */ }
    }, 5000);
    return () => clearInterval(interval);
  }, [uploadRunId]);

  async function handleUpload(file: File) {
    setUploadStatus("uploading");
    setUploadMsg(`Uploading "${file.name}"…`);
    setUploadRunId(null);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("tier", "4");
      form.append("classification", "INTERNAL");
      const r = await fetch("/api/documents/upload", { method: "POST", body: form });
      const data = await r.json();
      if (!r.ok || data.error) {
        setUploadStatus("error");
        setUploadMsg(data.error || "Upload failed.");
      } else if (data.run_id) {
        // Start polling job status
        setUploadRunId(data.run_id);
        setUploadMsg("File uploaded — ingestion job running…");
      } else {
        setUploadStatus("success");
        setUploadMsg(data.message || `"${file.name}" uploaded. Available for querying in ~2 min.`);
        setTimeout(() => setUploadStatus("idle"), 8000);
      }
    } catch {
      setUploadStatus("error");
      setUploadMsg("Network error — upload failed.");
    }
  }

  useEffect(() => {
    fetch("/api/documents")
      .then((r) => r.json())
      .then((d) => {
        setDocuments(d.data || []);
        setDemo(d.demo);
      })
      .catch(() => setDocuments([]))
      .finally(() => setLoading(false));
  }, []);  // initial load only — subsequent refreshes use fetchDocuments()

  const filtered = documents.filter((d) => {
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      d.title.toLowerCase().includes(q) ||
      d.doc_id.toLowerCase().includes(q) ||
      d.business_area.toLowerCase().includes(q) ||
      d.author.toLowerCase().includes(q);
    return (
      matchSearch &&
      (!filterClassification || d.classification === filterClassification) &&
      (!filterTier || d.access_tier_level === filterTier) &&
      (!filterFormat || d.format === filterFormat) &&
      (!filterType || d.doc_type === filterType)
    );
  });

  // Stats
  const stats = {
    total: documents.length,
    restricted: documents.filter((d) => d.classification === "RESTRICTED").length,
    confidential: documents.filter((d) => d.classification === "CONFIDENTIAL").length,
    formats: {
      pdf: documents.filter((d) => d.format === "pdf").length,
      pptx: documents.filter((d) => d.format === "pptx").length,
      xlsx: documents.filter((d) => d.format === "xlsx").length,
      txt: documents.filter((d) => d.format === "txt").length,
    },
  };

  const clearFilters = () => {
    setFilterClassification(null);
    setFilterTier(null);
    setFilterFormat(null);
    setFilterType(null);
    setSearch("");
  };

  const hasFilters = filterClassification || filterTier || filterFormat || filterType || search;

  return (
    <div className="space-y-5">
      {selected && <DocModal doc={selected} onClose={() => setSelected(null)} />}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".pdf,.pptx,.xlsx,.txt,.docx,.csv"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handleUpload(f);
          e.target.value = "";
        }}
      />

      {/* Upload toast */}
      {uploadStatus !== "idle" && (
        <div
          className={`flex items-center gap-3 px-4 py-3 rounded-lg border text-sm animate-slide-up
            ${uploadStatus === "uploading" ? "bg-blue-500/10 border-blue-500/30 text-blue-300" : ""}
            ${uploadStatus === "success"   ? "bg-green-500/10 border-green-500/30 text-green-300" : ""}
            ${uploadStatus === "error"     ? "bg-red-500/10 border-red-500/30 text-red-300" : ""}`}
        >
          {uploadStatus === "uploading" && <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />}
          {uploadStatus === "success"   && <CheckCircle size={16} />}
          {uploadStatus === "error"     && <AlertCircle size={16} />}
          <span className="flex-1">{uploadMsg}</span>
          <button onClick={() => setUploadStatus("idle")} className="text-current opacity-60 hover:opacity-100 cursor-pointer">
            <X size={14} />
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Document Library</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            {stats.total} documents across {Object.keys(stats.formats).length} formats
            {demo && (
              <span className="ml-2 text-[11px] px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20">
                Demo Data
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Database size={12} />
            <span>Unity Catalog Volume · {stats.total} docs ingested</span>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadStatus === "uploading"}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all cursor-pointer
              bg-gold/10 text-gold border-gold/30 hover:bg-gold/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Upload size={13} />
            Upload Document
          </button>
        </div>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Total Documents", value: stats.total, sub: "in Vector Search", color: "text-gold" },
          { label: "Restricted", value: stats.restricted, sub: "Board / C-Suite only", color: "text-red-400" },
          { label: "Confidential", value: stats.confidential, sub: "ELT access", color: "text-amber-400" },
          { label: "Rich Documents", value: stats.formats.pdf + stats.formats.pptx + stats.formats.xlsx, sub: "PDF · PPTX · XLSX", color: "text-blue-400" },
        ].map((s) => (
          <div key={s.label} className="glass-card p-4">
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs font-medium text-slate-300 mt-0.5">{s.label}</p>
            <p className="text-[11px] text-slate-500">{s.sub}</p>
          </div>
        ))}
      </div>

      {/* Search + Filters */}
      <div className="glass-card p-4">
        <div className="flex gap-3 items-center">
          <div className="flex-1 relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search by title, ID, author, area..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-dark-bg border border-dark-border rounded-lg pl-9 pr-4 py-2
                text-sm text-slate-200 placeholder-slate-500
                focus:outline-none focus:border-gold/40 focus:ring-1 focus:ring-gold/20"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm border transition-colors cursor-pointer
              ${showFilters ? "bg-gold/10 text-gold border-gold/30" : "border-dark-border text-slate-400 hover:text-slate-200 hover:border-slate-500"}`}
          >
            <Filter size={14} />
            Filters
            <ChevronDown size={12} className={`transition-transform ${showFilters ? "rotate-180" : ""}`} />
          </button>
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-red-400 border border-dark-border hover:border-red-500/30 transition-colors cursor-pointer"
            >
              <X size={14} />
              Clear
            </button>
          )}
        </div>

        {showFilters && (
          <div className="mt-3 pt-3 border-t border-dark-border grid grid-cols-4 gap-3">
            {/* Classification filter */}
            <div>
              <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-1.5">Classification</p>
              <div className="flex flex-col gap-1">
                {ALL_FILTERS.classification.map((c) => {
                  const cls = CLASSIFICATION_COLORS[c];
                  return (
                    <button
                      key={c}
                      onClick={() => setFilterClassification(filterClassification === c ? null : c)}
                      className={`text-left text-xs px-2 py-1 rounded-md border transition-all cursor-pointer
                        ${filterClassification === c ? `${cls.bg} ${cls.text} ${cls.border}` : "border-dark-border text-slate-400 hover:text-slate-200"}`}
                    >
                      {c}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tier filter */}
            <div>
              <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-1.5">Access Tier</p>
              <div className="flex flex-col gap-1">
                {ALL_FILTERS.tier.map((t) => (
                  <button
                    key={t}
                    onClick={() => setFilterTier(filterTier === t ? null : t)}
                    className={`text-left text-xs px-2 py-1 rounded-md border transition-all cursor-pointer
                      ${filterTier === t ? "bg-gold/10 text-gold border-gold/30" : "border-dark-border text-slate-400 hover:text-slate-200"}`}
                  >
                    Tier {t} · {TIER_LABELS[t]}
                  </button>
                ))}
              </div>
            </div>

            {/* Format filter */}
            <div>
              <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-1.5">Format</p>
              <div className="flex flex-col gap-1">
                {ALL_FILTERS.format.map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilterFormat(filterFormat === f ? null : f)}
                    className={`text-left text-xs px-2 py-1 rounded-md border transition-all cursor-pointer flex items-center gap-1.5
                      ${filterFormat === f ? "bg-gold/10 text-gold border-gold/30" : "border-dark-border text-slate-400 hover:text-slate-200"}`}
                  >
                    {FORMAT_ICONS[f]}
                    {FORMAT_LABELS[f]}
                  </button>
                ))}
              </div>
            </div>

            {/* Doc type filter */}
            <div>
              <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-1.5">Doc Type</p>
              <div className="flex flex-col gap-1">
                {ALL_FILTERS.doc_type.map((t) => (
                  <button
                    key={t}
                    onClick={() => setFilterType(filterType === t ? null : t)}
                    className={`text-left text-xs px-2 py-1 rounded-md border transition-all cursor-pointer
                      ${filterType === t ? "bg-gold/10 text-gold border-gold/30" : "border-dark-border text-slate-400 hover:text-slate-200"}`}
                  >
                    {DOC_TYPE_LABELS[t] || t}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results count */}
      {hasFilters && (
        <p className="text-sm text-slate-400">
          Showing <span className="text-gold font-medium">{filtered.length}</span> of {documents.length} documents
        </p>
      )}

      {/* Document grid */}
      {loading ? (
        <div className="grid grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card p-4 animate-pulse">
              <div className="h-4 bg-slate-700 rounded w-3/4 mb-3" />
              <div className="h-3 bg-slate-700 rounded w-1/2 mb-2" />
              <div className="h-3 bg-slate-700 rounded w-1/3" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <FileText size={32} className="text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No documents match your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {filtered.map((doc) => {
            const cls = CLASSIFICATION_COLORS[doc.classification] || CLASSIFICATION_COLORS["INTERNAL"];
            return (
              <div
                key={doc.doc_id}
                onClick={() => setSelected(doc)}
                className="glass-card p-4 cursor-pointer hover:border-gold/30 hover:bg-dark-card/80 transition-all duration-200 group"
              >
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className="w-9 h-9 rounded-lg bg-dark-bg border border-dark-border flex items-center justify-center flex-shrink-0 group-hover:border-gold/20 transition-colors">
                    {FORMAT_ICONS[doc.format] || FORMAT_ICONS["txt"]}
                  </div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${cls.bg} ${cls.text} ${cls.border} uppercase tracking-wider`}>
                    {doc.classification}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-slate-200 leading-snug mb-1 group-hover:text-gold transition-colors line-clamp-2">
                  {doc.title}
                </h3>
                <p className="text-[11px] text-slate-500 mb-3">{doc.doc_id} · {doc.business_area}</p>

                <div className="flex flex-wrap gap-1.5 mb-3">
                  {tierBadge(doc.access_tier_level)}
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-dark-bg border border-dark-border text-slate-500 uppercase">
                    {FORMAT_LABELS[doc.format] || doc.format}
                  </span>
                </div>

                <div className="pt-2.5 border-t border-dark-border/50 flex items-center justify-between">
                  <div>
                    <p className="text-[11px] text-slate-500">{DOC_TYPE_LABELS[doc.doc_type] || doc.doc_type}</p>
                    <p className="text-[10px] text-slate-600">{doc.effective_date}</p>
                  </div>
                  <Eye size={13} className="text-slate-600 group-hover:text-gold transition-colors" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
