"""05 Strategy Comparison — Side-by-Side Analysis and Out-of-Sample Backtesting."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from app.frontend.components.charts import (
    create_allocation_donut_chart,
    create_backtest_cumulative_chart
)
from app.frontend.components.allocation_table import render_rupee_allocation_table
from app.frontend.utils.api_client import api_client

st.title("⚖️ Strategy Comparison & Backtesting")
st.markdown("Compare the three quantitative optimization techniques side-by-side on identical market data and evaluate their historical out-of-sample performance.")

# Fetch comparison data
strategies = api_client.compare_strategies(max_weight=0.20)

if strategies:
    st.markdown("### **Model Performance Comparison**")

    metrics_records = []
    for name in ["Minimum Variance", "Markowitz Efficient", "Maximum Sharpe"]:
        s = strategies.get(name, {})
        metrics_records.append({
            "Optimization Model": name,
            "Expected Annual Return": f"{s.get('expected_annual_return', 0)*100:.2f}%",
            "Annualized Volatility": f"{s.get('annualized_volatility', 0)*100:.2f}%",
            "Sharpe Ratio": f"{s.get('sharpe_ratio', 0):.2f}",
            "Variance": f"{s.get('variance', 0):.4f}",
            "Holdings Count": s.get("stock_count", len(s.get("allocations", {})))
        })

    st.dataframe(pd.DataFrame(metrics_records), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Strategy Switcher & Inspection
    st.markdown("### **Inspect Strategy Allocations**")
    selected_view = st.radio(
        "Select Strategy to Inspect:",
        options=["Minimum Variance", "Markowitz Efficient", "Maximum Sharpe"],
        horizontal=True
    )

    chosen_strat = strategies.get(selected_view, {})
    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown(f"#### **{selected_view} Weights**")
        fig_donut = create_allocation_donut_chart(chosen_strat.get("allocations", {}))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_r:
        st.markdown("#### **Allocations Table**")
        alloc_items = [
            {"Stock": t, "Weight (%)": f"{w*100:.2f}%"}
            for t, w in sorted(chosen_strat.get("allocations", {}).items(), key=lambda x: x[1], reverse=True)
        ]
        st.dataframe(pd.DataFrame(alloc_items), use_container_width=True, hide_index=True)

st.markdown("---")

# Out-of-Sample Backtesting Section
st.markdown("### **Historical Out-of-Sample Backtesting**")
st.caption(
    "Strict chronological evaluation. Models are trained only on historical in-sample data (2023–2025) "
    "and tested forward into subsequent out-of-sample market observations (2025–2026). No lookahead bias."
)

with st.spinner("Running chronological out-of-sample backtest with transaction costs..."):
    bt_res = api_client.run_backtest({"train_ratio": 0.70, "transaction_cost_pct": 0.001, "max_stock_weight": 0.20})

if bt_res and "performance_summary" in bt_res:
    bt_summary = bt_res.get("performance_summary", {})

    b_records = []
    for strat, m in bt_summary.items():
        b_records.append({
            "Strategy": strat,
            "Total Return": f"{m.get('total_return_pct', 0):.2f}%",
            "Annualized Return": f"{m.get('annualized_return_pct', 0):.2f}%",
            "Annual Volatility": f"{m.get('annualized_volatility_pct', 0):.2f}%",
            "Sharpe Ratio": f"{m.get('sharpe_ratio', 0):.2f}",
            "Max Drawdown": f"{m.get('max_drawdown_pct', 0):.2f}%",
            "Holdings": m.get("stock_count", 0)
        })

    st.dataframe(pd.DataFrame(b_records), use_container_width=True, hide_index=True)

    if "cumulative_curves" in bt_res:
        fig_bt = create_backtest_cumulative_chart(bt_res["cumulative_curves"])
        st.plotly_chart(fig_bt, use_container_width=True)

    st.caption(f"ℹ️ **Backtest Configuration:** Split Date: {bt_res.get('split_date')} | Train Days: {bt_res.get('train_days')} | Test Days: {bt_res.get('test_days')} | Friction: {bt_res.get('transaction_cost_bps')} bps")
    st.info(f"📌 **Methodology Note:** {bt_res.get('notes')}")
