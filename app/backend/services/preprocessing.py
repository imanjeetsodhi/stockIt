"""Data preprocessing and alignment pipeline."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.core.exceptions import DataPreprocessingError
from app.backend.services.data_loader import DataLoader
from app.backend.services.feature_engineering import FeatureEngineeringService
from app.backend.utils.calculations import calculate_daily_returns

class PreprocessingPipeline:
    def __init__(
        self,
        raw_dir: Optional[Path] = None,
        processed_dir: Optional[Path] = None,
        reports_dir: Optional[Path] = None,
        risk_free_rate: float = settings.RISK_FREE_RATE,
        trading_days: int = settings.TRADING_DAYS_PER_YEAR
    ):
        self.raw_dir = Path(raw_dir) if raw_dir else settings.RAW_DATA_DIR
        self.processed_dir = Path(processed_dir) if processed_dir else settings.PROCESSED_DATA_DIR
        self.reports_dir = Path(reports_dir) if reports_dir else settings.REPORTS_DIR
        self.risk_free_rate = risk_free_rate
        self.trading_days = trading_days

        self.loader = DataLoader(self.raw_dir)
        self.feature_service = FeatureEngineeringService(self.trading_days, self.risk_free_rate)

    def run_pipeline(self, align_method: str = "intersection") -> Dict[str, Any]:
        """Executes full preprocessing and feature generation pipeline.
        
        Args:
            align_method: 'intersection' to keep all stocks with common dates,
                          or 'drop_short_history' to keep longest period stocks.
                          
        Returns:
            Dictionary summary of preprocessing results.
        """
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Starting preprocessing pipeline...")

        # 1. Load raw data
        valid_stocks, valid_reports, rejected_reports = self.loader.load_all_stocks()
        if not valid_stocks:
            raise DataPreprocessingError("No valid stock datasets found to process")

        # 2. Combine all raw valid data
        combined_dfs = []
        for ticker, df in valid_stocks.items():
            combined_dfs.append(df)
        combined_df = pd.concat(combined_dfs, ignore_index=True)
        combined_df = combined_df.sort_values(by=["Stock", "Date"]).reset_index(drop=True)
        
        combined_path = self.processed_dir / "combined_stock_data.csv"
        combined_df.to_csv(combined_path, index=False)
        logger.info(f"Saved combined stock data to {combined_path} ({len(combined_df)} rows)")

        # 3. Pivot Adjusted Close prices
        prices_df = combined_df.pivot(index="Date", columns="Stock", values="Adj Close")
        prices_df.index = pd.to_datetime(prices_df.index)
        prices_df = prices_df.sort_index()

        volume_df = combined_df.pivot(index="Date", columns="Stock", values="Volume")
        volume_df.index = pd.to_datetime(volume_df.index)
        volume_df = volume_df.sort_index()

        # 4. Alignment & Date Filtering
        earliest_date_overall = prices_df.index.min().strftime("%Y-%m-%d")
        latest_date_overall = prices_df.index.max().strftime("%Y-%m-%d")

        # Find date intersection
        # Clean stocks by removing dates where any stock in the included universe is NaN
        aligned_prices = prices_df.dropna()
        excluded_stocks: List[Dict[str, str]] = []

        # If aligned_prices has too few rows (< 252 days), we can investigate outliers
        if len(aligned_prices) < 252 and len(prices_df.columns) > 1:
            # Check if one or two stocks severely restrict the date range
            coverage_ratios = prices_df.count() / len(prices_df)
            short_coverage = coverage_ratios[coverage_ratios < settings.MIN_COMMON_HISTORY_RATIO]
            if not short_coverage.empty:
                for ticker, cov in short_coverage.items():
                    excluded_stocks.append({
                        "ticker": ticker,
                        "reason": f"Insufficient historical coverage: {cov:.1%} of overall dates"
                    })
                clean_tickers = [t for t in prices_df.columns if t not in short_coverage.index]
                aligned_prices = prices_df[clean_tickers].dropna()
                volume_df = volume_df[clean_tickers]

        # Calculate daily returns
        returns_df = calculate_daily_returns(aligned_prices)
        returns_df = returns_df.dropna()

        # 5. Save prices and returns
        prices_path = self.processed_dir / "adjusted_close_prices.csv"
        aligned_prices.to_csv(prices_path)

        returns_path = self.processed_dir / "daily_returns.csv"
        returns_df.to_csv(returns_path)

        # 6. Financial Feature Engineering
        stats_df = self.feature_service.compute_stock_statistics(
            prices_df=aligned_prices,
            returns_df=returns_df,
            volume_df=volume_df
        )
        stats_path = self.processed_dir / "stock_statistics.csv"
        stats_df.to_csv(stats_path)

        # 7. Covariance and Correlation Matrices
        cov_matrix, corr_matrix = self.feature_service.compute_covariance_and_correlation(returns_df)
        cov_path = self.processed_dir / "covariance_matrix.csv"
        cov_matrix.to_csv(cov_path)

        corr_path = self.processed_dir / "correlation_matrix.csv"
        corr_matrix.to_csv(corr_path)

        # 8. Data Quality & Ingestion Summary
        summary = {
            "discovered_files": len(valid_reports) + len(rejected_reports),
            "valid_stocks_count": len(valid_stocks),
            "included_in_optimization": len(aligned_prices.columns),
            "rejected_files_count": len(rejected_reports),
            "rejected_files": rejected_reports,
            "excluded_stocks": excluded_stocks,
            "overall_earliest_date": earliest_date_overall,
            "overall_latest_date": latest_date_overall,
            "aligned_earliest_date": aligned_prices.index.min().strftime("%Y-%m-%d"),
            "aligned_latest_date": aligned_prices.index.max().strftime("%Y-%m-%d"),
            "total_common_trading_days": int(len(aligned_prices)),
            "total_return_observations": int(len(returns_df)),
            "trading_days_per_year": self.trading_days,
            "risk_free_rate": self.risk_free_rate,
            "generated_files": [
                str(combined_path.name),
                str(prices_path.name),
                str(returns_path.name),
                str(stats_path.name),
                str(cov_path.name),
                str(corr_path.name)
            ]
        }

        # Save JSON & CSV reports
        json_report_path = self.reports_dir / "data_quality_report.json"
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)

        report_df = pd.DataFrame(valid_reports)
        csv_report_path = self.reports_dir / "data_quality_report.csv"
        report_df.to_csv(csv_report_path, index=False)

        logger.info(f"Preprocessing completed successfully. Processed {len(aligned_prices.columns)} stocks over {len(aligned_prices)} trading days.")
        return summary
