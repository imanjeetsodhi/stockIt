# Stackit: Project Overview

## 1. Executive Summary
**Stackit** is an enterprise-grade quantitative portfolio optimization and investment decision-support system built in Python. Designed for Indian equity markets, Stackit ingests historical daily observations across NIFTY 50 constituents, cleans and aligns the market data, computes financial return and risk metrics, and solves three fundamental Modern Portfolio Theory problems:

1. **Markowitz Mean-Variance Optimization:** Maximizes quadratic utility and traces the Efficient Frontier.
2. **Minimum Variance Portfolio:** Finds the lowest-volatility asset allocation.
3. **Maximum Sharpe Ratio Portfolio:** Solves for the tangency portfolio maximizing excess return per unit of volatility.

Stackit bridges the gap between theoretical quantitative finance and practical execution by converting optimal weights into executable whole-share quantities in Indian Rupees (₹) and providing transparent, deterministic, metric-grounded explanations for every stock selection.

---

## 2. Problem Statement
Retail and institutional investors in Indian equities face significant challenges:
- **Heuristic Stock Picking:** Investors frequently allocate capital based on hype or arbitrary equal weights, ignoring cross-asset covariance and concentration risk.
- **Opacity of Traditional Tools:** Existing portfolio tools often display opaque "black box" recommendations without explaining why a stock was picked or how it affects portfolio risk.
- **Inexecutable Allocations:** Many theoretical calculators recommend fractional shares (e.g. 14.37 shares), which cannot be purchased directly on Indian exchanges (NSE/BSE) without cash drag or rounding discrepancies.

Stackit resolves these problems with mathematical rigour, explicit constraint enforcement, whole-share integer rounding, and explainable quantitative metrics.

---

## 3. Key Capabilities
- **End-to-End Data Pipeline:** Discovers, validates, and aligns 50 NIFTY CSV files over 763 common trading days without manufactured observations.
- **Convex Portfolio Optimization:** Powered by convex quadratic solvers (PyPortfolioOpt / SciPy SLSQP).
- **Interactive Visualizations:** Dark-first Plotly dashboards showing weights, donut charts, risk-return scatter plots, and correlation heatmaps.
- **Deterministic Explanations:** Explains each stock's role (Defensive Stabilizer, Return Generator, Diversification Anchor) using actual annualized return, volatility, Sharpe ratio, and marginal risk contribution.
- **Chronological Out-of-Sample Backtesting:** Validates performance on held-out historical data without look-ahead bias.
