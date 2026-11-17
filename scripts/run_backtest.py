"""Script to execute an out-of-sample backtest of the portfolio models."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.backend.services.portfolio_service import PortfolioService
from app.backend.services.backtesting_service import BacktestService

def main():
    print("\n" + "=" * 55)
    print("      STACKIT: OUT-OF-SAMPLE BACKTESTING")
    print("=" * 55 + "\n")

    service = PortfolioService()
    service.ensure_data_loaded()

    backtester = BacktestService(
        prices_df=service.prices,
        returns_df=service.daily_returns,
        risk_free_rate=service.risk_free_rate
    )

    results = backtester.run_out_of_sample_backtest(train_ratio=0.70)
    print(f"Split Date (Train/Test) : {results['split_date']}")
    print(f"In-sample Train Days    : {results['train_days']}")
    print(f"Out-of-sample Test Days : {results['test_days']}")
    print(f"Transaction Cost        : {results['transaction_cost_bps']} bps\n")

    print(f"{'Strategy':<25} | {'Tot Ret%':<10} | {'Ann Ret%':<10} | {'Volatility%':<12} | {'Sharpe':<8} | {'Max DD%':<10}")
    print("-" * 85)

    for strat, m in results["performance_summary"].items():
        print(
            f"{strat:<25} | {m['total_return_pct']:>8.2f}% | {m['annualized_return_pct']:>8.2f}% | "
            f"{m['annualized_volatility_pct']:>10.2f}% | {m['sharpe_ratio']:>6.2f} | {m['max_drawdown_pct']:>8.2f}%"
        )
    print("\n" + results["notes"] + "\n")

if __name__ == "__main__":
    main()
