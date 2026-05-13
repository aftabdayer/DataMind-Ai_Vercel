# 🧠 DataMind AI — Business Intelligence Platform

> Upload any dataset → Get a full AI-written business report with charts, forecasts & PDF download

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![Groq](https://img.shields.io/badge/Powered%20by-Groq%20AI-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ What It Does

**DataMind AI** turns raw CSV or Excel files into a complete business intelligence report in under 60 seconds — no coding required.

| Feature | Details |
|---|---|
| 📊 **5 Smart Charts** | Trend, distribution, heatmap, scatter, violin — auto-built from your data |
| 🤖 **AI-Written Analysis** | Executive summary, key findings & recommendations via Groq LLM |
| 📈 **Trend Forecast** | Linear regression forecast with future projection |
| ⚠️ **Anomaly Detection** | Outliers, skewness, missing values & data quality scoring |
| 📄 **PDF Download** | Full professional report with all sections |
| 💬 **Chat With Data** | Ask questions about your dataset in natural language |

---

## 🚀 Live Demo

👉 **[Try it here](https://aftabdayer-datamind-ai-app.streamlit.app)** *(bring your own free Groq API key)*

---

## 🛠️ Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/aftabdayer/datamind-ai.git
cd datamind-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Get your **free Groq API key** at [console.groq.com](https://console.groq.com) — no credit card needed.

---

## 📁 Project Structure

```
datamind-ai/
├── app.py                # Main Streamlit application
├── data_analyzer.py      # Statistical analysis engine
├── report_generator.py   # PDF report builder (ReportLab)
├── requirements.txt      # Python dependencies
└── .streamlit/
    └── config.toml       # UI theme configuration
```

---

## 📦 Requirements

- Python 3.10+
- A free [Groq API key](https://console.groq.com)
- CSV or Excel file (.csv / .xlsx)

---

## 🔑 How To Use

1. Open the app and enter your **Groq API key** in the sidebar
2. Upload your **CSV or Excel** file
3. Fill in report title, company name, analyst name
4. Click **Generate Full AI Report**
5. Explore charts, findings, forecasts → download the PDF

---

## 🧰 Built With

- [Streamlit](https://streamlit.io) — Web UI
- [Groq](https://groq.com) — LLM inference (llama3)
- [Plotly](https://plotly.com) — Interactive charts
- [ReportLab](https://www.reportlab.com) — PDF generation
- [Pandas](https://pandas.pydata.org) / [NumPy](https://numpy.org) — Data processing

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built by [Aftab Dayer](https://github.com/aftabdayer)*
