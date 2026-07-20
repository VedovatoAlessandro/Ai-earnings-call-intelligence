"""
app.py - Main Streamlit Dashboard
Acts as the central entry point for the AI Earnings Call Summarizer.
Run locally with: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load local environment files
load_dotenv()

# Set up clean, professional page configuration
st.set_page_config(
    page_title="AI Earnings Call Summarizer | Institutional Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom css for a polished investor feel
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)

# Import our modular local pipeline components
try:
    from src.summarizer import EarningsSummarizer
    from src.sentiment import SentimentAnalyzer
    from src.visuals import create_sentiment_gauge, create_strategic_focus_chart, create_keyword_bar_chart
except ImportError as e:
    st.error(f"Error importing modules. Please ensure you are running this from the repository root: {str(e)}")

# Create sample transcripts for typical portfolio companies (Mocked data so it runs immediately)
# In real practice, these can be loaded from txt files.
SAMPLE_NVIDIA_TRANSCRIPT = """
Jensen Huang: Welcome to our Q4 FY25 earnings call. We have achieved another historic quarter. 
Our revenue reached a record $30.2B, up 22% sequentially and up 200% year-on-year. 
This incredible acceleration is driven globally by the transition to accelerated computing and generative AI. 
Our next-generation Blackwell platform is in full production. Demand for Blackwell is staggering, 
and we expect to ship several billion dollars of Blackwell systems in the upcoming quarters.
Colette Kress: GAAP gross margins were 76.0%. Net income was $16.8B. 
For Q1 FY26, we expect revenue to be $32.0B plus or minus 2%, reflecting continued supply tailwinds, 
though we continue to face some supply constraints on key silicon and packaging lines. 
We are expanding Capex to $2.5B to secure advanced packaging lines.
We are confident in our operational capabilities, but remain mindful of macroeconomic risks, 
including general inflation and export control dynamics in various jurisdictions.
"""

SAMPLE_APPLE_TRANSCRIPT = """
Tim Cook: Good afternoon. Today, Apple is reporting active devices reaching an all-time high of 2.2 billion. 
Our revenue for the quarter was $119.6 billion, up 2% year-on-year, driven by robust sales of the iPhone 15 lineup 
and double-digit growth in our services division, which hit $23.1 billion in revenue. 
Our margins remain highly resilient at 45.9%. We are investing heavily in our artificial intelligence roadmap, 
with Apple Intelligence launching across our ecosystems to overwhelmingly positive customer reception.
Luca Maestri: Our cash generation remains outstanding, returning $27 billion to shareholders this quarter 
via share buybacks and dividends. For our next quarter, we expect total company revenue to be flat year-on-year 
as we navigate general smartphone supply chain pressures and a challenging foreign exchange environment. 
However, services momentum remains extremely strong, offsetting minor hardware headwinds. R&D spending was $7.5B, 
reflecting our commitment to platform innovation.
"""

SAMPLE_TESLA_TRANSCRIPT = """
Elon Musk: Thanks for joining. In Q4, we delivered over 484,000 electric vehicles, achieving a record annual run-rate. 
However, we are currently between two major growth waves. The first wave was driven by Model 3 and Y, and the next wave 
will be driven by our upcoming next-generation low-cost vehicle, slated for production in late 2025. 
Our margins are under pressure due to pricing actions and competitive dynamics, with automotive gross margins excluding credits 
coming in at 17.2%. We are investing capital aggressively, especially on our FSD hardware and Dojo AI cluster.
Vaibhav Taneja: Free cash flow was $2.0 billion. Capex was $2.3 billion. 
We expect capital expenditure to exceed $10 billion in 2025 as we expand gigafactories and AI infrastructure. 
We expect automotive volume growth to be notably lower in 2025 as our teams work on launching the next-generation vehicle. 
Macro headwinds, particularly interest rates, remain a strong constraint on demand. We must operate with extreme fiscal caution.
"""

# Store sample transcripts in a convenient lookup dictionary
COMPANY_TRANSCRIPTS = {
    "Nvidia (NVDA) - Q4 FY25": SAMPLE_NVIDIA_TRANSCRIPT,
    "Apple (AAPL) - Q1 FY25": SAMPLE_APPLE_TRANSCRIPT,
    "Tesla (TSLA) - Q4 FY24": SAMPLE_TESLA_TRANSCRIPT
}

# ====================
# SIDEBAR
# ====================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=150&q=80", width=80)
    st.title("Earnings Call Analyzer")
    st.markdown("---")
    
    # 1. Company Selection Mode
    source_mode = st.radio("Select Transcript Source", ["Use Sample Companies", "Upload Custom Transcript (.txt)"])
    
    transcript_text = ""
    company_name = "Custom Company"
    
    if source_mode == "Use Sample Companies":
        selected_company = st.selectbox("Choose a Portfolio Company", list(COMPANY_TRANSCRIPTS.keys()))
        transcript_text = COMPANY_TRANSCRIPTS[selected_company]
        company_name = selected_company.split(" - ")[0]
    else:
        uploaded_file = st.file_uploader("Upload a transcript file", type=["txt"])
        company_name = st.text_input("Enter Company Name", placeholder="e.g., Microsoft (MSFT)")
        if uploaded_file is not None:
            transcript_text = uploaded_file.read().decode("utf-8")
            
    st.markdown("---")
    
    # 2. Configurable parameters
    st.subheader("Model Configuration")
    selected_model = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    
    max_chunk_size = st.slider("Max Chunk Size (Tokens)", 1500, 4000, 2500, step=500)
    
    st.markdown("---")
    st.caption("Developed by a Quantitative Finance & Data Science Student.")

# ====================
# MAIN DASHBOARD LAYOUT
# ====================
st.markdown(f"<h1 class='main-title'>📊 AI Earnings Call Summarizer & Analyst Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"**Target Company:** `{company_name}` | *Institutional-grade automated equity research*")
st.markdown("---")

# Verify OpenAI API Key and warn if missing
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning("⚠️ **OpenAI API Key is missing from local `.env` configuration.** The dashboard will load but will run with simulated LLM data fallback. To run real LLM queries, set `OPENAI_API_KEY` in your `.env` file.")

if not transcript_text:
    st.info("💡 **Please upload a transcript or select a sample portfolio company from the sidebar to begin analysis.**")
else:
    # Action button to trigger processing
    trigger_analysis = st.button("🚀 Run Comprehensive Analyst Ingestion Pipeline", type="primary")
    
    # We use Streamlit's session state to persist results once calculated
    if trigger_analysis or "summary_report" not in st.session_state or st.session_state.get("analyzed_company") != company_name:
        with st.spinner("Executing transcript chunking, sentiment scoring, and synthesis..."):
            
            # 1. Calculate keyword frequencies immediately (Fast & Local)
            from src.sentiment import count_financial_keywords
            local_keywords = count_financial_keywords(transcript_text)
            
            # 2. Initialize our analyzer and summarizer
            summarizer = EarningsSummarizer(api_key=api_key)
            analyzer = SentimentAnalyzer(api_key=api_key)
            
            # 3. Call OpenAI for Summary & Sentiment
            summary_report = summarizer.summarize(transcript_text, model=selected_model)
            tone_data = analyzer.analyze_tone(transcript_text, model=selected_model)
            
            # 4. Save to session state
            st.session_state["summary_report"] = summary_report
            st.session_state["tone_data"] = tone_data
            st.session_state["local_keywords"] = local_keywords
            st.session_state["analyzed_company"] = company_name

    # Load calculated results from session state
    if "summary_report" in st.session_state:
        summary_report = st.session_state["summary_report"]
        tone_data = st.session_state["tone_data"]
        local_keywords = st.session_state["local_keywords"]
        
        # ==========================================
        # TOP ROW: KPI CARDS
        # ==========================================
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            sentiment_val = tone_data.get("overall_sentiment", 0.0)
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Overall Sentiment Score</div>
                <div class='metric-value'>{sentiment_val} / 10</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi_col2:
            confidence_val = tone_data.get("confidence_rating", 0.0)
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Management Confidence</div>
                <div class='metric-value'>{confidence_val} / 10</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi_col3:
            # Highlight AI references (an important metric for tech recruits!)
            ai_refs = local_keywords.get("artificial intelligence", 0)
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>AI / LLM Mentions</div>
                <div class='metric-value'>{ai_refs} mentions</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi_col4:
            # Highlighting Capex mentions
            capex_refs = local_keywords.get("capex", 0)
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Capex & Capital Mentions</div>
                <div class='metric-value'>{capex_refs} references</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ==========================================
        # MIDDLE ROW: TWO-COLUMN INSIGHTS LAYOUT
        # ==========================================
        main_col, viz_col = st.columns([1.6, 1.0])
        
        with main_col:
            st.subheader("📋 Synthesis & Executive Summary")
            st.markdown(summary_report)
            
        with viz_col:
            st.subheader("📈 Quantitative Rhetorical Visualizations")
            
            # A. Draw Sentiment Gauge
            gauge_fig = create_sentiment_gauge(tone_data.get("overall_sentiment", 0.0))
            st.plotly_chart(gauge_fig, use_container_width=True)
            
            # B. Draw Strategic Focus Pie Chart
            focus_fig = create_strategic_focus_chart(tone_data.get("strategic_focus", {}))
            st.plotly_chart(focus_fig, use_container_width=True)
            
            # C. Draw Keyword Bar Chart
            bar_fig = create_keyword_bar_chart(local_keywords)
            st.plotly_chart(bar_fig, use_container_width=True)
            
        # ==========================================
        # BOTTOM ROW: DETAILED LINGUISTIC QUOTES
        # ==========================================
        st.markdown("---")
        st.subheader("💬 Key Linguistic Transcriptions")
        quote_col1, quote_col2 = st.columns(2)
        
        with quote_col1:
            st.markdown("🟢 **Top Bullish Corporate Statements**")
            for q in tone_data.get("bullish_quotes", []):
                with st.expander(f"\"{q.get('quote', '')[:60]}...\" — {q.get('speaker', 'CEO')}"):
                    st.write(f"**Full Quote:** \"{q.get('quote', '')}\"")
                    st.caption(f"**Strategic Context:** {q.get('context', '')}")
                    
        with quote_col2:
            st.markdown("🔴 **Top Cautious / Risk Disclosures**")
            for q in tone_data.get("bearish_quotes", []):
                with st.expander(f"\"{q.get('quote', '')[:60]}...\" — {q.get('speaker', 'CFO')}"):
                    st.write(f"**Full Quote:** \"{q.get('quote', '')}\"")
                    st.caption(f"**Strategic Context:** {q.get('context', '')}")

        # ==========================================
        # TRANSCRIPT VIEWER
        # ==========================================
        st.markdown("---")
        with st.expander("🔍 View Raw Transcript File"):
            st.text_area("Original Text Submitted", transcript_text, height=250, disabled=True)
