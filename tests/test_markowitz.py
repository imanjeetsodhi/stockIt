"""Tests for Markowitz Optimizer and Efficient Frontier."""

import pytest
from app.backend.services.portfolio_service import PortfolioService
from app.backend.optimization.markowitz import MarkowitzOptimizer

def test_markowitz_optimization():
    service = PortfolioService()
    service.ensure_data_loaded()

    opt = MarkowitzOptimizer(
        expected_returns=service.get_expected_returns(),
        cov_matrix=service.covariance_matrix,
        max_weight=0.20,
        risk_aversion=1.0
    )
    res = opt.optimize()

    assert res.status == "success"
    total_alloc = sum(res.allocations.values())
    assert pytest.approx(total_alloc, abs=1e-4) == 1.0

    for ticker, weight in res.allocations.items():
        assert weight >= 0.0
        assert weight <= 0.20 + 1e-4

def test_markowitz_efficient_frontier():
    service = PortfolioService()
    service.ensure_data_loaded()

    opt = MarkowitzOptimizer(
        expected_returns=service.get_expected_returns(),
        cov_matrix=service.covariance_matrix,
        max_weight=0.20
    )
    frontier = opt.generate_efficient_frontier(n_points=15)
    assert len(frontier) >= 5
    for p in frontier:
        assert "volatility" in p
        assert "return" in p
        assert "sharpe" in p
