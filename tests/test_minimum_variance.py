"""Tests for Minimum Variance Optimizer."""

import pytest
import numpy as np
import pandas as pd
from app.backend.services.portfolio_service import PortfolioService
from app.backend.optimization.minimum_variance import MinimumVarianceOptimizer

def test_minimum_variance_constraints():
    service = PortfolioService()
    service.ensure_data_loaded()

    opt = MinimumVarianceOptimizer(
        expected_returns=service.get_expected_returns(),
        cov_matrix=service.covariance_matrix,
        max_weight=0.20
    )
    res = opt.optimize()

    assert res.status == "success"
    total_alloc = sum(res.allocations.values())
    assert pytest.approx(total_alloc, abs=1e-4) == 1.0

    # Ensure no negative weights and max weight respected
    for ticker, weight in res.allocations.items():
        assert weight >= 0.0
        assert weight <= 0.20 + 1e-4

    assert res.annual_volatility > 0.0
    assert res.expected_annual_return is not None
