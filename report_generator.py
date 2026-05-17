"""
report_generator.py — Premium PDF Report Builder for DataMind AI
Professional A4 report: Cover · Executive Summary · Key Findings ·
Charts · Statistical Summary · Anomalies · Recommendations · Appendix
"""

import io
import copy
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

# Matplotlib for server-side chart rendering (works without display/kaleido)
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend — works on all servers
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, Image,
    NextPageTemplate, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, KeepTogether,
)
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─────────────────────────────────────────────
# PALETTE  (matches the dark-premium web UI)
# ─────────────────────────────────────────────
INK        = HexColor("#0f0c29")        # cover background
NAVY       = HexColor("#0d1b3e")        # cover accent
PURPLE     = HexColor("#7c3aed")        # primary accent
PURPLE_MID = HexColor("#6d28d9")        # darker purple
PURPLE_LT  = HexColor("#ede9fe")        # light purple tint
BLUE       = HexColor("#3b82f6")        # secondary accent
BLUE_LT    = HexColor("#eff6ff")        # light blue tint
GREEN      = HexColor("#059669")        # recommendation / positive
GREEN_LT   = HexColor("#ecfdf5")        # light green tint
AMBER      = HexColor("#d97706")        # warning
AMBER_LT   = HexColor("#fffbeb")        # light amber tint
RED        = HexColor("#dc2626")        # danger
RED_LT     = HexColor("#fef2f2")        # light red tint
DARK       = HexColor("#1e293b")        # body text
MID        = HexColor("#475569")        # secondary text
LIGHT      = HexColor("#94a3b8")        # muted text
BORDER     = HexColor("#e2e8f0")        # hairline
PAGE_BG    = HexColor("#ffffff")        # page background
ROW_ALT    = HexColor("#f8fafc")        # alternating row


# ─────────────────────────────────────────────
# CHART → PNG HELPER
# ─────────────────────────────────────────────

def _mpl_style(ax, title="", xlabel="", ylabel=""):
    BG, GRID, TEXT, MUTED = "#ffffff", "#f0f4f8", "#1e293b", "#64748b"
    ax.set_facecolor(BG)
    ax.figure.patch.set_facecolor(BG)
    ax.grid(True, color=GRID, linewidth=0.8, linestyle="-", axis="y", zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color("#e2e8f0"); spine.set_linewidth(0.6)
    ax.tick_params(colors=MUTED, labelsize=8)
    if title: ax.set_title(title, color=TEXT, fontsize=9, fontweight="bold", pad=8)
    if xlabel: ax.set_xlabel(xlabel, fontsize=7.5, color=MUTED)
    if ylabel: ax.set_ylabel(ylabel, fontsize=7.5, color=MUTED)

def _buf_from_fig(fig, dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="#ffffff", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf

_PAL = ["#7c3aed","#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#f97316"]

def _chart_img(buf, caption, S, width_mm=155, height_mm=75):
    if buf is None: return [Spacer(1, 2 * mm)]
    img = Image(buf, width=width_mm * mm, height=height_mm * mm)
    img.hAlign = "CENTRE"
    return [img, Paragraph(caption, S["caption"]), Spacer(1, 4 * mm)]

def _make_trend_chart(df):
    try:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
        if not num_cols: return None
        ycol = num_cols[0]
        fig, ax = plt.subplots(figsize=(7, 3))
        if date_cols:
            tmp = df[[date_cols[0], ycol]].dropna().sort_values(date_cols[0])
            ax.plot(tmp[date_cols[0]], tmp[ycol], color="#7c3aed", linewidth=1.6, zorder=3)
            ax.fill_between(tmp[date_cols[0]], tmp[ycol], alpha=0.12, color="#7c3aed")
        else:
            s = df[ycol].dropna().reset_index(drop=True)
            ax.plot(s.index, s.values, color="#7c3aed", linewidth=1.6, zorder=3)
            ax.fill_between(s.index, s.values, alpha=0.12, color="#7c3aed")
        _mpl_style(ax, title=f"{ycol} — Trend", ylabel=ycol)
        fig.tight_layout(); return _buf_from_fig(fig)
    except Exception: return None

def _make_bar_chart(df):
    try:
        cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        fig, ax = plt.subplots(figsize=(7, 3))
        if cat_cols:
            col = cat_cols[0]; vc = df[col].value_counts().head(10)
            colors = ["#3b82f6" if i % 2 == 0 else "#60a5fa" for i in range(len(vc))]
            ax.bar(range(len(vc)), vc.values, color=colors, zorder=3, edgecolor="none")
            ax.set_xticks(range(len(vc)))
            ax.set_xticklabels([str(x)[:12] for x in vc.index], rotation=35, ha="right", fontsize=7)
            _mpl_style(ax, title=f"{col} — Distribution", ylabel="Count")
        elif len(num_cols) >= 2:
            col = num_cols[1]
            vals, edges = np.histogram(df[col].dropna(), bins=12)
            ax.bar(edges[:-1], vals, width=np.diff(edges)*0.9, color="#3b82f6", zorder=3, edgecolor="none")
            _mpl_style(ax, title=f"{col} — Histogram", xlabel=col, ylabel="Frequency")
        else: return None
        fig.tight_layout(); return _buf_from_fig(fig)
    except Exception: return None

def _make_corr_heatmap(df):
    try:
        import matplotlib.colors as mcolors
        num_cols = df.select_dtypes(include=np.number).columns.tolist()[:8]
        if len(num_cols) < 2: return None
        corr = df[num_cols].corr().round(2)
        fig, ax = plt.subplots(figsize=(7, 4.5))
        cmap = mcolors.LinearSegmentedColormap.from_list("dm", ["#1e1040","#4c1d95","#7c3aed","#c4b5fd","#ede9fe"])
        im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(num_cols))); ax.set_yticks(range(len(num_cols)))
        ax.set_xticklabels([c[:10] for c in num_cols], rotation=35, ha="right", fontsize=7)
        ax.set_yticklabels([c[:10] for c in num_cols], fontsize=7)
        for i in range(len(num_cols)):
            for j in range(len(num_cols)):
                v = corr.values[i,j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=6.5, color="white" if abs(v)>0.3 else "#1e293b")
        plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
        _mpl_style(ax, title="Correlation Matrix")
        fig.tight_layout(); return _buf_from_fig(fig)
    except Exception: return None

def _make_boxplot(df):
    try:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()[:5]
        if not num_cols: return None
        data = [df[c].dropna().values for c in num_cols]
        fig, ax = plt.subplots(figsize=(7, 3.5))
        bp = ax.boxplot(data, patch_artist=True, medianprops=dict(color="white", linewidth=2))
        for i, patch in enumerate(bp["boxes"]):
            patch.set_facecolor(_PAL[i % len(_PAL)]); patch.set_alpha(0.75)
        for el in ["whiskers","caps","fliers"]:
            for item in bp[el]: item.set_color("#64748b"); item.set_linewidth(0.8)
        ax.set_xticks(range(1, len(num_cols)+1))
        ax.set_xticklabels([c[:12] for c in num_cols], rotation=20, ha="right", fontsize=7.5)
        _mpl_style(ax, title="Statistical Distribution (Box Plot)")
        fig.tight_layout(); return _buf_from_fig(fig)
    except Exception: return None

def _make_scatter(df):
    try:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        if len(num_cols) < 2: return None
        xcol, ycol = num_cols[0], num_cols[1]
        sample = df[[xcol,ycol]].dropna().sample(min(1500,len(df)), random_state=42)
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.scatter(sample[xcol], sample[ycol], alpha=0.35, s=12, color="#7c3aed", edgecolors="none", zorder=3)
        z = np.polyfit(sample[xcol], sample[ycol], 1); p = np.poly1d(z)
        xs = np.linspace(sample[xcol].min(), sample[xcol].max(), 100)
        ax.plot(xs, p(xs), color="#d97706", linewidth=1.5, zorder=4, label="Trend")
        ax.legend(fontsize=7, framealpha=0)
        _mpl_style(ax, title=f"{xcol} vs {ycol}", xlabel=xcol, ylabel=ycol)
        fig.tight_layout(); return _buf_from_fig(fig)
    except Exception: return None

def _make_donut(df):
    try:
        cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
        if not cat_cols: return None
        col = cat_cols[0]; vc = df[col].value_counts().head(7)
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.pie(vc.values, labels=[str(x)[:14] for x in vc.index], autopct="%1.1f%%",
               colors=_PAL[:len(vc)], startangle=90,
               wedgeprops=dict(width=0.55, edgecolor="white", linewidth=0.8),
               textprops=dict(fontsize=7, color="#1e293b"))
        ax.set_title(f"{col} — Composition", color="#1e293b", fontsize=9, fontweight="bold", pad=8)
        fig.patch.set_facecolor("#ffffff"); fig.tight_layout(); return _buf_from_fig(fig)
    except Exception: return None

def _make_topn_bar(df):
    try:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
        if not num_cols or not cat_cols: return None
        ncol, ccol = num_cols[0], cat_cols[0]
        top = df.groupby(ccol)[ncol].mean().nlargest(8)
        fig, ax = plt.subplots(figsize=(7, 3))
        colors = [plt.cm.Purples(0.4 + 0.6*i/len(top)) for i in range(len(top))]
        ax.barh(range(len(top)), top.values, color=colors, edgecolor="none", zorder=3)
        ax.set_yticks(range(len(top)))
        ax.set_yticklabels([str(x)[:16] for x in top.index], fontsize=7.5)
        ax.invert_yaxis()
        _mpl_style(ax, title=f"Top {ccol} by Avg {ncol}", xlabel=f"Avg {ncol}")
        fig.tight_layout(); return _buf_from_fig(fig)
    except Exception: return None

def _make_forecast_mpl(df):
    try:
        from scipy import stats as sp_stats
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        if not num_cols: return None
        ycol = num_cols[0]; y = df[ycol].dropna().values
        if len(y) < 10: return None
        x = np.arange(len(y))
        slope, intercept, r, p, se = sp_stats.linregress(x, y)
        future_n = max(10, len(x)//5)
        xf = np.arange(len(x), len(x)+future_n)
        yf = slope * xf + intercept
        ci = 1.96 * se * np.sqrt(1 + 1/len(x) + (xf - x.mean())**2 / np.sum((x-x.mean())**2))
        fig, ax = plt.subplots(figsize=(7, 3.2))
        ax.plot(x, y, color="#94a3b8", linewidth=1, alpha=0.6, label="Actual", zorder=2)
        ax.plot(x, slope*x+intercept, color="#7c3aed", linewidth=1.8, label="Fit", zorder=3)
        ax.plot(xf, yf, color="#7c3aed", linewidth=2, linestyle="--", label="Forecast", zorder=3)
        ax.fill_between(xf, yf-ci, yf+ci, alpha=0.15, color="#7c3aed", label="95% CI")
        ax.axvline(len(x)-1, color="#d97706", linewidth=0.8, linestyle=":", label="Now")
        ax.legend(fontsize=7, framealpha=0, ncol=3)
        _mpl_style(ax, title=f"{ycol} — Linear Regression Forecast", ylabel=ycol)
        fig.tight_layout(); return _buf_from_fig(fig)
    except Exception: return None

# ─────────────────────────────────────────────
# COVER PAGE
# ─────────────────────────────────────────────

def _build_cover(story: list, title: str, company: str, analyst: str,
                 filename: str, df: pd.DataFrame, tone: str,
                 industry: str, health_score: int, health_grade: str,
                 S: dict):
    W, H = A4

    # ── Full-page dark gradient block ──
    items_in_block = []
    items_in_block.append(Spacer(1, 22 * mm))

    # Eyebrow
    items_in_block.append(Paragraph("◈  DATAMIND AI  ·  POWERED BY GROQ LLAMA 3.3 · 70B", S["cover_eyebrow"]))
    items_in_block.append(Spacer(1, 8 * mm))

    # Title
    items_in_block.append(Paragraph(title, S["cover_title"]))
    items_in_block.append(Spacer(1, 3 * mm))
    items_in_block.append(Paragraph("AI-Generated Business Intelligence Report", S["cover_subtitle"]))
    items_in_block.append(Spacer(1, 6 * mm))

    # Divider line
    items_in_block.append(HRFlowable(
        width="55%", thickness=1, color=HexColor("#4c1d95"),
        spaceAfter=6, hAlign="CENTRE",
    ))

    # Meta
    items_in_block.append(Paragraph(
        f"Organisation: <b>{company}</b>   ·   Analyst: <b>{analyst}</b>   ·   Tone: <b>{tone}</b>",
        S["cover_meta"],
    ))
    items_in_block.append(Paragraph(
        f"Industry: <b>{industry}</b>   ·   Generated: <b>{datetime.now().strftime('%d %B %Y, %H:%M')}</b>",
        S["cover_meta"],
    ))
    items_in_block.append(Paragraph(
        f"Source file: {filename}",
        S["cover_meta"],
    ))
    items_in_block.append(Spacer(1, 10 * mm))

    # Health badge on cover
    health_colours = {
        "Excellent": "#16a34a", "Good": "#2563eb",
        "Fair": "#d97706", "Poor": "#dc2626",
    }
    hc = health_colours.get(health_grade, "#6d28d9")
    items_in_block.append(
        Table([[Paragraph(
            f'<font color="{hc}">◉</font>  Data Health: <b><font color="{hc}">{health_grade}</font></b> &nbsp; ({health_score}/100)',
            ParagraphStyle("hbadge", fontName="Helvetica-Bold", fontSize=9,
                           textColor=HexColor("#94a3b8"), alignment=TA_CENTER),
        )]], colWidths=[100 * mm])
    )
    items_in_block.append(Spacer(1, 10 * mm))

    cover_block = Table(
        [[item] for item in items_in_block],
        colWidths=[W],
    )
    cover_block.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), INK),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("ALIGN",         (0, 0), (-1, -1), "CENTRE"),
    ]))
    story.append(cover_block)

    # ── KPI tiles ──
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()
    miss_pct     = round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 1)
    dup_count    = int(df.duplicated().sum())

    story.append(Spacer(1, 6 * mm))
    story.append(_kpi_row([
        ("◻", f"{df.shape[0]:,}",     "Total Rows"),
        ("◻", str(df.shape[1]),        "Columns"),
        ("◻", str(len(numeric_cols)),  "Numeric"),
        ("◻", str(len(cat_cols)),      "Categorical"),
        ("◻", f"{miss_pct}%",          "Missing"),
        ("◻", str(dup_count),          "Duplicates"),
    ], S))
    story.append(Spacer(1, 8 * mm))

    # ── Table of Contents ──
    toc_hdr = Table([[
        Paragraph("Table of Contents",
                  ParagraphStyle("tochdr", fontName="Helvetica-Bold", fontSize=12,
                                 textColor=DARK, spaceAfter=0)),
    ]], colWidths=[W - 40 * mm])
    toc_hdr.setStyle(TableStyle([
        ("LINEBELOW",     (0, 0), (-1, -1), 2, PURPLE),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(toc_hdr)
    story.append(Spacer(1, 3 * mm))

    sections = [
        ("01", "Executive Summary",        "Overview of dataset scope, patterns, and business implications"),
        ("02", "Key Findings",             "Five data-driven insights with specific metrics"),
        ("03", "Charts & Visualisations",  "Trend, distribution, correlation, and composition charts"),
        ("04", "Statistical Summary",      "Descriptive statistics and correlation analysis"),
        ("05", "Anomalies & Data Quality", "Outliers, missing data, skewness, and data health"),
        ("06", "Actionable Recommendations","Five strategic actions based on the analysis"),
        ("07", "Appendix — Column Profiles","Per-column numeric and categorical breakdowns"),
    ]
    toc_rows = [[
        Paragraph(num, S["toc_num"]),
        Paragraph(f"<b>{name}</b>", S["toc_title"]),
        Paragraph(desc, S["body_small"]),
    ] for num, name, desc in sections]

    toc_t = Table(toc_rows, colWidths=[12 * mm, 52 * mm, W - 40 * mm - 64 * mm])
    toc_t.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [white, ROW_ALT]),
    ]))
    story.append(toc_t)


# ─────────────────────────────────────────────
# SECTION BUILDERS
# ─────────────────────────────────────────────

def _build_exec_summary(story: list, text: str, S: dict):
    story.extend(_section_header("1", "Executive Summary", S))
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    for i, para in enumerate(paras):
        story.append(Paragraph(para, S["body"]))
        if i < len(paras) - 1:
            story.append(Spacer(1, 3 * mm))


def _build_key_findings(story: list, text: str, S: dict):
    story.extend(_section_header("2", "Key Findings", S))
    lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 4]
    for line in lines:
        is_numbered = len(line) > 1 and line[0].isdigit()
        if is_numbered and ":" in line:
            parts = line.split(":", 1)
            t = parts[0].strip().lstrip("0123456789. ").strip("*").strip()
            b = parts[1].strip() if len(parts) > 1 else ""
            story.append(KeepTogether([
                _card(t, b, S, bar=PURPLE, bg=PURPLE_LT),
                Spacer(1, 3 * mm),
            ]))
        elif is_numbered:
            story.append(_card("", line, S, bar=PURPLE, bg=PURPLE_LT))
            story.append(Spacer(1, 3 * mm))
        else:
            story.append(_card("", line, S, bar=BORDER, bg=ROW_ALT))
            story.append(Spacer(1, 2 * mm))


def _build_charts_section(story: list, charts: list, forecast_fig, S: dict,
                          df: pd.DataFrame = None):
    story.extend(_section_header("3", "Charts & Visualisations", S))

    if df is None or df.empty:
        story.append(Paragraph("No dataset available for chart generation.", S["body"]))
        return

    # Generate all charts using matplotlib (works on all servers)
    chart_funcs = [
        (_make_trend_chart,   "Trend Over Time"),
        (_make_bar_chart,     "Category Distribution"),
        (_make_corr_heatmap,  "Correlation Matrix"),
        (_make_boxplot,       "Statistical Distribution"),
        (_make_scatter,       "Scatter Analysis"),
        (_make_donut,         "Composition Breakdown"),
        (_make_topn_bar,      "Top Segments by Average"),
    ]

    generated = 0
    i = 0
    while i < len(chart_funcs):
        fn, label = chart_funcs[i]
        # Side-by-side for trend + bar (first two)
        if i == 0 and i + 1 < len(chart_funcs):
            fn2, label2 = chart_funcs[i+1]
            buf_a = fn(df)
            buf_b = fn2(df)
            if buf_a and buf_b:
                pw = 74
                def _cell(buf, lbl, pw=pw, S=S):
                    if not buf: return [Paragraph(f"[{lbl}]", S["caption"])]
                    img = Image(buf, width=pw*mm, height=68*mm)
                    img.hAlign = "CENTRE"
                    return [img, Paragraph(lbl, S["caption"])]
                pair = Table([[_cell(buf_a, label), _cell(buf_b, label2)]],
                             colWidths=[(pw+3)*mm, (pw+3)*mm])
                pair.setStyle(TableStyle([
                    ("VALIGN",      (0,0),(-1,-1),"TOP"),
                    ("LEFTPADDING", (0,0),(-1,-1),2),
                    ("RIGHTPADDING",(0,0),(-1,-1),2),
                    ("LINEAFTER",   (0,0),(0,-1), 0.3, BORDER),
                ]))
                story.append(pair)
                story.append(Spacer(1, 5*mm))
                generated += 2; i += 2
                continue
        # Full-width for correlation, boxplot, forecast
        buf = fn(df)
        if buf:
            story.extend(_chart_img(buf, label, S, 155,
                         88 if fn in (_make_corr_heatmap, _make_boxplot) else 75))
            generated += 1
        i += 1

    # Forecast chart — full width
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    fc_buf = _make_forecast_mpl(df)
    if fc_buf:
        story.append(Paragraph("Trend Forecast (Linear Regression)", S["card_title"]))
        story.append(Spacer(1, 2*mm))
        story.extend(_chart_img(fc_buf, "Linear regression with 95% confidence band", S, 155, 80))
        generated += 1

    if generated == 0:
        story.append(Paragraph("Charts could not be generated for this dataset.", S["body"]))

def _build_statistical_summary(story: list, df: pd.DataFrame,
                                stats_summary: dict, S: dict):
    story.extend(_section_header("4", "Statistical Summary", S))

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        story.append(Paragraph("No numeric columns found.", S["body"]))
        return

    # Descriptive stats table (up to 6 cols)
    cols6 = numeric_cols[:6]
    desc  = df[cols6].describe().round(2)
    avail = A4[0] - 40 * mm
    cw    = [26 * mm] + [(avail - 26 * mm) / len(cols6)] * len(cols6)

    story.append(_data_table(
        ["Statistic"] + [str(c) for c in cols6],
        [[str(idx)] + [str(desc.loc[idx, c]) for c in cols6] for idx in desc.index],
        S, col_widths=cw,
    ))
    story.append(Spacer(1, 5 * mm))

    # If more than 6 columns, show the rest
    if len(numeric_cols) > 6:
        extra = numeric_cols[6:]
        desc2 = df[extra].describe().round(2)
        cw2   = [26 * mm] + [(avail - 26 * mm) / len(extra)] * len(extra)
        story.append(Paragraph("<b>Additional Numeric Columns</b>", S["card_title"]))
        story.append(Spacer(1, 2 * mm))
        story.append(_data_table(
            ["Statistic"] + [str(c) for c in extra],
            [[str(idx)] + [str(desc2.loc[idx, c]) for c in extra] for idx in desc2.index],
            S, col_widths=cw2,
        ))
        story.append(Spacer(1, 5 * mm))

    # Strong correlations
    corrs = stats_summary.get("strong_correlations", [])
    if corrs:
        story.append(Paragraph("<b>Notable Correlations</b>", S["card_title"]))
        story.append(Spacer(1, 2 * mm))
        cw_c = [avail * p for p in [0.28, 0.28, 0.22, 0.22]]
        story.append(_data_table(
            ["Column A", "Column B", "Pearson r", "Strength"],
            [[c["col1"], c["col2"], str(c["r"]), c["strength"]] for c in corrs[:10]],
            S, col_widths=cw_c, accent=BLUE,
        ))


def _build_anomalies(story: list, text: str, anomalies: dict, S: dict):
    story.extend(_section_header("5", "Anomalies & Data Quality", S))

    paras = [p.strip() for p in text.split("\n") if p.strip()]
    for para in paras:
        lo = para.lower()
        if any(w in lo for w in ["critical", "extreme", "major", "significant"]):
            bar, bg = RED, RED_LT
        elif any(w in lo for w in ["moderate", "warning", "missing", "outlier", "duplicate", "skew"]):
            bar, bg = AMBER, AMBER_LT
        else:
            bar, bg = GREEN, GREEN_LT
        story.append(_card("", para, S, bar=bar, bg=bg))
        story.append(Spacer(1, 3 * mm))

    # Outlier table
    outliers = anomalies.get("outliers", {})
    if outliers:
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph("<b>Outlier Summary — IQR Method</b>", S["card_title"]))
        story.append(Spacer(1, 2 * mm))
        avail = A4[0] - 40 * mm
        story.append(_data_table(
            ["Column", "Count", "Outlier %", "Lower Bound", "Upper Bound", "Data Max"],
            [[col, str(v["count"]), f"{v['pct']}%",
              str(v["lower_bound"]), str(v["upper_bound"]), str(v["extreme_max"])]
             for col, v in outliers.items()],
            S,
            col_widths=[avail * p for p in [0.22, 0.13, 0.13, 0.18, 0.18, 0.16]],
            accent=AMBER,
        ))

    # Other flags
    const      = anomalies.get("constant_columns", [])
    high_miss  = anomalies.get("high_missing", [])
    skewed     = anomalies.get("high_skewness", {})

    flags = []
    if const:
        flags.append(["Constant Columns", ", ".join(const)])
    if high_miss:
        flags.append(["High Missing (>20%)", ", ".join(high_miss)])
    for col, sk in skewed.items():
        flags.append([f"High Skewness — {col}", f"Skewness: {sk}"])

    if flags:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("<b>Additional Data Quality Flags</b>", S["card_title"]))
        story.append(Spacer(1, 2 * mm))
        avail = A4[0] - 40 * mm
        story.append(_data_table(
            ["Flag", "Detail"], flags, S,
            col_widths=[avail * 0.38, avail * 0.62],
            accent=RED,
        ))


def _build_recommendations(story: list, text: str, S: dict):
    story.extend(_section_header("6", "Actionable Recommendations", S))
    lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 4]
    for line in lines:
        is_numbered = len(line) > 1 and line[0].isdigit()
        if is_numbered and ":" in line:
            parts = line.split(":", 1)
            t = parts[0].strip().lstrip("0123456789. ").strip("*").strip()
            b = parts[1].strip() if len(parts) > 1 else ""
            story.append(KeepTogether([
                _card(t, b, S, bar=GREEN, bg=GREEN_LT),
                Spacer(1, 3 * mm),
            ]))
        else:
            story.append(_card("", line, S, bar=GREEN, bg=GREEN_LT))
            story.append(Spacer(1, 3 * mm))


def _build_appendix(story: list, df: pd.DataFrame, stats_summary: dict, S: dict):
    story.extend(_section_header("7", "Appendix — Column Profiles", S))

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()
    key_stats    = stats_summary.get("key_stats", {})
    cat_stats    = stats_summary.get("cat_stats", {})
    avail        = A4[0] - 40 * mm

    if numeric_cols and key_stats:
        story.append(Paragraph("<b>Numeric Column Profiles</b>", S["card_title"]))
        story.append(Spacer(1, 2 * mm))
        rows = []
        for col in numeric_cols:
            if col not in key_stats:
                continue
            st = key_stats[col]
            rows.append([
                col, str(st["mean"]), str(st["median"]), str(st["std"]),
                str(st["min"]), str(st["max"]), str(st["skew"]),
                f"{st['cv']}%" if "cv" in st else "—",
                f"{st['missing_pct']}%",
            ])
        cw = [avail * p for p in [0.17, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.10, 0.09]]
        story.append(_data_table(
            ["Column", "Mean", "Median", "Std Dev", "Min", "Max", "Skew", "CV%", "Missing%"],
            rows, S, col_widths=cw,
        ))
        story.append(Spacer(1, 6 * mm))

    if cat_cols and cat_stats:
        story.append(Paragraph("<b>Categorical Column Profiles</b>", S["card_title"]))
        story.append(Spacer(1, 2 * mm))
        rows = []
        for col in cat_cols:
            if col not in cat_stats:
                continue
            st = cat_stats[col]
            rows.append([
                col, str(st["unique"]), str(st["top"]),
                str(st["top_count"]), f"{st['top_pct']}%", f"{st['missing_pct']}%",
            ])
        cw = [avail * p for p in [0.22, 0.14, 0.28, 0.13, 0.11, 0.12]]
        story.append(_data_table(
            ["Column", "Unique", "Top Value", "Top Count", "Top %", "Missing%"],
            rows, S, col_widths=cw, accent=BLUE,
        ))


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def generate_pdf_report(
    title: str,
    company: str,
    analyst: str,
    filename: str,
    df: pd.DataFrame,
    exec_summary: str,
    key_findings: str,
    anomaly_narrative: str,
    recommendations: str,
    stats_summary: dict,
    anomalies: dict,
    charts: list,
    forecast_fig=None,
    tone: str = "Professional",
    industry: str = "General",
    health_score: int = 0,
    health_grade: str = "Good",
) -> bytes:
    """
    Build and return the complete premium PDF as bytes.
    Charts are embedded if kaleido is installed; otherwise a placeholder is shown.
    """
    buf = io.BytesIO()
    S   = _styles()

    doc = BaseDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
        author=analyst,
        subject=f"{company} — Business Intelligence Report",
        creator="DataMind AI",
        keywords="AI, analytics, business intelligence, data",
    )

    cover_tpl = _cover_tpl(doc)
    body_tpl  = _body_tpl(doc, title)
    doc.addPageTemplates([cover_tpl, body_tpl])

    story: list = []

    # ── Cover ──────────────────────────────────────
    story.append(NextPageTemplate("Cover"))
    _build_cover(
        story, title, company, analyst, filename, df,
        tone, industry, health_score, health_grade, S,
    )

    # ── Switch to body ──────────────────────────────
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    _build_exec_summary(story, exec_summary, S)
    story.append(PageBreak())

    _build_key_findings(story, key_findings, S)
    story.append(PageBreak())

    _build_charts_section(story, charts, forecast_fig, S, df=df)
    story.append(PageBreak())

    _build_statistical_summary(story, df, stats_summary, S)
    story.append(PageBreak())

    _build_anomalies(story, anomaly_narrative, anomalies, S)
    story.append(PageBreak())

    _build_recommendations(story, recommendations, S)
    story.append(PageBreak())

    _build_appendix(story, df, stats_summary, S)

    doc.build(story)
    buf.seek(0)
    return buf.read()
