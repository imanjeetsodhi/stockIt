"""Pydantic schemas for dataset exploration endpoints."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class StockMetricItem(BaseModel):
    stock: str
    average_daily_return: float
    annualized_return: float
    cagr: float
    annualized_volatility: float
    daily_variance: float
    annualized_variance: float
    maximum_drawdown: float
    sharpe_ratio: float
    average_daily_volume: float
    latest_price: float
    total_observations: int

class DatasetSummaryResponse(BaseModel):
    discovered_files: int
    valid_stocks_count: int
    included_in_optimization: int
    rejected_files_count: int
    rejected_files: List[Dict[str, Any]]
    excluded_stocks: List[Dict[str, Any]]
    overall_earliest_date: str
    overall_latest_date: str
    aligned_earliest_date: str
    aligned_latest_date: str
    total_common_trading_days: int
    total_return_observations: int
    trading_days_per_year: int
    risk_free_rate: float
    generated_files: List[str]

class StockHistoryPoint(BaseModel):
    date: str
    adj_close: float
    daily_return: Optional[float] = None
    volume: Optional[float] = None

class StockDetailResponse(BaseModel):
    stock: str
    metrics: StockMetricItem
    history: List[StockHistoryPoint]
