"""04 Portfolio Results — Visualizations, Rupee Allocations, and Selection Explanations."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.frontend.components.metrics import render_portfolio_summary_metrics
from app.frontend.components.charts import (
    create_allocation_donut_chart,
    create_allocation_bar_chart,
    create_efficient_frontier_chart
)
from app.frontend.components.allocation_table import render_rupee_allocation_table
from app.frontend.components.explanations import render_stock_explanations
from app.frontend.utils.api_client import api_client

# Check if portfolio exists in session_state, else generate a default one
if "portfolio_recommendation" not in st.session_state:
    with st.spinner("Generating recommended portfolio with default profile (₹1 Lakh, Moderate Risk)..."):
        default_payload = {
            "investment_amount": 100000.0,
            "risk_appetite": "Moderate",
            "investment_horizon": "3–5 years",
            "investment_objective": "Balanced Growth",
            "max_stock_weight": 0.20,
            "risk_free_rate": 0.065
        }
        res = api_client.recommend_portfolio(default_payload)
        st.session_state["portfolio_recommendation"] = res
        st.session_state["user_profile"] = default_payload

rec = st.session_state["portfolio_recommendation"]
selected_strategy = rec.get("selected_strategy", "Markowitz Efficient")
recommended = rec.get("recommended_portfolio", {})
rupee_summary = rec.get("rupee_allocation", {})
explanations = rec.get("explanations", [])
strategies = rec.get("all_strategies", {})
frontier = rec.get("efficient_frontier", [])

st.title(f"📊 Recommended Portfolio: {selected_strategy}")
st.markdown(f"**Strategy Selected:** {selected_strategy} based on your financial risk profile.")

# Selection Rationale Callout
rationale = rec.get("selection_rationale", "")
if rationale:
    st.info(rationale)

# Key Financial Metrics
render_portfolio_summary_metrics(recommended, rupee_summary)

st.markdown("---")

# Visualizations: Donut & Bar
st.markdown("### **Portfolio Allocation Breakdown**")
v1, v2 = st.columns(2)
with v1:
    fig_donut = create_allocation_donut_chart(recommended.get("allocations", {}))
    st.plotly_chart(fig_donut, use_container_width=True)
with v2:
    fig_bar = create_allocation_bar_chart(recommended.get("allocations", {}))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Rupee Allocation Table
st.markdown("### **Executable Whole-Share Rupee Allocation**")
st.caption("Target mathematical weights converted into integer share orders based on latest adjusted closing prices.")
render_rupee_allocation_table(rupee_summary)

st.markdown("---")

# Efficient Frontier Plot
st.markdown("### **Efficient Frontier Position**")
st.caption("Visualizing your portfolio on the Markowitz risk-return curve relative to other optimization models.")
fig_frontier = create_efficient_frontier_chart(
    frontier_points=frontier,
    strategies=strategies,
    selected_strategy_name=selected_strategy
)
st.plotly_chart(fig_frontier, use_container_width=True)

st.markdown("---")

# Why These Stocks? Explanations
render_stock_explanations(explanations)

st.markdown("---")
if st.button("🔄 Reconfigure Investment Profile", use_container_width=True):
    if "PAGES" in st.session_state and "builder" in st.session_state["PAGES"]:
        st.switch_page(st.session_state["PAGES"]["builder"])
    else:
        st.switch_page("pages/03_Portfolio_Builder.py")
