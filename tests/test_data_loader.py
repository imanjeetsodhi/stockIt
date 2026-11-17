"""Tests for data loader service."""

import pytest
from pathlib import Path
import pandas as pd
from app.backend.services.data_loader import DataLoader

def test_data_loader_discovery():
    loader = DataLoader()
    files = loader.discover_csv_files()
    assert len(files) == 50, f"Expected 50 CSV files, found {len(files)}"

def test_load_single_valid_csv():
    loader = DataLoader()
    files = loader.discover_csv_files()
    first_file = files[0]
    df, quality = loader.load_single_csv(first_file)

    assert df is not None
    assert quality["status"] == "valid"
    assert "Date" in df.columns
    assert "Adj Close" in df.columns
    assert len(df) > 700
    assert (df["Adj Close"] > 0).all()

def test_load_all_stocks():
    loader = DataLoader()
    valid_stocks, valid_reports, rejected_reports = loader.load_all_stocks()
    assert len(valid_stocks) == 50
    assert len(rejected_reports) == 0
    assert len(valid_reports) == 50
