"""Backtesting module for out-of-sample portfolio performance evaluation."""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.core.exceptions import BacktestingError
from app.backend.services.feature_engineering import FeatureEngineeringService
from app.backend.optimization.markowitz import MarkowitzOptimizer
from app.backend.optimization.minimum_variance import MinimumVarianceOptimizer
from app.backend.optimization.maximum_sharpe import MaximumSharpeOptimizer
from app.backend.utils.calculations import (
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_maximum_drawdown,
    calculate_sharpe_ratio
)

class BacktestService:
    def __init__(
        self,
        prices_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        risk_free_rate: float = settings.RISK_FREE_RATE,
        trading_days: int = settings.TRADING_DAYS_PER_YEAR
    ):
        self.prices_df = prices_df.copy()
        self.returns_df = returns_df.copy()
        self.risk_free_rate = risk_free_rate
        self.trading_days = trading_days

    def run_out_of_sample_backtest(
        self,
        split_date: Optional[str] = None,
        train_ratio: float = 0.70,
        transaction_cost_pct: float = 0.001,  # 10 bps (0.10%)
        max_stock_weight: float = 0.20
    ) -> Dict[str, Any]:
        """Runs chronological out-of-sample backtest across all three strategies and benchmark.
        
        Args:
            split_date: Optional YYYY-MM-DD string to split in-sample and out-of-sample.
            train_ratio: Fraction of dates used for in-sample estimation if split_date is None.
            transaction_cost_pct: One-way transaction cost / friction per trade.
            max_stock_weight: Maximum stock allocation bound.
            
        Returns:
            Dictionary with performance metrics, cumulative return series, and metadata.
        """
        all_dates = sorted(self.returns_df.index)
        n_dates = len(all_dates)

        if split_date:
            split_dt = pd.to_datetime(split_date)
            train_mask = self.returns_df.index < split_dt
            test_mask = self.returns_df.index >= split_dt
        else:
            split_idx = int(n_dates * train_ratio)
            split_dt = all_dates[split_idx]
            train_mask = self.returns_df.index < split_dt
            test_mask = self.returns_df.index >= split_dt

        train_returns = self.returns_df.loc[train_mask]
        test_returns = self.returns_df.loc[test_mask]

        if len(train_returns) < 100:
            raise BacktestingError("Insufficient training data for estimation (minimum 100 days)")
        if len(test_returns) < 20:
            raise BacktestingError("Insufficient testing data for evaluation (minimum 20 days)")

        logger.info(
            f"Backtesting: In-sample ({len(train_returns)} days: {train_returns.index.min().strftime('%Y-%m-%d')} to {train_returns.index.max().strftime('%Y-%m-%d')}) | "
            f"Out-of-sample ({len(test_returns)} days: {test_returns.index.min().strftime('%Y-%m-%d')} to {test_returns.index.max().strftime('%Y-%m-%d')})"
        )

        # 1. In-sample parameter estimation strictly using train_returns (No lookahead!)
        fe = FeatureEngineeringService(trading_days=self.trading_days, risk_free_rate=self.risk_free_rate)
        expected_returns = train_returns.mean() * self.trading_days
        cov_matrix = train_returns.cov() * self.trading_days

        # 2. Optimize portfolios using in-sample data
        min_opt = MinimumVarianceOptimizer(expected_returns, cov_matrix, self.risk_free_rate, max_weight=max_stock_weight)
        res_min = min_opt.optimize()

        mark_opt = MarkowitzOptimizer(expected_returns, cov_matrix, self.risk_free_rate, max_weight=max_stock_weight)
        res_mark = mark_opt.optimize()

        sharpe_opt = MaximumSharpeOptimizer(expected_returns, cov_matrix, self.risk_free_rate, max_weight=max_stock_weight)
        res_sharpe = sharpe_opt.optimize()

        # 3. Equal-weighted NIFTY 50 benchmark
        benchmark_weights = {ticker: 1.0 / len(test_returns.columns) for ticker in test_returns.columns}

        strategies_to_test = {
            "Minimum Variance": res_min.allocations,
            "Markowitz Efficient": res_mark.allocations,
            "Maximum Sharpe": res_sharpe.allocations,
            "Equal-Weight Benchmark": benchmark_weights
        }

        results = {}
        cumulative_curves = {}

        # 4. Out-of-sample simulation
        for name, weights_dict in strategies_to_test.items():
            # Align weights vector with test_returns columns
            w_series = pd.Series(0.0, index=test_returns.columns)
            for t, w in weights_dict.items():
                if t in w_series.index:
                    w_series[t] = w

            # Normalize
            if w_series.sum() > 0:
                w_series = w_series / w_series.sum()

            # Daily portfolio returns
            port_daily = test_returns.dot(w_series)

            # Deduct upfront transaction cost on first day
            port_daily.iloc[0] -= transaction_cost_pct

            # Performance metrics in out-of-sample period
            cum_ret = (1.0 + port_daily).cumprod()
            total_return = float(cum_ret.iloc[-1] - 1.0)
            ann_ret = float(calculate_annualized_return(port_daily, self.trading_days))
            ann_vol = float(calculate_annualized_volatility(port_daily, self.trading_days))
            sharpe = float(calculate_sharpe_ratio(ann_ret, ann_vol, self.risk_free_rate))
            max_dd = float(calculate_maximum_drawdown(cum_ret))

            results[name] = {
                "total_return_pct": round(total_return * 100, 2),
                "annualized_return_pct": round(ann_ret * 100, 2),
                "annualized_volatility_pct": round(ann_vol * 100, 2),
                "sharpe_ratio": round(sharpe, 2),
                "max_drawdown_pct": round(max_dd * 100, 2),
                "stock_count": len([w for w in weights_dict.values() if w > 0])
            }

            # Cumulative performance time series formatted for Plotly
            cumulative_curves[name] = [
                {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 4)}
                for d, v in cum_ret.items()
            ]

        return {
            "split_date": split_dt.strftime("%Y-%m-%d"),
            "train_days": int(len(train_returns)),
            "test_days": int(len(test_returns)),
            "transaction_cost_bps": round(transaction_cost_pct * 10000, 1),
            "performance_summary": results,
            "cumulative_curves": cumulative_curves,
            "notes": (
                "Evaluated out-of-sample. Models trained strictly on in-sample data. "
                "Constituents reflect current NIFTY 50, which carries survivorship bias."
            )
        }
