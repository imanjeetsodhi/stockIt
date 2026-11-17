"""03 Portfolio Builder — Investor Risk Profiling and Portfolio Generation."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.frontend.utils.api_client import api_client

st.title("⚙️ Portfolio Builder")
st.markdown("Configure your financial profile and investment parameters. Stackit will run all three optimization models to determine the optimal capital allocation.")

with st.form("portfolio_builder_form"):
    col1, col2 = st.columns(2)

    with col1:
        investment_amount = st.number_input(
            "1. Investment Amount (₹ INR)",
            min_value=1000.0,
            max_value=100000000.0,
            value=100000.0,
            step=5000.0,
            help="Total investment capital to allocate across NIFTY 50 stocks."
        )

        risk_appetite = st.selectbox(
            "2. Risk Appetite",
            options=["Low", "Moderate", "High"],
            index=1,
            help="Low: prioritize minimum volatility; Moderate: balanced risk-return; High: maximum excess risk-adjusted return."
        )

    with col2:
        investment_horizon = st.selectbox(
            "3. Investment Horizon",
            options=["< 1 year", "1–3 years", "3–5 years", "> 5 years"],
            index=2,
            help="Planned duration of capital deployment."
        )

        investment_objective = st.selectbox(
            "4. Investment Objective",
            options=["Capital Preservation", "Balanced Growth", "Long-Term Wealth Creation"],
            index=1,
            help="Primary financial goal."
        )

    with st.expander("🛠️ Advanced Mathematical Constraints (Optional)"):
        adv1, adv2 = st.columns(2)
        max_weight = adv1.slider("Maximum Stock Weight", min_value=0.05, max_value=0.50, value=0.20, step=0.05, help="Prevents excessive single-stock concentration (e.g. 20% limit).")
        risk_free = adv2.number_input("Risk-Free Rate (Annual)", min_value=0.0, max_value=0.15, value=0.065, step=0.005, format="%.3f", help="Proxy for Indian 10-Yr Government Bond yield.")

    submitted = st.form_submit_button("🚀 Generate My Portfolio", use_container_width=True)

if submitted:
    with st.spinner("Analyzing historical market data and executing optimization algorithms..."):
        payload = {
            "investment_amount": float(investment_amount),
            "risk_appetite": risk_appetite,
            "investment_horizon": investment_horizon,
            "investment_objective": investment_objective,
            "max_stock_weight": float(max_weight),
            "risk_free_rate": float(risk_free)
        }

        try:
            result = api_client.recommend_portfolio(payload)
            if result and "recommended_portfolio" in result:
                st.session_state["portfolio_recommendation"] = result
                st.session_state["user_profile"] = payload
                st.success(f"Portfolio generated successfully! Recommended strategy: **{result.get('selected_strategy')}**")
                if "PAGES" in st.session_state and "results" in st.session_state["PAGES"]:
                    st.switch_page(st.session_state["PAGES"]["results"])
                else:
                    st.switch_page("pages/04_Portfolio_Results.py")
            else:
                st.error("Failed to generate portfolio. Please check server logs.")
        except Exception as e:
            st.error(f"Error during optimization: {str(e)}")
