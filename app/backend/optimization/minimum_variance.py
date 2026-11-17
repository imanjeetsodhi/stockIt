"""Minimum Variance Portfolio Optimizer."""

import numpy as np
import pandas as pd
from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.core.exceptions import OptimizationError
from app.backend.models.portfolio import PortfolioResult
from app.backend.optimization.base_optimizer import BaseOptimizer
from app.backend.optimization.optimizer_utils import solve_quadratic_portfolio

try:
    from pypfopt import EfficientFrontier
    HAS_PYPFOPT = True
except ImportError:
    HAS_PYPFOPT = False

class MinimumVarianceOptimizer(BaseOptimizer):
    """Finds the portfolio allocation with the lowest historical portfolio volatility."""

    def __init__(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        risk_free_rate: float = settings.RISK_FREE_RATE,
        min_weight: float = settings.MIN_STOCK_WEIGHT,
        max_weight: float = settings.MAX_STOCK_WEIGHT
    ):
        super().__init__(expected_returns, cov_matrix, risk_free_rate, min_weight, max_weight)

    def optimize(self) -> PortfolioResult:
        """Minimizes portfolio variance: min w^T Sigma w."""
        logger.info(f"Running Minimum Variance optimization across {self.num_assets} stocks (max_weight={self.max_weight:.1%})")

        # Primary method: PyPortfolioOpt if available, with robust SciPy fallback
        if HAS_PYPFOPT:
            try:
                ef = EfficientFrontier(
                    expected_returns=pd.Series(self.expected_returns, index=self.tickers),
                    cov_matrix=pd.DataFrame(self.cov_matrix, index=self.tickers, columns=self.tickers),
                    weight_bounds=(self.min_weight, self.max_weight)
                )
                raw_weights = ef.min_volatility()
                weights_vec = np.array([raw_weights.get(t, 0.0) for t in self.tickers])
                return self.build_result(
                    portfolio_name="Minimum Variance",
                    weights=weights_vec,
                    status="success",
                    message="Optimized minimum variance using convex solver"
                )
            except Exception as e:
                logger.warning(f"PyPortfolioOpt min_volatility failed ({e}), falling back to SciPy SLSQP")

        # Fallback / Direct SciPy SLSQP Quadratic Optimization
        def objective_variance(w: np.ndarray) -> float:
            return float(np.dot(w.T, np.dot(self.cov_matrix, w)))

        optimal_w, success, msg = solve_quadratic_portfolio(
            objective_fn=objective_variance,
            num_assets=self.num_assets,
            expected_returns=self.expected_returns,
            cov_matrix=self.cov_matrix,
            min_weight=self.min_weight,
            max_weight=self.max_weight
        )

        if not success:
            logger.warning(f"SciPy SLSQP did not fully converge: {msg}")

        return self.build_result(
            portfolio_name="Minimum Variance",
            weights=optimal_w,
            status="success" if success else "warning",
            message=msg
        )
