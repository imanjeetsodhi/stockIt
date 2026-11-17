"""Tests for Out-of-Sample Backtesting Service."""

import pytest
from app.backend.services.portfolio_service import PortfolioService
from app.backend.services.backtesting_service import BacktestService

def test_backtest_service():
    service = PortfolioService()
    service.ensure_data_loaded()

    backtester = BacktestService(
        prices_df=service.prices,
        returns_df=service.daily_returns,
        risk_free_rate=service.risk_free_rate
    )

    result = backtester.run_out_of_sample_backtest(train_ratio=0.75)

    assert "performance_summary" in result
    assert "Minimum Variance" in result["performance_summary"]
    assert "Markowitz Efficient" in result["performance_summary"]
    assert "Maximum Sharpe" in result["performance_summary"]
    assert "Equal-Weight Benchmark" in result["performance_summary"]

    for strat, m in result["performance_summary"].items():
        assert "total_return_pct" in m
        assert "annualized_volatility_pct" in m
        assert "sharpe_ratio" in m
        assert "max_drawdown_pct" in m
