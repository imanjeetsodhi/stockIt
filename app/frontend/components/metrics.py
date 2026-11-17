"""Metric display cards for Stackit."""

import streamlit as st

def render_metric_card(col, label: str, value: str, subtitle: str = "", delta_color: str = "#3fb950"):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                {f'<div class="metric-subtitle" style="color: {delta_color}">{subtitle}</div>' if subtitle else ''}
            </div>
            """,
            unsafe_allow_html=True
        )

def render_portfolio_summary_metrics(portfolio_res, rupee_summary=None):
    c1, c2, c3, c4 = st.columns(4)

    if rupee_summary:
        render_metric_card(c1, "Total Investment", f"₹{rupee_summary.get('total_budget', 0):,.0f}", f"Allocated: ₹{rupee_summary.get('allocated_amount', 0):,.0f}")
    else:
        render_metric_card(c1, "Holdings Count", str(portfolio_res.get("stock_count", len(portfolio_res.get("allocations", {})))), "Optimized Assets")

    ret_pct = portfolio_res.get("expected_annual_return", 0) * 100
    render_metric_card(c2, "Expected Annual Return", f"{ret_pct:.2f}%", "Arithmetic Mean (252 Days)")

    vol_pct = portfolio_res.get("annual_volatility", 0) * 100
    render_metric_card(c3, "Annual Volatility", f"{vol_pct:.2f}%", f"Variance: {portfolio_res.get('variance', 0):.4f}", delta_color="#d29922")

    sharpe = portfolio_res.get("sharpe_ratio", 0)
    render_metric_card(c4, "Sharpe Ratio", f"{sharpe:.2f}", f"Rf: {portfolio_res.get('risk_free_rate', 0.065):.1%}")
