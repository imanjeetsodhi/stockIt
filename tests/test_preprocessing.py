"""Tests for preprocessing pipeline."""

import pytest
from app.backend.services.preprocessing import PreprocessingPipeline
from app.backend.core.config import settings

def test_preprocessing_pipeline_execution():
    pipeline = PreprocessingPipeline()
    summary = pipeline.run_pipeline()

    assert summary["valid_stocks_count"] == 50
    assert summary["included_in_optimization"] == 50
    assert summary["total_common_trading_days"] == 763
    assert (settings.PROCESSED_DATA_DIR / "combined_stock_data.csv").exists()
    assert (settings.PROCESSED_DATA_DIR / "adjusted_close_prices.csv").exists()
    assert (settings.PROCESSED_DATA_DIR / "daily_returns.csv").exists()
    assert (settings.PROCESSED_DATA_DIR / "stock_statistics.csv").exists()
    assert (settings.PROCESSED_DATA_DIR / "covariance_matrix.csv").exists()
    assert (settings.PROCESSED_DATA_DIR / "correlation_matrix.csv").exists()
