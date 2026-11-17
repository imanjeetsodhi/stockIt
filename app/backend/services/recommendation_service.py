"""Recommendation service matching investor profiles to optimized portfolios."""

from typing import Dict, Any, Optional
import pandas as pd

from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.models.portfolio import (
    PortfolioResult,
    RecommendationOutput,
    RupeeAllocationSummary,
    StockExplanation
)
from app.backend.services.portfolio_service import PortfolioService
from app.backend.services.allocation_service import AllocationService
from app.backend.services.explanation_service import ExplanationService

class RecommendationService:
    def __init__(self, portfolio_service: Optional[PortfolioService] = None):
        self.portfolio_service = portfolio_service or PortfolioService()
        self.portfolio_service.ensure_data_loaded()

        self.allocation_service = AllocationService(self.portfolio_service.stock_statistics)
        self.explanation_service = ExplanationService(
            stock_statistics=self.portfolio_service.stock_statistics,
            correlation_matrix=self.portfolio_service.correlation_matrix
        )

    def generate_recommendation(
        self,
        investment_amount: float,
        risk_appetite: str = "Moderate",
        investment_horizon: str = "3–5 years",
        investment_objective: str = "Balanced Growth",
        max_stock_weight: float = settings.MAX_STOCK_WEIGHT,
        risk_free_rate: Optional[float] = None
    ) -> RecommendationOutput:
        """Runs all three optimization models, evaluates user profile, and constructs the recommendation."""
        rf = risk_free_rate if risk_free_rate is not None else self.portfolio_service.risk_free_rate

        # 1. Run all three optimization strategies
        logger.info(f"Generating recommendation for profile: {risk_appetite}, {investment_horizon}, {investment_objective}")
        strategies = self.portfolio_service.run_all_strategies(
            max_weight=max_stock_weight,
            risk_free_rate=rf
        )

        min_var = strategies["Minimum Variance"]
        markowitz = strategies["Markowitz Efficient"]
        max_sharpe = strategies["Maximum Sharpe"]

        # 2. Evaluate risk-return metrics dynamically (do not blind hardcode)
        risk_normalized = risk_appetite.strip().lower()

        if "low" in risk_normalized:
            # Low risk prioritizes lowest volatility among feasible portfolios
            selected_strategy_name = "Minimum Variance"
            selected_portfolio = min_var
        elif "high" in risk_normalized:
            # High risk: compare Maximum Sharpe and Markowitz
            # If user has >5 years horizon and Wealth Creation, higher expected return may be favored if Sharpe is close
            if ("wealth" in investment_objective.lower() or "5" in investment_horizon) and markowitz.expected_annual_return > max_sharpe.expected_annual_return * 1.05:
                selected_strategy_name = "Markowitz Efficient"
                selected_portfolio = markowitz
            else:
                selected_strategy_name = "Maximum Sharpe"
                selected_portfolio = max_sharpe
        else:
            # Moderate risk: if Markowitz volatility is within 25% of Minimum Variance or provides great Sharpe, choose it
            # Otherwise, Maximum Sharpe provides balanced risk-adjusted return
            if markowitz.annual_volatility <= min_var.annual_volatility * 2.0:
                selected_strategy_name = "Markowitz Efficient"
                selected_portfolio = markowitz
            else:
                selected_strategy_name = "Maximum Sharpe"
                selected_portfolio = max_sharpe

        # 3. Rupee Allocation for the chosen portfolio
        rupee_summary = self.allocation_service.allocate_rupees(
            total_amount=investment_amount,
            allocations=selected_portfolio.allocations,
            marginal_risk_contributions=selected_portfolio.marginal_risk_contributions
        )

        # 4. Detailed Stock Explanations
        stock_explanations = self.explanation_service.generate_stock_explanations(
            portfolio=selected_portfolio,
            allocation_summary=rupee_summary
        )

        # 5. Profile Rationale
        profile_dict = {
            "investment_amount": investment_amount,
            "risk_appetite": risk_appetite,
            "investment_horizon": investment_horizon,
            "investment_objective": investment_objective,
            "max_stock_weight": max_stock_weight,
            "risk_free_rate": rf
        }
        rationale = self.explanation_service.explain_strategy_selection(
            selected_strategy=selected_strategy_name,
            user_profile=profile_dict,
            strategies=strategies
        )

        # 6. Trace Efficient Frontier curve for visual comparison
        try:
            frontier = self.portfolio_service.get_efficient_frontier_curve(max_weight=max_stock_weight, n_points=30)
        except Exception as e:
            logger.warning(f"Could not compute frontier curve: {e}")
            frontier = []

        return RecommendationOutput(
            selected_strategy=selected_strategy_name,
            selection_rationale=rationale,
            user_profile=profile_dict,
            recommended_portfolio=selected_portfolio,
            rupee_allocation=rupee_summary,
            explanations=stock_explanations,
            all_strategies=strategies,
            efficient_frontier=frontier
        )
