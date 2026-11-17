"""01 Home — System Introduction and Dataset Summary."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.frontend.components.metrics import render_metric_card
from app.frontend.utils.api_client import api_client

st.title("🏠 Stackit Overview")
st.markdown("A quantitative portfolio optimization and investment recommendation engine powered by historical NIFTY 50 data.")

# Dataset Quality & Ingestion Summary
st.markdown("### **Historical Dataset Summary**")
summary = api_client.get_dataset_summary()

if summary:
    c1, c2, c3, c4 = st.columns(4)
    render_metric_card(c1, "Discovered Stocks", str(summary.get("discovered_files", 50)), "Raw CSV Datasets")
    render_metric_card(c2, "Valid Constituents", str(summary.get("valid_stocks_count", 50)), "Zero Corrupt Files")
    render_metric_card(c3, "Common Trading Days", str(summary.get("total_common_trading_days", 763)), f"{summary.get('aligned_earliest_date')} to {summary.get('aligned_latest_date')}")
    render_metric_card(c4, "Risk-Free Proxy", f"{summary.get('risk_free_rate', 0.065):.2%}", "RBI 10-Yr G-Sec Benchmark")

st.markdown("---")

st.markdown("### **How Stackit Works**")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("#### **1. Data Ingestion & Features**")
    st.write(
        """
        - Discovers 50 individual stock CSV files from `data/raw/`.
        - Cleans and aligns Adjusted Closing prices across 763 common trading dates.
        - Calculates daily returns, annualized mean returns, covariance, variance, and maximum historical drawdown.
        """
    )

with c2:
    st.markdown("#### **2. Portfolio Optimization**")
    st.write(
        """
        - Solves **Markowitz Mean-Variance Optimization** for optimal risk-return tradeoff.
        - Computes **Minimum Variance Portfolio** for conservative capital preservation.
        - Solves **Maximum Sharpe Ratio Portfolio** for optimal risk-adjusted excess returns.
        """
    )

with c3:
    st.markdown("#### **3. Executable Allocation**")
    st.write(
        """
        - Translates mathematical weights into executable whole-share quantities in Indian Rupees.
        - Accounts for share prices and unallocated cash drag.
        - Generates metric-grounded explanations for every stock selection.
        """
    )

st.markdown("---")
st.markdown("### **Quick Actions**")
q1, q2 = st.columns(2)
with q1:
    if st.button("🚀 Launch Portfolio Builder", use_container_width=True):
        if "PAGES" in st.session_state and "builder" in st.session_state["PAGES"]:
            st.switch_page(st.session_state["PAGES"]["builder"])
        else:
            st.switch_page("pages/03_Portfolio_Builder.py")
with q2:
    if st.button("📊 View Dataset Explorer", use_container_width=True):
        if "PAGES" in st.session_state and "explorer" in st.session_state["PAGES"]:
            st.switch_page(st.session_state["PAGES"]["explorer"])
        else:
            st.switch_page("pages/02_Dataset_Explorer.py")
