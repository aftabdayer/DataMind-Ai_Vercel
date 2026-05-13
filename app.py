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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── CSS VARIABLES ── */
:root {
    --bg-base:       #0d0d12;
    --bg-surface:    #13131a;
    --bg-elevated:   #18181f;
    --bg-overlay:    #1e1e28;
    --border-subtle: rgba(255,255,255,0.06);
    --border-muted:  rgba(255,255,255,0.1);
    --border-accent: rgba(139,92,246,0.35);
    --text-primary:  #f0f0f5;
    --text-secondary:#94a3b8;
    --text-muted:    #475569;
    --accent-purple: #8b5cf6;
    --accent-blue:   #3b82f6;
    --accent-green:  #10b981;
    --accent-amber:  #f59e0b;
    --accent-red:    #ef4444;
    --accent-pink:   #ec4899;
    --radius-sm:  8px;
    --radius-md:  12px;
    --radius-lg:  18px;
    --radius-xl:  24px;
}

/* ── RESET & BASE ── */
html, body, [class*="css"] {
    font-family: 'Instrument Sans', sans-serif;
    background-color: var(--bg-base) !important;
    color: var(--text-primary);
}
.stApp { background: var(--bg-base); }
* { box-sizing: border-box; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #0a0a0f !important;
    border-right: 1px solid var(--border-subtle) !important;
    width: 240px !important;
}
section[data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
section[data-testid="stSidebar"] .stTextInput input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-muted) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    padding: 0.6rem 0.9rem !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-muted) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

/* ── SIDEBAR BRANDING ── */
.sb-brand { padding: 0.25rem 0 1.25rem; }
.sb-logo-row {
    display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.3rem;
}
.sb-logo-icon {
    width: 32px; height: 32px; border-radius: 9px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    box-shadow: 0 4px 14px rgba(124,58,237,0.4);
}
.sb-brand h2 {
    font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700;
    color: var(--text-primary) !important; margin: 0; letter-spacing: -0.3px;
}
.sb-brand p { font-size: 0.7rem; color: var(--text-muted) !important; margin: 0; letter-spacing: 0.5px; text-transform: uppercase; }
.sb-divider { border: none; border-top: 1px solid var(--border-subtle); margin: 0.85rem 0; }
.sb-label {
    font-size: 0.62rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 2px !important;
    color: var(--text-muted) !important; margin-bottom: 0.45rem !important;
    display: block !important;
}
.sb-nav-item {
    display: flex; align-items: center; gap: 0.7rem;
    padding: 0.55rem 0.75rem; border-radius: var(--radius-sm);
    font-size: 0.88rem; font-weight: 500; color: var(--text-secondary) !important;
    margin-bottom: 0.15rem; cursor: pointer;
    transition: background 0.15s, color 0.15s;
}
.sb-nav-item:hover { background: var(--bg-elevated); color: var(--text-primary) !important; }
.sb-nav-item.active {
    background: rgba(139,92,246,0.15);
    color: #c4b5fd !important;
    border: 1px solid rgba(139,92,246,0.25);
}
.sb-nav-icon { font-size: 0.95rem; opacity: 0.85; }

/* ── HERO ── */
.dm-hero {
    position: relative; overflow: hidden;
    background: linear-gradient(160deg, #0e0b20 0%, #130d2e 35%, #0b1530 70%, #0d0d14 100%);
    border-radius: var(--radius-xl); padding: 3.5rem 3rem 3rem;
    text-align: center; margin-bottom: 2rem;
    border: 1px solid rgba(139,92,246,0.18);
    box-shadow: 0 0 100px rgba(99,59,220,0.07), inset 0 1px 0 rgba(255,255,255,0.04);
}
.dm-hero::before {
    content: ''; position: absolute; top: -40%; left: 30%;
    width: 60%; height: 200%;
    background: radial-gradient(ellipse at center, rgba(99,59,220,0.14) 0%, transparent 65%);
    pointer-events: none; transform: rotate(-15deg);
}
.dm-hero::after {
    content: ''; position: absolute; bottom: -20%; left: -10%;
    width: 40%; height: 150%;
    background: radial-gradient(ellipse at center, rgba(59,130,246,0.07) 0%, transparent 60%);
    pointer-events: none;
}
.dm-hero-eyebrow {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.25);
    color: #a78bfa; font-size: 0.65rem; font-weight: 600; letter-spacing: 3.5px;
    text-transform: uppercase; padding: 0.35rem 1rem;
    border-radius: 999px; margin-bottom: 1.25rem;
}
.dm-hero h1 {
    font-family: 'Syne', sans-serif; font-size: 3.8rem; font-weight: 800;
    color: var(--text-primary); margin: 0 0 0.85rem; line-height: 1.05; letter-spacing: -2px;
}
.dm-hero h1 em { font-style: normal; color: #a78bfa; }
.dm-hero p {
    color: rgba(255,255,255,0.42); font-size: 1rem; margin: 0 auto 2rem;
    max-width: 500px; line-height: 1.75; font-weight: 400;
}
.dm-hero-features { display: flex; justify-content: center; gap: 0.65rem; flex-wrap: wrap; }
.dm-hero-feature {
    display: flex; align-items: center; gap: 0.4rem;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    color: rgba(255,255,255,0.5); font-size: 0.77rem; font-weight: 500;
    padding: 0.4rem 0.9rem; border-radius: var(--radius-sm);
    transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.dm-hero-feature:hover {
    background: rgba(139,92,246,0.08); border-color: rgba(139,92,246,0.25);
    color: #c4b5fd;
}

/* ── KPI STRIP ── */
.kpi-strip {
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 0.85rem; margin-bottom: 1.75rem;
}
.kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg); padding: 1.3rem 1rem;
    text-align: center; position: relative; overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(139,92,246,0.3);
    box-shadow: 0 8px 28px rgba(99,59,220,0.12);
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.5), transparent);
}
.kpi-icon { font-size: 1.35rem; margin-bottom: 0.55rem; display: block; }
.kpi-value {
    font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800;
    color: var(--text-primary); line-height: 1; margin-bottom: 0.3rem; display: block;
}
.kpi-label {
    font-size: 0.62rem; color: var(--text-muted);
    font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px;
}

/* ── HEALTH SCORE ── */
.health-panel {
    display: flex; align-items: center; gap: 1.75rem;
    border-radius: var(--radius-lg); padding: 1.5rem 2rem; margin-bottom: 1.75rem;
    border: 1px solid; position: relative; overflow: hidden;
}
.health-excellent { background: linear-gradient(135deg, rgba(5,46,22,0.8), rgba(10,54,34,0.8)); border-color: rgba(22,163,74,0.5); }
.health-good      { background: linear-gradient(135deg, rgba(12,26,58,0.8), rgba(15,37,80,0.8)); border-color: rgba(59,130,246,0.5); }
.health-fair      { background: linear-gradient(135deg, rgba(45,26,0,0.8), rgba(61,36,0,0.8));   border-color: rgba(245,158,11,0.5); }
.health-poor      { background: linear-gradient(135deg, rgba(45,10,10,0.8), rgba(61,16,16,0.8)); border-color: rgba(239,68,68,0.5); }
.health-ring {
    flex-shrink: 0; width: 72px; height: 72px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800;
    border: 2.5px solid currentColor;
}
.health-excellent .health-ring { color: #4ade80; box-shadow: 0 0 20px rgba(74,222,128,0.2); }
.health-good      .health-ring { color: #60a5fa; box-shadow: 0 0 20px rgba(96,165,250,0.2); }
.health-fair      .health-ring { color: #fbbf24; box-shadow: 0 0 20px rgba(251,191,36,0.2); }
.health-poor      .health-ring { color: #f87171; box-shadow: 0 0 20px rgba(248,113,113,0.2); }
.health-content h3 { margin: 0 0 0.25rem; font-size: 1rem; font-weight: 700; font-family: 'Syne', sans-serif; color: var(--text-primary); }
.health-content p  { margin: 0; font-size: 0.87rem; color: rgba(255,255,255,0.5); line-height: 1.65; }

/* ── SECTION HEADERS ── */
.dm-section {
    display: flex; align-items: center; gap: 0.7rem;
    margin: 2.25rem 0 1.1rem; padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--border-subtle);
}
.dm-section-bar {
    width: 3px; height: 20px; border-radius: 2px;
    background: linear-gradient(180deg, #8b5cf6, #3b82f6); flex-shrink: 0;
}
.dm-section h2 {
    margin: 0; font-size: 1.05rem; font-weight: 700;
    font-family: 'Syne', sans-serif;
    color: var(--text-primary); letter-spacing: -0.2px;
}
.dm-section span { font-size: 0.77rem; color: var(--text-muted); font-weight: 400; margin-left: 0.2rem; }

/* ── CONTENT CARDS ── */
.dm-card {
    background: var(--bg-surface); border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md); padding: 1.1rem 1.4rem; margin-bottom: 0.65rem;
    line-height: 1.8; color: var(--text-secondary); font-size: 0.91rem;
    transition: border-color 0.2s ease;
}
.dm-card:hover { border-color: var(--border-muted); }
.dm-card-finding {
    border-left: 2px solid var(--accent-purple);
    background: linear-gradient(to right, rgba(139,92,246,0.05), var(--bg-surface));
}
.dm-card-anomaly {
    border-left: 2px solid var(--accent-amber);
    background: linear-gradient(to right, rgba(245,158,11,0.05), var(--bg-surface));
}
.dm-card-reco {
    border-left: 2px solid var(--accent-green);
    background: linear-gradient(to right, rgba(16,185,129,0.05), var(--bg-surface));
}
.dm-card-summary {
    border-left: 2px solid var(--accent-blue);
    background: linear-gradient(to right, rgba(59,130,246,0.05), var(--bg-surface));
}

/* ── ANOMALY CARD (Stitch-style) ── */
.anomaly-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.85rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative;
}
.anomaly-card:hover {
    border-color: rgba(245,158,11,0.3);
    box-shadow: 0 4px 20px rgba(245,158,11,0.06);
}
.anomaly-card-high   { border-top: 2px solid var(--accent-red); }
.anomaly-card-medium { border-top: 2px solid var(--accent-amber); }
.anomaly-card-low    { border-top: 2px solid var(--accent-green); }
.anomaly-meta {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.5rem;
}
.anomaly-title {
    font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700;
    color: var(--text-primary); margin: 0 0 0.35rem; display: block;
}
.anomaly-body {
    font-size: 0.88rem; color: var(--text-secondary); line-height: 1.7; display: block;
}
.anomaly-time { font-size: 0.72rem; color: var(--text-muted); }
.anomaly-action {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.2px; color: var(--text-muted);
    margin-top: 0.75rem; cursor: pointer;
    transition: color 0.15s;
}
.anomaly-action:hover { color: var(--accent-amber); }

/* ── NUMBERED BADGES ── */
.num-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 24px; height: 24px; border-radius: 7px;
    font-size: 0.7rem; font-weight: 700; font-family: 'Syne', sans-serif;
    margin-right: 0.6rem; vertical-align: middle; flex-shrink: 0;
}
.num-badge-purple { background: rgba(139,92,246,0.18); color: #a78bfa; border: 1px solid rgba(139,92,246,0.28); }
.num-badge-green  { background: rgba(16,185,129,0.15);  color: #34d399; border: 1px solid rgba(16,185,129,0.28); }

/* ── SEVERITY BADGES ── */
.sev-badge {
    display: inline-block; font-size: 0.6rem; font-weight: 700;
    padding: 0.18rem 0.6rem; border-radius: 5px;
    text-transform: uppercase; letter-spacing: 1px; vertical-align: middle;
}
.sev-high   { background: rgba(239,68,68,0.15);   color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.sev-medium { background: rgba(245,158,11,0.15);  color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.sev-low    { background: rgba(16,185,129,0.15);  color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.crit-badge { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.28); font-size: 0.6rem; font-weight: 700; padding: 0.18rem 0.6rem; border-radius: 5px; letter-spacing: 0.8px; text-transform: uppercase; }
.attn-badge { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.28); font-size: 0.6rem; font-weight: 700; padding: 0.18rem 0.6rem; border-radius: 5px; letter-spacing: 0.8px; text-transform: uppercase; }

/* ── FINDING TITLE ── */
.finding-title { font-weight: 700; font-family: 'Syne', sans-serif; color: var(--text-primary); font-size: 0.95rem; display: block; margin-bottom: 0.25rem; }
.finding-body  { color: var(--text-secondary); font-size: 0.88rem; line-height: 1.75; }

/* ── CHAT ── */
.chat-wrap {
    background: var(--bg-surface); border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl); padding: 1.5rem;
    margin-bottom: 1rem; max-height: 480px; overflow-y: auto;
}
.chat-wrap::-webkit-scrollbar { width: 4px; }
.chat-wrap::-webkit-scrollbar-track { background: transparent; }
.chat-wrap::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
.chat-user { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
.chat-user .bubble {
    background: linear-gradient(135deg, #5b21b6, #3730a3);
    color: #e9d5ff; padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px; max-width: 70%;
    font-size: 0.88rem; line-height: 1.6;
    box-shadow: 0 4px 16px rgba(91,33,182,0.35);
}
.chat-ai { display: flex; gap: 0.65rem; margin-bottom: 1rem; align-items: flex-start; }
.chat-avatar {
    width: 32px; height: 32px; border-radius: 9px; flex-shrink: 0;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; color: white; font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    box-shadow: 0 3px 10px rgba(124,58,237,0.35);
}
.chat-ai .bubble {
    background: var(--bg-elevated); border: 1px solid var(--border-subtle);
    color: var(--text-secondary); padding: 0.75rem 1.1rem;
    border-radius: 4px 18px 18px 18px; max-width: 80%;
    font-size: 0.88rem; line-height: 1.75;
}
.chat-pill {
    display: inline-block; background: var(--bg-elevated);
    border: 1px solid rgba(139,92,246,0.22);
    color: #a78bfa; font-size: 0.76rem; padding: 0.3rem 0.85rem;
    border-radius: 999px; margin: 0.2rem; cursor: pointer;
    transition: all 0.15s ease;
}
.chat-pill:hover { background: rgba(139,92,246,0.12); border-color: rgba(139,92,246,0.45); color: #c4b5fd; }

/* ── FORECAST BADGE ── */
.fc-badge {
    display: inline-block;
    background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.22);
    color: #a78bfa; font-size: 0.62rem; font-weight: 700;
    padding: 0.18rem 0.65rem; border-radius: 5px;
    text-transform: uppercase; letter-spacing: 0.8px; margin-left: 0.5rem;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #4338ca 100%) !important;
    color: white !important; border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.85rem 2rem !important; font-weight: 700 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.92rem !important; width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 18px rgba(124,58,237,0.3) !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 26px rgba(124,58,237,0.42) !important;
}
.dl-btn .stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    box-shadow: 0 4px 18px rgba(5,150,105,0.28) !important;
}
.dl-btn .stDownloadButton > button:hover {
    box-shadow: 0 8px 26px rgba(5,150,105,0.42) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important; gap: 2px !important;
    border: 1px solid var(--border-subtle) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important; color: var(--text-muted) !important;
    font-weight: 600 !important; font-size: 0.82rem !important;
    padding: 0.5rem 1rem !important;
    font-family: 'Instrument Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #4338ca) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(124,58,237,0.3) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0 0 !important; }

/* ── EXPANDERS ── */
div[data-testid="stExpander"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 0.5rem !important;
}
div[data-testid="stExpander"] summary { color: var(--text-primary) !important; font-weight: 600 !important; }

/* ── INPUTS ── */
.stTextInput input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-muted) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
}
.stSelectbox > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-muted) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
}
.stFileUploader {
    background: var(--bg-elevated) !important;
    border: 1px dashed rgba(139,92,246,0.3) !important;
    border-radius: var(--radius-md) !important;
}
.stTextInput label, .stSelectbox label, .stFileUploader label {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
    background: var(--bg-surface) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-subtle) !important;
}
.stDataFrame thead th {
    background: rgba(139,92,246,0.12) !important;
    color: var(--text-primary) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.5px !important;
}

/* ── ALERTS ── */
.stAlert { background: var(--bg-surface) !important; border-radius: var(--radius-md) !important; border-left-width: 2px !important; }
.stSuccess { border-left-color: var(--accent-green) !important; }
.stInfo    { border-left-color: var(--accent-blue) !important; }
.stWarning { border-left-color: var(--accent-amber) !important; }
.stError   { border-left-color: var(--accent-red) !important; }

/* ── PROGRESS ── */
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #3b82f6) !important; border-radius: 999px !important; }

/* ── FOOTER ── */
.dm-footer {
    text-align: center; margin-top: 4rem; padding: 2rem;
    border-top: 1px solid var(--border-subtle);
    color: var(--text-muted); font-size: 0.76rem; letter-spacing: 0.3px;
}
.dm-footer strong { color: #475569; }
.dm-footer a { color: #475569; text-decoration: none; }
.dm-footer a:hover { color: var(--text-secondary); }

/* ── UPLOAD ZONE ── */
.upload-zone {
    background: linear-gradient(135deg, rgba(10,10,24,0.9), rgba(15,15,32,0.9));
    border: 2px dashed rgba(139,92,246,0.28);
    border-radius: var(--radius-xl); padding: 4rem 2rem;
    text-align: center; margin-top: 1rem;
    transition: border-color 0.2s ease, background 0.2s ease;
}
.upload-zone:hover {
    border-color: rgba(139,92,246,0.55);
    background: linear-gradient(135deg, rgba(15,10,32,0.9), rgba(15,15,32,0.9));
}
.upload-zone h3 {
    color: #c4b5fd; font-family: 'Syne', sans-serif;
    font-size: 1.4rem; font-weight: 700; margin: 0.6rem 0 0.25rem;
}
.upload-zone p { color: var(--text-muted); font-size: 0.85rem; margin: 0; }

/* ── OUTLIER TABLE ── */
.outlier-table { width: 100%; border-collapse: collapse; font-size: 0.87rem; }
.outlier-table th {
    background: rgba(139,92,246,0.1); color: var(--text-secondary);
    padding: 0.7rem 1rem; text-align: left;
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;
    border-bottom: 1px solid var(--border-subtle);
}
.outlier-table td {
    padding: 0.8rem 1rem; color: var(--text-secondary);
    border-bottom: 1px solid var(--border-subtle);
}
.outlier-table tr:last-child td { border-bottom: none; }
.outlier-table td:first-child { color: var(--accent-purple); font-weight: 600; }
.outlier-table tr:hover td { background: rgba(255,255,255,0.02); }

/* ── CORR TABLE ── */
.corr-table { width: 100%; border-collapse: collapse; font-size: 0.87rem; }
.corr-table th {
    background: rgba(59,130,246,0.08); color: var(--text-secondary);
    padding: 0.65rem 1rem; text-align: left;
    font-size: 0.68rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;
    border-bottom: 1px solid var(--border-subtle);
}
.corr-table td { padding: 0.75rem 1rem; color: var(--text-secondary); border-bottom: 1px solid var(--border-subtle); }
.corr-table tr:last-child td { border-bottom: none; }
.corr-table td:first-child { color: var(--accent-blue); font-weight: 600; }
.corr-table tr:hover td { background: rgba(255,255,255,0.02); }
.r-strong-pos { color: #4ade80 !important; font-weight: 700; }
.r-strong-neg { color: #f87171 !important; font-weight: 700; }
.r-moderate   { color: #fbbf24 !important; font-weight: 600; }
.strength-badge {
    display: inline-block; font-size: 0.62rem; font-weight: 700;
    padding: 0.15rem 0.55rem; border-radius: 5px;
    text-transform: uppercase; letter-spacing: 0.8px;
}
.strength-strong-pos { background: rgba(74,222,128,0.12); color: #4ade80; border: 1px solid rgba(74,222,128,0.25); }
.strength-strong-neg { background: rgba(248,113,113,0.12); color: #f87171; border: 1px solid rgba(248,113,113,0.25); }
.strength-moderate   { background: rgba(251,191,36,0.12);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.25); }
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
        <div class="sb-logo-row">
            <div class="sb-logo-icon">◈</div>
            <h2>DataMind</h2>
        </div>
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
    <div class="dm-section-bar"></div>
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
    st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Executive Summary</h2></div>""", unsafe_allow_html=True)
    for para in exec_summary.split("\n"):
        if para.strip():
            st.markdown(f'<div class="dm-card dm-card-summary">{para.strip()}</div>', unsafe_allow_html=True)

    st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Key Findings</h2><span>— 5 data-driven insights</span></div>""", unsafe_allow_html=True)
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

    st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Statistical Summary</h2></div>""", unsafe_allow_html=True)
    if numeric_cols:
        st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)

    # Correlation table
    corrs = (st.session_state.stats_summary or {}).get("strong_correlations", [])
    if corrs:
        st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Strong Correlations</h2></div>""", unsafe_allow_html=True)
        rows_html = ""
        for c in corrs:
            r_val = c["r"]
            if c["strength"] == "Strong" and r_val > 0:
                r_class, s_class, s_label = "r-strong-pos", "strength-strong-pos", "STRONG POSITIVE"
            elif c["strength"] == "Strong" and r_val < 0:
                r_class, s_class, s_label = "r-strong-neg", "strength-strong-neg", "INVERSE STRONG"
            else:
                r_class, s_class, s_label = "r-moderate", "strength-moderate", "MODERATE"
            conf = round(min(99.9, abs(r_val) * 105), 1)
            rows_html += f"""<tr>
                <td>{c['col1']} &amp; {c['col2']}</td>
                <td class="{r_class}">{r_val}</td>
                <td><span class="strength-badge {s_class}">{s_label}</span></td>
                <td>{conf}%</td>
            </tr>"""
        st.markdown(f"""
        <div class="dm-card" style="padding:0;overflow:hidden;">
        <table class="corr-table">
            <thead><tr>
                <th>Variable Pair (A &amp; B)</th>
                <th>Pearson R</th><th>Strength</th><th>Confidence</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

# ── TAB 2: VISUALISATIONS ─────────────────────────────────────────────────────
with tab2:
    st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Visualisations</h2><span>— auto-generated from your data</span></div>""", unsafe_allow_html=True)
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
    st.markdown(f"""<div class="dm-section"><div class="dm-section-bar"></div><h2>Trend Forecast</h2><span class="fc-badge">Linear Regression</span></div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Anomalies & Data Quality</h2></div>""", unsafe_allow_html=True)
    lines = [a.strip() for a in anomaly_narrative.split("\n") if a.strip()]
    for idx, line in enumerate(lines):
        if any(w in line.lower() for w in ["extreme", "critical", "significant", "major"]):
            sev_class, badge_class, badge_label = "anomaly-card-high", "crit-badge", "CRITICAL: HIGH"
        elif any(w in line.lower() for w in ["moderate", "warning", "missing", "outlier", "duplicate", "skew"]):
            sev_class, badge_class, badge_label = "anomaly-card-medium", "attn-badge", "ATTENTION: MEDIUM"
        else:
            sev_class, badge_class, badge_label = "anomaly-card-low", "sev-low", "INFO: LOW"

        if "." in line[:60]:
            title_part = line.split(".")[0].strip()
            body_part  = line[len(title_part)+1:].strip()
        elif ":" in line[:60]:
            title_part = line.split(":")[0].strip()
            body_part  = line[len(title_part)+1:].strip()
        else:
            title_part = f"Anomaly #{idx+1}"
            body_part  = line

        st.markdown(f"""
        <div class="anomaly-card {sev_class}">
            <div class="anomaly-meta">
                <span class="{badge_class}">{badge_label}</span>
                <span class="anomaly-time">{idx+1} of {len(lines)}</span>
            </div>
            <span class="anomaly-title">{title_part}</span>
            <span class="anomaly-body">{body_part if body_part else line}</span>
            <div class="anomaly-action">Investigate &nbsp;→</div>
        </div>""", unsafe_allow_html=True)

    outliers = anomalies.get("outliers", {})
    if outliers:
        st.markdown("""<div class="dm-section" style="margin-top:1.5rem;"><div class="dm-section-bar"></div><h2>Outlier Detail Matrix</h2></div>""", unsafe_allow_html=True)
        rows_html = "".join([f"""<tr>
            <td>{col}</td><td>{v['count']:,}</td><td>{v['pct']}%</td>
            <td>{v['lower_bound']:,}</td><td>{v['upper_bound']:,}</td>
            <td>{v['extreme_min']:,}</td><td>{v['extreme_max']:,}</td>
        </tr>""" for col, v in outliers.items()])
        st.markdown(f"""
        <div class="dm-card" style="padding:0;overflow:hidden;">
        <table class="outlier-table">
            <thead><tr>
                <th>Metric / Column</th><th>Count</th><th>%</th>
                <th>Lower Bound</th><th>Upper Bound</th><th>Data Min</th><th>Data Max</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

    const = anomalies.get("constant_columns", [])
    high_miss = anomalies.get("high_missing", [])
    skewed = anomalies.get("high_skewness", {})

    if const or high_miss or skewed:
        st.markdown("""<div class="dm-section" style="margin-top:1.5rem;"><div class="dm-section-bar"></div><h2>Additional Flags</h2></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="dm-card"><b style="color:#f87171;">Constant Columns</b><br><span style="font-size:0.85rem;color:#94a3b8;">{", ".join(const) if const else "None detected"}</span></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="dm-card"><b style="color:#fbbf24;">High Missing (&gt;20%)</b><br><span style="font-size:0.85rem;color:#94a3b8;">{", ".join(high_miss) if high_miss else "None detected"}</span></div>', unsafe_allow_html=True)
        with c3:
            skew_txt = ", ".join(f"{k}: {v}" for k, v in skewed.items()) if skewed else "None detected"
            st.markdown(f'<div class="dm-card"><b style="color:#fb923c;">High Skewness (&gt;2)</b><br><span style="font-size:0.85rem;color:#94a3b8;">{skew_txt}</span></div>', unsafe_allow_html=True)

# ── TAB 5: RECOMMENDATIONS ────────────────────────────────────────────────────
with tab5:
    st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Actionable Recommendations</h2><span>— AI-generated strategic actions</span></div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Chat With Your Data</h2><span>— ask anything</span></div>""", unsafe_allow_html=True)
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
st.markdown("""<div class="dm-section"><div class="dm-section-bar"></div><h2>Download Report</h2><span>— full PDF with charts, findings & recommendations</span></div>""", unsafe_allow_html=True)
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
