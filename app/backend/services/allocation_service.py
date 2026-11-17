"""Rupee allocation engine for converting portfolio weights into whole-share orders."""

import math
from typing import Dict, List, Optional
import pandas as pd

from app.backend.core.logging import logger
from app.backend.models.portfolio import RupeeAllocationSummary, WholeShareAllocationItem

class AllocationService:
    def __init__(self, stock_statistics: pd.DataFrame):
        self.stats = stock_statistics

    def allocate_rupees(
        self,
        total_amount: float,
        allocations: Dict[str, float],
        marginal_risk_contributions: Optional[Dict[str, float]] = None
    ) -> RupeeAllocationSummary:
        """Calculates executable whole-share stock allocations and residual cash.
        
        Args:
            total_amount: Total investment budget in INR (e.g., 100,000)
            allocations: Dict of {ticker: target_weight} summing to ~1.0
            marginal_risk_contributions: Optional map of risk contribution per stock
            
        Returns:
            RupeeAllocationSummary with holding items and residual cash.
        """
        if total_amount <= 0:
            raise ValueError("Total investment amount must be positive")

        items: List[WholeShareAllocationItem] = []
        total_actual_invested = 0.0

        for ticker, target_w in sorted(allocations.items(), key=lambda x: x[1], reverse=True):
            if target_w <= 0:
                continue

            target_investment = total_amount * target_w

            latest_price = 0.0
            ann_ret = None
            ann_vol = None

            if ticker in self.stats.index:
                row = self.stats.loc[ticker]
                latest_price = float(row["Latest_Price"])
                ann_ret = float(row["Annualized_Return"])
                ann_vol = float(row["Annualized_Volatility"])

            if latest_price <= 0:
                logger.warning(f"Stock {ticker} has invalid latest price: {latest_price}")
                latest_price = 1.0  # Fallback

            # Calculate executable whole shares
            shares = int(target_investment // latest_price)
            actual_investment = shares * latest_price
            total_actual_invested += actual_investment

            rc = marginal_risk_contributions.get(ticker) if marginal_risk_contributions else None

            items.append(
                WholeShareAllocationItem(
                    stock=ticker,
                    target_weight=round(target_w, 4),
                    target_investment=round(target_investment, 2),
                    latest_price=round(latest_price, 2),
                    shares=shares,
                    actual_investment=round(actual_investment, 2),
                    actual_weight=0.0,  # Computed below
                    risk_contribution_pct=round(rc * 100, 2) if rc is not None else None,
                    annualized_return=round(ann_ret, 4) if ann_ret is not None else None,
                    annualized_volatility=round(ann_vol, 4) if ann_vol is not None else None
                )
            )

        # Compute actual weight based on total_budget
        for item in items:
            item.actual_weight = round(item.actual_investment / total_amount, 4) if total_amount > 0 else 0.0

        unallocated_cash = round(total_amount - total_actual_invested, 2)
        cash_drag_pct = round((unallocated_cash / total_amount) * 100, 2) if total_amount > 0 else 0.0

        return RupeeAllocationSummary(
            total_budget=round(total_amount, 2),
            allocated_amount=round(total_actual_invested, 2),
            unallocated_cash=unallocated_cash,
            cash_drag_pct=cash_drag_pct,
            holdings=items
        )
