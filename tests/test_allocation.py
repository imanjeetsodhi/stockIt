"""Tests for Rupee Allocation Service."""

import pytest
from app.backend.services.portfolio_service import PortfolioService
from app.backend.services.allocation_service import AllocationService

def test_rupee_allocation():
    service = PortfolioService()
    service.ensure_data_loaded()

    allocator = AllocationService(service.stock_statistics)
    budget = 100000.0  # ₹1 Lakh
    allocations = {"RELIANCE": 0.40, "TCS": 0.35, "INFY": 0.25}

    summary = allocator.allocate_rupees(budget, allocations)

    assert summary.total_budget == budget
    assert summary.allocated_amount <= budget
    assert summary.unallocated_cash >= 0.0
    assert summary.allocated_amount + summary.unallocated_cash == pytest.approx(budget, abs=0.01)

    for item in summary.holdings:
        assert isinstance(item.shares, int)
        assert item.shares >= 0
        assert item.actual_investment <= item.target_investment + item.latest_price
