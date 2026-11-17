"""Script to regenerate and display stock financial statistics."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.backend.services.portfolio_service import PortfolioService

def main():
    service = PortfolioService()
    service.ensure_data_loaded()
    df = service.stock_statistics

    print("\n" + "=" * 80)
    print("                STACKIT: NIFTY 50 FINANCIAL STATISTICS SUMMARY")
    print("=" * 80 + "\n")
    print(f"Total stocks analyzed: {len(df)}")
    print("\nTop 10 Stocks by Sharpe Ratio:")
    top_sharpe = df.sort_values(by="Sharpe_Ratio", ascending=False)[
        ["Annualized_Return", "Annualized_Volatility", "Sharpe_Ratio", "Maximum_Drawdown", "Latest_Price"]
    ].head(10)

    # Format percentages for display
    display_df = top_sharpe.copy()
    display_df["Annualized_Return"] = (display_df["Annualized_Return"] * 100).map("{:.2f}%".format)
    display_df["Annualized_Volatility"] = (display_df["Annualized_Volatility"] * 100).map("{:.2f}%".format)
    display_df["Maximum_Drawdown"] = (display_df["Maximum_Drawdown"] * 100).map("{:.2f}%".format)
    display_df["Sharpe_Ratio"] = display_df["Sharpe_Ratio"].map("{:.2f}".format)
    display_df["Latest_Price"] = display_df["Latest_Price"].map("₹{:,.2f}".format)

    print(display_df.to_string())
    print("\n")

if __name__ == "__main__":
    main()
