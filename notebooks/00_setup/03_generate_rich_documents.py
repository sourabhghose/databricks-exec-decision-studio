# Databricks notebook source
# MAGIC %md
# MAGIC # Executive Decision Studio — Generate Rich Synthetic Documents
# MAGIC **Alinta Energy | Databricks Executive Decision Studio**
# MAGIC
# MAGIC Generates 7 rich synthetic documents (PDF, PPTX, XLSX) with actual embedded charts
# MAGIC and writes them directly to the Unity Catalog volume at:
# MAGIC
# MAGIC ```
# MAGIC /Volumes/ausnet_process_intel_catalog/eds_raw/documents/
# MAGIC   tier1/   ← DOC-019 (Board Strategy PPTX), DOC-021 (Budget XLSX)
# MAGIC   tier2/   ← DOC-016 (Financial PDF), DOC-020 (ELT Review PPTX), DOC-022 (Risk XLSX)
# MAGIC   tier3/   ← DOC-017 (Generation PDF), DOC-018 (Safety PDF)
# MAGIC ```
# MAGIC
# MAGIC **Document formats:**
# MAGIC - PDF: matplotlib PdfPages with embedded chart figures
# MAGIC - PPTX: python-pptx with native chart objects
# MAGIC - XLSX: openpyxl with BarChart / LineChart embedded in sheets
# MAGIC
# MAGIC After generation, metadata is inserted into `ausnet_process_intel_catalog.eds_synthetic.documents`.

# COMMAND ----------

# MAGIC %pip install reportlab python-pptx openpyxl matplotlib --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import os
import io
import uuid
import requests
from datetime import datetime, date

CATALOG = "ausnet_process_intel_catalog"
VOLUME_ROOT = f"/Volumes/{CATALOG}/eds_raw/documents"

spark.sql(f"USE CATALOG {CATALOG}")

def _api_token():
    return dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

def _workspace_host():
    return "https://" + spark.conf.get("spark.databricks.workspaceUrl")

def write_binary_to_volume(buf: io.BytesIO, volume_path: str):
    """Upload in-memory binary content to a UC Volume via the Databricks Files API."""
    host = _workspace_host()
    token = _api_token()
    # volume_path is like /Volumes/catalog/schema/vol/file.pdf
    url = f"{host}/api/2.0/fs/files{volume_path}"
    buf.seek(0)
    resp = requests.put(
        url,
        headers={"Authorization": f"Bearer {token}"},
        data=buf.read(),
    )
    resp.raise_for_status()
    size_kb = len(buf.getvalue()) / 1024
    print(f"[OK] {os.path.basename(volume_path)} ({size_kb:.1f} KB) → {volume_path}")

print("=" * 65)
print("EDS — Rich Document Generation")
print("=" * 65)
print(f"Target volume : {VOLUME_ROOT}")
print(f"Started       : {datetime.utcnow().isoformat()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Ensure tier directories exist

# COMMAND ----------

for tier in ["tier1", "tier2", "tier3", "tier4"]:
    path = f"{VOLUME_ROOT}/{tier}"
    dbutils.fs.mkdirs(path)
    print(f"[OK] {path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Generate PDFs with matplotlib embedded charts

# COMMAND ----------

import matplotlib
matplotlib.use("Agg")  # non-interactive backend required on cluster
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# ---------------------------------------------------------------------------
# Helper: styled text page
# ---------------------------------------------------------------------------

def add_text_page(pdf, title, classification, doc_id, paragraphs, subtitle=None):
    """Add a letterhead + body text page to a PdfPages object."""
    fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4
    ax.set_axis_off()

    # Background colour band at top
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 0.93), 1, 0.07,
        boxstyle="square,pad=0", transform=ax.transAxes,
        facecolor="#1B3A5C", edgecolor="none", clip_on=False
    ))
    # Classification banner at bottom
    banner_color = {
        "RESTRICTED": "#8B0000",
        "CONFIDENTIAL": "#C0392B",
        "INTERNAL": "#2471A3",
        "PUBLIC": "#1E8449",
    }.get(classification, "#555555")
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 0), 1, 0.025,
        boxstyle="square,pad=0", transform=ax.transAxes,
        facecolor=banner_color, edgecolor="none", clip_on=False
    ))

    # Company name
    ax.text(0.05, 0.965, "ALINTA ENERGY", transform=ax.transAxes,
            fontsize=14, fontweight="bold", color="white", va="center")
    ax.text(0.95, 0.965, f"{classification}  |  {doc_id}", transform=ax.transAxes,
            fontsize=8, color="#AECBE8", va="center", ha="right")

    # Document title
    ax.text(0.05, 0.885, title, transform=ax.transAxes,
            fontsize=16, fontweight="bold", color="#1B3A5C", va="top",
            wrap=True)
    y_cursor = 0.855
    if subtitle:
        ax.text(0.05, y_cursor, subtitle, transform=ax.transAxes,
                fontsize=11, color="#2E4057", va="top", style="italic")
        y_cursor -= 0.03

    # Divider line
    ax.axhline(y=y_cursor, xmin=0.05, xmax=0.95, color="#1B3A5C", linewidth=1.2)
    y_cursor -= 0.025

    # Body paragraphs
    for para in paragraphs:
        if para.startswith("##"):
            ax.text(0.05, y_cursor, para.lstrip("# "), transform=ax.transAxes,
                    fontsize=11, fontweight="bold", color="#1B3A5C", va="top")
            y_cursor -= 0.035
        elif para.startswith("-"):
            ax.text(0.07, y_cursor, para, transform=ax.transAxes,
                    fontsize=9, color="#2C3E50", va="top")
            y_cursor -= 0.028
        else:
            # wrap long paragraphs at ~110 chars
            import textwrap
            lines = textwrap.wrap(para, width=110)
            for line in lines:
                ax.text(0.05, y_cursor, line, transform=ax.transAxes,
                        fontsize=9, color="#2C3E50", va="top")
                y_cursor -= 0.026
            y_cursor -= 0.01
        if y_cursor < 0.06:
            break

    ax.text(0.5, 0.012, f"ALINTA ENERGY  |  {classification}  |  {doc_id}  |  GENERATED {datetime.utcnow().strftime('%B %Y')}",
            transform=ax.transAxes, fontsize=7, color="white", ha="center", va="center")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def add_chart_page(pdf, fig):
    """Save a pre-built matplotlib figure into the PDF."""
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# DOC-016  FY2025 Financial Performance Dashboard  (CONFIDENTIAL, Tier 2)
# ---------------------------------------------------------------------------

doc_016_vol = f"{VOLUME_ROOT}/tier2/DOC-016.pdf"
doc_016_buf = io.BytesIO()

quarters = ["1Q FY24", "2Q FY24", "3Q FY24", "4Q FY24", "1Q FY25", "2Q FY25"]
revenue   = [740, 768, 802, 820, 842, 850]   # $M
ebitda    = [132, 140, 148, 155, 148, 150]

# EBITDA by BU (1H FY25)
bus   = ["Retail", "Generation", "Trading", "Corporate"]
ebitda_bu = [94, 168, 52, -16]

# CapEx waterfall (cumulative)
capex_cats   = ["Opening", "LYB Refurb", "Yandin O&M", "Grid Conn", "IT & Systems", "Closing"]
capex_vals   = [0, 78, 34, 22, 18, 0]   # $M incremental
capex_cumul  = [0, 78, 112, 134, 152, 152]

with PdfPages(doc_016_buf) as pdf:
    # Cover page
    add_text_page(pdf,
        title="FY2025 Financial Performance Dashboard",
        classification="CONFIDENTIAL",
        doc_id="DOC-016",
        subtitle="Half-Year to 31 December 2024",
        paragraphs=[
            "## Executive Summary",
            "Alinta Energy delivered group revenue of $1,692M in 1H FY25, an increase of 6.2% on "
            "the prior corresponding period. EBITDA of $298M was in line with internal guidance "
            "and reflects the phased recovery of wholesale electricity costs in the retail segment.",
            "## Key Financials — 1H FY25",
            "- Revenue: $1,692M (vs $1,594M 1H FY24)",
            "- EBITDA: $298M (vs $275M 1H FY24, +8.4%)",
            "- NPAT: $87M (vs $66M 1H FY24)",
            "- Net Debt: $1.24B (leverage: 2.1x EBITDA)",
            "## Business Unit Revenue (1H FY25)",
            "- Retail:     $892M  — residential and SME customers across SA, WA, VIC",
            "- Generation: $1,247M (annualised) — Loy Yang B, Yandin, Pinjarra, Newman",
            "- Trading:    $445M (annualised) — wholesale electricity and gas",
            "- Corporate:  ($84M) cost centre, includes group insurance and shared services",
            "## FY25 Full-Year Guidance",
            "Management reaffirms full-year EBITDA guidance of $590–620M, underpinned by "
            "higher contract cover on the Generation portfolio and continued retail margin "
            "discipline. CapEx guidance maintained at $152M, weighted to H2.",
        ]
    )

    # Chart 1 — Revenue trend (line)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(quarters, revenue, marker="o", color="#1B3A5C", linewidth=2.5, markersize=8, label="Revenue ($M)")
    ax2 = ax.twinx()
    ax2.bar(quarters, ebitda, alpha=0.35, color="#F39C12", label="EBITDA ($M)")
    ax.set_title("Revenue & EBITDA Trend — Quarterly", fontsize=14, fontweight="bold", color="#1B3A5C")
    ax.set_ylabel("Revenue ($M)", color="#1B3A5C")
    ax2.set_ylabel("EBITDA ($M)", color="#F39C12")
    ax.set_ylim(680, 900)
    ax2.set_ylim(0, 220)
    ax.tick_params(axis="y", labelcolor="#1B3A5C")
    ax2.tick_params(axis="y", labelcolor="#F39C12")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    add_chart_page(pdf, fig)

    # Chart 2 — EBITDA by BU (bar)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#1B3A5C" if v >= 0 else "#C0392B" for v in ebitda_bu]
    bars = ax.bar(bus, ebitda_bu, color=colors, width=0.55, edgecolor="white")
    ax.axhline(0, color="#555", linewidth=0.8)
    for bar, v in zip(bars, ebitda_bu):
        ax.text(bar.get_x() + bar.get_width() / 2, v + (4 if v >= 0 else -8),
                f"${v}M", ha="center", va="bottom", fontsize=10, fontweight="bold", color="#1B3A5C")
    ax.set_title("EBITDA by Business Unit — 1H FY25", fontsize=14, fontweight="bold", color="#1B3A5C")
    ax.set_ylabel("EBITDA ($M)")
    ax.set_ylim(-40, 220)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    add_chart_page(pdf, fig)

    # Chart 3 — CapEx waterfall (bar approximation)
    fig, ax = plt.subplots(figsize=(10, 5))
    bottoms = [0, 0, 78, 112, 134, 0]
    bar_colors = ["#1B3A5C", "#27AE60", "#27AE60", "#27AE60", "#27AE60", "#2E86AB"]
    bar_heights = [0, 78, 34, 22, 18, 152]
    bars = ax.bar(capex_cats, bar_heights, bottom=bottoms, color=bar_colors, width=0.5, edgecolor="white")
    for bar, bot, h in zip(bars, bottoms, bar_heights):
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bot + h + 2,
                    f"${h}M", ha="center", fontsize=9, fontweight="bold", color="#1B3A5C")
    ax.set_title("CapEx Bridge FY25 — $M", fontsize=14, fontweight="bold", color="#1B3A5C")
    ax.set_ylabel("Cumulative CapEx ($M)")
    ax.set_ylim(0, 200)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    add_chart_page(pdf, fig)

write_binary_to_volume(doc_016_buf, doc_016_vol)

# ---------------------------------------------------------------------------
# DOC-017  Generation Asset Performance Report Q3 FY25  (INTERNAL, Tier 3)
# ---------------------------------------------------------------------------

doc_017_vol = f"{VOLUME_ROOT}/tier3/DOC-017.pdf"
doc_017_buf = io.BytesIO()

assets_names = ["Loy Yang B\n(1,000 MW)", "Yandin Wind\n(132 MW)", "Pinjarra Gas\n(180 MW)", "Newman Gas\n(60 MW)"]
capacity_factors = [88.4, 43.1, 72.6, 61.8]   # %
months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
lyb_output    = [588, 612, 598, 605, 620, 608]   # GWh
yandin_output = [38, 42, 35, 47, 51, 44]          # GWh
availability_actual = [88.4, 43.1, 72.6, 61.8]
availability_target = [90.0, 45.0, 85.0, 70.0]

with PdfPages(doc_017_buf) as pdf:
    add_text_page(pdf,
        title="Generation Asset Performance Report",
        classification="INTERNAL",
        doc_id="DOC-017",
        subtitle="Quarter 3 FY2025 — October to December 2024",
        paragraphs=[
            "## Portfolio Summary",
            "Alinta Energy's generation portfolio delivered 4,210 GWh of output in Q3 FY25, "
            "a 2.1% increase on Q2 FY25 driven by higher Loy Yang B availability following "
            "completion of the Unit 1 rotor inspection in October.",
            "## Loy Yang B Power Station (1,000 MW, VIC)",
            "- Output: 3,631 GWh Q3 FY25 (+3.2% on Q2)",
            "- Availability: 88.4% (target: 90.0%)",
            "- Forced Outage Rate: 1.8% (below 2.5% target)",
            "- Water consumption: 14.2 GL, within licence limits",
            "- Carbon intensity: 1.31 t CO2e/MWh (brown coal)",
            "## Yandin Wind Farm (132 MW, WA)",
            "- Output: 280 GWh Q3 FY25",
            "- Capacity factor: 43.1% (target: 45%); below target due to low wind in Oct",
            "- Availability: 97.2% (turbine fleet — above target of 96%)",
            "## Pinjarra Gas Turbine (180 MW, WA)",
            "- Output: 236 GWh Q3 FY25",
            "- Availability: 72.6% — planned maintenance outage Unit 2 completed November",
            "- Heat rate: 9.42 GJ/MWh (target 9.10 GJ/MWh; investigating)",
            "## Newman Gas Station (60 MW, WA)",
            "- Output: 63 GWh Q3 FY25",
            "- Availability: 61.8% — unplanned trip event Unit 3 under investigation",
            "- RCFAs issued for two compressor trips; corrective actions in progress",
        ]
    )

    # Chart 1 — Capacity factor by asset (horizontal bar)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_cf = ["#C0392B" if cf < t else "#27AE60"
                 for cf, t in zip(capacity_factors, availability_target)]
    bars = ax.barh(assets_names, capacity_factors, color=colors_cf, height=0.45, edgecolor="white")
    ax.barh(assets_names, availability_target, color="none", height=0.45,
            edgecolor="#1B3A5C", linewidth=1.5, linestyle="--", label="Target")
    for bar, cf in zip(bars, capacity_factors):
        ax.text(cf + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{cf}%", va="center", fontsize=10, fontweight="bold")
    ax.set_title("Availability / Capacity Factor by Asset — Q3 FY25", fontsize=13, fontweight="bold", color="#1B3A5C")
    ax.set_xlabel("Availability / Capacity Factor (%)")
    ax.set_xlim(0, 105)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    green_patch = mpatches.Patch(color="#27AE60", label="At/above target")
    red_patch   = mpatches.Patch(color="#C0392B", label="Below target")
    ax.legend(handles=[green_patch, red_patch], loc="lower right", fontsize=9)
    fig.tight_layout()
    add_chart_page(pdf, fig)

    # Chart 2 — Monthly output (area)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(months, lyb_output, alpha=0.75, color="#1B3A5C", label="Loy Yang B (GWh)")
    ax.plot(months, lyb_output, color="#1B3A5C", linewidth=2, marker="o")
    ax2 = ax.twinx()
    ax2.fill_between(months, yandin_output, alpha=0.55, color="#27AE60", label="Yandin Wind (GWh)")
    ax2.plot(months, yandin_output, color="#27AE60", linewidth=2, marker="s")
    ax.set_title("Monthly Generation Output — Loy Yang B & Yandin", fontsize=13, fontweight="bold", color="#1B3A5C")
    ax.set_ylabel("Loy Yang B (GWh)", color="#1B3A5C")
    ax2.set_ylabel("Yandin Wind (GWh)", color="#27AE60")
    ax.tick_params(axis="y", labelcolor="#1B3A5C")
    ax2.tick_params(axis="y", labelcolor="#27AE60")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    add_chart_page(pdf, fig)

    # Chart 3 — Availability vs target (grouped bar)
    x = np.arange(len(assets_names))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    bars1 = ax.bar(x - width / 2, availability_actual, width, label="Actual", color="#1B3A5C")
    bars2 = ax.bar(x + width / 2, availability_target, width, label="Target", color="#AEB6BF", edgecolor="#1B3A5C", linewidth=0.8)
    for bar, v in zip(bars1, availability_actual):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.5, f"{v}%", ha="center", fontsize=9, fontweight="bold")
    for bar, v in zip(bars2, availability_target):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.5, f"{v}%", ha="center", fontsize=9, color="#555")
    ax.set_xticks(x)
    ax.set_xticklabels(assets_names, fontsize=9)
    ax.set_ylabel("Availability / Capacity Factor (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Availability vs Target — Q3 FY25", fontsize=13, fontweight="bold", color="#1B3A5C")
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    add_chart_page(pdf, fig)

write_binary_to_volume(doc_017_buf, doc_017_vol)

# ---------------------------------------------------------------------------
# DOC-018  Safety & Sustainability Report FY2024  (INTERNAL, Tier 3)
# ---------------------------------------------------------------------------

doc_018_vol = f"{VOLUME_ROOT}/tier3/DOC-018.pdf"
doc_018_buf = io.BytesIO()

fy_labels  = ["FY21", "FY22", "FY23", "FY24"]
trifr_vals = [7.1, 6.3, 5.8, 4.2]
trifr_tgt  = [6.0, 5.5, 5.0, 3.5]

scope1_vals = [9.8, 9.3, 8.9, 8.4]   # Mt CO2e
scope2_vals = [0.6, 0.55, 0.52, 0.48]
scope_tgt   = [9.5, 9.0, 8.5, 8.0]   # not FY27 target but year-by-year trajectory

renewable_pct = [5, 6, 7, 8]
renewable_other = [95, 94, 93, 92]

with PdfPages(doc_018_buf) as pdf:
    add_text_page(pdf,
        title="Safety & Sustainability Report FY2024",
        classification="INTERNAL",
        doc_id="DOC-018",
        subtitle="Annual Report — Year ended 30 June 2024",
        paragraphs=[
            "## Safety Performance",
            "Alinta Energy's Total Recordable Injury Frequency Rate (TRIFR) of 4.2 at 30 June 2024 "
            "represents a 27% improvement on FY23 (5.8) and continues a four-year trend of improvement. "
            "Despite this progress, the FY24 target of 3.5 was not achieved. Two Lost Time Injuries "
            "were recorded during the year — one at Loy Yang B involving a contractor, one in the "
            "Retail field operations team.",
            "- TRIFR: 4.2 (FY24 target 3.5; FY25 target 3.0)",
            "- LTIs: 2 (FY23: 3)",
            "- Near misses reported: 218 (FY23: 187) — increased reporting culture positive",
            "- High-potential incidents: 4 (FY23: 7)",
            "## Scope 1 & 2 Emissions",
            "Scope 1 emissions reduced to 8.4 Mt CO2e in FY24 (FY23: 8.9 Mt), primarily from "
            "lower Loy Yang B dispatch volume (3% reduction) and fuel efficiency improvements. "
            "The FY27 target of 6.0 Mt CO2e requires an additional 2.4 Mt reduction over three years.",
            "- Scope 1: 8.4 Mt CO2e (FY27 target: 6.0 Mt)",
            "- Scope 2: 0.48 Mt CO2e (market-based)",
            "- Carbon intensity: 1.31 t CO2e/MWh at Loy Yang B",
            "- Offset credits purchased: 0.2 Mt (voluntary, Gold Standard certified)",
            "## Renewable Energy",
            "Renewables represented 8% of total generation in FY24, up from 7% in FY23. "
            "The FY28 target of 25% requires approximately 1,200 GWh of additional renewable "
            "capacity. Feasibility studies underway for a 400 MW wind development in WA.",
            "- Renewable % of generation: 8% (FY28 target: 25%)",
            "- Yandin Wind Farm: 1,010 GWh generated FY24",
            "- Rooftop solar facilitated (retail customers): 380 MW aggregated",
        ]
    )

    # Chart 1 — TRIFR trend with target line
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(fy_labels, trifr_vals, marker="o", color="#C0392B", linewidth=2.5,
            markersize=9, label="TRIFR (Actual)", zorder=5)
    ax.plot(fy_labels, trifr_tgt, marker="s", color="#27AE60", linewidth=2,
            linestyle="--", markersize=7, label="TRIFR (Target)")
    for x_val, y_val in zip(fy_labels, trifr_vals):
        ax.annotate(f"{y_val}", (x_val, y_val), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=11, fontweight="bold", color="#C0392B")
    ax.fill_between(fy_labels, trifr_vals, trifr_tgt,
                    where=[a > t for a, t in zip(trifr_vals, trifr_tgt)],
                    alpha=0.12, color="#C0392B", label="Gap to target")
    ax.set_title("TRIFR Trend vs Target (FY21–FY24)", fontsize=13, fontweight="bold", color="#1B3A5C")
    ax.set_ylabel("TRIFR (per million hours worked)")
    ax.set_ylim(0, 9)
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    add_chart_page(pdf, fig)

    # Chart 2 — Scope 1+2 emissions (stacked bar)
    x_idx = np.arange(len(fy_labels))
    fig, ax = plt.subplots(figsize=(10, 5))
    bars1 = ax.bar(x_idx, scope1_vals, label="Scope 1 (Mt CO2e)", color="#E67E22", width=0.5)
    bars2 = ax.bar(x_idx, scope2_vals, bottom=scope1_vals, label="Scope 2 (Mt CO2e)",
                   color="#F0B27A", width=0.5)
    ax.plot(x_idx, [s1 + s2 for s1, s2 in zip(scope1_vals, scope2_vals)],
            color="#1B3A5C", marker="o", linewidth=1.5, linestyle=":", label="Total GHG")
    ax.set_xticks(x_idx)
    ax.set_xticklabels(fy_labels)
    ax.set_ylabel("Emissions (Mt CO2e)")
    ax.set_title("Scope 1 + Scope 2 Emissions (FY21–FY24)", fontsize=13, fontweight="bold", color="#1B3A5C")
    ax.set_ylim(0, 12)
    ax.axhline(6.0, color="#C0392B", linewidth=1.8, linestyle="--", label="FY27 Target (6.0 Mt)")
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, v in zip(bars1, scope1_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v / 2,
                f"{v}", ha="center", va="center", fontsize=9, color="white", fontweight="bold")
    fig.tight_layout()
    add_chart_page(pdf, fig)

    # Chart 3 — Renewable % pie (FY24)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].pie([8, 92], labels=["Renewables", "Thermal/Gas"],
                colors=["#27AE60", "#AEB6BF"], autopct="%1.0f%%",
                startangle=90, textprops={"fontsize": 12})
    axes[0].set_title("Generation Mix FY24", fontsize=12, fontweight="bold", color="#1B3A5C")
    axes[1].pie([25, 75], labels=["Renewables (target)", "Other"],
                colors=["#27AE60", "#AEB6BF"], autopct="%1.0f%%",
                startangle=90, textprops={"fontsize": 12})
    axes[1].set_title("Target Mix FY28", fontsize=12, fontweight="bold", color="#1B3A5C")
    fig.suptitle("Renewable Energy — Actual vs FY28 Target", fontsize=13,
                 fontweight="bold", color="#1B3A5C")
    fig.tight_layout()
    add_chart_page(pdf, fig)

write_binary_to_volume(doc_018_buf, doc_018_vol)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Generate PPTX presentations with native chart objects

# COMMAND ----------

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.chart.data import ChartData, CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


def set_slide_background(slide, hex_color="FFFFFF"):
    """Set solid background fill for a slide."""
    from pptx.util import Emu
    from pptx.dml.color import RGBColor
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(hex_color)


def add_title_slide(prs, title, subtitle, classification, doc_id):
    """Add a formatted title slide."""
    slide_layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(slide_layout)
    set_slide_background(slide, "1B3A5C")

    # Title box
    txBox = slide.shapes.add_textbox(Inches(0.6), Inches(2.5), Inches(8.8), Inches(1.4))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(34)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Subtitle
    sub_box = slide.shapes.add_textbox(Inches(0.6), Inches(4.0), Inches(8.8), Inches(0.8))
    tf2 = sub_box.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = subtitle
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(0xAE, 0xCB, 0xE8)

    # Classification
    cl_box = slide.shapes.add_textbox(Inches(0.6), Inches(5.1), Inches(8.8), Inches(0.4))
    tf3 = cl_box.text_frame
    p3 = tf3.paragraphs[0]
    p3.text = f"{classification}  |  {doc_id}  |  Alinta Energy"
    p3.font.size = Pt(11)
    p3.font.color.rgb = RGBColor(0xAE, 0xB6, 0xBF)

    return slide


def add_content_slide(prs, title, bullet_points, classification):
    """Add a text content slide with bullets."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, "FFFFFF")

    # Title bar
    bar = slide.shapes.add_textbox(Inches(0), Inches(0), Inches(10), Inches(0.75))
    bar.fill.solid()
    bar.fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x5C)
    tf = bar.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p.alignment = PP_ALIGN.LEFT

    # Bullets
    body = slide.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(9.0), Inches(5.5))
    tf2 = body.text_frame
    tf2.word_wrap = True
    for i, bullet in enumerate(bullet_points):
        para = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        para.text = bullet
        para.level = 1 if bullet.startswith("  ") else 0
        para.font.size = Pt(13)
        para.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

    # Footer classification
    ft = slide.shapes.add_textbox(Inches(0), Inches(6.8), Inches(10), Inches(0.3))
    ft.fill.solid()
    ft.fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x5C)
    tf_ft = ft.text_frame
    p_ft = tf_ft.paragraphs[0]
    p_ft.text = f"ALINTA ENERGY  |  {classification}  |  CONFIDENTIAL — NOT FOR DISTRIBUTION"
    p_ft.font.size = Pt(8)
    p_ft.font.color.rgb = RGBColor(0xAE, 0xCB, 0xE8)
    p_ft.alignment = PP_ALIGN.CENTER
    return slide


# ---------------------------------------------------------------------------
# DOC-019  Board Strategy Presentation March 2025  (RESTRICTED, Tier 1)
# ---------------------------------------------------------------------------

doc_019_vol = f"{VOLUME_ROOT}/tier1/DOC-019.pptx"
doc_019_buf = io.BytesIO()

prs = Presentation()
prs.slide_width  = Inches(10)
prs.slide_height = Inches(7.5)

add_title_slide(prs,
    title="Board Strategy Presentation",
    subtitle="March 2025  |  Presented to the Alinta Energy Board of Directors",
    classification="RESTRICTED",
    doc_id="DOC-019"
)

add_content_slide(prs, "Strategic Agenda", [
    "1. FY25 Performance Snapshot",
    "2. Energy Market Context & Outlook",
    "3. Strategic Priorities FY25–FY28",
    "4. Decarbonisation Roadmap Update",
    "5. Investment Pipeline Approval",
    "6. Capital Allocation Framework",
    "7. Risk Appetite & Key Exposures",
], "RESTRICTED")

# Slide 3 — Market Position bar chart
slide3 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide3, "FFFFFF")
bar = slide3.shapes.add_textbox(Inches(0), Inches(0), Inches(10), Inches(0.75))
bar.fill.solid()
bar.fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x5C)
tf = bar.text_frame
tf.paragraphs[0].text = "Market Position — NEM & WEM Generation Share"
tf.paragraphs[0].font.size = Pt(20)
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

chart_data_3 = CategoryChartData()
chart_data_3.categories = ["Alinta Energy", "AGL Energy", "Origin Energy", "EnergyAustralia", "Snowy Hydro", "Other"]
chart_data_3.add_series("Market Share (%)", (8.4, 20.1, 18.7, 14.2, 9.8, 28.8))

chart3 = slide3.shapes.add_chart(
    XL_CHART_TYPE.BAR_CLUSTERED,
    Inches(0.5), Inches(1.0), Inches(9.0), Inches(5.5),
    chart_data_3
).chart
chart3.has_title = True
chart3.chart_title.text_frame.text = "NEM + WEM Installed Capacity Share (%) — 2024"

# Slide 4 — Investment pipeline waterfall (bar approximation via clustered bar)
slide4 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide4, "FFFFFF")
bar4 = slide4.shapes.add_textbox(Inches(0), Inches(0), Inches(10), Inches(0.75))
bar4.fill.solid()
bar4.fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x5C)
tf4 = bar4.text_frame
tf4.paragraphs[0].text = "Investment Pipeline FY25–FY28 ($M)"
tf4.paragraphs[0].font.size = Pt(20)
tf4.paragraphs[0].font.bold = True
tf4.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

chart_data_4 = CategoryChartData()
chart_data_4.categories = ["LYB Asset Life Ext.", "WA Wind Dev.", "Battery Storage", "Grid Conn.", "Retail Tech", "Other"]
chart_data_4.add_series("FY25 ($M)",   (42, 0, 15, 8, 22, 18))
chart_data_4.add_series("FY26 ($M)",   (38, 55, 35, 12, 18, 12))
chart_data_4.add_series("FY27–28 ($M)", (20, 320, 80, 25, 15, 20))

chart4 = slide4.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_STACKED,
    Inches(0.5), Inches(1.0), Inches(9.0), Inches(5.5),
    chart_data_4
).chart
chart4.has_title = True
chart4.chart_title.text_frame.text = "Capital Investment Pipeline by Project and Year ($M)"
chart4.has_legend = True

add_content_slide(prs, "Strategic Priorities FY25–FY28", [
    "Priority 1: Maximise value from existing thermal assets (LYB life extension)",
    "  — $100M asset life extension program targeting 2032 operation",
    "  — Regulatory engagement: EME review and market ancillary services",
    "Priority 2: Accelerate renewable growth (target 25% by FY28)",
    "  — WA wind development: 400 MW greenfield project under feasibility",
    "  — Battery storage: 200 MWh BESS co-located with existing WA assets",
    "Priority 3: Retail excellence and customer NPS improvement",
    "  — Current NPS: +18; target +30 by FY27",
    "  — Digital self-service investment: $22M over 3 years",
    "Priority 4: Decarbonisation and net-zero pathway",
    "  — Scope 1 target: 6.0 Mt CO2e by FY27 (currently 8.4 Mt)",
    "  — Committed to net-zero by 2050; interim milestones under Board review",
], "RESTRICTED")

add_content_slide(prs, "Board Resolution Items", [
    "RESOLUTION 1: Approve FY26 Capital Budget of $285M (as presented)",
    "RESOLUTION 2: Authorise management to progress WA Wind Development to Stage 2 "
    "feasibility (budget $8M; 12 months)",
    "RESOLUTION 3: Approve updated Risk Appetite Statement (Attachment B)",
    "RESOLUTION 4: Note the FY27 decarbonisation targets and associated CapEx programme",
    "RESOLUTION 5: Approve Board Committee composition changes (Attachment C)",
], "RESTRICTED")

prs.save(doc_019_buf)
write_binary_to_volume(doc_019_buf, doc_019_vol)

# ---------------------------------------------------------------------------
# DOC-020  ELT Monthly Operations Review February 2025  (CONFIDENTIAL, Tier 2)
# ---------------------------------------------------------------------------

doc_020_vol = f"{VOLUME_ROOT}/tier2/DOC-020.pptx"
doc_020_buf = io.BytesIO()

prs2 = Presentation()
prs2.slide_width  = Inches(10)
prs2.slide_height = Inches(7.5)

add_title_slide(prs2,
    title="ELT Monthly Operations Review",
    subtitle="February 2025  |  Executive Leadership Team",
    classification="CONFIDENTIAL",
    doc_id="DOC-020"
)

add_content_slide(prs2, "February 2025 — Month in Review", [
    "Safety: TRIFR YTD 3.9 (target 3.5) — on improving trajectory",
    "Generation: Portfolio output 1,392 GWh in Feb (vs 1,285 GWh Jan)",
    "  — Loy Yang B: 1,092 GWh (89.1% availability, above target)",
    "  — Yandin Wind: 198 GWh (50.2% capacity factor, above target)",
    "  — Pinjarra: 82 GWh (maintenance completed 14 Feb)",
    "Retail: 1,042,000 active accounts (net +1,200 vs Jan)",
    "  — Churn rate: 14.2% annualised (industry: 18.6%)",
    "  — NPS: +19 (target +25; improvement from +16 Dec)",
    "Trading: Wholesale position — net long 280 GWh Feb, favourable outcome",
    "Financial: Revenue $284M Feb; EBITDA $47M (on track vs guidance)",
], "CONFIDENTIAL")

# Slide 3 — KPI Scorecard (bar chart)
slide_kpi = prs2.slides.add_slide(prs2.slide_layouts[6])
set_slide_background(slide_kpi, "FFFFFF")
bar_kpi = slide_kpi.shapes.add_textbox(Inches(0), Inches(0), Inches(10), Inches(0.75))
bar_kpi.fill.solid()
bar_kpi.fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x5C)
tf_kpi = bar_kpi.text_frame
tf_kpi.paragraphs[0].text = "KPI Scorecard — YTD FY25 vs Target"
tf_kpi.paragraphs[0].font.size = Pt(20)
tf_kpi.paragraphs[0].font.bold = True
tf_kpi.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

kpi_data = CategoryChartData()
kpi_data.categories = ["TRIFR\n(lower=better)", "EBITDA\n($M YTD)", "NPS\n(score)", "LYB Avail.\n(%)", "Yandin CF\n(%)"]
kpi_data.add_series("Actual",  (3.9, 298, 19, 88.4, 43.1))
kpi_data.add_series("Target",  (3.5, 295, 25, 90.0, 45.0))

chart_kpi = slide_kpi.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(0.5), Inches(1.0), Inches(9.0), Inches(5.5),
    kpi_data
).chart
chart_kpi.has_title = True
chart_kpi.chart_title.text_frame.text = "Key Performance Indicators — YTD Feb FY25"
chart_kpi.has_legend = True

# Slide 4 — Retail Metrics bar chart
slide_retail = prs2.slides.add_slide(prs2.slide_layouts[6])
set_slide_background(slide_retail, "FFFFFF")
bar_ret = slide_retail.shapes.add_textbox(Inches(0), Inches(0), Inches(10), Inches(0.75))
bar_ret.fill.solid()
bar_ret.fill.fore_color.rgb = RGBColor(0x1B, 0x3A, 0x5C)
tf_ret = bar_ret.text_frame
tf_ret.paragraphs[0].text = "Retail Business Unit — Monthly Metrics"
tf_ret.paragraphs[0].font.size = Pt(20)
tf_ret.paragraphs[0].font.bold = True
tf_ret.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

retail_data = CategoryChartData()
retail_data.categories = ["Aug FY25", "Sep FY25", "Oct FY25", "Nov FY25", "Dec FY25", "Jan FY26", "Feb FY26"]
retail_data.add_series("Revenue ($M)",  (139, 142, 145, 148, 150, 147, 144))
retail_data.add_series("Gross Margin ($M)", (28, 29, 30, 31, 32, 30, 29))

chart_ret = slide_retail.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(0.5), Inches(1.0), Inches(9.0), Inches(5.5),
    retail_data
).chart
chart_ret.has_title = True
chart_ret.chart_title.text_frame.text = "Retail Revenue & Gross Margin — Monthly ($M)"
chart_ret.has_legend = True

add_content_slide(prs2, "Key Actions — March 2025", [
    "ACTION-1: CFO to present revised FY25 H2 EBITDA bridge at March ELT [CFO, 28 Mar]",
    "ACTION-2: Generation GM to complete Newman Unit 3 RCFA and present findings [GM Gen, 14 Mar]",
    "ACTION-3: CCO to present Retail NPS improvement plan with Q4 initiatives [CCO, 14 Mar]",
    "ACTION-4: CDO to update ELT on Digital self-service platform go-live timeline [CDO, 28 Mar]",
    "ACTION-5: Risk team to refresh top-10 risk register for March Board meeting [CRO, 21 Mar]",
    "ACTION-6: HR to circulate updated People & Culture survey results [CHRO, 7 Mar]",
], "CONFIDENTIAL")

prs2.save(doc_020_buf)
write_binary_to_volume(doc_020_buf, doc_020_vol)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Generate XLSX workbooks with native embedded charts

# COMMAND ----------

import openpyxl
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def style_header_row(ws, row_num, num_cols, fill_hex="1B3A5C", font_hex="FFFFFF"):
    """Apply header styling to a row."""
    fill = PatternFill(start_color=fill_hex, end_color=fill_hex, fill_type="solid")
    font = Font(bold=True, color=font_hex, size=11)
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row_num, column=col)
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center")


def add_thin_borders(ws, min_row, max_row, min_col, max_col):
    """Add thin borders to a range."""
    thin = Side(style="thin", color="AAAAAA")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col):
        for cell in row:
            cell.border = border


# ---------------------------------------------------------------------------
# DOC-021  FY2026 Budget Model  (RESTRICTED, Tier 1)
# ---------------------------------------------------------------------------

doc_021_vol = f"{VOLUME_ROOT}/tier1/DOC-021.xlsx"
doc_021_buf = io.BytesIO()

wb_021 = openpyxl.Workbook()

# ---- Sheet 1: P&L Summary ----
ws_pl = wb_021.active
ws_pl.title = "P&L Summary"

ws_pl.merge_cells("A1:F1")
ws_pl["A1"] = "ALINTA ENERGY — FY2026 Budget: P&L by Business Unit ($M)"
ws_pl["A1"].font = Font(bold=True, size=14, color="1B3A5C")
ws_pl["A1"].alignment = Alignment(horizontal="center")
ws_pl.row_dimensions[1].height = 28

headers_pl = ["Business Unit", "Revenue", "Direct Costs", "Gross Margin", "Overheads", "EBITDA"]
for col_idx, h in enumerate(headers_pl, 1):
    ws_pl.cell(row=2, column=col_idx, value=h)
style_header_row(ws_pl, 2, len(headers_pl))

pl_data = [
    ("Retail",      1890,  1562, 158),
    ("Generation",  2580,  1820, 195),
    ("Trading",      920,   845,  48),
    ("Corporate",      0,     0, 178),
]

# Write data with formulas
for i, (bu, rev, dc, oh) in enumerate(pl_data, start=3):
    ws_pl.cell(row=i, column=1, value=bu)
    ws_pl.cell(row=i, column=2, value=rev)
    ws_pl.cell(row=i, column=3, value=dc)
    ws_pl.cell(row=i, column=4, value=f"=B{i}-C{i}")   # Gross Margin
    ws_pl.cell(row=i, column=5, value=oh)
    ws_pl.cell(row=i, column=6, value=f"=D{i}-E{i}")   # EBITDA
    for col in range(2, 7):
        ws_pl.cell(row=i, column=col).number_format = '#,##0'

# Group total row
ws_pl.cell(row=7, column=1, value="Group Total")
ws_pl.cell(row=7, column=1).font = Font(bold=True, color="1B3A5C")
for col in range(2, 7):
    col_letter = get_column_letter(col)
    ws_pl.cell(row=7, column=col, value=f"=SUM({col_letter}3:{col_letter}6)")
    ws_pl.cell(row=7, column=col).font = Font(bold=True, color="1B3A5C")
    ws_pl.cell(row=7, column=col).number_format = '#,##0'

style_header_row(ws_pl, 7, 6, fill_hex="AEB6BF", font_hex="1B3A5C")
add_thin_borders(ws_pl, 2, 7, 1, 6)

# Column widths
col_widths_pl = [18, 12, 14, 14, 12, 12]
for i, w in enumerate(col_widths_pl, 1):
    ws_pl.column_dimensions[get_column_letter(i)].width = w

# Bar chart — EBITDA by BU
chart_pl = BarChart()
chart_pl.type = "col"
chart_pl.title = "FY26 Budget EBITDA by Business Unit ($M)"
chart_pl.y_axis.title = "EBITDA ($M)"
chart_pl.x_axis.title = "Business Unit"
chart_pl.height = 14
chart_pl.width  = 22

cats_pl = Reference(ws_pl, min_col=1, min_row=3, max_row=6)
data_pl = Reference(ws_pl, min_col=6, min_row=2, max_row=6)
chart_pl.add_data(data_pl, titles_from_data=True)
chart_pl.set_categories(cats_pl)
ws_pl.add_chart(chart_pl, "H3")

# ---- Sheet 2: CapEx by Quarter ----
ws_capex = wb_021.create_sheet("CapEx by Quarter")

ws_capex.merge_cells("A1:F1")
ws_capex["A1"] = "ALINTA ENERGY — FY2026 Capital Expenditure Plan ($M)"
ws_capex["A1"].font = Font(bold=True, size=14, color="1B3A5C")
ws_capex["A1"].alignment = Alignment(horizontal="center")
ws_capex.row_dimensions[1].height = 28

headers_cx = ["Project", "Q1 FY26", "Q2 FY26", "Q3 FY26", "Q4 FY26", "FY26 Total"]
for col_idx, h in enumerate(headers_cx, 1):
    ws_capex.cell(row=2, column=col_idx, value=h)
style_header_row(ws_capex, 2, len(headers_cx))

capex_rows = [
    ("LYB Asset Life Extension",    18, 22, 20, 16, None),
    ("WA Wind Development (Stage2)", 8, 12, 18, 17, None),
    ("Battery Storage BESS",         5,  8, 12, 10, None),
    ("Grid Connection Upgrades",     4,  4,  4,  4, None),
    ("Retail Digital Platform",      8,  7,  4,  3, None),
    ("Fleet & Equipment",            3,  3,  3,  3, None),
    ("Other / Contingency",          4,  5,  4,  3, None),
]

for i, (proj, q1, q2, q3, q4, _) in enumerate(capex_rows, start=3):
    ws_capex.cell(row=i, column=1, value=proj)
    ws_capex.cell(row=i, column=2, value=q1)
    ws_capex.cell(row=i, column=3, value=q2)
    ws_capex.cell(row=i, column=4, value=q3)
    ws_capex.cell(row=i, column=5, value=q4)
    ws_capex.cell(row=i, column=6, value=f"=SUM(B{i}:E{i})")
    for col in range(2, 7):
        ws_capex.cell(row=i, column=col).number_format = '#,##0'

total_row_cx = len(capex_rows) + 3
ws_capex.cell(row=total_row_cx, column=1, value="Total CapEx").font = Font(bold=True, color="1B3A5C")
for col in range(2, 7):
    cl = get_column_letter(col)
    ws_capex.cell(row=total_row_cx, column=col, value=f"=SUM({cl}3:{cl}{total_row_cx-1})")
    ws_capex.cell(row=total_row_cx, column=col).font = Font(bold=True, color="1B3A5C")
    ws_capex.cell(row=total_row_cx, column=col).number_format = '#,##0'

style_header_row(ws_capex, total_row_cx, 6, fill_hex="AEB6BF", font_hex="1B3A5C")
add_thin_borders(ws_capex, 2, total_row_cx, 1, 6)

col_widths_cx = [28, 10, 10, 10, 10, 12]
for i, w in enumerate(col_widths_cx, 1):
    ws_capex.column_dimensions[get_column_letter(i)].width = w

# Line chart — CapEx by quarter (quarterly totals)
chart_cx = LineChart()
chart_cx.title = "FY26 CapEx by Quarter ($M) — Project Breakdown"
chart_cx.y_axis.title = "CapEx ($M)"
chart_cx.x_axis.title = "Quarter"
chart_cx.height = 14
chart_cx.width  = 22

for col_offset in range(1, 5):   # Q1–Q4
    data_ref = Reference(ws_capex, min_col=col_offset + 1, min_row=2, max_row=total_row_cx - 1)
    chart_cx.add_data(data_ref, titles_from_data=True)

cats_cx = Reference(ws_capex, min_col=1, min_row=3, max_row=total_row_cx - 1)
chart_cx.set_categories(cats_cx)
ws_capex.add_chart(chart_cx, "H3")

# ---- Sheet 3: Assumptions ----
ws_ass = wb_021.create_sheet("Assumptions")
ws_ass["A1"] = "FY26 Budget Model — Key Assumptions"
ws_ass["A1"].font = Font(bold=True, size=14, color="1B3A5C")

assumptions = [
    ("Macro & Market", ""),
    ("Electricity price (NEM baseload)", "AUD $95/MWh average FY26"),
    ("Electricity price (WEM)", "AUD $88/MWh average FY26"),
    ("Gas price (WA domestic)", "AUD $6.80/GJ"),
    ("CPI assumption", "3.5% pa"),
    ("USD/AUD FX", "0.645"),
    ("", ""),
    ("Generation", ""),
    ("Loy Yang B — output", "7,200 GWh (90% availability assumed)"),
    ("Yandin Wind — output", "1,100 GWh (45% CF)"),
    ("Pinjarra — output",   "900 GWh (72% availability)"),
    ("Newman — output",     "280 GWh (70% availability, after repairs)"),
    ("", ""),
    ("Retail", ""),
    ("Customer accounts (avg)", "1,045,000"),
    ("Churn rate (annual)",     "14.0%"),
    ("Average margin per account", "AUD $172/year"),
    ("", ""),
    ("Financing", ""),
    ("Weighted average cost of debt", "5.8%"),
    ("Net debt at 30 June 2026 (forecast)", "AUD $1.18B"),
    ("Leverage (Net Debt / EBITDA)", "1.9x"),
]

for i, (key, val) in enumerate(assumptions, start=3):
    ws_ass.cell(row=i, column=1, value=key)
    ws_ass.cell(row=i, column=2, value=val)
    if not val:   # section header
        ws_ass.cell(row=i, column=1).font = Font(bold=True, color="1B3A5C", size=11)

ws_ass.column_dimensions["A"].width = 38
ws_ass.column_dimensions["B"].width = 38

wb_021.save(doc_021_buf)
write_binary_to_volume(doc_021_buf, doc_021_vol)

# ---------------------------------------------------------------------------
# DOC-022  Risk Quantitative Assessment FY2025  (CONFIDENTIAL, Tier 2)
# ---------------------------------------------------------------------------

doc_022_vol = f"{VOLUME_ROOT}/tier2/DOC-022.xlsx"
doc_022_buf = io.BytesIO()

wb_022 = openpyxl.Workbook()

# ---- Sheet 1: Risk Register ----
ws_risk = wb_022.active
ws_risk.title = "Risk Register"

ws_risk.merge_cells("A1:H1")
ws_risk["A1"] = "ALINTA ENERGY — Risk Quantitative Assessment FY2025"
ws_risk["A1"].font = Font(bold=True, size=14, color="1B3A5C")
ws_risk["A1"].alignment = Alignment(horizontal="center")
ws_risk.row_dimensions[1].height = 28

headers_risk = ["Risk ID", "Risk Description", "Category", "Likelihood\n(1-5)", "Consequence\n(1-5)", "Risk Score", "Financial Impact\n($M, 90th pct)", "Status"]
for col_idx, h in enumerate(headers_risk, 1):
    ws_risk.cell(row=2, column=col_idx, value=h)
style_header_row(ws_risk, 2, len(headers_risk))
ws_risk.row_dimensions[2].height = 30

risks = [
    ("RSK-001", "Loy Yang B unplanned outage >30 days",          "Operational",  3, 5, None, 185, "Open"),
    ("RSK-002", "Wholesale electricity price collapse NEM",       "Market",       2, 5, None, 210, "Monitored"),
    ("RSK-003", "Carbon regulation — accelerated phase-out",     "Regulatory",   3, 4, None, 320, "Active Mgmt"),
    ("RSK-004", "Retail mass churn event (competitor disruption)","Market",       2, 4, None, 145, "Monitored"),
    ("RSK-005", "Yandin turbine blade failure (multiple units)",  "Operational",  2, 3, None,  42, "Open"),
    ("RSK-006", "Cyber-attack on SCADA / OT systems",            "Cyber",        3, 5, None, 265, "Active Mgmt"),
    ("RSK-007", "Gas supply curtailment WA (force majeure)",     "Supply Chain", 2, 4, None,  88, "Monitored"),
    ("RSK-008", "Interest rate increase — refinancing risk",     "Financial",    3, 3, None,  55, "Hedged"),
    ("RSK-009", "Extreme weather event — asset damage",          "Climate",      3, 4, None, 120, "Insured"),
    ("RSK-010", "Regulatory change — retail price regulation",   "Regulatory",   2, 3, None,  75, "Monitored"),
]

for i, (rid, desc, cat, lik, cons, _, impact, status) in enumerate(risks, start=3):
    ws_risk.cell(row=i, column=1, value=rid)
    ws_risk.cell(row=i, column=2, value=desc)
    ws_risk.cell(row=i, column=3, value=cat)
    ws_risk.cell(row=i, column=4, value=lik)
    ws_risk.cell(row=i, column=5, value=cons)
    ws_risk.cell(row=i, column=6, value=f"=D{i}*E{i}")   # Risk Score
    ws_risk.cell(row=i, column=7, value=impact)
    ws_risk.cell(row=i, column=8, value=status)
    ws_risk.cell(row=i, column=7).number_format = '#,##0'
    # Colour-code risk score
    score = lik * cons
    if score >= 15:
        fill_colour = "C0392B"
    elif score >= 9:
        fill_colour = "F39C12"
    else:
        fill_colour = "27AE60"
    ws_risk.cell(row=i, column=6).fill = PatternFill(start_color=fill_colour, end_color=fill_colour, fill_type="solid")
    ws_risk.cell(row=i, column=6).font = Font(bold=True, color="FFFFFF")

add_thin_borders(ws_risk, 2, len(risks) + 2, 1, 8)

col_widths_r = [10, 42, 14, 12, 14, 11, 20, 14]
for i, w in enumerate(col_widths_r, 1):
    ws_risk.column_dimensions[get_column_letter(i)].width = w

# Bar chart — Financial Impact
chart_risk = BarChart()
chart_risk.type = "bar"   # horizontal
chart_risk.title = "Financial Impact by Risk (90th Percentile $M)"
chart_risk.x_axis.title = "Financial Impact ($M)"
chart_risk.y_axis.title = "Risk"
chart_risk.height = 16
chart_risk.width  = 24

risk_ids   = Reference(ws_risk, min_col=1, min_row=3, max_row=12)
impact_ref = Reference(ws_risk, min_col=7, min_row=2, max_row=12)
chart_risk.add_data(impact_ref, titles_from_data=True)
chart_risk.set_categories(risk_ids)
ws_risk.add_chart(chart_risk, "J3")

# ---- Sheet 2: Sensitivity Analysis ----
ws_sens = wb_022.create_sheet("Sensitivity Analysis")

ws_sens.merge_cells("A1:D1")
ws_sens["A1"] = "EBITDA Sensitivity — Key Value Drivers (FY25 Full Year, $M EBITDA Impact)"
ws_sens["A1"].font = Font(bold=True, size=13, color="1B3A5C")
ws_sens["A1"].alignment = Alignment(horizontal="center")
ws_sens.row_dimensions[1].height = 28

headers_s = ["Value Driver", "Downside (-1σ)", "Base Case", "Upside (+1σ)"]
for col_idx, h in enumerate(headers_s, 1):
    ws_sens.cell(row=2, column=col_idx, value=h)
style_header_row(ws_sens, 2, 4)

sens_data = [
    ("Electricity price (NEM) ±$10/MWh",  -68,  0,  +68),
    ("LYB availability ±5%",              -42,  0,  +42),
    ("Gas cost ±$0.50/GJ",                -18,  0,  +18),
    ("Retail volume ±50,000 accounts",    -15,  0,  +15),
    ("FX (USD/AUD) ±0.03",               -12,  0,  +12),
    ("Interest rate ±50bps",              -10,  0,  +10),
    ("Yandin CF ±5%",                      -8,  0,   +8),
]

for i, (driver, down, base, up) in enumerate(sens_data, start=3):
    ws_sens.cell(row=i, column=1, value=driver)
    ws_sens.cell(row=i, column=2, value=down)
    ws_sens.cell(row=i, column=3, value=base)
    ws_sens.cell(row=i, column=4, value=up)
    for col in range(2, 5):
        ws_sens.cell(row=i, column=col).number_format = '+#,##0;-#,##0;0'

add_thin_borders(ws_sens, 2, len(sens_data) + 2, 1, 4)
col_widths_s = [36, 16, 12, 14]
for i, w in enumerate(col_widths_s, 1):
    ws_sens.column_dimensions[get_column_letter(i)].width = w

# Tornado chart (horizontal bar — downside only for now, styled as tornado)
chart_tornado = BarChart()
chart_tornado.type = "bar"
chart_tornado.title = "EBITDA Sensitivity Tornado — Downside ($M)"
chart_tornado.x_axis.title = "EBITDA Impact ($M)"
chart_tornado.y_axis.title = "Value Driver"
chart_tornado.height = 14
chart_tornado.width  = 22

drivers_ref  = Reference(ws_sens, min_col=1, min_row=3, max_row=len(sens_data) + 2)
downside_ref = Reference(ws_sens, min_col=2, min_row=2, max_row=len(sens_data) + 2)
chart_tornado.add_data(downside_ref, titles_from_data=True)
chart_tornado.set_categories(drivers_ref)
ws_sens.add_chart(chart_tornado, "F3")

wb_022.save(doc_022_buf)
write_binary_to_volume(doc_022_buf, doc_022_vol)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Register document metadata in eds_synthetic.documents

# COMMAND ----------

from pyspark.sql import Row
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    BooleanType, DateType, TimestampType
)
from datetime import date as dt_date

doc_metadata = [
    {
        "doc_id": "DOC-016",
        "title": "FY2025 Financial Performance Dashboard",
        "doc_type": "Financial Report",
        "classification": "CONFIDENTIAL",
        "access_tier_level": 2,
        "business_area": "Finance",
        "effective_date": dt_date(2025, 2, 14),
        "author": "Chief Financial Officer",
        "version": "v1.0",
        "content": (
            "FY2025 Financial Performance Dashboard for Alinta Energy covering 1H FY25 results. "
            "Group revenue $1,692M (up 6.2% on pcp). EBITDA $298M. "
            "Revenue by BU: Retail $892M, Generation $1,247M annualised, Trading $445M annualised. "
            "Corporate cost centre ($84M). Net debt $1.24B, leverage 2.1x EBITDA. "
            "Full-year EBITDA guidance reaffirmed at $590-620M. CapEx guidance $152M. "
            "Charts: revenue/EBITDA quarterly trend, EBITDA by business unit, CapEx waterfall bridge."
        ),
        "is_synthetic": True,
        "source_system": "Generated",
    },
    {
        "doc_id": "DOC-017",
        "title": "Generation Asset Performance Report Q3 FY25",
        "doc_type": "Operations Report",
        "classification": "INTERNAL",
        "access_tier_level": 3,
        "business_area": "Generation",
        "effective_date": dt_date(2025, 1, 31),
        "author": "General Manager Generation",
        "version": "v1.0",
        "content": (
            "Generation Asset Performance Report for Q3 FY25 (October–December 2024). "
            "Portfolio output 4,210 GWh. "
            "Loy Yang B (1,000 MW brown coal, VIC): output 3,631 GWh, availability 88.4% (target 90%), "
            "forced outage rate 1.8%, carbon intensity 1.31 t CO2e/MWh. "
            "Yandin Wind Farm (132 MW, WA): output 280 GWh, capacity factor 43.1% (target 45%), "
            "turbine availability 97.2%. "
            "Pinjarra Gas (180 MW, WA): output 236 GWh, availability 72.6% post-maintenance. "
            "Newman Gas (60 MW, WA): output 63 GWh, availability 61.8%, RCFA underway for compressor trips. "
            "Charts: capacity factor by asset, monthly generation output area chart, availability vs target grouped bar."
        ),
        "is_synthetic": True,
        "source_system": "Generated",
    },
    {
        "doc_id": "DOC-018",
        "title": "Safety & Sustainability Report FY2024",
        "doc_type": "ESG Report",
        "classification": "INTERNAL",
        "access_tier_level": 3,
        "business_area": "Safety & Sustainability",
        "effective_date": dt_date(2024, 9, 30),
        "author": "Chief Safety & Sustainability Officer",
        "version": "v1.0",
        "content": (
            "Safety and Sustainability Annual Report for FY2024. "
            "TRIFR: 4.2 (FY24 target 3.5; improved from 5.8 in FY23, 27% reduction). "
            "2 Lost Time Injuries recorded. Near misses reported increased to 218 (positive reporting culture). "
            "Scope 1 emissions: 8.4 Mt CO2e (FY23: 8.9 Mt). FY27 target: 6.0 Mt CO2e. "
            "Scope 2 emissions: 0.48 Mt CO2e (market-based). Carbon intensity LYB: 1.31 t CO2e/MWh. "
            "Offset credits purchased: 0.2 Mt voluntary Gold Standard. "
            "Renewable energy: 8% of generation mix (FY28 target 25%). "
            "Yandin Wind: 1,010 GWh FY24. Rooftop solar facilitated: 380 MW aggregated. "
            "Charts: TRIFR trend vs target (line), Scope 1+2 stacked bar, renewable mix pie."
        ),
        "is_synthetic": True,
        "source_system": "Generated",
    },
    {
        "doc_id": "DOC-019",
        "title": "Board Strategy Presentation March 2025",
        "doc_type": "Board Paper",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Strategy",
        "effective_date": dt_date(2025, 3, 18),
        "author": "Chief Executive Officer",
        "version": "v1.0",
        "content": (
            "Board Strategy Presentation for March 2025 Board meeting. "
            "Topics: FY25 performance snapshot, energy market context and outlook, "
            "strategic priorities FY25-FY28, decarbonisation roadmap update, investment pipeline approval, "
            "capital allocation framework, risk appetite and key exposures. "
            "Strategic priorities: (1) LYB life extension ($100M, targeting 2032 operation); "
            "(2) Renewable growth — WA wind 400 MW greenfield feasibility, 200 MWh BESS; "
            "(3) Retail excellence — NPS +18 target +30 by FY27, $22M digital investment; "
            "(4) Decarbonisation — 6.0 Mt target FY27, net-zero by 2050. "
            "Board resolutions: FY26 capital budget $285M approved; WA Wind Stage 2 feasibility authorised ($8M); "
            "updated Risk Appetite Statement; decarbonisation CapEx programme noted. "
            "Charts: NEM+WEM market share bar, investment pipeline stacked column by project and year."
        ),
        "is_synthetic": True,
        "source_system": "Generated",
    },
    {
        "doc_id": "DOC-020",
        "title": "ELT Monthly Operations Review February 2025",
        "doc_type": "Executive Review",
        "classification": "CONFIDENTIAL",
        "access_tier_level": 2,
        "business_area": "Operations",
        "effective_date": dt_date(2025, 2, 28),
        "author": "Chief Operating Officer",
        "version": "v1.0",
        "content": (
            "Executive Leadership Team Monthly Operations Review for February 2025. "
            "Safety: TRIFR YTD 3.9 (target 3.5). "
            "Generation: Portfolio output 1,392 GWh Feb (vs 1,285 GWh Jan). "
            "LYB: 1,092 GWh, 89.1% availability. Yandin: 198 GWh, 50.2% capacity factor. Pinjarra: 82 GWh. "
            "Retail: 1,042,000 active accounts (net +1,200). Churn 14.2% annualised. NPS +19 (target +25). "
            "Trading: Net long 280 GWh, favourable outcome. "
            "Financial: Revenue $284M, EBITDA $47M Feb. On track vs guidance. "
            "Actions: CFO H2 EBITDA bridge, Newman Unit 3 RCFA presentation, Retail NPS plan, "
            "digital platform go-live, top-10 risk refresh, People & Culture survey results. "
            "Charts: KPI scorecard clustered bar (actual vs target), retail revenue and gross margin monthly."
        ),
        "is_synthetic": True,
        "source_system": "Generated",
    },
    {
        "doc_id": "DOC-021",
        "title": "FY2026 Budget Model",
        "doc_type": "Financial Model",
        "classification": "RESTRICTED",
        "access_tier_level": 1,
        "business_area": "Finance",
        "effective_date": dt_date(2025, 4, 30),
        "author": "Chief Financial Officer",
        "version": "v1.0",
        "content": (
            "FY2026 Annual Budget Model for Alinta Energy. "
            "P&L Summary by Business Unit: "
            "Retail revenue $1,890M, direct costs $1,562M, overheads $158M. "
            "Generation revenue $2,580M, direct costs $1,820M, overheads $195M. "
            "Trading revenue $920M, direct costs $845M, overheads $48M. "
            "Corporate overheads $178M. "
            "Total group EBITDA target approximately $620M. "
            "CapEx plan $285M: LYB life extension $76M, WA Wind Stage 2 $55M, BESS $35M, "
            "grid connections $16M, retail digital $22M, fleet and equipment $12M, contingency $16M (approx). "
            "Key assumptions: NEM electricity price $95/MWh, WEM $88/MWh, gas $6.80/GJ, CPI 3.5%, "
            "USD/AUD 0.645, LYB output 7,200 GWh at 90% availability, Yandin 1,100 GWh at 45% CF. "
            "Net debt target $1.18B, leverage 1.9x. WACD 5.8%. "
            "Charts: EBITDA bar chart by business unit, CapEx quarterly line chart by project."
        ),
        "is_synthetic": True,
        "source_system": "Generated",
    },
    {
        "doc_id": "DOC-022",
        "title": "Risk Quantitative Assessment FY2025",
        "doc_type": "Risk Report",
        "classification": "CONFIDENTIAL",
        "access_tier_level": 2,
        "business_area": "Risk",
        "effective_date": dt_date(2025, 3, 31),
        "author": "Chief Risk Officer",
        "version": "v1.0",
        "content": (
            "Risk Quantitative Assessment for FY2025. "
            "Top 10 risks with likelihood (1-5), consequence (1-5), and 90th percentile financial impact. "
            "RSK-001 LYB unplanned outage >30 days: score 15 (3x5), impact $185M. "
            "RSK-002 Wholesale electricity price collapse NEM: score 10 (2x5), impact $210M. "
            "RSK-003 Carbon regulation accelerated phase-out: score 12 (3x4), impact $320M — highest impact. "
            "RSK-004 Retail mass churn: score 8 (2x4), impact $145M. "
            "RSK-005 Yandin turbine blade failure: score 6 (2x3), impact $42M. "
            "RSK-006 Cyber-attack on SCADA/OT systems: score 15 (3x5), impact $265M. "
            "RSK-007 Gas supply curtailment WA: score 8, impact $88M. "
            "RSK-008 Interest rate refinancing: score 9, impact $55M — hedged. "
            "RSK-009 Extreme weather asset damage: score 12, impact $120M — insured. "
            "RSK-010 Retail price regulation: score 6, impact $75M. "
            "Sensitivity analysis: electricity price ±$10/MWh = ±$68M EBITDA; LYB availability ±5% = ±$42M; "
            "gas cost ±$0.50/GJ = ±$18M; retail volume ±50k accounts = ±$15M; FX ±0.03 = ±$12M. "
            "Charts: horizontal financial impact bar chart, EBITDA sensitivity tornado chart."
        ),
        "is_synthetic": True,
        "source_system": "Generated",
    },
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Upsert metadata into eds_synthetic.documents

# COMMAND ----------

# Ensure eds_synthetic.documents table exists with expected schema (idempotent)
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.eds_synthetic.documents (
    doc_id              STRING      NOT NULL COMMENT 'Unique document identifier',
    title               STRING      COMMENT 'Document title',
    doc_type            STRING      COMMENT 'Document type (e.g. Board Paper, Risk Report)',
    classification      STRING      COMMENT 'Security classification',
    access_tier_level   INT         COMMENT 'Access tier 1–4',
    business_area       STRING      COMMENT 'Business area',
    effective_date      DATE        COMMENT 'Document effective date',
    author              STRING      COMMENT 'Author or role',
    version             STRING      COMMENT 'Document version',
    content             STRING      COMMENT 'Text summary / extracted content',
    is_synthetic        BOOLEAN     COMMENT 'True for synthetic documents',
    source_system       STRING      COMMENT 'Source system or generation method',
    created_at          TIMESTAMP   COMMENT 'Record creation timestamp'
)
USING DELTA
COMMENT 'Synthetic document registry for Executive Decision Studio'
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
""")

print(f"[OK] {CATALOG}.eds_synthetic.documents ready")

# COMMAND ----------

from pyspark.sql import Row
from datetime import datetime

ingest_ts = datetime.utcnow()

rows_meta = [
    Row(
        doc_id=d["doc_id"],
        title=d["title"],
        doc_type=d["doc_type"],
        classification=d["classification"],
        access_tier_level=d["access_tier_level"],
        business_area=d["business_area"],
        effective_date=d["effective_date"],
        author=d["author"],
        version=d["version"],
        content=d["content"],
        is_synthetic=d["is_synthetic"],
        source_system=d["source_system"],
        created_at=ingest_ts,
    )
    for d in doc_metadata
]

from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    BooleanType, DateType, TimestampType
)

meta_schema = StructType([
    StructField("doc_id",             StringType(),    False),
    StructField("title",              StringType(),    True),
    StructField("doc_type",           StringType(),    True),
    StructField("classification",     StringType(),    True),
    StructField("access_tier_level",  IntegerType(),   True),
    StructField("business_area",      StringType(),    True),
    StructField("effective_date",     DateType(),      True),
    StructField("author",             StringType(),    True),
    StructField("version",            StringType(),    True),
    StructField("content",            StringType(),    True),
    StructField("is_synthetic",       BooleanType(),   True),
    StructField("source_system",      StringType(),    True),
    StructField("created_at",         TimestampType(), True),
])

meta_df = spark.createDataFrame(rows_meta, schema=meta_schema)
meta_df.createOrReplaceTempView("new_doc_metadata")

spark.sql(f"""
MERGE INTO {CATALOG}.eds_synthetic.documents AS target
USING new_doc_metadata AS source
ON target.doc_id = source.doc_id
WHEN MATCHED THEN UPDATE SET
    target.title             = source.title,
    target.doc_type          = source.doc_type,
    target.classification    = source.classification,
    target.access_tier_level = source.access_tier_level,
    target.business_area     = source.business_area,
    target.effective_date    = source.effective_date,
    target.author            = source.author,
    target.version           = source.version,
    target.content           = source.content,
    target.is_synthetic      = source.is_synthetic,
    target.source_system     = source.source_system,
    target.created_at        = source.created_at
WHEN NOT MATCHED THEN INSERT *
""")

print(f"[OK] Merged {len(rows_meta)} document metadata records into eds_synthetic.documents")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Verify — list volume files with sizes

# COMMAND ----------

print("\n" + "=" * 65)
print("VOLUME VERIFICATION — Rich Documents")
print("=" * 65)

total_files = 0
total_bytes = 0
doc_ext_map = {
    "DOC-016": "pdf", "DOC-017": "pdf", "DOC-018": "pdf",
    "DOC-019": "pptx", "DOC-020": "pptx",
    "DOC-021": "xlsx", "DOC-022": "xlsx",
}
tier_map = {
    "DOC-016": 2, "DOC-017": 3, "DOC-018": 3,
    "DOC-019": 1, "DOC-020": 2,
    "DOC-021": 1, "DOC-022": 2,
}

for tier in ["tier1", "tier2", "tier3"]:
    path = f"{VOLUME_ROOT}/{tier}"
    try:
        files = dbutils.fs.ls(path)
        if not files:
            print(f"\n  {path}/  (empty)")
            continue
        print(f"\n  {path}/  ({len(files)} files)")
        for f in files:
            size_kb = f.size / 1024
            total_files += 1
            total_bytes += f.size
            print(f"    {f.name:35s}  {size_kb:8.1f} KB")
    except Exception as e:
        print(f"\n  {path}/  [WARN: {e}]")

print(f"\n  Total rich document files : {total_files}")
print(f"  Total size                : {total_bytes / 1024:.1f} KB  ({total_bytes / (1024*1024):.2f} MB)")
print("=" * 65)

# Also verify metadata table
count_meta = spark.sql(f"""
    SELECT COUNT(*) as cnt
    FROM {CATALOG}.eds_synthetic.documents
    WHERE doc_id IN ('DOC-016','DOC-017','DOC-018','DOC-019','DOC-020','DOC-021','DOC-022')
""").collect()[0]["cnt"]

print(f"\n[OK] eds_synthetic.documents: {count_meta}/7 rich documents registered")

spark.sql(f"""
    SELECT doc_id, title, doc_type, classification, access_tier_level
    FROM {CATALOG}.eds_synthetic.documents
    WHERE doc_id IN ('DOC-016','DOC-017','DOC-018','DOC-019','DOC-020','DOC-021','DOC-022')
    ORDER BY doc_id
""").show(truncate=60)

print("\n[OK] Rich document generation complete. Run 01_document_ingestion to ingest these files.")
