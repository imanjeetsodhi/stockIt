"""Feature engineering service for computing stock metrics and matrices."""

from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.utils.calculations import (
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_daily_variance,
    calculate_annualized_variance,
    calculate_maximum_drawdown,
    calculate_sharpe_ratio,
    calculate_cagr,
    calculate_annualized_covariance,
    calculate_correlation_matrix
)

class FeatureEngineeringService:
    def __init__(
        self,
        trading_days: int = settings.TRADING_DAYS_PER_YEAR,
        risk_free_rate: float = settings.RISK_FREE_RATE
    ):
        self.trading_days = trading_days
        self.risk_free_rate = risk_free_rate

    def compute_stock_statistics(
        self,
        prices_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        volume_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Computes comprehensive financial metrics for each stock.
        
        Args:
            prices_df: DataFrame of Adjusted Close prices (index: Date, columns: tickers)
            returns_df: DataFrame of daily percentage returns
            volume_df: Optional DataFrame of daily volumes
            
        Returns:
            DataFrame where rows are stock tickers and columns are metrics.
        """
        tickers = list(prices_df.columns)
        records = []

        avg_daily_ret = returns_df.mean()
        ann_ret = calculate_annualized_return(returns_df, self.trading_days)
        ann_vol = calculate_annualized_volatility(returns_df, self.trading_days)
        daily_var = calculate_daily_variance(returns_df)
        ann_var = calculate_annualized_variance(returns_df, self.trading_days)
        max_dd = calculate_maximum_drawdown(prices_df)
        cagr = calculate_cagr(prices_df, self.trading_days)
        sharpe = calculate_sharpe_ratio(ann_ret, ann_vol, self.risk_free_rate)

        for ticker in tickers:
            avg_vol = float(volume_df[ticker].mean()) if (volume_df is not None and ticker in volume_df.columns) else 0.0
            latest_price = float(prices_df[ticker].dropna().iloc[-1]) if not prices_df[ticker].dropna().empty else 0.0

            records.append({
                "Stock": ticker,
                "Average_Daily_Return": float(avg_daily_ret[ticker]),
                "Annualized_Return": float(ann_ret[ticker]),
                "CAGR": float(cagr[ticker]),
                "Annualized_Volatility": float(ann_vol[ticker]),
                "Daily_Variance": float(daily_var[ticker]),
                "Annualized_Variance": float(ann_var[ticker]),
                "Maximum_Drawdown": float(max_dd[ticker]),
                "Sharpe_Ratio": float(sharpe[ticker]),
                "Average_Daily_Volume": avg_vol,
                "Latest_Price": latest_price,
                "Total_Observations": int(returns_df[ticker].count())
            })

        stats_df = pd.DataFrame(records).set_index("Stock")
        logger.info(f"Computed financial statistics for {len(stats_df)} stocks")
        return stats_df

    def compute_covariance_and_correlation(
        self,
        returns_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Calculates annualized covariance matrix and correlation matrix."""
        cov_matrix = calculate_annualized_covariance(returns_df, self.trading_days)
        corr_matrix = calculate_correlation_matrix(returns_df)
        return cov_matrix, corr_matrix
