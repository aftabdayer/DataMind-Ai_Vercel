# ⚙️ DataMind AI — Backend (FastAPI)

> **FastAPI backend** for DataMind AI — statistical analysis engine, data quality scoring, Groq LLM integration, and PDF report generation from any CSV/Excel upload.

👉 **[Live App](https://datamind-ai-frontend.vercel.app/)** &nbsp;|&nbsp; 🖥️ **[Frontend Repo](https://github.com/aftabdayer/datamind-frontend)**

---

## What This Repo Contains

This is the API and analysis engine for DataMind AI. Upload a dataset → get back AI-written analysis, interactive charts, forecasts, anomaly detection, and a downloadable PDF — all in under 60 seconds.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check — confirms the server is up |
| `GET` | `/api/warmup` | Wakes up the Render free-tier instance on first load |
| `POST` | `/api/analyse` | **Main endpoint** — upload CSV/Excel + settings → returns full analysis JSON (stats, anomalies, AI narratives, charts, forecast, health score, dataset preview) |
| `POST` | `/api/pdf` | Generate and download a PDF report from pre-computed analysis data |
| `POST` | `/api/chat` | Natural language Q&A about the uploaded dataset via Groq LLM |
| `POST` | `/api/validate-key` | Validate a Groq API key before running analysis |

---

## `/api/analyse` — What It Returns

```json
{
  "meta":       { "filename", "rows", "cols", "missing_pct", ... },
  "health":     { "score": 87, "grade": "Excellent", "commentary": "..." },
  "stats":      { "key_stats per column" },
  "anomalies":  { "outliers", "constant_columns", "high_missing" },
  "narratives": {
    "exec_summary":       "3-paragraph AI summary",
    "key_findings":       "5 numbered findings with data",
    "anomaly_narrative":  "Business significance of anomalies",
    "recommendations":    "5 numbered actionable recommendations"
  },
  "charts":     [ "Plotly JSON — trend, bar, heatmap, violin, scatter, donut, top-N" ],
  "forecast":   "Plotly JSON — linear regression projection with confidence band",
  "preview":    { "columns", "rows (first 50)" },
  "col_info":   [ "dtype, missing%, unique count per column" ]
}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI · Python |
| Analysis | pandas · NumPy · SciPy · scikit-learn |
| Charts | Plotly |
| PDF Generation | ReportLab |
| LLM | Groq API · LLaMA-3.3-70b |
| Deployment | Render |

---

## Project Structure

```
datamind-backend/
├── main.py              ← All FastAPI routes
├── data_analyzer.py     ← Statistical analysis + anomaly detection
├── report_generator.py  ← ReportLab PDF builder
├── render.yaml          ← Render deployment config
└── requirements.txt
```

---

## Running Locally

```bash
# 1. Clone
git clone https://github.com/aftabdayer/datamind-backend.git
cd datamind-backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

Get a free Groq API key at [console.groq.com](https://console.groq.com) — no credit card needed.

---

## Origin

> The original single-file Streamlit prototype is preserved at [datamind-ai](https://github.com/aftabdayer/datamind-ai) (archived — live app no longer running).  
> This backend + [datamind-frontend](https://github.com/aftabdayer/datamind-frontend) is the full production version.

---

## Author

**Aftab Dayer** · [LinkedIn](https://linkedin.com/in/aftabdayer) · [GitHub](https://github.com/aftabdayer)  
NIT Hamirpur 2025 · IEEE Published · Microsoft Power BI Certified (PL-300)
