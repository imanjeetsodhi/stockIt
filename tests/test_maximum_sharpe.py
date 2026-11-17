"""Tests for Maximum Sharpe Ratio Optimizer."""

import pytest
from app.backend.services.portfolio_service import PortfolioService
from app.backend.optimization.maximum_sharpe import MaximumSharpeOptimizer

def test_maximum_sharpe_constraints():
    service = PortfolioService()
    service.ensure_data_loaded()

    opt = MaximumSharpeOptimizer(
        expected_returns=service.get_expected_returns(),
        cov_matrix=service.covariance_matrix,
        max_weight=0.20,
        risk_free_rate=0.065
    )
    res = opt.optimize()

    assert res.status == "success"
    total_alloc = sum(res.allocations.values())
    assert pytest.approx(total_alloc, abs=1e-4) == 1.0

    for ticker, weight in res.allocations.items():
        assert weight >= 0.0
        assert weight <= 0.20 + 1e-4

    assert res.sharpe_ratio > 0.5  # Historical NIFTY 50 top performers have solid Sharpe
