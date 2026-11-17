"""Backtesting API routes."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.backend.core.logging import logger
from app.backend.api.schemas.response_schema import StandardResponse
from app.backend.api.schemas.portfolio_schema import BacktestRequest
from app.backend.services.portfolio_service import PortfolioService
from app.backend.services.backtesting_service import BacktestService

router = APIRouter(prefix="/backtesting", tags=["Backtesting"])
portfolio_service = PortfolioService()

@router.post("/run", response_model=StandardResponse[Dict[str, Any]])
def run_backtest(request: BacktestRequest):
    """Executes chronological out-of-sample backtest across all three strategies and equal-weighted benchmark."""
    try:
        portfolio_service.ensure_data_loaded()
        backtester = BacktestService(
            prices_df=portfolio_service.prices,
            returns_df=portfolio_service.daily_returns,
            risk_free_rate=portfolio_service.risk_free_rate
        )

        res = backtester.run_out_of_sample_backtest(
            split_date=request.split_date,
            train_ratio=request.train_ratio,
            transaction_cost_pct=request.transaction_cost_pct,
            max_stock_weight=request.max_stock_weight
        )
        return StandardResponse(
            success=True,
            message="Out-of-sample backtest executed successfully",
            data=res
        )
    except Exception as e:
        logger.error(f"Backtesting execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
