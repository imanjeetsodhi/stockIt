"""Explanation engine generating deterministic, metric-grounded portfolio insights."""

from typing import Dict, List, Optional
import pandas as pd
from app.backend.models.portfolio import PortfolioResult, StockExplanation, RupeeAllocationSummary

class ExplanationService:
    def __init__(self, stock_statistics: pd.DataFrame, correlation_matrix: pd.DataFrame):
        self.stats = stock_statistics
        self.corr_matrix = correlation_matrix

    def generate_stock_explanations(
        self,
        portfolio: PortfolioResult,
        allocation_summary: RupeeAllocationSummary
    ) -> List[StockExplanation]:
        """Generates comprehensive explanations for each stock in the portfolio."""
        explanations: List[StockExplanation] = []
        selected_tickers = list(portfolio.allocations.keys())

        # Average correlation among selected assets
        avg_correlations = {}
        if len(selected_tickers) > 1 and not self.corr_matrix.empty:
            sub_corr = self.corr_matrix.loc[
                [t for t in selected_tickers if t in self.corr_matrix.index],
                [t for t in selected_tickers if t in self.corr_matrix.columns]
            ]
            for t in selected_tickers:
                if t in sub_corr.index:
                    other_tickers = [o for o in selected_tickers if o != t and o in sub_corr.columns]
                    if other_tickers:
                        avg_correlations[t] = float(sub_corr.loc[t, other_tickers].mean())
                    else:
                        avg_correlations[t] = 0.5
                else:
                    avg_correlations[t] = 0.5
        else:
            for t in selected_tickers:
                avg_correlations[t] = 0.5

        # Build holding lookup
        holding_map = {item.stock: item for item in allocation_summary.holdings}

        for ticker, weight in sorted(portfolio.allocations.items(), key=lambda x: x[1], reverse=True):
            if weight <= 0:
                continue

            stat = self.stats.loc[ticker] if ticker in self.stats.index else None
            ann_ret = float(stat["Annualized_Return"]) if stat is not None else 0.0
            ann_vol = float(stat["Annualized_Volatility"]) if stat is not None else 0.0
            sharpe = float(stat["Sharpe_Ratio"]) if stat is not None else 0.0
            max_dd = float(stat["Maximum_Drawdown"]) if stat is not None else 0.0
            avg_corr = avg_correlations.get(ticker, 0.5)

            rc = portfolio.marginal_risk_contributions.get(ticker, weight) if portfolio.marginal_risk_contributions else weight
            rc_pct = rc * 100

            holding_item = holding_map.get(ticker)
            rupee_alloc = holding_item.actual_investment if holding_item else 0.0

            # Determine qualitative role
            if ann_vol < portfolio.annual_volatility and rc_pct < (weight * 100):
                role = "Defensive Stabilizer (Reduces portfolio volatility)"
            elif ann_ret > portfolio.expected_annual_return and sharpe > portfolio.sharpe_ratio:
                role = "Primary Return Generator (Boosts excess returns)"
            elif avg_corr < 0.40:
                role = "Diversification Anchor (Low cross-asset correlation)"
            else:
                role = "Balanced Core Holding"

            # Diversification assessment
            if avg_corr < 0.35:
                div_score = f"High Diversifier (Average correlation: {avg_corr:.2f})"
            elif avg_corr < 0.60:
                div_score = f"Moderate Diversifier (Average correlation: {avg_corr:.2f})"
            else:
                div_score = f"Clustered / Co-moving (Average correlation: {avg_corr:.2f})"

            # Build narrative
            reason = (
                f"{ticker} received a {weight:.1%} portfolio allocation (₹{rupee_alloc:,.2f}) "
                f"due to its historical annualized return of {ann_ret:.1%} and annualized volatility of {ann_vol:.1%}. "
                f"Its Sharpe ratio stands at {sharpe:.2f} with a historical maximum drawdown of {max_dd:.1%}. "
                f"In the optimized portfolio, it contributes {rc_pct:.1f}% to total portfolio risk, "
                f"serving as an effective {role.split('(')[0].strip().lower()} under the configured constraints."
            )

            explanations.append(
                StockExplanation(
                    stock=ticker,
                    weight_pct=round(weight * 100, 2),
                    allocation_rupees=round(rupee_alloc, 2),
                    annualized_return_pct=round(ann_ret * 100, 2),
                    annualized_volatility_pct=round(ann_vol * 100, 2),
                    sharpe_ratio=round(sharpe, 2),
                    max_drawdown_pct=round(max_dd * 100, 2),
                    risk_contribution_pct=round(rc_pct, 2),
                    diversification_score=div_score,
                    selection_reason=reason,
                    role_in_portfolio=role
                )
            )

        return explanations

    def explain_strategy_selection(
        self,
        selected_strategy: str,
        user_profile: Dict[str, str],
        strategies: Dict[str, PortfolioResult]
    ) -> str:
        """Explains why the selected optimization strategy was matched to the user's risk profile."""
        risk = user_profile.get("risk_appetite", "Moderate")
        horizon = user_profile.get("investment_horizon", "3–5 years")
        objective = user_profile.get("investment_objective", "Balanced Growth")

        sel_res = strategies.get(selected_strategy)
        min_res = strategies.get("Minimum Variance")
        max_s_res = strategies.get("Maximum Sharpe")
        mark_res = strategies.get("Markowitz Efficient")

        text = (
            f"Based on your profile — Risk Appetite: '{risk}', Horizon: '{horizon}', and Goal: '{objective}' — "
            f"the system selected the **{selected_strategy}** strategy.\n\n"
        )

        if selected_strategy == "Minimum Variance":
            text += (
                f"• **Why this model:** You prioritized capital preservation and low volatility. "
                f"Minimum Variance delivered the lowest historical volatility ({sel_res.annual_volatility:.1%}) "
                f"among all alternatives, spreading capital across {sel_res.stock_count} stocks to dampen market swings. "
                f"While its expected return ({sel_res.expected_annual_return:.1%}) is conservative, "
                f"it provides the smoothest equity curve under historical conditions."
            )
        elif selected_strategy == "Maximum Sharpe":
            text += (
                f"• **Why this model:** You selected a high-risk or long-term growth profile, where maximizing risk-adjusted "
                f"excess returns is paramount. Maximum Sharpe delivered the highest Sharpe Ratio ({sel_res.sharpe_ratio:.2f}) "
                f"with an expected annualized return of {sel_res.expected_annual_return:.1%} at a volatility of {sel_res.annual_volatility:.1%}. "
                f"This offers the optimal return per unit of total risk compared to the higher-volatility Markowitz solution "
                f"({mark_res.annual_volatility:.1%}) or conservative Minimum Variance ({min_res.annual_volatility:.1%})."
            )
        else:  # Markowitz Efficient
            text += (
                f"• **Why this model:** For a moderate risk appetite and balanced objective, the Markowitz Efficient solution "
                f"strikes an ideal equilibrium between growth and risk control. It generates an expected return of "
                f"{sel_res.expected_annual_return:.1%} with {sel_res.annual_volatility:.1%} volatility, providing higher upside "
                f"than Minimum Variance ({min_res.expected_annual_return:.1%}) without incurring unnecessary concentration risk."
            )

        return text
