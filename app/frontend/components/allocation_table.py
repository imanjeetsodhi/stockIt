"""Rupee allocation table component."""

import streamlit as st
import pandas as pd
from typing import Dict, Any

def render_rupee_allocation_table(rupee_summary: Dict[str, Any]):
    """Renders formatted whole-share allocation table and cash drag summary."""
    holdings = rupee_summary.get("holdings", [])
    if not holdings:
        st.info("No holdings in allocation summary")
        return

    records = []
    for h in holdings:
        records.append({
            "Stock Symbol": h.get("stock"),
            "Target Weight": f"{h.get('target_weight', 0)*100:.2f}%",
            "Target Amount": f"₹{h.get('target_investment', 0):,.2f}",
            "Latest Price": f"₹{h.get('latest_price', 0):,.2f}",
            "Whole Shares": int(h.get("shares", 0)),
            "Actual Invested": f"₹{h.get('actual_investment', 0):,.2f}",
            "Actual Weight": f"{h.get('actual_weight', 0)*100:.2f}%",
            "Risk Contribution": f"{h.get('risk_contribution_pct', 0):.2f}%" if h.get('risk_contribution_pct') is not None else "N/A"
        })

    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Budget", f"₹{rupee_summary.get('total_budget', 0):,.2f}")
    c2.metric("Total Invested", f"₹{rupee_summary.get('allocated_amount', 0):,.2f}")
    c3.metric("Remaining Cash", f"₹{rupee_summary.get('unallocated_cash', 0):,.2f}", f"Cash Drag: {rupee_summary.get('cash_drag_pct', 0):.2f}%")
