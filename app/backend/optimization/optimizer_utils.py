"""Utility functions for mathematical portfolio optimization."""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from app.backend.core.exceptions import InfeasibleConstraintsError
from app.backend.core.logging import logger
from app.backend.utils.calculations import calculate_portfolio_metrics

def clean_and_normalize_weights(
    weights: np.ndarray,
    tickers: List[str],
    tolerance: float = 1e-4
) -> Dict[str, float]:
    """Cleans tiny weights below tolerance, zeros them out, and strictly normalizes to sum to 1.0."""
    w = np.copy(weights)
    w[w < tolerance] = 0.0
    total = np.sum(w)
    if total <= 0:
        # Fallback to equal weight across non-zero or all tickers
        w = np.ones_like(w) / len(w)
    else:
        w = w / total

    # Round to 6 decimal places and ensure sum is exact
    w_dict = {ticker: round(float(weight), 6) for ticker, weight in zip(tickers, w) if weight > 0}
    
    # Re-normalize dictionary to sum exactly to 1.0
    sum_d = sum(w_dict.values())
    if sum_d > 0 and abs(sum_d - 1.0) > 1e-6:
        # Adjust the largest weight slightly to maintain exact 1.0 sum
        max_k = max(w_dict, key=w_dict.get)
        w_dict[max_k] = round(w_dict[max_k] + (1.0 - sum_d), 6)

    return w_dict

def validate_bounds(num_assets: int, min_weight: float, max_weight: float) -> None:
    """Validates if the bounds can physically sum to 1.0."""
    if max_weight * num_assets < 1.0 - 1e-6:
        raise InfeasibleConstraintsError(
            f"Infeasible constraint: Maximum weight ({max_weight:.1%}) across {num_assets} assets "
            f"sums to only {max_weight * num_assets:.1%}, which cannot reach 100% allocation. "
            f"Increase max_weight to at least {1.0 / num_assets:.4f}."
        )
    if min_weight * num_assets > 1.0 + 1e-6:
        raise InfeasibleConstraintsError(
            f"Infeasible constraint: Minimum weight ({min_weight:.1%}) across {num_assets} assets "
            f"exceeds 100% total allocation."
        )

def solve_quadratic_portfolio(
    objective_fn,
    num_assets: int,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    min_weight: float = 0.0,
    max_weight: float = 0.20,
    extra_constraints: Optional[List[dict]] = None,
    initial_weights: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, bool, str]:
    """Solves bounded constrained optimization using SciPy SLSQP.
    
    Returns:
        Tuple of (optimal_weights, success_bool, message_str)
    """
    validate_bounds(num_assets, min_weight, max_weight)

    bounds = tuple((min_weight, max_weight) for _ in range(num_assets))
    base_constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

    if extra_constraints:
        base_constraints.extend(extra_constraints)

    if initial_weights is None:
        # Default uniform weights
        w0 = np.ones(num_assets) / num_assets
    else:
        w0 = np.copy(initial_weights)

    try:
        res = minimize(
            fun=objective_fn,
            x0=w0,
            method='SLSQP',
            bounds=bounds,
            constraints=base_constraints,
            options={'ftol': 1e-9, 'maxiter': 1000, 'disp': False}
        )

        if res.success:
            return res.x, True, "Optimization converged successfully"
        else:
            return res.x, False, res.message
    except Exception as e:
        logger.error(f"Solver encountered exception: {e}")
        return w0, False, str(e)
