# AI Earnings Call Summarizer & Analyst Dashboard


[![Python](https://img.shields.com/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.com/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.com/badge/LLM-OpenAI_GPT--4o--mini-00A67E.svg)](https://openai.com/)
[![Plotly](https://img.shields.com/badge/Data_Viz-Plotly-3F4F75.svg)](https://plotly.com/)



An institutional-grade, AI-powered financial intelligence application designed to ingest long, unstructured corporate earnings call transcripts and output high-fidelity executive summaries, management sentiment analysis, capital allocation guides, and key bullish/bearish catalysts. 

Built in a single weekend to demonstrate full-stack Python engineering, professional prompt engineering, and quant-focused data visualization techniques suitable for modern FinTech, equity research, and AI data science roles.

---

##  Project Overview & Recruiter Value

When tech companies or hedge funds review student portfolios, they are often fatigued by generic "to-do lists" or "movie recommendation" apps. This project demonstrates **deep domain knowledge** paired with practical engineering skill:
- **Financial Rigor**: Standard NLP pipelines fail on corporate jargon. This tool implements highly structured prompts matching institutional buy-side frameworks to pull exact numbers, quantitative guidance ranges, and Capex shifts.
- **Robust NLP Chunking**: Instead of hitting model context limits, the pipeline implements an elegant sliding-window token chunker utilizing `tiktoken` to synthesize transcripts of arbitrary length.
- **Corporate Linguistics**: Highlights executive rhetorical strategies by tracking word-use frequencies (e.g., *accelerating* vs. *headwinds*) with `pandas` and displaying them in clean, high-contrast Plotly visualizers.

---

##  Architecture & Summarization Pipeline

```
┌────────────────────────────────────────────────────────┐
│               Streamlit Web Interface                  │
│  (Company Selection, File Upload, Controls, Insights)  │
└───────────────────────────┬────────────────────────────┘
                            │ Raw Transcript Text
                            ▼
┌────────────────────────────────────────────────────────┐
│                  src/chunker.py                        │
│ - Split by speaker (exec vs. analyst QA)               │
│ - Sliding-window chunking (using tiktoken)             │
└───────────────────────────┬────────────────────────────┘
                            │ token-bounded chunks
                            ▼
┌────────────────────────────────────────────────────────┐
│                 src/summarizer.py                      │
│ - Map Phase: Generate qualitative findings per chunk   │
│ - Reduce Phase: Synthesize findings into memo format   │
│ - Financial Prompts (GPT-4o-mini / buy-side filters)    │
└───────────────────────────┬────────────────────────────┘
                            │ structured summaries & tables
                            ▼
┌────────────────────────────────────────────────────────┐
│                 src/sentiment.py                       │
│ - Linguistic scoring (sentiment index: -10 to +10)    │
│ - Strategic Focus (Growth vs. Margin Defense vs. Capex)│
│ - Regex count of buy-side vocabulary (Pandas)          │
└───────────────────────────┬────────────────────────────┘
                            │ parsed metrics & quotes
                            ▼
┌────────────────────────────────────────────────────────┐
│                  src/visuals.py                        │
│ - High-contrast Plotly sentiment gauge                 │
│ - Donut chart of strategic focus                       │
│ - Horizontal bar chart of vocabulary distribution      │
└────────────────────────────────────────────────────────┘
```

1. **Transcript Ingestion**: Ingests raw `.txt` transcript files.
2. **Chunking Engine (`src/chunker.py`)**: Uses `tiktoken` to compute precise token counts. Text is split recursively into 2,500-token chunks with a 200-token overlap to maintain textual coherence.
3. **Map-Reduce Summarizer (`src/summarizer.py`)**: Processes chunks in parallel (Map Phase) to pull structured insights, then compresses them (Reduce Phase) into a master institutional memo.
4. **Sentiment & Linguistic Engine (`src/sentiment.py`)**: Evaluates management confidence and strategic priority levels, utilizing Python's `re` module to count corporate buzzwords.
5. **Visualization Layer (`src/visuals.py`)**: Converts linguistic data into real-time interactive Plotly charts (sentiment gauge, strategic donut, and vocabulary horizontal bar chart).

---

##  Features

- **Multi-Source Ingestion**: Choose from pre-loaded sample earnings calls (Nvidia, Apple, Tesla) or drag-and-drop any custom transcript `.txt` file.
- **C-Suite Sentiment Gauge**: Interactive gauge chart rating the tone of the call on an institutional scale (-10 to +10).
- **Interactive Strategic Focus Allocation**: View the percentage of discussion time split among Growth, Margin Defense, Macro Headwinds, and AI Innovation.
- **Dynamic Guidance Table**: Highlights changes in guidance (Revenue, Margins, Capex) in an easy-to-read, structured grid.
- **Contrast-Adjusted Dark/Light Ready Layout**: Clean typography designed for high readability in investment meetings.

---

##  Quick Start & Installation

### Prerequisites
- Python 3.9 or higher
- An OpenAI API Key (configured in `.env`)

### 1. Clone & Set Up Directory
```bash
git clone https://github.com/yourusername/ai-earnings-summarizer.git
cd ai-earnings-summarizer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Secrets
Create a `.env` file in the root directory and add your OpenAI key:
```env
OPENAI_API_KEY="your-actual-openai-api-key"
```

### 4. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
The app will automatically launch in your default web browser at `http://localhost:8501`.

---

##  Future Roadmaps & Enhancements

- [ ] **SEC EDGAR Integration**: Automatically fetch transcripts and 10-K filings directly from the SEC database using ticker symbols.
- [ ] **Voice-to-Text Ingestion**: Integrate whisper-1 model to process live audio streams of earnings call recordings directly.
- [ ] **Vector Database Search (RAG)**: Store historical calls in Pinecone/Chroma to let analysts query and compare quarter-over-quarter guidance shifts using semantic search.
- [ ] **Multi-Company Comparatives**: Overlay sentiment trajectories for peer groups (e.g., Big Tech or Semiconductor leaders) on a unified line chart.
