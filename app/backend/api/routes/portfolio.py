"""Portfolio optimization and recommendation API routes."""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from app.backend.core.logging import logger
from app.backend.api.schemas.response_schema import StandardResponse
from app.backend.api.schemas.portfolio_schema import (
    PortfolioOptimizationRequest,
    StrategyExecutionRequest
)
from app.backend.models.portfolio import RecommendationOutput, PortfolioResult
from app.backend.services.recommendation_service import RecommendationService
from app.backend.services.portfolio_service import PortfolioService
from app.shared.constants import OptimizationMethod

router = APIRouter(prefix="/portfolio", tags=["Portfolio Optimization"])
portfolio_service = PortfolioService()
recommendation_service = RecommendationService(portfolio_service)

@router.post("/recommend", response_model=StandardResponse[RecommendationOutput])
def recommend_portfolio(request: PortfolioOptimizationRequest):
    """Processes user profile, runs all 3 portfolio models, allocates rupees, and produces grounded explanations."""
    try:
        rec = recommendation_service.generate_recommendation(
            investment_amount=request.investment_amount,
            risk_appetite=request.risk_appetite.value,
            investment_horizon=request.investment_horizon.value,
            investment_objective=request.investment_objective.value,
            max_stock_weight=request.max_stock_weight,
            risk_free_rate=request.risk_free_rate
        )
        return StandardResponse(
            success=True,
            message=f"Recommended {rec.selected_strategy} based on user profile",
            data=rec
        )
    except Exception as e:
        logger.error(f"Portfolio recommendation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.post("/optimize", response_model=StandardResponse[PortfolioResult])
def optimize_strategy(request: StrategyExecutionRequest):
    """Runs a specific standalone portfolio optimization technique."""
    try:
        if request.strategy == OptimizationMethod.MIN_VARIANCE:
            res = portfolio_service.run_minimum_variance(
                max_weight=request.max_stock_weight,
                risk_free_rate=request.risk_free_rate
            )
        elif request.strategy == OptimizationMethod.MAX_SHARPE:
            res = portfolio_service.run_maximum_sharpe(
                max_weight=request.max_stock_weight,
                risk_free_rate=request.risk_free_rate
            )
        else:
            res = portfolio_service.run_markowitz(
                max_weight=request.max_stock_weight,
                risk_free_rate=request.risk_free_rate,
                risk_aversion=request.risk_aversion,
                target_return=request.target_return
            )

        return StandardResponse(success=True, data=res)
    except Exception as e:
        logger.error(f"Strategy optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare", response_model=StandardResponse[Dict[str, PortfolioResult]])
def compare_strategies(
    max_weight: float = Query(default=0.20, gt=0.02, le=1.0),
    risk_free_rate: Optional[float] = Query(default=None, ge=0.0, le=0.20)
):
    """Runs all three optimization techniques under identical parameters and returns side-by-side results."""
    try:
        results = portfolio_service.run_all_strategies(
            max_weight=max_weight,
            risk_free_rate=risk_free_rate
        )
        return StandardResponse(success=True, data=results)
    except Exception as e:
        logger.error(f"Strategy comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/frontier", response_model=StandardResponse[List[Dict[str, float]]])
def get_efficient_frontier(
    max_weight: float = Query(default=0.20, gt=0.02, le=1.0),
    points: int = Query(default=35, ge=10, le=100)
):
    """Generates the Markowitz Efficient Frontier curve points."""
    try:
        curve = portfolio_service.get_efficient_frontier_curve(max_weight=max_weight, n_points=points)
        return StandardResponse(success=True, data=curve)
    except Exception as e:
        logger.error(f"Frontier generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
