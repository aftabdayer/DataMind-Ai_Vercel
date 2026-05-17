# ⚙️ DataMind AI — Backend (FastAPI)

> **FastAPI backend** for DataMind AI — statistical analysis engine, data quality scoring, Groq LLM integration, and PDF report generation from any CSV/Excel upload.

👉 **[Live App](https://datamind-ai-frontend.vercel.app/)** &nbsp;|&nbsp; 🖥️ **[Frontend Repo](https://github.com/aftabdayer/datamind-frontend)**

> **Note:** This repo was previously named `DataMind-Ai_Vercel`. Renamed to `datamind-backend` for clarity — this contains the FastAPI backend, not a Vercel deployment.

---

## What This Repo Contains

This is the API and analysis engine for DataMind AI. It handles:

- Ingesting CSV/Excel uploads
- Statistical analysis (distributions, correlations, outlier detection)
- Data quality scoring (flags skewness, missing values, anomalies)
- Linear regression forecasting
- Groq + LLaMA3 AI analysis and natural language Q&A
- PDF report generation via ReportLab

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /analyze` | Upload CSV/Excel → returns stats, charts, quality score |
| `POST /forecast` | Run linear regression forecast on a numeric column |
| `POST /report` | Generate and return full PDF report |
| `POST /chat` | Natural language Q&A about the uploaded dataset |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI · Python |
| Analysis | pandas · NumPy · scikit-learn |
| Charts | Plotly |
| PDF Generation | ReportLab |
| LLM | Groq API · LLaMA3 |
| Deployment | Render |

---

## Running Locally

```bash
# 1. Clone
git clone https://github.com/aftabdayer/datamind-backend.git
cd datamind-backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Groq API key
export GROQ_API_KEY=your_key_here

# 4. Start the server
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`  
Docs at `http://localhost:8000/docs`

---

## Origin

> The original single-file Streamlit prototype of this project is preserved at [datamind-ai](https://github.com/aftabdayer/datamind-ai).  
> This backend, combined with [datamind-frontend](https://github.com/aftabdayer/datamind-frontend), is the full production version.

---

## Author

**Aftab Dayer** · [LinkedIn](https://linkedin.com/in/aftabdayer) · [GitHub](https://github.com/aftabdayer)  
NIT Hamirpur 2025 · IEEE Published · Microsoft Power BI Certified (PL-300)
