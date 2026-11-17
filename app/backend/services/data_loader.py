"""Data loader service for discovering and validating raw CSV stock files."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.core.exceptions import DataIngestionError

REQUIRED_COLUMNS = ["Stock", "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]

class DataLoader:
    def __init__(self, raw_dir: Optional[Path] = None):
        self.raw_dir = Path(raw_dir) if raw_dir else settings.RAW_DATA_DIR

    def discover_csv_files(self) -> List[Path]:
        """Discovers all .csv files in the raw directory."""
        if not self.raw_dir.exists():
            logger.error(f"Raw data directory does not exist: {self.raw_dir}")
            raise DataIngestionError(f"Raw data directory not found: {self.raw_dir}")
        files = sorted(list(self.raw_dir.glob("*.csv")))
        logger.info(f"Discovered {len(files)} CSV files in {self.raw_dir}")
        return files

    def load_single_csv(self, file_path: Path) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
        """Loads and validates a single stock CSV file.
        
        Returns:
            Tuple of (cleaned_df, quality_metrics_dict).
            If invalid/rejected, cleaned_df is None.
        """
        file_name = file_path.name
        ticker_guess = file_path.stem

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return None, {
                "file": file_name,
                "ticker": ticker_guess,
                "status": "rejected",
                "reason": f"File read error: {str(e)}"
            }

        if df.empty:
            return None, {
                "file": file_name,
                "ticker": ticker_guess,
                "status": "rejected",
                "reason": "File is empty"
            }

        # Check column presence
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing_cols:
            # Check if Close is available when Adj Close is missing
            if "Adj Close" in missing_cols and "Close" in df.columns:
                logger.warning(f"File {file_name} missing 'Adj Close', falling back to 'Close'")
                df["Adj Close"] = df["Close"]
                missing_cols.remove("Adj Close")
            
            if missing_cols:
                return None, {
                    "file": file_name,
                    "ticker": ticker_guess,
                    "status": "rejected",
                    "reason": f"Missing required columns: {missing_cols}"
                }

        initial_rows = len(df)

        # Parse Date
        try:
            df["Date"] = pd.to_datetime(df["Date"])
        except Exception as e:
            return None, {
                "file": file_name,
                "ticker": ticker_guess,
                "status": "rejected",
                "reason": f"Failed to parse Date column: {str(e)}"
            }

        # Deduplicate on Date
        duplicates_count = int(df.duplicated(subset=["Date"]).sum())
        if duplicates_count > 0:
            logger.info(f"{file_name}: removing {duplicates_count} duplicate date rows")
            df = df.drop_duplicates(subset=["Date"], keep="first")

        # Sort chronologically
        df = df.sort_values(by="Date").reset_index(drop=True)

        # Ensure numeric financial columns
        numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Sanity validation
        null_adj = int(df["Adj Close"].isna().sum())
        non_positive_adj = int((df["Adj Close"] <= 0).sum())
        invalid_spread = int((df["High"] < df["Low"]).sum())

        # Drop rows where Adj Close is NaN or non-positive
        if null_adj > 0 or non_positive_adj > 0:
            df = df[df["Adj Close"] > 0].reset_index(drop=True)

        if len(df) == 0:
            return None, {
                "file": file_name,
                "ticker": ticker_guess,
                "status": "rejected",
                "reason": "No valid positive price rows remain after cleaning"
            }

        ticker = str(df["Stock"].iloc[0]).strip() if "Stock" in df.columns else ticker_guess
        df["Stock"] = ticker

        quality = {
            "file": file_name,
            "ticker": ticker,
            "status": "valid",
            "initial_rows": initial_rows,
            "valid_rows": len(df),
            "duplicates_removed": duplicates_count,
            "null_adj_close": null_adj,
            "non_positive_prices": non_positive_adj,
            "invalid_spreads": invalid_spread,
            "min_date": df["Date"].min().strftime("%Y-%m-%d"),
            "max_date": df["Date"].max().strftime("%Y-%m-%d"),
            "latest_adj_close": float(df["Adj Close"].iloc[-1]),
            "avg_volume": float(df["Volume"].mean())
        }

        return df, quality

    def load_all_stocks(self) -> Tuple[Dict[str, pd.DataFrame], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Loads and validates all CSV files in the raw data directory.
        
        Returns:
            Tuple of:
            - dict of {ticker: clean_df}
            - list of valid quality reports
            - list of rejected quality reports
        """
        files = self.discover_csv_files()
        valid_stocks: Dict[str, pd.DataFrame] = {}
        valid_reports: List[Dict[str, Any]] = []
        rejected_reports: List[Dict[str, Any]] = []

        for f in files:
            df, report = self.load_single_csv(f)
            if df is not None and report["status"] == "valid":
                ticker = report["ticker"]
                valid_stocks[ticker] = df
                valid_reports.append(report)
            else:
                rejected_reports.append(report)

        logger.info(
            f"Data loading complete: {len(valid_stocks)} valid stocks, "
            f"{len(rejected_reports)} rejected files."
        )
        return valid_stocks, valid_reports, rejected_reports
