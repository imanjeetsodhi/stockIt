"""Tests for Portfolio Recommendation Service."""

import pytest
from app.backend.services.recommendation_service import RecommendationService

def test_recommendation_workflow():
    service = RecommendationService()
    rec = service.generate_recommendation(
        investment_amount=100000.0,
        risk_appetite="Moderate",
        investment_horizon="3–5 years",
        investment_objective="Balanced Growth",
        max_stock_weight=0.20
    )

    assert rec.selected_strategy in ["Markowitz Efficient", "Minimum Variance", "Maximum Sharpe"]
    assert rec.rupee_allocation.total_budget == 100000.0
    assert len(rec.explanations) > 0
    assert len(rec.all_strategies) == 3
    assert rec.selection_rationale != ""

    for exp in rec.explanations:
        assert exp.stock in rec.recommended_portfolio.allocations
        assert exp.weight_pct > 0
        assert exp.role_in_portfolio != ""
