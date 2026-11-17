"""Markowitz Mean-Variance Portfolio Optimizer and Efficient Frontier generator."""

from typing import Dict, List, Optional, Tuple
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

class MarkowitzOptimizer(BaseOptimizer):
    """Mean-variance portfolio optimizer balancing risk and return."""

    def __init__(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        risk_free_rate: float = settings.RISK_FREE_RATE,
        min_weight: float = settings.MIN_STOCK_WEIGHT,
        max_weight: float = settings.MAX_STOCK_WEIGHT,
        target_return: Optional[float] = None,
        risk_aversion: float = 1.0
    ):
        super().__init__(expected_returns, cov_matrix, risk_free_rate, min_weight, max_weight)
        self.target_return = target_return
        self.risk_aversion = risk_aversion

    def optimize(self) -> PortfolioResult:
        """Optimizes mean-variance tradeoff.
        
        If target_return is provided, minimizes variance for target_return.
        Otherwise, optimizes quadratic utility: max w^T mu - 0.5 * lambda * w^T Sigma w.
        """
        logger.info(
            f"Running Markowitz optimization across {self.num_assets} stocks "
            f"(target_return={self.target_return}, risk_aversion={self.risk_aversion})"
        )

        if HAS_PYPFOPT:
            try:
                ef = EfficientFrontier(
                    expected_returns=pd.Series(self.expected_returns, index=self.tickers),
                    cov_matrix=pd.DataFrame(self.cov_matrix, index=self.tickers, columns=self.tickers),
                    weight_bounds=(self.min_weight, self.max_weight)
                )

                if self.target_return is not None:
                    raw_weights = ef.efficient_return(target_return=self.target_return)
                else:
                    # Maximize quadratic utility: w^T mu - 0.5 * risk_aversion * w^T Sigma w
                    raw_weights = ef.max_quadratic_utility(risk_aversion=self.risk_aversion)

                weights_vec = np.array([raw_weights.get(t, 0.0) for t in self.tickers])
                return self.build_result(
                    portfolio_name="Markowitz Efficient",
                    weights=weights_vec,
                    status="success",
                    message="Optimized mean-variance utility using quadratic programming"
                )
            except Exception as e:
                logger.warning(f"PyPortfolioOpt Markowitz failed ({e}), using SciPy solver")

        # SciPy fallback solver
        # Maximize utility: w^T mu - 0.5 * lambda * w^T Sigma w  <=>  minimize 0.5 * lambda * w^T Sigma w - w^T mu
        def utility_objective(w: np.ndarray) -> float:
            port_ret = float(np.dot(w, self.expected_returns))
            port_var = float(np.dot(w.T, np.dot(self.cov_matrix, w)))
            return 0.5 * self.risk_aversion * port_var - port_ret

        extra_constraints = []
        if self.target_return is not None:
            extra_constraints.append({
                'type': 'eq',
                'fun': lambda w: np.dot(w, self.expected_returns) - self.target_return
            })

        optimal_w, success, msg = solve_quadratic_portfolio(
            objective_fn=utility_objective,
            num_assets=self.num_assets,
            expected_returns=self.expected_returns,
            cov_matrix=self.cov_matrix,
            min_weight=self.min_weight,
            max_weight=self.max_weight,
            extra_constraints=extra_constraints
        )

        return self.build_result(
            portfolio_name="Markowitz Efficient",
            weights=optimal_w,
            status="success" if success else "warning",
            message=msg
        )

    def generate_efficient_frontier(self, n_points: int = 40) -> List[Dict[str, float]]:
        """Traces the Efficient Frontier curve by varying target returns or risk aversion.
        
        Returns:
            List of points with {'return': float, 'volatility': float, 'sharpe': float}
        """
        frontier_points: List[Dict[str, float]] = []

        # Find min and max feasible returns under individual bounds
        sorted_rets = np.sort(self.expected_returns)
        k = int(1.0 / self.max_weight)
        min_possible_ret = float(np.mean(sorted_rets[:k]))
        max_possible_ret = float(np.mean(sorted_rets[-k:]))

        target_returns = np.linspace(min_possible_ret * 1.02, max_possible_ret * 0.98, n_points)

        for tr in target_returns:
            try:
                if HAS_PYPFOPT:
                    ef = EfficientFrontier(
                        expected_returns=pd.Series(self.expected_returns, index=self.tickers),
                        cov_matrix=pd.DataFrame(self.cov_matrix, index=self.tickers, columns=self.tickers),
                        weight_bounds=(self.min_weight, self.max_weight)
                    )
                    raw_w = ef.efficient_return(target_return=float(tr))
                    w_vec = np.array([raw_w.get(t, 0.0) for t in self.tickers])
                else:
                    def var_obj(w: np.ndarray) -> float:
                        return float(np.dot(w.T, np.dot(self.cov_matrix, w)))
                    
                    w_vec, success, _ = solve_quadratic_portfolio(
                        objective_fn=var_obj,
                        num_assets=self.num_assets,
                        expected_returns=self.expected_returns,
                        cov_matrix=self.cov_matrix,
                        min_weight=self.min_weight,
                        max_weight=self.max_weight,
                        extra_constraints=[{'type': 'eq', 'fun': lambda w, ret=tr: np.dot(w, self.expected_returns) - ret}]
                    )
                    if not success:
                        continue

                port_ret = float(np.dot(w_vec, self.expected_returns))
                port_var = max(float(np.dot(w_vec.T, np.dot(self.cov_matrix, w_vec))), 0.0)
                port_vol = float(np.sqrt(port_var))
                sharpe = (port_ret - self.risk_free_rate) / port_vol if port_vol > 1e-8 else 0.0

                frontier_points.append({
                    "return": round(port_ret, 4),
                    "volatility": round(port_vol, 4),
                    "sharpe": round(sharpe, 4)
                })
            except Exception:
                continue

        # Sort by volatility
        frontier_points.sort(key=lambda p: p["volatility"])
        return frontier_points
