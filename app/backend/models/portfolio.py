"""Pydantic models for portfolio entities and responses."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class PortfolioResult(BaseModel):
    portfolio_name: str
    expected_annual_return: float
    annual_volatility: float
    variance: float
    sharpe_ratio: float
    allocations: Dict[str, float] = Field(..., description="Map of stock ticker to allocation weight [0.0 - 1.0]")
    status: str = "success"
    message: Optional[str] = None
    marginal_risk_contributions: Optional[Dict[str, float]] = None
    risk_free_rate: float = 0.065
    stock_count: int = 0
    additional_metrics: Optional[Dict[str, Any]] = None

class WholeShareAllocationItem(BaseModel):
    stock: str
    target_weight: float
    target_investment: float
    latest_price: float
    shares: int
    actual_investment: float
    actual_weight: float
    risk_contribution_pct: Optional[float] = None
    annualized_return: Optional[float] = None
    annualized_volatility: Optional[float] = None

class RupeeAllocationSummary(BaseModel):
    total_budget: float
    allocated_amount: float
    unallocated_cash: float
    cash_drag_pct: float
    holdings: List[WholeShareAllocationItem]

class StockExplanation(BaseModel):
    stock: str
    weight_pct: float
    allocation_rupees: float
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    risk_contribution_pct: float
    diversification_score: str
    selection_reason: str
    role_in_portfolio: str

class RecommendationOutput(BaseModel):
    selected_strategy: str
    selection_rationale: str
    user_profile: Dict[str, Any]
    recommended_portfolio: PortfolioResult
    rupee_allocation: RupeeAllocationSummary
    explanations: List[StockExplanation]
    all_strategies: Dict[str, PortfolioResult]
    efficient_frontier: Optional[List[Dict[str, float]]] = None
