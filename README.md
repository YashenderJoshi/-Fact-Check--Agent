# TruthLens AI — Automated Claim Verification Engine

> Upload any PDF. Get every factual claim verified against live web data in seconds.

![TruthLens AI Banner](https://via.placeholder.com/900x300/0a0a0f/6347ff?text=TruthLens+AI)

---

## What it does

TruthLens AI is an end-to-end fact-checking agent that:

1. **Extracts** factual claims, statistics, dates, and figures from any PDF
2. **Searches** the live web (DuckDuckGo) for evidence per claim
3. **Verifies** each claim with Gemini AI reasoning
4. **Returns** a verdict — Verified / Inaccurate / False — plus the corrected fact

---

## Features

| Feature | Detail |
|---|---|
| 📄 PDF ingestion | Any research paper, article, report, or whitepaper |
| 🤖 AI claim extraction | Gemini 1.5 Flash isolates verifiable statements |
| 🌐 Live web search | DuckDuckGo — no API key needed |
| ✅ AI verification | Gemini reasons over evidence to classify each claim |
| 📝 Corrected facts | Not just True/False — the right answer is always shown |
| 📊 Metrics dashboard | Total, Verified, Inaccurate, False at a glance |
| ⬇️ CSV export | Download full results for your records |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI / LLM | Google Gemini 1.5 Flash |
| Web Search | DuckDuckGo Search (duckduckgo-search) |
| PDF Parsing | PyMuPDF (fitz) |
| Deployment | Streamlit Community Cloud |

---

## Project Structure

```
fact-check-agent/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md
│
├── .streamlit/
│   └── config.toml         # Theme & server config
│
└── utils/
    ├── __init__.py
    ├── pdf_reader.py       # PDF → text extraction
    ├── extractor.py        # Text → claims via Gemini
    └── verifier.py         # Claims → verdicts via DDG + Gemini
```

---

## Setup & Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/fact-check-agent.git
cd fact-check-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a free Gemini API key

Go to [Google AI Studio](https://aistudio.google.com) → Get API Key → Copy it.

### 4. Run the app

```bash
streamlit run app.py
```

Enter your Gemini API key in the sidebar, upload a PDF, and hit run.

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New app** → select your repo → set `app.py` as the entry point
4. Deploy — it's live in under 2 minutes

> Users enter their own Gemini API key in the sidebar. No secrets needed server-side.

---

## Example Output

| Claim | Status | Corrected Fact |
|---|---|---|
| India's population is 1.2 billion | 🟡 Inaccurate | India's population is approximately 1.44 billion (2024) |
| Tesla was founded in 2003 | ✅ Verified | — |
| Global GDP grew by 15% in 2023 | 🔴 False | Global GDP growth was approximately 3.1% in 2023 |

---

## Architecture

```
PDF Upload
    │
    ▼
PyMuPDF → Raw Text
    │
    ▼
Gemini 1.5 Flash → Claim List (JSON)
    │
    ▼  (per claim, parallel-ready)
DuckDuckGo Search → Evidence Snippets
    │
    ▼
Gemini 1.5 Flash → Verdict + Corrected Fact
    │
    ▼
Streamlit UI → Results Table + CSV Export
```

---

## Built by

Made as a demonstration of applied AI product thinking:
- Prompt engineering for structured extraction
- Agentic search-then-verify loop
- Clean modular Python architecture
- Production-ready deployment

---

*TruthLens AI — because facts matter.*
