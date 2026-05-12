"""
DataMind AI — Premium Business Intelligence Platform
app.py — Main Streamlit application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from groq import Groq
import json
import io
import os
from datetime import datetime
from report_generator import generate_pdf_report
from data_analyzer import analyze_dataframe, detect_anomalies, get_column_insights

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataMind AI — Intelligence Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f !important;
    color: #e2e8f0;
}
.stApp { background: #0a0a0f; }
section[data-testid="stSidebar"] { background: #0f0f1a !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stSelectbox select { background: #1a1a2e !important; border-color: rgba(255,255,255,0.1) !important; color: #e2e8f0 !important; }

/* ── HERO ── */
.dm-hero {
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #0f0c29 0%, #1a1040 40%, #0d1b3e 100%);
    border-radius: 24px; padding: 4rem 3rem 3.5rem;
    text-align: center; margin-bottom: 2.5rem;
    border: 1px solid rgba(139,92,246,0.2);
    box-shadow: 0 0 80px rgba(139,92,246,0.08), inset 0 1px 0 rgba(255,255,255,0.05);
}
.dm-hero::before {
    content: ''; position: absolute; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at 60% 20%, rgba(139,92,246,0.12) 0%, transparent 60%),
                radial-gradient(ellipse at 20% 80%, rgba(59,130,246,0.08) 0%, transparent 50%);
    pointer-events: none;
}
.dm-hero-eyebrow {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.3);
    color: #a78bfa; font-size: 0.7rem; font-weight: 600; letter-spacing: 3px;
    text-transform: uppercase; padding: 0.4rem 1.2rem;
    border-radius: 999px; margin-bottom: 1.5rem;
}
.dm-hero h1 {
    font-family: 'DM Serif Display', serif; font-size: 3.5rem;
    color: #f8fafc; margin: 0 0 1rem; line-height: 1.1; letter-spacing: -1px;
}
.dm-hero h1 em { font-style: italic; color: #a78bfa; }
.dm-hero p { color: rgba(255,255,255,0.5); font-size: 1.05rem; margin: 0 auto 2rem; max-width: 520px; line-height: 1.7; }
.dm-hero-features { display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; }
.dm-hero-feature {
    display: flex; align-items: center; gap: 0.5rem;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.6); font-size: 0.8rem; font-weight: 500;
    padding: 0.45rem 1rem; border-radius: 10px;
}

/* ── KPI CARDS ── */
.kpi-strip { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 2rem; }
.kpi-card {
    background: #111118; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 1.4rem 1.2rem; text-align: center;
    position: relative; overflow: hidden;
    transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-4px); border-color: rgba(139,92,246,0.4); box-shadow: 0 12px 32px rgba(139,92,246,0.1); }
.kpi-card::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #8b5cf6, #3b82f6); opacity: 0.6;
}
.kpi-icon { font-size: 1.5rem; margin-bottom: 0.5rem; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 2.2rem; color: #f8fafc; line-height: 1; margin-bottom: 0.3rem; }
.kpi-label { font-size: 0.68rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

/* ── HEALTH SCORE ── */
.health-panel {
    display: flex; align-items: center; gap: 2rem;
    border-radius: 18px; padding: 1.75rem 2.25rem; margin-bottom: 2rem;
    border: 1px solid; position: relative; overflow: hidden;
}
.health-excellent { background: linear-gradient(135deg, #052e16, #0a3622); border-color: #16a34a; }
.health-good      { background: linear-gradient(135deg, #0c1a3a, #0f2550); border-color: #3b82f6; }
.health-fair      { background: linear-gradient(135deg, #2d1a00, #3d2400); border-color: #f59e0b; }
.health-poor      { background: linear-gradient(135deg, #2d0a0a, #3d1010); border-color: #ef4444; }
.health-ring {
    flex-shrink: 0; width: 80px; height: 80px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Serif Display', serif; font-size: 1.8rem; font-weight: 700;
    border: 3px solid currentColor;
}
.health-excellent .health-ring { color: #4ade80; }
.health-good      .health-ring { color: #60a5fa; }
.health-fair      .health-ring { color: #fbbf24; }
.health-poor      .health-ring { color: #f87171; }
.health-content h3 { margin: 0 0 0.3rem; font-size: 1.1rem; font-weight: 700; color: #f1f5f9; }
.health-content p  { margin: 0; font-size: 0.9rem; color: rgba(255,255,255,0.55); line-height: 1.6; }

/* ── SECTION HEADERS ── */
.dm-section {
    display: flex; align-items: center; gap: 0.75rem;
    margin: 2.5rem 0 1.25rem; padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.dm-section-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: linear-gradient(135deg, #8b5cf6, #3b82f6); flex-shrink: 0;
}
.dm-section h2 { margin: 0; font-size: 1.2rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.3px; }
.dm-section span { font-size: 0.8rem; color: #475569; font-weight: 400; margin-left: 0.25rem; }

/* ── CONTENT CARDS ── */
.dm-card {
    background: #111118; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 0.75rem;
    line-height: 1.8; color: #cbd5e1; font-size: 0.93rem;
    transition: border-color 0.2s;
}
.dm-card:hover { border-color: rgba(255,255,255,0.12); }
.dm-card-finding { border-left: 3px solid #8b5cf6; background: linear-gradient(to right, #1a1030, #111118); }
.dm-card-anomaly { border-left: 3px solid #f59e0b; background: linear-gradient(to right, #1e1500, #111118); }
.dm-card-reco    { border-left: 3px solid #10b981; background: linear-gradient(to right, #001a12, #111118); }
.dm-card-summary { border-left: 3px solid #3b82f6; background: linear-gradient(to right, #050f2a, #111118); }

/* ── NUMBERED BADGES ── */
.num-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; border-radius: 8px; font-size: 0.72rem; font-weight: 700;
    margin-right: 0.6rem; vertical-align: middle; flex-shrink: 0;
}
.num-badge-purple { background: rgba(139,92,246,0.2); color: #a78bfa; border: 1px solid rgba(139,92,246,0.3); }
.num-badge-green  { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }

/* ── SEVERITY BADGES ── */
.sev-badge {
    display: inline-block; font-size: 0.65rem; font-weight: 700;
    padding: 0.15rem 0.55rem; border-radius: 6px;
    text-transform: uppercase; letter-spacing: 0.8px; margin-left: 0.5rem; vertical-align: middle;
}
.sev-high   { background: rgba(239,68,68,0.15);   color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.sev-medium { background: rgba(245,158,11,0.15);  color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.sev-low    { background: rgba(16,185,129,0.15);  color: #34d399; border: 1px solid rgba(16,185,129,0.3); }

/* ── FINDING TITLE ── */
.finding-title { font-weight: 700; color: #e2e8f0; font-size: 0.98rem; display: block; margin-bottom: 0.3rem; }
.finding-body  { color: #94a3b8; font-size: 0.9rem; line-height: 1.75; }

/* ── CHAT ── */
.chat-wrap { background: #0c0c14; border: 1px solid rgba(255,255,255,0.06); border-radius: 18px; padding: 1.5rem; margin-bottom: 1rem; max-height: 500px; overflow-y: auto; }
.chat-user { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
.chat-user .bubble { background: linear-gradient(135deg, #6d28d9, #4c1d95); color: white; padding: 0.8rem 1.2rem; border-radius: 18px 18px 4px 18px; max-width: 72%; font-size: 0.9rem; line-height: 1.5; box-shadow: 0 4px 12px rgba(109,40,217,0.3); }
.chat-ai { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
.chat-avatar { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #8b5cf6, #3b82f6); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; flex-shrink: 0; color: white; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.chat-ai .bubble { background: #161622; border: 1px solid rgba(255,255,255,0.08); color: #cbd5e1; padding: 0.8rem 1.2rem; border-radius: 4px 18px 18px 18px; max-width: 78%; font-size: 0.9rem; line-height: 1.7; }
.chat-pill { display: inline-block; background: #151520; border: 1px solid rgba(139,92,246,0.25); color: #a78bfa; font-size: 0.78rem; padding: 0.35rem 0.9rem; border-radius: 999px; margin: 0.2rem; cursor: pointer; transition: all 0.15s; }
.chat-pill:hover { background: rgba(139,92,246,0.15); border-color: rgba(139,92,246,0.5); }

/* ── FORECAST BADGE ── */
.fc-badge { display: inline-block; background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.25); color: #a78bfa; font-size: 0.68rem; font-weight: 700; padding: 0.2rem 0.7rem; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.5px; margin-left: 0.5rem; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    padding: 0.9rem 2rem !important; font-weight: 700 !important; font-size: 0.95rem !important;
    width: 100% !important; transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important; letter-spacing: 0.3px !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 28px rgba(124,58,237,0.45) !important; }
.dl-btn .stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    box-shadow: 0 4px 20px rgba(5,150,105,0.3) !important;
}
.dl-btn .stDownloadButton > button:hover { box-shadow: 0 8px 28px rgba(5,150,105,0.45) !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] { background: #0e0e18 !important; border-radius: 14px !important; padding: 4px !important; gap: 2px !important; border: 1px solid rgba(255,255,255,0.06) !important; }
.stTabs [data-baseweb="tab"] { border-radius: 10px !important; color: #64748b !important; font-weight: 600 !important; font-size: 0.85rem !important; padding: 0.55rem 1.1rem !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important; box-shadow: 0 4px 12px rgba(124,58,237,0.3) !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0 0 !important; }

/* ── EXPANDERS ── */
div[data-testid="stExpander"] { background: #0f0f1a !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 14px !important; margin-bottom: 0.5rem !important; }
div[data-testid="stExpander"] summary { color: #e2e8f0 !important; font-weight: 600 !important; }

/* ── INPUTS ── */
.stTextInput input, .stSelectbox > div > div, .stFileUploader { background: #0f0f1a !important; border-color: rgba(255,255,255,0.1) !important; color: #e2e8f0 !important; border-radius: 10px !important; }
.stTextInput label, .stSelectbox label, .stFileUploader label { color: #94a3b8 !important; font-size: 0.82rem !important; font-weight: 600 !important; }

/* ── DATAFRAME ── */
.stDataFrame { background: #0f0f1a !important; border-radius: 14px !important; border: 1px solid rgba(255,255,255,0.07) !important; }

/* ── ALERTS ── */
.stAlert { background: #0f0f1a !important; border-radius: 12px !important; border-left-width: 3px !important; }
.stSuccess { border-left-color: #10b981 !important; }
.stInfo    { border-left-color: #3b82f6 !important; }
.stWarning { border-left-color: #f59e0b !important; }
.stError   { border-left-color: #ef4444 !important; }

/* ── PROGRESS ── */
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #3b82f6) !important; border-radius: 999px !important; }

/* ── FOOTER ── */
.dm-footer {
    text-align: center; margin-top: 4rem; padding: 2rem;
    border-top: 1px solid rgba(255,255,255,0.06);
    color: #334155; font-size: 0.78rem;
}
.dm-footer strong { color: #475569; }

/* ── SIDEBAR BRANDING ── */
.sb-brand { padding: 0.5rem 0 1.5rem; }
.sb-brand h2 { font-family: 'DM Serif Display', serif; font-size: 1.6rem; color: #f1f5f9 !important; margin: 0; letter-spacing: -0.5px; }
.sb-brand p { font-size: 0.75rem; color: #475569 !important; margin: 0.2rem 0 0; }
.sb-divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 1rem 0; }
.sb-label { font-size: 0.68rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; color: #475569 !important; margin-bottom: 0.5rem !important; display: block; }

/* ── UPLOAD AREA ── */
.upload-zone {
    background: linear-gradient(135deg, #0a0a18, #0f0f20);
    border: 2px dashed rgba(139,92,246,0.3);
    border-radius: 20px; padding: 4rem 2rem; text-align: center; margin-top: 1rem;
    transition: border-color 0.2s;
}
.upload-zone:hover { border-color: rgba(139,92,246,0.6); }
.upload-zone h3 { color: #a78bfa; font-family: 'DM Serif Display', serif; font-size: 1.5rem; margin: 0.5rem 0 0.25rem; }
.upload-zone p { color: #475569; font-size: 0.88rem; margin: 0; }

/* ── STAT TABLE STYLING ── */
.stDataFrame thead th { background: rgba(139,92,246,0.2) !important; color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────────────────────
def init_groq(api_key):
    return Groq(api_key=api_key)


def call_groq(client, prompt, system="", max_tokens=1800):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.4,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def load_data(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding=enc)
            except Exception:
                continue
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")


def compute_health_score(df, anomalies):
    score = 100
    missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
    score -= min(30, missing_pct * 3)
    dupes = anomalies.get("duplicate_rows", {}).get("pct", 0)
    score -= min(20, dupes * 2)
    outlier_cols = len(anomalies.get("outliers", {}))
    score -= min(20, outlier_cols * 5)
    constant_cols = len(anomalies.get("constant_columns", []))
    score -= min(10, constant_cols * 5)
    score = max(0, round(score))
    if score >= 85:
        return score, "Excellent", "health-excellent"
    elif score >= 65:
        return score, "Good", "health-good"
    elif score >= 45:
        return score, "Fair", "health-fair"
    else:
        return score, "Poor", "health-poor"


# ── CHART BUILDER ─────────────────────────────────────────────────────────────
def build_charts(df):
    charts = []
    all_numeric = df.select_dtypes(include=np.number).columns.tolist()
    id_keywords = ["key", "id", "no", "number", "sr", "index", "code", "sku", "zip", "phone", "order"]
    numeric_cols = [c for c in all_numeric if not any(k == c.lower() or c.lower().endswith(k) for k in id_keywords)]
    if len(numeric_cols) < 2:
        numeric_cols = all_numeric
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = [c for c in df.columns if any(k in c.lower() for k in ["date", "time", "year", "month", "day"])]

    # Dark premium palette
    C1, C2, C3 = "#8b5cf6", "#3b82f6", "#10b981"
    COLORS = [C1, C2, C3, "#f59e0b", "#ec4899", "#06b6d4", "#84cc16"]
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,17,30,0.8)",
        font=dict(family="DM Sans", size=11, color="#94a3b8"),
        margin=dict(t=50, b=35, l=40, r=20),
        height=340,
    )

    # 1. Time series
    try:
        if date_cols and numeric_cols:
            for dc in date_cols:
                nc = numeric_cols[0]
                try:
                    tmp = df[[dc, nc]].dropna().copy()
                    tmp[dc] = pd.to_datetime(tmp[dc], errors="coerce")
                    tmp = tmp.dropna().sort_values(dc)
                    if len(tmp) > 2:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=tmp[dc], y=tmp[nc], mode="lines",
                            line=dict(color=C1, width=2.5, shape="spline"),
                            fill="tozeroy", fillcolor="rgba(139,92,246,0.08)",
                            name=nc, hovertemplate=f"<b>{nc}</b>: %{{y:,.2f}}<extra></extra>",
                        ))
                        fig.update_layout(
                            **base,
                            title=dict(text=f"<b>{nc}</b> over Time", font=dict(size=13, color="#e2e8f0"), x=0.02),
                        )
                        fig.update_xaxes(showgrid=False, linecolor="#1e1e2e", zeroline=False)
                        fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", linecolor="#1e1e2e", zeroline=False)
                        charts.append(("time_series", fig))
                        break
                except Exception:
                    pass
    except Exception:
        pass

    # 2. Bar — category vs numeric
    try:
        if cat_cols and numeric_cols:
            best_cat = next((c for c in cat_cols if 2 <= df[c].nunique() <= 15), None)
            if best_cat:
                nc = numeric_cols[0]
                agg = df.groupby(best_cat)[nc].mean().sort_values(ascending=False).head(12)
                fig = go.Figure(go.Bar(
                    x=agg.index.astype(str), y=agg.values,
                    marker=dict(
                        color=agg.values,
                        colorscale=[[0, "#1e1e3a"], [0.5, "#6d28d9"], [1, "#8b5cf6"]],
                        line=dict(width=0),
                    ),
                    hovertemplate="<b>%{x}</b><br>Avg: %{y:,.2f}<extra></extra>",
                ))
                fig.update_layout(
                    **base,
                    title=dict(text=f"Avg <b>{nc}</b> by {best_cat}", font=dict(size=13, color="#e2e8f0"), x=0.02),
                    bargap=0.35,
                )
                fig.update_xaxes(showgrid=False, linecolor="#1e1e2e")
                fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", linecolor="#1e1e2e")
                charts.append(("bar_cat", fig))
    except Exception:
        pass

    # 3. Correlation heatmap
    try:
        if len(numeric_cols) >= 2:
            cols_for_corr = numeric_cols[:8]
            corr = df[cols_for_corr].corr().round(2)
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.index,
                colorscale=[[0, "#1e0a3c"], [0.25, "#4c1d95"], [0.5, "#111118"],
                            [0.75, "#1d4ed8"], [1, "#3b82f6"]],
                zmid=0,
                text=corr.values,
                texttemplate="%{text:.2f}",
                textfont=dict(size=9, color="white"),
                showscale=True,
                colorbar=dict(
                    thickness=12, len=0.8,
                    tickfont=dict(color="#64748b", size=9),
                    outlinewidth=0,
                ),
            ))
            hbase = {**base, "height": 360}
            fig.update_layout(
                **hbase,
                title=dict(text="Correlation Matrix", font=dict(size=13, color="#e2e8f0"), x=0.02),
            )
            fig.update_xaxes(tickfont=dict(size=9), side="bottom", linecolor="#1e1e2e")
            fig.update_yaxes(tickfont=dict(size=9), linecolor="#1e1e2e")
            charts.append(("heatmap", fig))
    except Exception:
        pass

    # 4. Distribution violin
    try:
        if numeric_cols:
            target = numeric_cols[0]
            data = df[target].dropna()
            if len(data) > 5:
                fig = go.Figure()
                fig.add_trace(go.Violin(
                    y=data, name=target, box_visible=True, meanline_visible=True,
                    fillcolor="rgba(139,92,246,0.2)", line_color=C1,
                    meanline=dict(color="#f8fafc", width=2),
                    box=dict(fillcolor="rgba(139,92,246,0.35)", line_color=C1),
                    hoverinfo="y",
                ))
                fig.update_layout(
                    **base,
                    title=dict(text=f"<b>{target}</b> Distribution", font=dict(size=13, color="#e2e8f0"), x=0.02),
                    showlegend=False,
                )
                fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", linecolor="#1e1e2e")
                charts.append(("violin", fig))
    except Exception:
        pass

    # 5. Scatter
    try:
        if len(numeric_cols) >= 2:
            x_col, y_col = numeric_cols[0], numeric_cols[1]
            color_col = next((c for c in cat_cols if df[c].nunique() <= 8), None)
            sample = df.sample(min(2000, len(df)), random_state=42) if len(df) > 2000 else df
            fig = px.scatter(
                sample, x=x_col, y=y_col, color=color_col,
                color_discrete_sequence=COLORS, opacity=0.65,
            )
            fig.update_traces(marker=dict(size=7, line=dict(width=0.5, color="rgba(255,255,255,0.2)")))
            fig.update_layout(
                **base,
                title=dict(text=f"<b>{x_col}</b> vs <b>{y_col}</b>", font=dict(size=13, color="#e2e8f0"), x=0.02),
                legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
            )
            fig.update_xaxes(showgrid=False, linecolor="#1e1e2e", zeroline=False)
            fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", linecolor="#1e1e2e", zeroline=False)
            charts.append(("scatter", fig))
    except Exception:
        pass

    # 6. Donut / Pie
    try:
        if cat_cols and numeric_cols:
            for c in cat_cols:
                if 2 <= df[c].nunique() <= 8:
                    nc = numeric_cols[0]
                    agg = df.groupby(c)[nc].sum().sort_values(ascending=False)
                    fig = go.Figure(go.Pie(
                        values=agg.values, labels=agg.index.astype(str),
                        hole=0.55,
                        marker=dict(
                            colors=COLORS[:len(agg)],
                            line=dict(color="#0a0a0f", width=3),
                        ),
                        textfont=dict(size=10, color="white"),
                        hovertemplate="<b>%{label}</b><br>%{value:,.2f} (%{percent})<extra></extra>",
                    ))
                    fig.update_layout(
                        **base,
                        title=dict(text=f"<b>{nc}</b> by {c}", font=dict(size=13, color="#e2e8f0"), x=0.02),
                        showlegend=True,
                        legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
                        annotations=[dict(
                            text=f"<b>{nc}</b>", x=0.5, y=0.5,
                            font_size=11, font_color="#94a3b8",
                            showarrow=False,
                        )],
                    )
                    charts.append(("donut", fig))
                    break
    except Exception:
        pass

    # 7. Top-N bar (second categorical)
    try:
        if cat_cols and numeric_cols and len(cat_cols) > 1:
            for c in cat_cols[1:]:
                if 2 <= df[c].nunique() <= 20:
                    nc = numeric_cols[0]
                    agg = df.groupby(c)[nc].sum().sort_values(ascending=True).tail(10)
                    fig = go.Figure(go.Bar(
                        x=agg.values, y=agg.index.astype(str),
                        orientation="h",
                        marker=dict(
                            color=agg.values,
                            colorscale=[[0, "#0f2a3a"], [1, "#10b981"]],
                            line=dict(width=0),
                        ),
                        hovertemplate="<b>%{y}</b>: %{x:,.2f}<extra></extra>",
                    ))
                    fig.update_layout(
                        **base,
                        title=dict(text=f"Top {c} by <b>{nc}</b>", font=dict(size=13, color="#e2e8f0"), x=0.02),
                    )
                    fig.update_xaxes(showgrid=False, linecolor="#1e1e2e")
                    fig.update_yaxes(gridcolor="rgba(255,255,255,0.03)", linecolor="#1e1e2e")
                    charts.append(("top_n", fig))
                    break
    except Exception:
        pass

    return [fig for _, fig in charts[:7]]


# ── FORECAST BUILDER ──────────────────────────────────────────────────────────
def build_forecast_chart(df):
    date_cols = [c for c in df.columns if any(k in c.lower() for k in ["date", "time", "year", "month"])]
    all_numeric = df.select_dtypes(include=np.number).columns.tolist()
    id_keywords = ["key", "id", "no", "number", "sr", "index", "code", "sku", "zip", "phone", "order"]
    numeric_cols = [c for c in all_numeric if not any(k == c.lower() or c.lower().endswith(k) for k in id_keywords)]
    if not numeric_cols:
        numeric_cols = all_numeric
    if not date_cols or not numeric_cols:
        return None
    dc, nc = date_cols[0], numeric_cols[0]
    try:
        tmp = df[[dc, nc]].dropna().copy()
        tmp[dc] = pd.to_datetime(tmp[dc], errors="coerce")
        tmp = tmp.dropna().sort_values(dc)
        if len(tmp) < 4:
            return None
        tmp["x_num"] = (tmp[dc] - tmp[dc].min()).dt.days
        coeffs = np.polyfit(tmp["x_num"], tmp[nc], 1)
        last_x = tmp["x_num"].max()
        future_x = np.linspace(last_x, last_x * 1.35, 10)
        future_dates = tmp[dc].min() + pd.to_timedelta(future_x, unit="D")
        future_vals = np.polyval(coeffs, future_x)
        trend_vals = np.polyval(coeffs, tmp["x_num"])

        # Confidence band
        residuals = tmp[nc].values - trend_vals
        std_res = np.std(residuals)
        upper = future_vals + 1.5 * std_res
        lower = future_vals - 1.5 * std_res

        fig = go.Figure()
        # Confidence band
        fig.add_trace(go.Scatter(
            x=list(future_dates) + list(future_dates[::-1]),
            y=list(upper) + list(lower[::-1]),
            fill="toself", fillcolor="rgba(139,92,246,0.08)",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))
        # Actual
        fig.add_trace(go.Scatter(
            x=tmp[dc], y=tmp[nc], mode="lines",
            line=dict(color="#8b5cf6", width=2.5, shape="spline"),
            name="Actual", hovertemplate="%{x|%d %b %Y}: <b>%{y:,.2f}</b><extra></extra>",
        ))
        # Trend
        fig.add_trace(go.Scatter(
            x=tmp[dc], y=trend_vals, mode="lines",
            line=dict(color="#6d28d9", width=1.5, dash="dot"),
            name="Trend line", hoverinfo="skip",
        ))
        # Forecast
        fig.add_trace(go.Scatter(
            x=future_dates, y=future_vals, mode="lines+markers",
            name="Forecast",
            line=dict(color="#10b981", width=2.5, dash="dash"),
            marker=dict(size=8, symbol="diamond", color="#10b981",
                       line=dict(width=1.5, color="#f8fafc")),
            hovertemplate="%{x|%d %b %Y}: <b>%{y:,.2f}</b><extra></extra>",
        ))
        fig.add_vrect(
            x0=tmp[dc].max(), x1=future_dates.max(),
            fillcolor="rgba(16,185,129,0.04)", line_width=0,
            annotation_text="Forecast", annotation_position="top left",
            annotation_font=dict(size=10, color="#10b981"),
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,17,30,0.8)",
            font=dict(family="DM Sans", size=11, color="#94a3b8"),
            margin=dict(t=55, b=40, l=45, r=20), height=380,
            title=dict(text=f"<b>{nc}</b> — Linear Trend Forecast", font=dict(size=14, color="#e2e8f0"), x=0.02),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                       font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
        )
        fig.update_xaxes(showgrid=False, linecolor="#1e1e2e", zeroline=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", linecolor="#1e1e2e", zeroline=False)
        return fig
    except Exception:
        return None


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <h2>◈ DataMind</h2>
        <p>AI Business Intelligence Platform</p>
    </div>
    <hr class="sb-divider">
    """, unsafe_allow_html=True)

    st.markdown('<span class="sb-label">🔑 Groq API Key</span>', unsafe_allow_html=True)
    api_key = st.text_input(
        "API Key", type="password", placeholder="gsk_…",
        label_visibility="collapsed",
        help="Free key at console.groq.com — powers the AI analysis",
    )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<span class="sb-label">📂 Dataset</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload", type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
        help="CSV, XLSX, or XLS — any size",
    )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<span class="sb-label">⚙️ Report Settings</span>', unsafe_allow_html=True)
    report_title    = st.text_input("Report Title",    value="Business Intelligence Report")
    company_name    = st.text_input("Organisation",    value="My Organisation")
    analyst_name    = st.text_input("Prepared By",     value="Data Analyst")
    report_tone     = st.selectbox("Tone", ["Professional", "Executive", "Technical", "Simplified"])
    report_industry = st.selectbox("Industry", [
        "General", "Retail / E-Commerce", "Finance / Banking",
        "Healthcare", "Manufacturing", "SaaS / Tech", "HR / People Analytics",
        "Logistics & Supply Chain", "Real Estate",
    ])

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.75rem; color:#334155; line-height:1.9;">
        <b style="color:#475569;">How to use:</b><br>
        1 · Enter Groq API key<br>
        2 · Upload CSV / Excel<br>
        3 · Fill report settings<br>
        4 · Click Generate Report<br>
        5 · Chat with your data<br>
        6 · Download PDF
    </div>
    """, unsafe_allow_html=True)


# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dm-hero">
    <div class="dm-hero-eyebrow">◈ &nbsp; Groq LLaMA 3.3 · 70B</div>
    <h1>DataMind <em>AI</em></h1>
    <p>Upload any dataset and get a full AI-generated business intelligence report — executive summaries, insights, anomaly detection, forecasts, and a beautiful PDF in seconds.</p>
    <div class="dm-hero-features">
        <span class="dm-hero-feature">🤖 AI Executive Summary</span>
        <span class="dm-hero-feature">📊 Smart Visualisations</span>
        <span class="dm-hero-feature">🔮 Trend Forecasting</span>
        <span class="dm-hero-feature">⚠️ Anomaly Detection</span>
        <span class="dm-hero-feature">💬 Chat With Data</span>
        <span class="dm-hero-feature">📄 PDF Download</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── API KEY GATE ──────────────────────────────────────────────────────────────
if not api_key:
    st.info("👈 **Step 1:** Enter your free Groq API key in the sidebar — get one at [console.groq.com](https://console.groq.com)")
    st.stop()

# ── FILE GATE ────────────────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size:2.8rem;margin-bottom:0.75rem;">⬆</div>
        <h3>Drop your dataset here</h3>
        <p>CSV · XLSX · XLS &nbsp;·&nbsp; Any business data</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── LOAD DATA ────────────────────────────────────────────────────────────────
try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"❌ Could not read file: {e}")
    st.stop()

if df.empty:
    st.error("❌ Uploaded file is empty.")
    st.stop()

df.columns = df.columns.str.strip()
df = df.dropna(how="all").reset_index(drop=True)
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()
missing_pct  = round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 1)

# ── DATASET OVERVIEW ─────────────────────────────────────────────────────────
st.markdown("""
<div class="dm-section">
    <div class="dm-section-dot"></div>
    <h2>Dataset Overview</h2>
    <span>— snapshot of your uploaded file</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-strip">
    <div class="kpi-card"><div class="kpi-icon">📦</div><div class="kpi-value">{df.shape[0]:,}</div><div class="kpi-label">Rows</div></div>
    <div class="kpi-card"><div class="kpi-icon">📐</div><div class="kpi-value">{df.shape[1]}</div><div class="kpi-label">Columns</div></div>
    <div class="kpi-card"><div class="kpi-icon">🔢</div><div class="kpi-value">{len(numeric_cols)}</div><div class="kpi-label">Numeric</div></div>
    <div class="kpi-card"><div class="kpi-icon">🏷</div><div class="kpi-value">{len(cat_cols)}</div><div class="kpi-label">Categorical</div></div>
    <div class="kpi-card">
        <div class="kpi-icon">{"✅" if missing_pct == 0 else "⚠️"}</div>
        <div class="kpi-value" style="color:{'#4ade80' if missing_pct == 0 else '#fbbf24'}">{missing_pct}%</div>
        <div class="kpi-label">Missing</div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("👁 Preview Data (first 50 rows)"):
    st.dataframe(df.head(50), use_container_width=True)

with st.expander("📐 Column Information"):
    st.dataframe(pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.values,
        "Non-Null": df.notnull().sum().values,
        "Missing": df.isnull().sum().values,
        "Missing %": (df.isnull().sum() / len(df) * 100).round(1).values,
        "Unique Values": df.nunique().values,
        "Sample": [str(df[c].dropna().iloc[0]) if df[c].notna().any() else "—" for c in df.columns],
    }), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("🚀  Generate Full AI Report", use_container_width=True)

if not generate_btn and "report_generated" not in st.session_state:
    st.stop()

# ── GENERATE REPORT ───────────────────────────────────────────────────────────
if generate_btn or "report_generated" not in st.session_state:
    try:
        client = init_groq(api_key)
    except Exception:
        st.error("❌ Invalid Groq API key. Please check and try again.")
        st.stop()

    progress = st.progress(0, text="🔍 Analysing dataset structure…")
    stats_summary = analyze_dataframe(df)
    anomalies     = detect_anomalies(df)
    col_insights  = get_column_insights(df)
    health_score, health_grade, health_class = compute_health_score(df, anomalies)

    sys_p = f"""You are a senior data analyst writing a {report_tone.lower()} business intelligence report for the {report_industry} industry.
Always reference actual column names, real numbers from the data, and draw meaningful business conclusions.
Write clear, professional business English. No markdown asterisks, pound signs, or bullet symbols in output.
Be specific, insightful, and use precise numbers."""

    progress.progress(12, text="🤖 Writing Executive Summary…")
    exec_summary = call_groq(client, f"""Write a 3-paragraph executive summary for this dataset.
Dataset: {df.shape[0]:,} rows, {df.shape[1]} columns. File: {uploaded_file.name}
Columns: {list(df.columns[:20])}
Numeric columns: {numeric_cols[:10]}
Categorical columns: {cat_cols[:10]}
Key statistics: {json.dumps(stats_summary.get('key_stats', {}), default=str)[:1500]}
Organisation: {company_name}. Industry: {report_industry}

Paragraph 1: What the dataset covers — scope, time period if available, number of records.
Paragraph 2: Key patterns and trends with specific numbers from the statistics.
Paragraph 3: Business implications and strategic significance for {company_name}.""", sys_p, 800)

    progress.progress(27, text="🤖 Identifying key findings…")
    key_findings = call_groq(client, f"""Write exactly 5 key findings numbered 1 to 5.
Each finding must follow this exact format:
[number]. [Finding Title]: [2 sentences with specific numbers and column names]

Use actual numbers from the statistics below.
Statistics: {json.dumps(stats_summary, default=str)[:2200]}
Insights: {json.dumps(col_insights, default=str)[:1500]}
All columns: {list(df.columns)}""", sys_p, 900)

    progress.progress(43, text="🤖 Detecting anomalies and data quality issues…")
    anomaly_narrative = call_groq(client, f"""Analyse these anomalies and explain their business significance clearly.
Anomalies: {json.dumps(anomalies, default=str)[:1800]}
Dataset: {df.shape[0]:,} rows, columns: {list(df.columns[:15])}

Write 4-6 short paragraphs. Each paragraph covers: what the anomaly is, exact numbers,
and what it means for the business. Be specific and practical.""", sys_p, 700)

    progress.progress(58, text="🤖 Generating actionable recommendations…")
    recommendations = call_groq(client, f"""Write exactly 5 numbered actionable recommendations.
Each must follow this exact format:
[number]. [Action Title]: [2 sentences — specific, actionable, referencing data]

Base recommendations on the findings and anomalies below.
Key findings: {key_findings[:1000]}
Anomalies: {json.dumps(anomalies, default=str)[:700]}
Industry: {report_industry}
Organisation: {company_name}""", sys_p, 800)

    progress.progress(68, text="🧠 Generating data health commentary…")
    health_commentary = call_groq(client,
        f"""Write 2 sentences explaining the data health score of {health_score}/100 (grade: {health_grade}).
Mention: {missing_pct}% missing data, {len(anomalies.get('outliers', {}))} columns with outliers, {anomalies.get('duplicate_rows', {}).get('count', 0)} duplicate rows.
Be specific, {report_tone.lower()}, and constructive. No markdown.""", sys_p, 220)

    progress.progress(78, text="📊 Building premium charts…")
    charts       = build_charts(df)
    forecast_fig = build_forecast_chart(df)

    progress.progress(91, text="📄 Generating PDF report…")
    try:
        pdf_bytes = generate_pdf_report(
            title=report_title, company=company_name, analyst=analyst_name,
            filename=uploaded_file.name, df=df,
            exec_summary=exec_summary, key_findings=key_findings,
            anomaly_narrative=anomaly_narrative, recommendations=recommendations,
            stats_summary=stats_summary, anomalies=anomalies,
            charts=charts, forecast_fig=forecast_fig, tone=report_tone,
            industry=report_industry,
            health_score=health_score, health_grade=health_grade,
        )
    except Exception as e:
        st.warning(f"⚠️ PDF generation encountered an issue: {e}. Continuing with web report.")
        pdf_bytes = b""

    progress.progress(100, text="✅ Report ready!")
    import time; time.sleep(0.4)
    progress.empty()

    st.session_state.update({
        "report_generated": True,
        "exec_summary": exec_summary,
        "key_findings": key_findings,
        "anomaly_narrative": anomaly_narrative,
        "recommendations": recommendations,
        "health_score": health_score,
        "health_grade": health_grade,
        "health_class": health_class,
        "health_commentary": health_commentary,
        "stats_summary": stats_summary,
        "anomalies": anomalies,
        "charts": charts,
        "forecast_fig": forecast_fig,
        "pdf_bytes": pdf_bytes,
        "chat_history": [],
        "groq_client": client,
        "df_context": json.dumps({
            "columns": list(df.columns),
            "shape": [int(df.shape[0]), int(df.shape[1])],
            "key_stats": stats_summary.get("key_stats", {}),
            "cat_stats": stats_summary.get("cat_stats", {}),
            "anomalies": {k: str(v)[:200] for k, v in anomalies.items()},
            "correlations": stats_summary.get("strong_correlations", []),
        }, default=str)[:3500],
    })

# ── RESTORE STATE ─────────────────────────────────────────────────────────────
exec_summary      = st.session_state.exec_summary
key_findings      = st.session_state.key_findings
anomaly_narrative = st.session_state.anomaly_narrative
recommendations   = st.session_state.recommendations
health_score      = st.session_state.health_score
health_grade      = st.session_state.health_grade
health_class      = st.session_state.health_class
health_commentary = st.session_state.health_commentary
anomalies         = st.session_state.anomalies
charts            = st.session_state.charts
forecast_fig      = st.session_state.forecast_fig
pdf_bytes         = st.session_state.pdf_bytes

# ── SUCCESS BANNER ────────────────────────────────────────────────────────────
st.success("✅ AI Report generated — explore the tabs below")

# ── HEALTH SCORE ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="health-panel {health_class}">
    <div class="health-ring">{health_score}</div>
    <div class="health-content">
        <h3>Data Health Score: {health_grade}</h3>
        <p>{health_commentary}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Summary & Findings",
    "📊 Visualisations",
    "🔮 Forecast",
    "⚠️ Anomalies",
    "✅ Recommendations",
    "💬 Chat",
])

# ── TAB 1: SUMMARY & FINDINGS ─────────────────────────────────────────────────
with tab1:
    st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Executive Summary</h2></div>""", unsafe_allow_html=True)
    for para in exec_summary.split("\n"):
        if para.strip():
            st.markdown(f'<div class="dm-card dm-card-summary">{para.strip()}</div>', unsafe_allow_html=True)

    st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Key Findings</h2><span>— 5 data-driven insights</span></div>""", unsafe_allow_html=True)
    lines = [l.strip() for l in key_findings.split("\n") if l.strip() and len(l.strip()) > 5]
    for i, line in enumerate(lines):
        is_num = len(line) > 1 and line[0].isdigit()
        if is_num and ":" in line:
            parts = line.split(":", 1)
            title = parts[0].strip().lstrip("0123456789. ").strip()
            body  = parts[1].strip() if len(parts) > 1 else ""
            st.markdown(f"""
            <div class="dm-card dm-card-finding">
                <span class="num-badge num-badge-purple">{i+1}</span>
                <span class="finding-title">{title}</span>
                <span class="finding-body">{body}</span>
            </div>""", unsafe_allow_html=True)
        elif is_num:
            st.markdown(f'<div class="dm-card dm-card-finding"><span class="num-badge num-badge-purple">{i+1}</span> {line}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="dm-card">{line}</div>', unsafe_allow_html=True)

    st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Statistical Summary</h2></div>""", unsafe_allow_html=True)
    if numeric_cols:
        st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)

    # Correlation table
    corrs = (st.session_state.stats_summary or {}).get("strong_correlations", [])
    if corrs:
        st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Strong Correlations</h2></div>""", unsafe_allow_html=True)
        corr_df = pd.DataFrame([{
            "Column A": c["col1"], "Column B": c["col2"],
            "Pearson r": c["r"], "Strength": c["strength"]
        } for c in corrs])
        st.dataframe(corr_df, use_container_width=True)

# ── TAB 2: VISUALISATIONS ─────────────────────────────────────────────────────
with tab2:
    st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Visualisations</h2><span>— auto-generated from your data</span></div>""", unsafe_allow_html=True)
    if charts:
        for i in range(0, len(charts), 2):
            if i + 1 < len(charts):
                c1, c2 = st.columns(2, gap="medium")
                with c1:
                    st.plotly_chart(charts[i],   use_container_width=True)
                with c2:
                    st.plotly_chart(charts[i+1], use_container_width=True)
            else:
                st.plotly_chart(charts[i], use_container_width=True)
    else:
        st.info("Not enough numeric data to generate charts.")

# ── TAB 3: FORECAST ───────────────────────────────────────────────────────────
with tab3:
    st.markdown(f"""<div class="dm-section"><div class="dm-section-dot"></div><h2>Trend Forecast</h2><span class="fc-badge">Linear Regression</span></div>""", unsafe_allow_html=True)
    if forecast_fig:
        st.plotly_chart(forecast_fig, use_container_width=True)
        st.markdown("""
        <div class="dm-card" style="font-size:0.83rem;color:#475569;">
            ⚠️ <b>Disclaimer:</b> Linear regression forecast for directional guidance only.
            Not a financial prediction. Actual results may vary significantly.
        </div>""", unsafe_allow_html=True)
    else:
        st.info("📅 Forecasting requires at least one date column and one numeric column with 4+ data points.")

# ── TAB 4: ANOMALIES ──────────────────────────────────────────────────────────
with tab4:
    st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Anomalies & Data Quality</h2></div>""", unsafe_allow_html=True)
    lines = [a.strip() for a in anomaly_narrative.split("\n") if a.strip()]
    for line in lines:
        if any(w in line.lower() for w in ["extreme", "critical", "significant", "major"]):
            sev, label = "sev-high", "High"
        elif any(w in line.lower() for w in ["moderate", "warning", "missing", "outlier", "duplicate", "skew"]):
            sev, label = "sev-medium", "Medium"
        else:
            sev, label = "sev-low", "Low"
        st.markdown(f'<div class="dm-card dm-card-anomaly">{line} <span class="sev-badge {sev}">{label}</span></div>', unsafe_allow_html=True)

    outliers = anomalies.get("outliers", {})
    if outliers:
        st.markdown("""<div class="dm-section" style="margin-top:1.5rem;"><div class="dm-section-dot"></div><h2>Outlier Detail</h2></div>""", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{
            "Column": col, "Outlier Count": v["count"], "Outlier %": f"{v['pct']}%",
            "Lower Bound": v["lower_bound"], "Upper Bound": v["upper_bound"],
            "Data Min": v["extreme_min"], "Data Max": v["extreme_max"],
        } for col, v in outliers.items()]), use_container_width=True)

    # Constant / high-missing columns
    const = anomalies.get("constant_columns", [])
    high_miss = anomalies.get("high_missing", [])
    skewed = anomalies.get("high_skewness", {})

    if const or high_miss or skewed:
        st.markdown("""<div class="dm-section" style="margin-top:1.5rem;"><div class="dm-section-dot"></div><h2>Additional Flags</h2></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="dm-card"><b style="color:#f87171;">Constant Columns</b><br><span style="font-size:0.85rem;color:#94a3b8;">{", ".join(const) if const else "None"}</span></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="dm-card"><b style="color:#fbbf24;">High Missing (>20%)</b><br><span style="font-size:0.85rem;color:#94a3b8;">{", ".join(high_miss) if high_miss else "None"}</span></div>', unsafe_allow_html=True)
        with c3:
            skew_txt = ", ".join(f"{k}: {v}" for k, v in skewed.items()) if skewed else "None"
            st.markdown(f'<div class="dm-card"><b style="color:#fb923c;">High Skewness (&gt;2)</b><br><span style="font-size:0.85rem;color:#94a3b8;">{skew_txt}</span></div>', unsafe_allow_html=True)

# ── TAB 5: RECOMMENDATIONS ────────────────────────────────────────────────────
with tab5:
    st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Actionable Recommendations</h2><span>— AI-generated strategic actions</span></div>""", unsafe_allow_html=True)
    rlines = [r.strip() for r in recommendations.split("\n") if r.strip() and len(r.strip()) > 5]
    for i, reco in enumerate(rlines):
        is_num = len(reco) > 1 and reco[0].isdigit()
        if is_num and ":" in reco:
            parts = reco.split(":", 1)
            title = parts[0].strip().lstrip("0123456789. ").strip()
            body  = parts[1].strip() if len(parts) > 1 else ""
            st.markdown(f"""
            <div class="dm-card dm-card-reco">
                <span class="num-badge num-badge-green">{i+1}</span>
                <span class="finding-title">{title}</span>
                <span class="finding-body">{body}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="dm-card dm-card-reco"><span class="num-badge num-badge-green">{i+1}</span> {reco}</div>', unsafe_allow_html=True)

# ── TAB 6: CHAT ───────────────────────────────────────────────────────────────
with tab6:
    st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Chat With Your Data</h2><span>— ask anything</span></div>""", unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.83rem;color:#475569;margin-bottom:0.75rem;">💡 Try asking:</p>
    <div style="margin-bottom:1.25rem;display:flex;flex-wrap:wrap;gap:0.4rem;">
        <span class="chat-pill">Which column has the highest variability?</span>
        <span class="chat-pill">What is the biggest business risk?</span>
        <span class="chat-pill">Which category performs best?</span>
        <span class="chat-pill">Summarise this dataset in one sentence.</span>
        <span class="chat-pill">What trends should we act on?</span>
    </div>""", unsafe_allow_html=True)

    if st.session_state.get("chat_history"):
        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f'<div class="chat-user"><div class="bubble">{msg["content"]}</div></div>'
            else:
                chat_html += f'<div class="chat-ai"><div class="chat-avatar">AI</div><div class="bubble">{msg["content"]}</div></div>'
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

    user_q = st.text_input(
        "Question", placeholder="e.g. Which region drives the most revenue?",
        key="chat_input", label_visibility="collapsed",
    )
    col_send, col_clear = st.columns([5, 1])
    with col_send:
        send = st.button("Send ↗", use_container_width=True)
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if send and user_q.strip():
        chat_sys = f"""You are a senior data analyst. Answer questions about this specific dataset only.
Be concise, specific, reference actual column names and real numbers from the data.
Dataset context: {st.session_state.df_context}
Executive summary: {exec_summary[:500]}
Key findings: {key_findings[:500]}
Write in plain, professional English. No markdown symbols."""
        msgs = [{"role": "system", "content": chat_sys}]
        for h in st.session_state.chat_history[-6:]:
            msgs.append(h)
        msgs.append({"role": "user", "content": user_q})
        with st.spinner("Thinking…"):
            try:
                resp = st.session_state.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile", messages=msgs,
                    temperature=0.3, max_tokens=600,
                )
                answer = resp.choices[0].message.content.strip()
            except Exception as e:
                answer = f"Sorry, I encountered an error: {e}"
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<div class="dm-section"><div class="dm-section-dot"></div><h2>Download Report</h2><span>— full PDF with charts, findings & recommendations</span></div>""", unsafe_allow_html=True)
safe_title = report_title.replace(" ", "_").replace("/", "-")
st.markdown('<div class="dl-btn">', unsafe_allow_html=True)
if pdf_bytes:
    st.download_button(
        label="📥  Download Full PDF Report",
        data=pdf_bytes,
        file_name=f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
else:
    st.warning("PDF generation failed. Please try regenerating the report.")
st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dm-footer">
    <strong>DataMind AI</strong> &nbsp;·&nbsp;
    {datetime.now().strftime('%B %d, %Y')} &nbsp;·&nbsp;
    Groq LLaMA 3.3 · 70B &nbsp;·&nbsp;
    {df.shape[0]:,} rows &times; {df.shape[1]} columns analysed
</div>""", unsafe_allow_html=True)
