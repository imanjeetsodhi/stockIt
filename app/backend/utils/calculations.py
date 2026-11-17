"""Pure financial and mathematical calculation utilities."""

from typing import Union, Tuple
import numpy as np
import pandas as pd
from app.backend.core.config import settings

def calculate_daily_returns(prices: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
    """Calculates daily percentage returns: R_t = (P_t / P_{t-1}) - 1."""
    return prices.pct_change().dropna(how="all")

def calculate_annualized_return(
    daily_returns: Union[pd.Series, pd.DataFrame],
    trading_days: int = settings.TRADING_DAYS_PER_YEAR
) -> Union[float, pd.Series]:
    """Calculates annualized arithmetic mean return: Mean(R_daily) * 252."""
    return daily_returns.mean() * trading_days

def calculate_cagr(
    prices: Union[pd.Series, pd.DataFrame],
    trading_days: int = settings.TRADING_DAYS_PER_YEAR
) -> Union[float, pd.Series]:
    """Calculates Compounded Annual Growth Rate (CAGR)."""
    if isinstance(prices, pd.DataFrame):
        n_days = len(prices)
        years = n_days / trading_days
        return (prices.iloc[-1] / prices.iloc[0]) ** (1.0 / years) - 1.0
    else:
        n_days = len(prices)
        years = n_days / trading_days
        return (prices.iloc[-1] / prices.iloc[0]) ** (1.0 / years) - 1.0

def calculate_annualized_volatility(
    daily_returns: Union[pd.Series, pd.DataFrame],
    trading_days: int = settings.TRADING_DAYS_PER_YEAR
) -> Union[float, pd.Series]:
    """Calculates annualized volatility: Std(R_daily) * sqrt(252)."""
    return daily_returns.std() * np.sqrt(trading_days)

def calculate_daily_variance(
    daily_returns: Union[pd.Series, pd.DataFrame]
) -> Union[float, pd.Series]:
    """Calculates daily return variance."""
    return daily_returns.var()

def calculate_annualized_variance(
    daily_returns: Union[pd.Series, pd.DataFrame],
    trading_days: int = settings.TRADING_DAYS_PER_YEAR
) -> Union[float, pd.Series]:
    """Calculates annualized variance: Var(R_daily) * 252."""
    return daily_returns.var() * trading_days

def calculate_maximum_drawdown(prices: Union[pd.Series, pd.DataFrame]) -> Union[float, pd.Series]:
    """Calculates maximum historical peak-to-trough drawdown."""
    if isinstance(prices, pd.DataFrame):
        running_max = prices.cummax()
        drawdown = (prices - running_max) / running_max
        return drawdown.min()
    else:
        running_max = prices.cummax()
        drawdown = (prices - running_max) / running_max
        return float(drawdown.min())

def calculate_sharpe_ratio(
    expected_return: Union[float, pd.Series],
    volatility: Union[float, pd.Series],
    risk_free_rate: float = settings.RISK_FREE_RATE
) -> Union[float, pd.Series]:
    """Calculates Sharpe Ratio: (E[R] - R_f) / Volatility."""
    denom = np.where(volatility == 0, np.nan, volatility)
    return (expected_return - risk_free_rate) / denom

def calculate_annualized_covariance(
    daily_returns: pd.DataFrame,
    trading_days: int = settings.TRADING_DAYS_PER_YEAR
) -> pd.DataFrame:
    """Calculates annualized covariance matrix: Cov(R_daily) * 252."""
    return daily_returns.cov() * trading_days

def calculate_correlation_matrix(daily_returns: pd.DataFrame) -> pd.DataFrame:
    """Calculates Pearson correlation matrix."""
    return daily_returns.corr()

def calculate_portfolio_metrics(
    weights: np.ndarray,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = settings.RISK_FREE_RATE
) -> Tuple[float, float, float, float]:
    """Calculates portfolio metrics for a given weight vector.
    
    Returns:
        Tuple of (expected_annual_return, annual_volatility, annual_variance, sharpe_ratio)
    """
    weights = np.asarray(weights, dtype=float)
    port_return = float(np.dot(weights, expected_returns))
    port_variance = float(np.dot(weights.T, np.dot(cov_matrix, weights)))
    # Numerical stability check
    port_variance = max(port_variance, 0.0)
    port_volatility = float(np.sqrt(port_variance))
    sharpe = float((port_return - risk_free_rate) / port_volatility) if port_volatility > 1e-8 else 0.0
    return port_return, port_volatility, port_variance, sharpe

def calculate_marginal_risk_contributions(
    weights: np.ndarray,
    cov_matrix: np.ndarray
) -> np.ndarray:
    """Calculates the percentage contribution of each asset to the total portfolio variance/risk.
    
    RC_i = w_i * (Sigma * w)_i / sigma_p^2
    """
    weights = np.asarray(weights, dtype=float)
    port_variance = float(np.dot(weights.T, np.dot(cov_matrix, weights)))
    if port_variance <= 1e-12:
        return np.zeros_like(weights)
    
    marginal_contrib = np.dot(cov_matrix, weights)
    risk_contribution = weights * marginal_contrib / port_variance
    return risk_contribution
