"""Pydantic schemas for portfolio optimization and recommendation requests."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from app.shared.constants import (
    RiskAppetite,
    InvestmentHorizon,
    InvestmentObjective,
    OptimizationMethod,
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_MAX_WEIGHT
)
from app.backend.models.portfolio import RecommendationOutput, PortfolioResult

class PortfolioOptimizationRequest(BaseModel):
    investment_amount: float = Field(
        default=100000.0,
        gt=100.0,
        le=100000000.0,
        description="Total capital to invest in Indian Rupees (₹100 to ₹10 Crore)"
    )
    risk_appetite: RiskAppetite = Field(
        default=RiskAppetite.MODERATE,
        description="Investor risk preference: Low, Moderate, or High"
    )
    investment_horizon: InvestmentHorizon = Field(
        default=InvestmentHorizon.THREE_TO_FIVE_YEARS,
        description="Planned investment time horizon"
    )
    investment_objective: InvestmentObjective = Field(
        default=InvestmentObjective.BALANCED_GROWTH,
        description="Financial goal: Capital Preservation, Balanced Growth, or Long-Term Wealth Creation"
    )
    max_stock_weight: float = Field(
        default=DEFAULT_MAX_WEIGHT,
        gt=0.02,
        le=1.0,
        description="Maximum allocation weight bound per individual stock (default 0.20 or 20%)"
    )
    risk_free_rate: Optional[float] = Field(
        default=DEFAULT_RISK_FREE_RATE,
        ge=0.0,
        le=0.20,
        description="Configurable risk-free benchmark rate (default 0.065 or 6.5%)"
    )

class StrategyExecutionRequest(BaseModel):
    strategy: OptimizationMethod = Field(default=OptimizationMethod.MAX_SHARPE)
    max_stock_weight: float = Field(default=DEFAULT_MAX_WEIGHT, gt=0.02, le=1.0)
    risk_free_rate: Optional[float] = Field(default=DEFAULT_RISK_FREE_RATE, ge=0.0, le=0.20)
    risk_aversion: float = Field(default=1.0, ge=0.01, le=50.0)
    target_return: Optional[float] = Field(default=None, ge=-0.50, le=2.0)

class BacktestRequest(BaseModel):
    split_date: Optional[str] = None
    train_ratio: float = Field(default=0.70, gt=0.20, lt=0.95)
    transaction_cost_pct: float = Field(default=0.001, ge=0.0, le=0.05)
    max_stock_weight: float = Field(default=DEFAULT_MAX_WEIGHT, gt=0.02, le=1.0)
