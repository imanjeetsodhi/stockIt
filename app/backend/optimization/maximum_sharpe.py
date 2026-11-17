"""Maximum Sharpe Ratio Portfolio Optimizer."""

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

class MaximumSharpeOptimizer(BaseOptimizer):
    """Finds the portfolio allocation that maximizes the historical Sharpe Ratio."""

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
        """Maximizes Sharpe Ratio: max (w^T mu - Rf) / sqrt(w^T Sigma w)."""
        logger.info(f"Running Maximum Sharpe optimization across {self.num_assets} stocks (Rf={self.risk_free_rate:.2%})")

        # Primary method: PyPortfolioOpt
        if HAS_PYPFOPT:
            try:
                ef = EfficientFrontier(
                    expected_returns=pd.Series(self.expected_returns, index=self.tickers),
                    cov_matrix=pd.DataFrame(self.cov_matrix, index=self.tickers, columns=self.tickers),
                    weight_bounds=(self.min_weight, self.max_weight)
                )
                raw_weights = ef.max_sharpe(risk_free_rate=self.risk_free_rate)
                weights_vec = np.array([raw_weights.get(t, 0.0) for t in self.tickers])
                return self.build_result(
                    portfolio_name="Maximum Sharpe",
                    weights=weights_vec,
                    status="success",
                    message="Optimized maximum Sharpe ratio using convex transformation"
                )
            except Exception as e:
                logger.warning(f"PyPortfolioOpt max_sharpe failed ({e}), falling back to SciPy SLSQP")

        # Fallback SciPy SLSQP minimizing negative Sharpe
        def negative_sharpe(w: np.ndarray) -> float:
            port_ret = float(np.dot(w, self.expected_returns))
            port_var = float(np.dot(w.T, np.dot(self.cov_matrix, w)))
            port_vol = np.sqrt(max(port_var, 1e-12))
            return - float((port_ret - self.risk_free_rate) / port_vol)

        # Smart initial guess: pick top historical Sharpe stocks
        sharpes = (self.expected_returns - self.risk_free_rate) / np.sqrt(np.diag(self.cov_matrix))
        top_indices = np.argsort(sharpes)[-int(1.0 / self.max_weight):]
        w0 = np.zeros(self.num_assets)
        w0[top_indices] = 1.0 / len(top_indices)

        optimal_w, success, msg = solve_quadratic_portfolio(
            objective_fn=negative_sharpe,
            num_assets=self.num_assets,
            expected_returns=self.expected_returns,
            cov_matrix=self.cov_matrix,
            min_weight=self.min_weight,
            max_weight=self.max_weight,
            initial_weights=w0
        )

        return self.build_result(
            portfolio_name="Maximum Sharpe",
            weights=optimal_w,
            status="success" if success else "warning",
            message=msg
        )
