"""Constants used across Stackit frontend and backend."""

from enum import Enum

DEFAULT_RISK_FREE_RATE = 0.065  # 6.5% typical Indian RBI / 10-Yr G-Sec proxy
TRADING_DAYS_PER_YEAR = 252
DEFAULT_MAX_WEIGHT = 0.20
DEFAULT_MIN_WEIGHT = 0.0
WEIGHT_TOLERANCE = 1e-4

class RiskAppetite(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"

class InvestmentHorizon(str, Enum):
    LESS_THAN_1_YEAR = "< 1 year"
    ONE_TO_THREE_YEARS = "1–3 years"
    THREE_TO_FIVE_YEARS = "3–5 years"
    MORE_THAN_5_YEARS = "> 5 years"

class InvestmentObjective(str, Enum):
    CAPITAL_PRESERVATION = "Capital Preservation"
    BALANCED_GROWTH = "Balanced Growth"
    WEALTH_CREATION = "Long-Term Wealth Creation"

class OptimizationMethod(str, Enum):
    MARKOWITZ = "Markowitz Efficient"
    MIN_VARIANCE = "Minimum Variance"
    MAX_SHARPE = "Maximum Sharpe"
