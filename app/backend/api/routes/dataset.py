"""Dataset exploration and metadata routes."""

import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.api.schemas.response_schema import StandardResponse
from app.backend.api.schemas.dataset_schema import (
    DatasetSummaryResponse,
    StockMetricItem,
    StockDetailResponse,
    StockHistoryPoint
)
from app.backend.services.portfolio_service import PortfolioService
from app.backend.services.preprocessing import PreprocessingPipeline

router = APIRouter(prefix="/dataset", tags=["Dataset"])
portfolio_service = PortfolioService()

@router.get("/summary", response_model=StandardResponse[DatasetSummaryResponse])
def get_dataset_summary():
    """Returns overall dataset ingestion, quality, and date range summary."""
    report_file = settings.REPORTS_DIR / "data_quality_report.json"
    if not report_file.exists():
        # Trigger preprocessing if needed
        pipeline = PreprocessingPipeline()
        pipeline.run_pipeline()

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return StandardResponse(success=True, data=DatasetSummaryResponse(**data))
    except Exception as e:
        logger.error(f"Failed to read dataset summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stocks", response_model=StandardResponse[List[StockMetricItem]])
def list_stocks(search: Optional[str] = Query(default=None, description="Optional search filter by stock symbol")):
    """Returns list of all analyzed stocks with their financial metrics."""
    try:
        df = portfolio_service.stock_statistics.reset_index()
        if search:
            search_clean = search.strip().upper()
            df = df[df["Stock"].str.contains(search_clean)]

        items = []
        for _, row in df.iterrows():
            items.append(
                StockMetricItem(
                    stock=row["Stock"],
                    average_daily_return=round(float(row["Average_Daily_Return"]), 6),
                    annualized_return=round(float(row["Annualized_Return"]), 4),
                    cagr=round(float(row["CAGR"]), 4),
                    annualized_volatility=round(float(row["Annualized_Volatility"]), 4),
                    daily_variance=round(float(row["Daily_Variance"]), 6),
                    annualized_variance=round(float(row["Annualized_Variance"]), 6),
                    maximum_drawdown=round(float(row["Maximum_Drawdown"]), 4),
                    sharpe_ratio=round(float(row["Sharpe_Ratio"]), 2),
                    average_daily_volume=round(float(row["Average_Daily_Volume"]), 0),
                    latest_price=round(float(row["Latest_Price"]), 2),
                    total_observations=int(row["Total_Observations"])
                )
            )
        return StandardResponse(success=True, data=items)
    except Exception as e:
        logger.error(f"Failed to list stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stocks/{ticker}", response_model=StandardResponse[StockDetailResponse])
def get_stock_detail(ticker: str):
    """Returns comprehensive time-series and metrics for a specific stock."""
    ticker_clean = ticker.strip().upper()
    stats_df = portfolio_service.stock_statistics
    prices_df = portfolio_service.prices
    returns_df = portfolio_service.daily_returns

    if ticker_clean not in stats_df.index:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker_clean}' not found in active dataset")

    row = stats_df.loc[ticker_clean]
    metrics = StockMetricItem(
        stock=ticker_clean,
        average_daily_return=round(float(row["Average_Daily_Return"]), 6),
        annualized_return=round(float(row["Annualized_Return"]), 4),
        cagr=round(float(row["CAGR"]), 4),
        annualized_volatility=round(float(row["Annualized_Volatility"]), 4),
        daily_variance=round(float(row["Daily_Variance"]), 6),
        annualized_variance=round(float(row["Annualized_Variance"]), 6),
        maximum_drawdown=round(float(row["Maximum_Drawdown"]), 4),
        sharpe_ratio=round(float(row["Sharpe_Ratio"]), 2),
        average_daily_volume=round(float(row["Average_Daily_Volume"]), 0),
        latest_price=round(float(row["Latest_Price"]), 2),
        total_observations=int(row["Total_Observations"])
    )

    history = []
    if ticker_clean in prices_df.columns:
        p_series = prices_df[ticker_clean]
        r_series = returns_df[ticker_clean] if ticker_clean in returns_df.columns else None

        for date, price in p_series.items():
            dt_str = date.strftime("%Y-%m-%d")
            ret_val = float(r_series.loc[date]) if (r_series is not None and date in r_series.index) else None
            history.append(
                StockHistoryPoint(
                    date=dt_str,
                    adj_close=round(float(price), 2),
                    daily_return=round(ret_val, 4) if ret_val is not None else None
                )
            )

    return StandardResponse(
        success=True,
        data=StockDetailResponse(stock=ticker_clean, metrics=metrics, history=history)
    )

@router.get("/correlation", response_model=StandardResponse[Dict[str, Any]])
def get_correlation_matrix(stocks: Optional[str] = Query(default=None, description="Comma-separated ticker list")):
    """Returns correlation matrix data, optionally filtered by selected tickers."""
    corr_df = portfolio_service.correlation_matrix
    if stocks:
        requested = [s.strip().upper() for s in stocks.split(",") if s.strip()]
        valid_cols = [s for s in requested if s in corr_df.columns]
        if valid_cols:
            corr_df = corr_df.loc[valid_cols, valid_cols]

    return StandardResponse(
        success=True,
        data={
            "tickers": list(corr_df.columns),
            "matrix": [[round(float(val), 4) for val in row] for row in corr_df.values]
        }
    )

@router.post("/reload", response_model=StandardResponse[DatasetSummaryResponse])
def reload_dataset():
    """Forces regeneration of preprocessed datasets from raw CSV files."""
    try:
        pipeline = PreprocessingPipeline()
        summary = pipeline.run_pipeline()
        return StandardResponse(
            success=True,
            message="Dataset regenerated successfully",
            data=DatasetSummaryResponse(**summary)
        )
    except Exception as e:
        logger.error(f"Dataset reload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
