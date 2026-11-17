"""Stock explanation card UI components."""

import streamlit as st
from typing import List, Dict, Any

def render_stock_explanations(explanations: List[Dict[str, Any]]):
    """Renders structured cards explaining why each stock was selected."""
    if not explanations:
        st.info("No explanations available")
        return

    st.markdown("#### **Why Were These Stocks Selected?**")
    st.caption("Deterministic, metric-driven rationale computed from historical return, volatility, drawdown, and covariance.")

    for exp in explanations:
        stock = exp.get("stock")
        weight_pct = exp.get("weight_pct", 0)
        rupees = exp.get("allocation_rupees", 0)
        role = exp.get("role_in_portfolio", "Core Holding")
        reason = exp.get("selection_reason", "")
        div_score = exp.get("diversification_score", "")

        ann_ret = exp.get("annualized_return_pct", 0)
        ann_vol = exp.get("annualized_volatility_pct", 0)
        sharpe = exp.get("sharpe_ratio", 0)
        max_dd = exp.get("max_drawdown_pct", 0)
        risk_contrib = exp.get("risk_contribution_pct", 0)

        with st.expander(f"**{stock}** — Allocation: {weight_pct:.1f}% (₹{rupees:,.2f}) | {role}", expanded=(weight_pct >= 10.0)):
            st.markdown(f"**Selection Rationale:** {reason}")
            st.markdown(f"**Diversification Contribution:** {div_score}")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Ann. Return", f"{ann_ret:.1f}%")
            c2.metric("Ann. Volatility", f"{ann_vol:.1f}%")
            c3.metric("Sharpe Ratio", f"{sharpe:.2f}")
            c4.metric("Max Drawdown", f"{max_dd:.1f}%")
            c5.metric("Risk Contribution", f"{risk_contrib:.1f}%")
