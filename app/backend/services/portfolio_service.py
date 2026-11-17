"""Portfolio service orchestrating dataset loading and portfolio optimization algorithms."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.core.exceptions import DataIngestionError, OptimizationError
from app.backend.models.portfolio import PortfolioResult
from app.backend.optimization.markowitz import MarkowitzOptimizer
from app.backend.optimization.minimum_variance import MinimumVarianceOptimizer
from app.backend.optimization.maximum_sharpe import MaximumSharpeOptimizer
from app.backend.services.preprocessing import PreprocessingPipeline

class PortfolioService:
    def __init__(
        self,
        processed_dir: Optional[Path] = None,
        risk_free_rate: float = settings.RISK_FREE_RATE
    ):
        self.processed_dir = Path(processed_dir) if processed_dir else settings.PROCESSED_DATA_DIR
        self.risk_free_rate = risk_free_rate
        self._stats_df: Optional[pd.DataFrame] = None
        self._cov_matrix: Optional[pd.DataFrame] = None
        self._corr_matrix: Optional[pd.DataFrame] = None
        self._prices_df: Optional[pd.DataFrame] = None
        self._returns_df: Optional[pd.DataFrame] = None

    def ensure_data_loaded(self) -> None:
        """Loads processed datasets from disk, triggering preprocessing if missing."""
        stats_path = self.processed_dir / "stock_statistics.csv"
        cov_path = self.processed_dir / "covariance_matrix.csv"
        corr_path = self.processed_dir / "correlation_matrix.csv"
        prices_path = self.processed_dir / "adjusted_close_prices.csv"
        returns_path = self.processed_dir / "daily_returns.csv"

        if not (stats_path.exists() and cov_path.exists() and prices_path.exists()):
            logger.info("Processed data files missing. Running preprocessing pipeline...")
            pipeline = PreprocessingPipeline(
                processed_dir=self.processed_dir,
                risk_free_rate=self.risk_free_rate
            )
            pipeline.run_pipeline()

        if self._stats_df is None:
            self._stats_df = pd.read_csv(stats_path, index_col="Stock")
        if self._cov_matrix is None:
            self._cov_matrix = pd.read_csv(cov_path, index_col=0)
        if self._corr_matrix is None:
            self._corr_matrix = pd.read_csv(corr_path, index_col=0)
        if self._prices_df is None:
            self._prices_df = pd.read_csv(prices_path, index_col="Date", parse_dates=True)
        if self._returns_df is None:
            self._returns_df = pd.read_csv(returns_path, index_col="Date", parse_dates=True)

    @property
    def stock_statistics(self) -> pd.DataFrame:
        self.ensure_data_loaded()
        return self._stats_df

    @property
    def covariance_matrix(self) -> pd.DataFrame:
        self.ensure_data_loaded()
        return self._cov_matrix

    @property
    def correlation_matrix(self) -> pd.DataFrame:
        self.ensure_data_loaded()
        return self._corr_matrix

    @property
    def prices(self) -> pd.DataFrame:
        self.ensure_data_loaded()
        return self._prices_df

    @property
    def daily_returns(self) -> pd.DataFrame:
        self.ensure_data_loaded()
        return self._returns_df

    def get_expected_returns(self) -> pd.Series:
        self.ensure_data_loaded()
        return self._stats_df["Annualized_Return"]

    def run_minimum_variance(
        self,
        max_weight: float = settings.MAX_STOCK_WEIGHT,
        risk_free_rate: Optional[float] = None
    ) -> PortfolioResult:
        rf = risk_free_rate if risk_free_rate is not None else self.risk_free_rate
        optimizer = MinimumVarianceOptimizer(
            expected_returns=self.get_expected_returns(),
            cov_matrix=self.covariance_matrix,
            risk_free_rate=rf,
            max_weight=max_weight
        )
        return optimizer.optimize()

    def run_maximum_sharpe(
        self,
        max_weight: float = settings.MAX_STOCK_WEIGHT,
        risk_free_rate: Optional[float] = None
    ) -> PortfolioResult:
        rf = risk_free_rate if risk_free_rate is not None else self.risk_free_rate
        optimizer = MaximumSharpeOptimizer(
            expected_returns=self.get_expected_returns(),
            cov_matrix=self.covariance_matrix,
            risk_free_rate=rf,
            max_weight=max_weight
        )
        return optimizer.optimize()

    def run_markowitz(
        self,
        max_weight: float = settings.MAX_STOCK_WEIGHT,
        risk_free_rate: Optional[float] = None,
        risk_aversion: float = 1.0,
        target_return: Optional[float] = None
    ) -> PortfolioResult:
        rf = risk_free_rate if risk_free_rate is not None else self.risk_free_rate
        optimizer = MarkowitzOptimizer(
            expected_returns=self.get_expected_returns(),
            cov_matrix=self.covariance_matrix,
            risk_free_rate=rf,
            max_weight=max_weight,
            risk_aversion=risk_aversion,
            target_return=target_return
        )
        return optimizer.optimize()

    def run_all_strategies(
        self,
        max_weight: float = settings.MAX_STOCK_WEIGHT,
        risk_free_rate: Optional[float] = None,
        risk_aversion: float = 1.0
    ) -> Dict[str, PortfolioResult]:
        """Runs all three optimization techniques under consistent data and constraints."""
        rf = risk_free_rate if risk_free_rate is not None else self.risk_free_rate
        return {
            "Minimum Variance": self.run_minimum_variance(max_weight=max_weight, risk_free_rate=rf),
            "Markowitz Efficient": self.run_markowitz(max_weight=max_weight, risk_free_rate=rf, risk_aversion=risk_aversion),
            "Maximum Sharpe": self.run_maximum_sharpe(max_weight=max_weight, risk_free_rate=rf)
        }

    def get_efficient_frontier_curve(
        self,
        max_weight: float = settings.MAX_STOCK_WEIGHT,
        n_points: int = 35
    ) -> List[Dict[str, float]]:
        optimizer = MarkowitzOptimizer(
            expected_returns=self.get_expected_returns(),
            cov_matrix=self.covariance_matrix,
            risk_free_rate=self.risk_free_rate,
            max_weight=max_weight
        )
        return optimizer.generate_efficient_frontier(n_points=n_points)
