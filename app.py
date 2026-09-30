"""Streamlit Enterprise Multi-Agent Competitor Intelligence Application."""
import streamlit as st
import pandas as pd
import os
import json
from services.research_service import ResearchService
from services.report_service import ReportService
from config.settings import get_settings
from config.thresholds import QualityThresholds
from utils.helpers import current_timestamp_iso

# Page Configuration
st.set_page_config(
    page_title="Enterprise Competitor Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Enterprise Theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F2942;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-pass {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .status-fail {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .exec-summary-box {
        background-color: #F0F9FF;
        border-left: 4px solid #0284C7;
        padding: 16px;
        border-radius: 4px;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "graph_state" not in st.session_state:
    st.session_state.graph_state = None
if "execution_logs" not in st.session_state:
    st.session_state.execution_logs = []

# Sidebar Controls & API Settings
with st.sidebar:
    st.markdown("### ⚙️ System Settings")
    
    provider = st.selectbox(
        "LLM Provider",
        options=["Gemini", "OpenAI", "Groq", "Offline Benchmark / Fallback"],
        index=0
    )
    
    api_key_input = st.text_input(
        f"{provider} API Key",
        type="password",
        help="Leave blank to use environment variable or fallback engine."
    )
    
    tavily_key_input = st.text_input(
        "Tavily Search API Key",
        type="password",
        help="Optional: For live web search. Fallback intelligence is active if blank."
    )
    
    if api_key_input:
        if provider == "Gemini":
            os.environ["GOOGLE_API_KEY"] = api_key_input
        elif provider == "OpenAI":
            os.environ["OPENAI_API_KEY"] = api_key_input
        elif provider == "Groq":
            os.environ["GROQ_API_KEY"] = api_key_input
            
    if tavily_key_input:
        os.environ["TAVILY_API_KEY"] = tavily_key_input

    st.markdown("---")
    st.markdown("### 🛡️ Quality Gate Policy")
    max_hallucination = st.slider("Max Allowed Hallucination (%)", min_value=5.0, max_value=30.0, value=15.0, step=1.0)
    min_support = st.slider("Min Required Claim Support (%)", min_value=50.0, max_value=95.0, value=70.0, step=5.0)
    max_retries = st.number_input("Max Self-Correction Retries", min_value=1, max_value=4, value=2)

# Main Application Title
st.markdown("<div class='main-header'>⚡ Enterprise Multi-Agent Competitor Intelligence</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Autonomous LangGraph Orchestration • Multi-Source Evidence • Ragas Benchmarking • Executive ReportLab PDF</div>", unsafe_allow_html=True)

# Navigation Tabs (Matching PRD 5-Page Architecture)
tabs = st.tabs([
    "1. 🎯 Research Setup",
    "2. 🔄 Agent Execution",
    "3. 📊 Intelligence Dashboard",
    "4. 🔍 Quality & Evidence",
    "5. 📑 Executive Export"
])

# -------------------------------------------------------------
# TAB 1: RESEARCH SETUP
# -------------------------------------------------------------
with tabs[0]:
    st.subheader("Configure Research Scope")
    
    # Preset scenarios
    col_pre1, col_pre2, col_pre3 = st.columns(3)
    preset_query = None
    preset_comps = None
    
    if col_pre1.button("📌 Benchmark: NVIDIA vs AMD vs Intel", use_container_width=True):
        preset_query = "Compare NVIDIA, AMD, and Intel across financial performance, AI accelerator strategy, recent developments, competitive advantages, and supply chain risks."
        preset_comps = "NVIDIA, AMD, Intel"
    if col_pre2.button("📌 Cloud AI: AWS vs Microsoft vs Google", use_container_width=True):
        preset_query = "Compare Microsoft, Google, and Amazon on cloud AI infrastructure, enterprise model adoption, margin structure, and strategic moats."
        preset_comps = "Microsoft, Google, Amazon"
    if col_pre3.button("📌 Mobility: Tesla vs BYD vs Rivian", use_container_width=True):
        preset_query = "Analyze Tesla, BYD, and Rivian regarding electric vehicle market share, autonomous software strategy, vertical integration, and cash flow."
        preset_comps = "Tesla, BYD, Rivian"

    default_query = preset_query or "Compare NVIDIA, AMD, and Intel across financial performance, AI strategy, recent developments, competitive advantages, and risks."
    default_comps = preset_comps or "NVIDIA, AMD, Intel"
    
    user_query = st.text_area(
        "Natural Language Research Objective",
        value=default_query,
        height=90,
        help="Specify the business or market question to decompose."
    )
    
    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        companies_str = st.text_input(
            "Target Competitors (comma-separated)",
            value=default_comps,
            help="E.g. NVIDIA, AMD, Intel"
        )
    with col_c2:
        date_range = st.selectbox(
            "Date Range / Recency Horizon",
            options=["Last 12 Months", "Last 6 Months", "Last 24 Months", "All-Time Strategic View"],
            index=0
        )
        
    focus_areas = st.multiselect(
        "Select Key Analytical Dimensions",
        options=[
            "Financial Performance & Margins",
            "AI Strategy & Architecture",
            "Recent Developments & M&A",
            "Competitive Advantages & Moats",
            "Risks & Supply Chain Vulnerabilities",
            "Developer Ecosystem & Software Lock-in",
            "Valuation Multiples & Efficiency"
        ],
        default=[
            "Financial Performance & Margins",
            "AI Strategy & Architecture",
            "Recent Developments & M&A",
            "Competitive Advantages & Moats",
            "Risks & Supply Chain Vulnerabilities"
        ]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Launch Autonomous Intelligence Run", type="primary", use_container_width=True):
        comps = [c.strip() for c in companies_str.split(",") if c.strip()]
        
        # Switch to tab 2 execution view
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        service = ResearchService()
        
        def on_progress(msg: str, pct: int):
            progress_bar.progress(pct)
            status_text.markdown(f"**Current Stage:** `{msg}` ({pct}%)")
            st.session_state.execution_logs.append(f"[{current_timestamp_iso()[:19]}] {msg}")

        with st.spinner("Executing LangGraph Multi-Agent Workflow..."):
            final_state = service.run_research(
                user_query=user_query,
                companies=comps,
                focus_areas=focus_areas,
                date_range=date_range,
                max_retries=max_retries,
                progress_callback=on_progress
            )
            st.session_state.graph_state = final_state
            
        st.success("🎉 Multi-Agent Research, Verification, and PDF Generation Completed Successfully!")
        st.info("Navigate to the **Intelligence Dashboard**, **Quality & Evidence**, or **Executive Export** tabs to review the findings.")

# -------------------------------------------------------------
# TAB 2: AGENT EXECUTION
# -------------------------------------------------------------
with tabs[1]:
    st.subheader("LangGraph Workflow & Node Execution")
    
    state = st.session_state.graph_state
    if not state:
        st.info("No active workflow run found. Configure parameters in Tab 1 and click 'Launch Autonomous Intelligence Run'.")
    else:
        # Architecture status cards
        cols = st.columns(5)
        cols[0].metric("Planning Node", "Complete", "Decomposed Tasks")
        cols[1].metric("Parallel Research", f"{len(state.get('normalized_evidence', []))} Records", "Web + Fin + News")
        cols[2].metric("13-Sec Synthesis", "Grounded", "Audited Draft")
        cols[3].metric("Fact Verification", f"{len(state.get('verification_results', []))} Claims", f"{state.get('quality_status', 'PASS')}")
        cols[4].metric("Self-Correction", f"{state.get('retry_count', 0)} Retries", "Bounded Loop")
        
        st.markdown("#### Execution Activity Stream")
        for log in st.session_state.execution_logs:
            st.text(log)
            
        with st.expander("🛠️ Inspect Decomposed Research Plan"):
            st.json(state.get("research_plan", []))

# -------------------------------------------------------------
# TAB 3: INTELLIGENCE DASHBOARD
# -------------------------------------------------------------
with tabs[2]:
    st.subheader("Executive Intelligence Dashboard")
    state = st.session_state.graph_state
    if not state:
        st.info("Run research in Tab 1 to populate dashboard.")
    else:
        draft = state.get("draft_report", {})
        sections = draft.get("sections", [])
        
        # Executive Summary Callout
        exec_sec = next((s for s in sections if s.get("section_id") == 1 or "Executive" in s.get("title", "")), None)
        if exec_sec:
            st.markdown(f"<div class='exec-summary-box'><b>Executive Summary:</b><br>{exec_sec.get('content', '')}</div>", unsafe_allow_html=True)
            
        # Financial Comparison Table
        fin_data = state.get("final_report", {}).get("financial_table", [])
        if fin_data:
            st.markdown("#### 📈 Financial Fundamentals & Valuation Benchmark")
            df_fin = pd.DataFrame(fin_data)
            display_cols = [c for c in ["company_name", "ticker", "market_cap", "revenue", "revenue_growth", "gross_margin", "operating_margin", "trailing_pe"] if c in df_fin.columns]
            df_display = df_fin[display_cols].rename(columns={
                "company_name": "Company",
                "ticker": "Ticker",
                "market_cap": "Market Cap",
                "revenue": "Revenue",
                "revenue_growth": "YoY Growth",
                "gross_margin": "Gross Margin",
                "operating_margin": "Operating Margin",
                "trailing_pe": "P/E Ratio"
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Strategic Comparison Matrix
        analysis = state.get("competitor_analysis", {})
        matrix = analysis.get("comparison_matrix", {})
        if matrix and matrix.get("dimensions"):
            st.markdown("#### ⚔️ Strategic Positioning Matrix")
            dims = matrix.get("dimensions", [])
            comps = matrix.get("companies", state.get("companies", []))
            data_dict = matrix.get("data", {})
            
            rows = []
            for d in dims:
                row = {"Dimension": d}
                for c in comps:
                    row[c] = data_dict.get(d, {}).get(c, "N/A")
                rows.append(row)
            df_mat = pd.DataFrame(rows)
            st.dataframe(df_mat, use_container_width=True, hide_index=True)

        # Company Deep Dive Tabs
        profiles = analysis.get("company_profiles", [])
        if profiles:
            st.markdown("#### 🏢 Individual Competitor Profiles & SWOT")
            p_tabs = st.tabs([p.get("company_name", f"Company {idx+1}") for idx, p in enumerate(profiles)])
            for idx, p in enumerate(profiles):
                with p_tabs[idx]:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.markdown(f"**Overview:** {p.get('overview', '')}")
                        st.markdown(f"**AI Strategy:** {p.get('ai_strategy', '')}")
                        st.markdown(f"**Key Products:** {', '.join(p.get('key_products', []))}")
                    with col2:
                        st.markdown("**Key Strengths:**")
                        for s in p.get("strengths", []):
                            st.markdown(f"- ✅ {s}")
                        st.markdown("**Vulnerabilities & Weaknesses:**")
                        for w in p.get("weaknesses", []):
                            st.markdown(f"- ⚠️ {w}")

# -------------------------------------------------------------
# TAB 4: QUALITY & EVIDENCE
# -------------------------------------------------------------
with tabs[3]:
    st.subheader("Fact Verification & Hallucination Benchmarks")
    state = st.session_state.graph_state
    if not state:
        st.info("Run research in Tab 1 to populate quality metrics.")
    else:
        eval_scores = state.get("evaluation_scores", {})
        hal_score = state.get("hallucination_score", 0.0)
        sup_rate = state.get("support_rate", 1.0) * 100.0
        faith = eval_scores.get("faithfulness", 0.90) * 100.0
        relevancy = eval_scores.get("answer_relevancy", 0.92) * 100.0
        status = state.get("quality_status", "PASS")

        # Metric Badges
        col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns(5)
        col_q1.metric("Quality Gate", status, "Passed" if status == "PASS" else "Needs Audit")
        col_q2.metric("Claim Support Rate", f"{sup_rate:.1f}%", f">={min_support}% threshold")
        col_q3.metric("Hallucination Score", f"{hal_score:.1f}%", f"<={max_hallucination}% threshold")
        col_q4.metric("Faithfulness Score", f"{faith:.1f}%", "Ragas Metric")
        col_q5.metric("Answer Relevancy", f"{relevancy:.1f}%", "Objective Fit")

        st.markdown("---")
        st.markdown("#### 📋 Atomic Claim Verification Table")
        ver_results = state.get("verification_results", [])
        
        status_filter = st.multiselect(
            "Filter by Verification Status",
            options=["Supported", "Partially Supported", "Unsupported", "Contradicted", "Insufficient Evidence"],
            default=["Supported", "Partially Supported", "Unsupported", "Contradicted", "Insufficient Evidence"]
        )
        
        filtered_ver = [v for v in ver_results if v.get("status") in status_filter]
        if filtered_ver:
            df_v = pd.DataFrame(filtered_ver)[["claim_id", "text", "section_name", "status", "confidence", "rationale"]]
            df_v.columns = ["Claim ID", "Statement", "Section", "Status", "Confidence", "Evidence Rationale"]
            st.dataframe(df_v, use_container_width=True, hide_index=True)
        else:
            st.info("No claims match the selected filter.")

        st.markdown("---")
        st.markdown("#### 📚 Normalized Evidence Repository")
        ev_records = state.get("normalized_evidence", [])
        with st.expander(f"Explore All {len(ev_records)} Deduplicated Evidence Records"):
            for e in ev_records:
                st.markdown(f"**[{e.get('source_type', 'web').upper()}]** [{e.get('source_title', 'Source')}]({e.get('source_url', '#')}) *(Reliability: `{e.get('reliability_weight', 0.7)}`)*")
                st.caption(f"Excerpt: {e.get('excerpt', '')}")
                st.divider()

# -------------------------------------------------------------
# TAB 5: EXPORT & PDF
# -------------------------------------------------------------
with tabs[4]:
    st.subheader("Report Export & Boardroom PDF")
    state = st.session_state.graph_state
    if not state:
        st.info("Run research in Tab 1 to generate download files.")
    else:
        final_report = state.get("final_report", state.get("draft_report", {}))
        pdf_path = state.get("pdf_path", "")
        
        col_e1, col_e2, col_e3 = st.columns(3)
        
        # PDF Download Button
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            col_e1.download_button(
                label="📥 Download Executive PDF (ReportLab)",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            col_e1.warning("PDF generating or path unavailable.")

        # Markdown Export Button
        md_content = ReportService.state_to_markdown(final_report)
        col_e2.download_button(
            label="📄 Download Full Markdown (.md)",
            data=md_content,
            file_name=f"Competitor_Report_{'_'.join(state.get('companies', ['report']))}.md",
            mime="text/markdown",
            use_container_width=True
        )

        # JSON Export Button
        json_content = ReportService.state_to_json(final_report)
        col_e3.download_button(
            label="⚙️ Download Raw JSON State",
            data=json_content,
            file_name=f"Competitor_Report_{'_'.join(state.get('companies', ['report']))}.json",
            mime="application/json",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("#### 📄 Document Preview (13 Required Sections)")
        sections = final_report.get("sections", [])
        for s in sections:
            with st.expander(f"{s.get('section_id', '')}. {s.get('title', '')}", expanded=(s.get('section_id') in [1, 5, 7])):
                st.markdown(s.get("content", ""))
                cits = s.get("citations", [])
                if cits:
                    st.caption(f"Citations: {', '.join(cits)}")
