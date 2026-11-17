"""02 Dataset Explorer — Stock Statistics, Price Charts, and Correlation Analysis."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from app.frontend.components.charts import (
    create_correlation_heatmap,
    create_price_and_returns_chart
)
from app.frontend.utils.api_client import api_client

st.title("🔍 NIFTY 50 Dataset Explorer")
st.markdown("Inspect historical market prices, calculated statistics, and correlation structures.")

# Search & Filter
search_query = st.text_input("Filter stocks by ticker symbol (e.g. RELIANCE, TCS, INFY):", "")

stocks = api_client.get_stocks(search=search_query)

if stocks:
    df_display = pd.DataFrame(stocks)
    formatted = df_display.copy()
    formatted["Annualized Return"] = (formatted["annualized_return"] * 100).map("{:.2f}%".format)
    formatted["Annual Volatility"] = (formatted["annualized_volatility"] * 100).map("{:.2f}%".format)
    formatted["Sharpe Ratio"] = formatted["sharpe_ratio"].map("{:.2f}".format)
    formatted["Max Drawdown"] = (formatted["maximum_drawdown"] * 100).map("{:.2f}%".format)
    formatted["Latest Price"] = formatted["latest_price"].map("₹{:,.2f}".format)
    formatted["Avg Daily Volume"] = formatted["average_daily_volume"].map("{:,.0f}".format)

    columns_to_show = ["stock", "Annualized Return", "Annual Volatility", "Sharpe Ratio", "Max Drawdown", "Latest Price", "Avg Daily Volume"]
    
    st.dataframe(formatted[columns_to_show].rename(columns={"stock": "Stock Ticker"}), use_container_width=True, hide_index=True)
else:
    st.warning("No stocks found matching the filter.")

st.markdown("---")

# Stock Deep Dive
st.markdown("### **Individual Stock Performance Inspection**")
all_tickers = [s["stock"] for s in api_client.get_stocks()]
selected_ticker = st.selectbox("Select a stock to inspect historical prices:", all_tickers, index=all_tickers.index("RELIANCE") if "RELIANCE" in all_tickers else 0)

if selected_ticker:
    detail = api_client.get_stock_detail(selected_ticker)
    if detail and "history" in detail:
        m = detail.get("metrics", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Price", f"₹{m.get('latest_price', 0):,.2f}")
        c2.metric("Annualized Return", f"{m.get('annualized_return', 0)*100:.2f}%")
        c3.metric("Annual Volatility", f"{m.get('annualized_volatility', 0)*100:.2f}%")
        c4.metric("Sharpe Ratio", f"{m.get('sharpe_ratio', 0):.2f}")

        fig = create_price_and_returns_chart(detail["history"], selected_ticker)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Correlation Heatmap
st.markdown("### **Inter-Stock Correlation Heatmap**")
corr_selection = st.multiselect(
    "Select stocks for correlation analysis (default: Top 10 by market weight):",
    options=all_tickers,
    default=["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "ITC", "BHARTIARTL", "SBIN", "BAJFINANCE", "LT"]
)

if corr_selection:
    corr_data = api_client.get_correlation_matrix(corr_selection)
    if corr_data and "matrix" in corr_data:
        corr_df = pd.DataFrame(corr_data["matrix"], index=corr_data["tickers"], columns=corr_data["tickers"])
        fig_corr = create_correlation_heatmap(corr_df, title=f"Correlation Matrix ({len(corr_selection)} Stocks)")
        st.plotly_chart(fig_corr, use_container_width=True)
