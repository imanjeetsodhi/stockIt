"""Base class for all portfolio optimizers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from app.backend.core.config import settings
from app.backend.core.exceptions import OptimizationError
from app.backend.models.portfolio import PortfolioResult
from app.backend.optimization.optimizer_utils import clean_and_normalize_weights
from app.backend.utils.calculations import (
    calculate_portfolio_metrics,
    calculate_marginal_risk_contributions
)

class BaseOptimizer(ABC):
    def __init__(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        risk_free_rate: float = settings.RISK_FREE_RATE,
        min_weight: float = settings.MIN_STOCK_WEIGHT,
        max_weight: float = settings.MAX_STOCK_WEIGHT
    ):
        # Align tickers
        common_tickers = [t for t in expected_returns.index if t in cov_matrix.index and t in cov_matrix.columns]
        if len(common_tickers) == 0:
            raise OptimizationError("No matching tickers between expected returns and covariance matrix")

        self.tickers = sorted(common_tickers)
        self.expected_returns = expected_returns.loc[self.tickers].values.astype(float)
        self.cov_matrix = cov_matrix.loc[self.tickers, self.tickers].values.astype(float)
        self.risk_free_rate = float(risk_free_rate)
        self.min_weight = float(min_weight)
        self.max_weight = float(max_weight)
        self.num_assets = len(self.tickers)

    @abstractmethod
    def optimize(self) -> PortfolioResult:
        """Runs the optimization algorithm and returns PortfolioResult."""
        pass

    def build_result(
        self,
        portfolio_name: str,
        weights: np.ndarray,
        status: str = "success",
        message: Optional[str] = None
    ) -> PortfolioResult:
        """Formats optimized weights into a standardized PortfolioResult."""
        cleaned_weights_dict = clean_and_normalize_weights(
            weights,
            self.tickers,
            tolerance=settings.WEIGHT_THRESHOLD
        )

        # Vector of final cleaned weights
        final_w = np.array([cleaned_weights_dict.get(t, 0.0) for t in self.tickers])

        # Recalculate true metrics strictly on the final cleaned weights
        ret, vol, var, sharpe = calculate_portfolio_metrics(
            weights=final_w,
            expected_returns=self.expected_returns,
            cov_matrix=self.cov_matrix,
            risk_free_rate=self.risk_free_rate
        )

        # Marginal risk contribution
        mrc = calculate_marginal_risk_contributions(final_w, self.cov_matrix)
        mrc_dict = {
            t: round(float(rc), 4)
            for t, rc in zip(self.tickers, mrc)
            if cleaned_weights_dict.get(t, 0.0) > 0
        }

        # Filter allocations to only positive holdings
        positive_allocations = {k: v for k, v in cleaned_weights_dict.items() if v > 0}

        return PortfolioResult(
            portfolio_name=portfolio_name,
            expected_annual_return=round(ret, 6),
            annual_volatility=round(vol, 6),
            variance=round(var, 6),
            sharpe_ratio=round(sharpe, 4),
            allocations=positive_allocations,
            status=status,
            message=message or "Optimized successfully",
            marginal_risk_contributions=mrc_dict,
            risk_free_rate=self.risk_free_rate,
            stock_count=len(positive_allocations)
        )
