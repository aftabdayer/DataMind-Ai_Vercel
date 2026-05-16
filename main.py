"""
DataMind AI — FastAPI Backend
Replaces Streamlit app.py. Exposes all AI + analysis endpoints.
"""

import io
import json
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from groq import Groq
from pydantic import BaseModel
from scipy import stats

from data_analyzer import analyze_dataframe, detect_anomalies, get_column_insights
from report_generator import generate_pdf_report

# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────

app = FastAPI(
    title="DataMind AI API",
    description="AI-powered business intelligence backend",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _load_df(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse uploaded file into a DataFrame."""
    ext = filename.rsplit(".", 1)[-1].lower()
    buf = io.BytesIO(file_bytes)
    if ext == "csv":
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                buf.seek(0)
                return pd.read_csv(buf, encoding=enc)
            except Exception:
                continue
        raise ValueError("Could not parse CSV file")
    elif ext in ("xlsx", "xls"):
        return pd.read_excel(buf)
    elif ext == "json":
        return pd.read_json(buf)
    elif ext == "parquet":
        return pd.read_parquet(buf)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _call_groq(client: Groq, prompt: str, system: str = "",
               max_tokens: int = 1800) -> str:
    """Single Groq LLM call."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()


def _compute_health_score(df: pd.DataFrame, anomalies: dict) -> tuple[int, str]:
    score = 100
    miss_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
    score -= min(30, int(miss_pct * 3))
    dup_pct = df.duplicated().sum() / len(df) * 100
    score -= min(20, int(dup_pct * 2))
    n_outlier_cols = len(anomalies.get("outliers", {}))
    score -= min(20, n_outlier_cols * 4)
    score -= len(anomalies.get("constant_columns", [])) * 5
    score -= len(anomalies.get("high_missing", [])) * 3
    score = max(0, min(100, score))
    if score >= 85:   grade = "Excellent"
    elif score >= 70: grade = "Good"
    elif score >= 50: grade = "Fair"
    else:             grade = "Poor"
    return score, grade


def _build_charts(df: pd.DataFrame) -> list:
    """Build Plotly figures — same logic as original Streamlit app."""
    charts = []
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols    = df.select_dtypes(include=["datetime64"]).columns.tolist()

    DARK = "#0d0d12"
    SURFACE = "#13131a"
    PURPLE = "#8b5cf6"
    BLUE   = "#3b82f6"
    TEXT   = "#94a3b8"
    GRID   = "rgba(255,255,255,0.05)"

    base_layout = dict(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE,
        font=dict(color=TEXT, family="Inter, sans-serif", size=11),
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID),
    )

    # 1. Trend / time-series
    if date_cols and numeric_cols:
        dcol, ycol = date_cols[0], numeric_cols[0]
        tmp = df[[dcol, ycol]].dropna().sort_values(dcol)
        fig = go.Figure(go.Scatter(
            x=tmp[dcol], y=tmp[ycol], mode="lines",
            line=dict(color=PURPLE, width=2),
            fill="tozeroy", fillcolor="rgba(139,92,246,0.08)",
        ))
        fig.update_layout(**base_layout, title=dict(text=f"{ycol} over time", font=dict(size=13)))
        charts.append(fig)
    elif len(numeric_cols) >= 1:
        col = numeric_cols[0]
        tmp = df[col].dropna().reset_index()
        fig = go.Figure(go.Scatter(
            x=tmp["index"], y=tmp[col], mode="lines",
            line=dict(color=PURPLE, width=2),
            fill="tozeroy", fillcolor="rgba(139,92,246,0.08)",
        ))
        fig.update_layout(**base_layout, title=dict(text=f"{col} trend", font=dict(size=13)))
        charts.append(fig)

    # 2. Bar chart — categorical
    if cat_cols:
        col = cat_cols[0]
        vc = df[col].value_counts().head(10)
        fig = go.Figure(go.Bar(
            x=vc.index.tolist(), y=vc.values.tolist(),
            marker=dict(
                color=vc.values.tolist(),
                colorscale=[[0, "rgba(59,130,246,0.4)"], [1, BLUE]],
                line=dict(width=0),
            ),
        ))
        fig.update_layout(**base_layout, title=dict(text=f"{col} distribution", font=dict(size=13)))
        charts.append(fig)
    elif len(numeric_cols) >= 2:
        col = numeric_cols[1]
        vc = pd.cut(df[col].dropna(), bins=10).value_counts().sort_index()
        fig = go.Figure(go.Bar(
            x=[str(i) for i in vc.index], y=vc.values.tolist(),
            marker_color=BLUE,
        ))
        fig.update_layout(**base_layout, title=dict(text=f"{col} bins", font=dict(size=13)))
        charts.append(fig)

    # 3. Correlation heatmap
    if len(numeric_cols) >= 2:
        cols6 = numeric_cols[:8]
        corr = df[cols6].corr().round(2)
        fig = go.Figure(go.Heatmap(
            z=corr.values, x=cols6, y=cols6,
            colorscale=[[0, "#1e1040"], [0.5, "#4c1d95"], [1, "#a78bfa"]],
            zmin=-1, zmax=1,
            text=corr.values.round(2),
            texttemplate="%{text}",
        ))
        fig.update_layout(**base_layout, title=dict(text="Correlation Matrix", font=dict(size=13)))
        charts.append(fig)

    # 4. Violin plot
    if len(numeric_cols) >= 1:
        cols_v = numeric_cols[:4]
        fig = go.Figure()
        colours = [PURPLE, BLUE, "#10b981", "#f59e0b"]
        for i, col in enumerate(cols_v):
            fig.add_trace(go.Violin(
                y=df[col].dropna(), name=col,
                fillcolor=colours[i % len(colours)],
                line_color=colours[i % len(colours)],
                opacity=0.75, box_visible=True, meanline_visible=True,
            ))
        fig.update_layout(**base_layout, title=dict(text="Statistical Variance", font=dict(size=13)))
        charts.append(fig)

    # 5. Scatter
    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        color_col = cat_cols[0] if cat_cols else None
        fig = px.scatter(
            df.sample(min(2000, len(df))),
            x=x_col, y=y_col, color=color_col,
            color_discrete_sequence=px.colors.sequential.Purples_r,
            opacity=0.65,
        )
        fig.update_layout(**base_layout, title=dict(text=f"{x_col} vs {y_col}", font=dict(size=13)))
        charts.append(fig)

    # 6. Donut chart
    if cat_cols:
        col = cat_cols[0]
        vc = df[col].value_counts().head(7)
        fig = go.Figure(go.Pie(
            labels=vc.index.tolist(), values=vc.values.tolist(),
            hole=0.55,
            marker=dict(colors=px.colors.sequential.Purples_r[:len(vc)]),
        ))
        fig.update_layout(**base_layout, title=dict(text=f"{col} composition", font=dict(size=13)))
        charts.append(fig)

    # 7. Top-N bar
    if len(numeric_cols) >= 1 and cat_cols:
        num_col, cat_col = numeric_cols[0], cat_cols[0]
        top = df.groupby(cat_col)[num_col].mean().nlargest(8)
        fig = go.Figure(go.Bar(
            x=top.values.tolist(), y=top.index.tolist(),
            orientation="h",
            marker=dict(
                color=top.values.tolist(),
                colorscale=[[0, "rgba(139,92,246,0.3)"], [1, PURPLE]],
            ),
        ))
        fig.update_layout(**base_layout, title=dict(text=f"Top {cat_col} by avg {num_col}", font=dict(size=13)))
        charts.append(fig)

    return charts


def _build_forecast(df: pd.DataFrame) -> Optional[go.Figure]:
    """Linear regression forecast chart."""
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        return None

    DARK = "#0d0d12"
    SURFACE = "#13131a"
    PURPLE = "#8b5cf6"
    TEXT = "#94a3b8"
    GRID = "rgba(255,255,255,0.05)"

    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    if date_cols:
        dcol = date_cols[0]
        ycol = numeric_cols[0]
        tmp = df[[dcol, ycol]].dropna().sort_values(dcol)
        x_num = np.arange(len(tmp))
        y = tmp[ycol].values
    else:
        ycol = numeric_cols[0]
        y = df[ycol].dropna().values
        x_num = np.arange(len(y))

    if len(x_num) < 10:
        return None

    slope, intercept, r, p, se = stats.linregress(x_num, y)
    future = np.arange(len(x_num), len(x_num) + max(10, len(x_num) // 5))
    y_fit  = slope * x_num + intercept
    y_fut  = slope * future + intercept
    ci     = 1.96 * se * np.sqrt(1 + 1 / len(x_num) + (future - x_num.mean()) ** 2 /
                                  np.sum((x_num - x_num.mean()) ** 2))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(x_num) + list(future),
        y=list(y_fit) + list(y_fut),
        mode="lines", name="Projection",
        line=dict(color=PURPLE, width=2, dash="solid"),
    ))
    fig.add_trace(go.Scatter(
        x=list(future) + list(future[::-1]),
        y=list(y_fut + ci) + list((y_fut - ci)[::-1]),
        fill="toself",
        fillcolor="rgba(139,92,246,0.1)",
        line=dict(width=0),
        name="1.5σ Confidence Band",
    ))
    fig.add_trace(go.Scatter(
        x=list(x_num), y=list(y),
        mode="lines", name="Actual",
        line=dict(color="rgba(148,163,184,0.4)", width=1),
    ))
    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=SURFACE,
        font=dict(color=TEXT, family="Inter, sans-serif", size=11),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=GRID, linecolor=GRID),
        yaxis=dict(gridcolor=GRID, linecolor=GRID),
        title=dict(text="Linear Regression Projection", font=dict(size=14, color="#f0f0f5")),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    )
    return fig


def _fig_to_json(fig) -> dict:
    """Convert Plotly figure to JSON-serialisable dict."""
    if fig is None:
        return None
    return json.loads(fig.to_json())


# ─────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    api_key: str
    message: str
    history: List[Dict[str, str]] = []
    dataset_context: str = ""


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/", response_model=HealthResponse)
def root():
    return {"status": "ok", "version": "2.0.0", "timestamp": datetime.utcnow().isoformat()}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/warmup")
def warmup():
    """Called by frontend on first load to wake up the Render free tier instance."""
    return {"status": "warm", "timestamp": datetime.utcnow().isoformat()}


# ── UPLOAD & ANALYSE ─────────────────────────────────────────────────────────

@app.post("/api/analyse")
async def analyse(
    file: UploadFile = File(...),
    api_key: str = Form(...),
    report_title: str = Form("Business Intelligence Report"),
    organisation: str = Form("My Organisation"),
    analyst: str = Form("DataMind AI"),
    tone: str = Form("Professional"),
    industry: str = Form("General"),
):
    """
    Main endpoint. Accepts a dataset file + settings.
    Returns full analysis JSON: stats, anomalies, AI narratives,
    chart data, forecast, health score, and dataset preview.
    """
    # 1. Load data
    try:
        raw = await file.read()
        df  = _load_df(raw, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parse error: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Sample large datasets to prevent timeout on free tier
    original_rows = len(df)
    MAX_ROWS = 5000
    if len(df) > MAX_ROWS:
        df = df.sample(n=MAX_ROWS, random_state=42).reset_index(drop=True)

    # 2. Statistical analysis
    stats_summary = analyze_dataframe(df)
    anomalies     = detect_anomalies(df)
    col_insights  = get_column_insights(df)
    health_score, health_grade = _compute_health_score(df, anomalies)

    # 3. Groq AI narratives
    try:
        client = Groq(api_key=api_key)
        # Quick validation call
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Groq API key.")

    context = (
        f"Dataset: {file.filename} | Rows: {df.shape[0]} | Cols: {df.shape[1]} | "
        f"Organisation: {organisation} | Industry: {industry} | Tone: {tone} | "
        f"Numeric cols: {df.select_dtypes(include=np.number).columns.tolist()} | "
        f"Categorical cols: {df.select_dtypes(include=['object','category']).columns.tolist()} | "
        f"Stats summary: {json.dumps(stats_summary, default=str)[:1500]}"
    )

    exec_summary = _call_groq(client, f"""
Write a 3-paragraph executive summary for this dataset.
Cover: scope & structure, key statistical patterns, and business implications.
Tone: {tone}. Organisation: {organisation}. Industry: {industry}.
{context}
""")

    key_findings = _call_groq(client, f"""
Write exactly 5 key findings numbered 1 to 5.
Format each as: NUMBER. TITLE: Description with specific numbers from the data.
{context}
""")

    anomaly_context = json.dumps(anomalies, default=str)[:1200]
    anomaly_narrative = _call_groq(client, f"""
Analyse these anomalies and explain their business significance clearly.
Anomalies: {anomaly_context}
Dataset context: {context}
""")

    recommendations = _call_groq(client, f"""
Write exactly 5 numbered actionable recommendations based on this analysis.
Format: NUMBER. TITLE: Specific action with expected outcome.
{context}
Anomalies: {anomaly_context}
""")

    health_commentary = _call_groq(client, f"""
In 2-3 sentences explain what a data health score of {health_score}/100 ({health_grade}) means
for this specific dataset and what it implies for analysis reliability.
{context}
""", max_tokens=200)

    # 4. Charts
    charts     = _build_charts(df)
    forecast   = _build_forecast(df)

    # 5. Dataset preview — convert Timestamps and other non-serializable types to str
    import pandas as _pd
    preview_df = df.head(50).replace({np.nan: None})
    # Convert datetime columns to ISO strings
    for col in preview_df.columns:
        if preview_df[col].dtype == "object":
            preview_df[col] = preview_df[col].astype(str).where(preview_df[col].notna(), None)
        elif hasattr(preview_df[col], "dt"):
            preview_df[col] = preview_df[col].astype(str)
    preview_rows = []
    for row in preview_df.to_dict(orient="records"):
        clean = {}
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                clean[k] = v.isoformat()
            elif hasattr(v, "item"):          # numpy scalar
                clean[k] = v.item()
            else:
                clean[k] = v
        preview_rows.append(clean)
    preview_cols = [{"key": c, "label": c} for c in df.columns]

    # 6. Column info
    col_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        col_info.append({
            "name": col,
            "dtype": dtype,
            "missing": int(df[col].isnull().sum()),
            "missing_pct": round(df[col].isnull().sum() / len(df) * 100, 1),
            "unique": int(df[col].nunique()),
        })

    return JSONResponse({
        "meta": {
            "filename": file.filename,
            "rows": int(df.shape[0]),
            "cols": int(df.shape[1]),
            "numeric_cols": int(len(df.select_dtypes(include=np.number).columns)),
            "cat_cols": int(len(df.select_dtypes(include=["object", "category"]).columns)),
            "missing_pct": round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 1),
            "duplicate_rows": int(df.duplicated().sum()),
            "report_title": report_title,
            "organisation": organisation,
            "analyst": analyst,
            "tone": tone,
            "industry": industry,
            "generated_at": datetime.utcnow().isoformat(),
        },
        "health": {
            "score": health_score,
            "grade": health_grade,
            "commentary": health_commentary,
        },
        "stats": stats_summary,
        "anomalies": anomalies,
        "col_insights": col_insights,
        "narratives": {
            "exec_summary": exec_summary,
            "key_findings": key_findings,
            "anomaly_narrative": anomaly_narrative,
            "recommendations": recommendations,
        },
        "charts": [_fig_to_json(f) for f in charts],
        "forecast": _fig_to_json(forecast),
        "preview": {
            "columns": preview_cols,
            "rows": preview_rows,
        },
        "col_info": col_info,
    })


# ── PDF EXPORT ───────────────────────────────────────────────────────────────

@app.post("/api/pdf")
async def generate_pdf(
    file: UploadFile = File(...),
    api_key: str = Form(...),
    report_title: str = Form("Business Intelligence Report"),
    organisation: str = Form("My Organisation"),
    analyst: str = Form("DataMind AI"),
    tone: str = Form("Professional"),
    industry: str = Form("General"),
    exec_summary: str = Form(""),
    key_findings: str = Form(""),
    anomaly_narrative: str = Form(""),
    recommendations: str = Form(""),
    health_score: int = Form(0),
    health_grade: str = Form("Good"),
    charts_json: str = Form("[]"),
    forecast_json: str = Form("null"),
):
    """Generate and return the PDF report as bytes."""
    try:
        raw = await file.read()
        df  = _load_df(raw, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parse error: {e}")

    # Use smaller sample for PDF to keep generation fast on free tier
    if len(df) > 2000:
        df = df.sample(n=2000, random_state=42).reset_index(drop=True)

    stats_summary = analyze_dataframe(df)
    anomalies     = detect_anomalies(df)

    # Skip chart reconstruction — charts are handled client-side
    # PDF chart rendering requires kaleido which may not be available on server
    charts: list = []
    forecast = None

    try:
        pdf_bytes = generate_pdf_report(
            title=report_title,
            company=organisation,
            analyst=analyst,
            filename=file.filename,
            df=df,
            exec_summary=exec_summary,
            key_findings=key_findings,
            anomaly_narrative=anomaly_narrative,
            recommendations=recommendations,
            stats_summary=stats_summary,
            anomalies=anomalies,
            charts=charts,
            forecast_fig=forecast,
            tone=tone,
            industry=industry,
            health_score=health_score,
            health_grade=health_grade,
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{report_title}.pdf"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)[:200]}")


# ── CHAT ─────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Chat with the dataset via Groq."""
    try:
        client = Groq(api_key=req.api_key)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Groq API key.")

    system = f"""You are a senior data analyst assistant for DataMind AI.
Answer questions about this specific dataset only. Be concise and insightful.
Dataset context: {req.dataset_context[:2000]}"""

    messages = [{"role": "system", "content": system}]
    for h in req.history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": req.message})

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=600,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq error: {e}")

    return {"answer": answer}


# ── VALIDATE API KEY ─────────────────────────────────────────────────────────

@app.post("/api/validate-key")
async def validate_key(api_key: str = Form(...)):
    """Quick check that the Groq key works."""
    try:
        client = Groq(api_key=api_key)
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        return {"valid": True}
    except Exception:
        return {"valid": False}
