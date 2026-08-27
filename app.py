"""
AMG Dashboard Generator - Main Streamlit Application (Enterprise Grade)
Streamlit UI orchestrator with universal CRM and Financial support
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add core to path
sys.path.insert(0, os.path.dirname(__file__))

from core.qa_engine import QAEngine
from core.chart_builder import ChartBuilder
from core.exporter import Exporter
from config import (
    THEMES, TIER_DEFINITIONS, SECTOR_DEFINITIONS, SESSION_STATE_DEFAULTS
)

# Page Config
st.set_page_config(
    page_title="AMG Dashboard Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization
for key, value in SESSION_STATE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================
# SIDEBAR - CONFIGURATION
# ============================================

with st.sidebar:
    st.header("📋 Dashboard Settings")
    
    st.session_state.client_name = st.text_input(
        "Client/Company Name:",
        value=st.session_state.client_name,
        placeholder="e.g., Acme Global Inc."
    )
    
    st.session_state.sector = st.selectbox(
        "Industry Sector:",
        list(SECTOR_DEFINITIONS.keys()),
        index=0
    )
    
    tier_option = st.radio(
        "Dashboard Tier:",
        list(TIER_DEFINITIONS.keys()),
        format_func=lambda x: TIER_DEFINITIONS[x]["name"],
        index=1
    )
    st.session_state.tier = tier_option
    
    st.session_state.theme = st.selectbox(
        "Visual Theme:",
        list(THEMES.keys()),
        index=0
    )
    
    st.write("---")
    tier_info = TIER_DEFINITIONS[st.session_state.tier]
    st.info(f"💼 **{tier_info['name']}**\n\nPages: {tier_info['pages']} | Price: ${tier_info['price_usd']} / ₹{tier_info['price_inr']}")

# ============================================
# MAIN CONTENT
# ============================================

st.title("📊 AMG Dashboard Generator")
st.caption("Enterprise Business Intelligence Engine | Sales, Finance & CRM Lead Support")

# Step 1: File Ingestion
st.header("Step 1: Upload Dataset")
uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file:",
    type=["csv", "xlsx", "xls"],
    help="Mode A: Raw CSV/Excel | Mode B: Standardized 5-Sheet Workbook"
)

if uploaded_file is None:
    st.info("👉 Please upload a client dataset to start data profiling.")
    st.stop()

# Process file on upload
if st.session_state.dataframe is None or st.session_state.get("_last_uploaded_name") != uploaded_file.name:
    with st.spinner("Profiling dataset and running QA inspection..."):
        file_bytes = uploaded_file.getvalue()
        engine = QAEngine()
        raw_df, mode = engine.load_workbook_safely(uploaded_file.name, file_bytes)
        
        if raw_df is None:
            for err in engine.errors:
                st.error(err)
            st.stop()
            
        qa_results = engine.process_and_qa(raw_df, st.session_state.sector)
        
        st.session_state.dataframe = raw_df
        st.session_state.cleaned_df = qa_results["cleaned_df"]
        st.session_state.qa_report = qa_results["report"]
        st.session_state.numeric_cols = qa_results["numeric_cols"]
        st.session_state.date_cols = qa_results["date_cols"]
        st.session_state.category_cols = qa_results["category_cols"]
        st.session_state.qa_warnings = qa_results["warnings"]
        st.session_state.qa_errors = qa_results["errors"]
        st.session_state.ingestion_mode = mode
        st.session_state._last_uploaded_name = uploaded_file.name
        st.session_state.dashboard_generated = False
        st.session_state.figures = {}

cleaned_df = st.session_state.cleaned_df
qa_report = st.session_state.qa_report
numeric_cols = st.session_state.numeric_cols
date_cols = st.session_state.date_cols
category_cols = st.session_state.category_cols

# Step 2: Quality Analysis Metrics
st.header("Step 2: Quality Inspection")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Quality Score", f"{qa_report['quality_score']:.0f}%")
with col2:
    status = "🟢 HEALTHY" if qa_report['quality_score'] >= 80 else "🟡 AUDITED"
    st.metric("Status", status)
with col3:
    st.metric("Metrics Tracked", len(numeric_cols))
with col4:
    st.metric("Dimensions", len(category_cols))

with st.expander("📋 Inspection Audit Log", expanded=False):
    for w in st.session_state.qa_warnings:
        st.write(w)
    for e in st.session_state.qa_errors:
        st.error(e)

# Step 3: Data Preview
st.header("Step 3: Data Preview")
col_p1, col_p2 = st.columns(2)
with col_p1:
    st.write("**Sanitized Preview (First 5 Rows):**")
    st.dataframe(cleaned_df.head(5), use_container_width=True, height=220)
with col_p2:
    st.write("**Schema Metadata:**")
    schema_df = pd.DataFrame({
        "Column": cleaned_df.columns,
        "Type": cleaned_df.dtypes.astype(str),
        "Non-Null": cleaned_df.count().values
    })
    st.dataframe(schema_df, use_container_width=True, height=220)

# Step 4: Dashboard Generation
st.header("Step 4: Interactive Dashboard")

if st.button("🚀 Generate Executive Dashboard", use_container_width=True, type="primary"):
    with st.spinner("Building interactive charts and executive metrics..."):
        builder = ChartBuilder(theme=st.session_state.theme)
        figs = {}
        figs["kpis"] = builder.create_kpi_cards(cleaned_df, numeric_cols, category_cols)
        
        # Primary Trend Chart
        if date_cols:
            metric_to_plot = [c for c in numeric_cols if c != "Record Count"] or numeric_cols
            fig, _ = builder.create_trend_chart(cleaned_df, date_cols[0], metric_to_plot)
            figs["trend"] = fig
            
        # Category Breakdown Charts (Works for CRM & Sales)
        if category_cols:
            metric_target = numeric_cols[0] if numeric_cols else "Record Count"
            fig_bar, _ = builder.create_bar_chart(cleaned_df, category_cols[0], metric_target)
            fig_pie, _ = builder.create_pie_chart(cleaned_df, category_cols[0], metric_target)
            figs["bar"] = fig_bar
            figs["pie"] = fig_pie
            
        real_num = [c for c in numeric_cols if c != "Record Count"]
        if real_num:
            fig_hist, _ = builder.create_histogram(cleaned_df, real_num[0])
            figs["histogram"] = fig_hist
            
        figs["insights"] = builder.generate_executive_insights(cleaned_df, numeric_cols, category_cols)
        
        st.session_state.figures = figs
        st.session_state.dashboard_generated = True

# Persistent Rendering (Safe Columns Guard)
if st.session_state.dashboard_generated and st.session_state.figures:
    figures = st.session_state.figures
    page_count = min(st.session_state.tier + 1, 3)
    tabs = st.tabs([f"📄 Page {i+1}" for i in range(page_count)])
    
    with tabs[0]:
        st.subheader("Executive Overview & KPIs")
        kpis_dict = figures.get("kpis", {})
        num_cards = max(1, min(3, len(kpis_dict)))
        kpi_cols = st.columns(num_cards)
        
        for i, (k_name, k_val) in enumerate(list(kpis_dict.items())[:3]):
            with kpi_cols[i]:
                st.metric(k_name, k_val["total"], f"{k_val['average']}")
                
        if "insights" in figures and figures["insights"]:
            st.info("\n\n".join([f"• {ins}" for ins in figures["insights"]]))
            
        if "trend" in figures and figures["trend"]:
            st.plotly_chart(figures["trend"], use_container_width=True)
            
    if page_count >= 2 and len(tabs) > 1:
        with tabs[1]:
            st.subheader("Category Breakdown & Distribution")
            col1, col2 = st.columns(2)
            with col1:
                if "bar" in figures and figures["bar"]:
                    st.plotly_chart(figures["bar"], use_container_width=True)
            with col2:
                if "pie" in figures and figures["pie"]:
                    st.plotly_chart(figures["pie"], use_container_width=True)
            if "histogram" in figures and figures["histogram"]:
                st.plotly_chart(figures["histogram"], use_container_width=True)
                
    if page_count >= 3 and len(tabs) > 2:
        with tabs[2]:
            st.subheader("Data Explorer")
            st.dataframe(cleaned_df, use_container_width=True, height=450)

# Step 5: Export Deliverables
if st.session_state.dashboard_generated:
    st.header("Step 5: Export Deliverables")
    exporter = Exporter(
        client_name=st.session_state.client_name,
        sector=st.session_state.sector,
        quality_score=qa_report['quality_score']
    )
    
    col_e1, col_e2, col_e3 = st.columns(3)
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with col_e1:
        html_bytes = exporter.create_html_dashboard(
            cleaned_df, st.session_state.figures, tier=st.session_state.tier
        ).encode('utf-8')
        st.download_button(
            label="🌐 Download Standalone HTML",
            data=html_bytes,
            file_name=f"Dashboard_{st.session_state.client_name}_{timestamp_str}.html",
            mime="text/html",
            use_container_width=True
        )
        
    with col_e2:
        excel_bytes = exporter.create_excel_export(cleaned_df)
        st.download_button(
            label="📊 Download Audited Excel",
            data=excel_bytes,
            file_name=f"Cleaned_Data_{st.session_state.client_name}_{timestamp_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_e3:
        csv_bytes = cleaned_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Clean CSV",
            data=csv_bytes,
            file_name=f"Data_{st.session_state.client_name}_{timestamp_str}.csv",
            mime="text/csv",
            use_container_width=True
        )

st.divider()
st.caption("AMG Dashboard Engine | High-Precision Business Intelligence | Zero Hallucination Guarantee")
