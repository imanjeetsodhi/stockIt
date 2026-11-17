"""Tests for financial feature engineering and calculations."""

import pytest
import numpy as np
import pandas as pd
from app.backend.utils.calculations import (
    calculate_daily_returns,
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_maximum_drawdown,
    calculate_portfolio_metrics
)

def test_daily_returns_calculation():
    prices = pd.Series([100.0, 105.0, 99.75])
    returns = calculate_daily_returns(prices)
    assert len(returns) == 2
    assert pytest.approx(returns.iloc[0], rel=1e-4) == 0.05
    assert pytest.approx(returns.iloc[1], rel=1e-4) == -0.05

def test_annualized_return_and_volatility():
    daily_rets = pd.Series([0.001] * 252)
    ann_ret = calculate_annualized_return(daily_rets, trading_days=252)
    assert pytest.approx(ann_ret, rel=1e-4) == 0.252

    vol_rets = pd.Series([0.01, -0.01] * 126)
    ann_vol = calculate_annualized_volatility(vol_rets, trading_days=252)
    assert ann_vol > 0

def test_sharpe_ratio():
    ret = 0.15
    vol = 0.10
    rf = 0.05
    sharpe = calculate_sharpe_ratio(ret, vol, rf)
    assert pytest.approx(sharpe, rel=1e-4) == 1.0

def test_maximum_drawdown():
    prices = pd.Series([100.0, 120.0, 90.0, 110.0])
    max_dd = calculate_maximum_drawdown(prices)
    # Peak was 120, trough was 90 -> drawdown = (90 - 120) / 120 = -0.25 (-25%)
    assert pytest.approx(max_dd, rel=1e-4) == -0.25

def test_portfolio_metrics():
    weights = np.array([0.5, 0.5])
    expected_returns = np.array([0.10, 0.20])
    cov_matrix = np.array([[0.04, 0.01], [0.01, 0.09]])
    ret, vol, var, sharpe = calculate_portfolio_metrics(weights, expected_returns, cov_matrix, risk_free_rate=0.05)

    assert pytest.approx(ret, rel=1e-4) == 0.15
    assert var > 0
    assert vol == pytest.approx(np.sqrt(var), rel=1e-4)
    assert sharpe == pytest.approx((0.15 - 0.05) / vol, rel=1e-4)
