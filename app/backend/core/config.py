"""Centralized application configuration management."""

import os
from pathlib import Path
from typing import Any, Dict
import yaml

# Project Root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

SETTINGS_PATH = BASE_DIR / "config" / "settings.yaml"

def load_yaml_config() -> Dict[str, Any]:
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

_config = load_yaml_config()

class Settings:
    PROJECT_NAME: str = _config.get("app", {}).get("name", "Stackit")
    VERSION: str = _config.get("app", {}).get("version", "1.0.0")
    DESCRIPTION: str = _config.get("app", {}).get("description", "Portfolio Optimization System")

    # Server settings
    HOST: str = os.getenv("API_HOST", _config.get("server", {}).get("host", "127.0.0.1"))
    PORT: int = int(os.getenv("API_PORT", _config.get("server", {}).get("port", 8000)))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", _config.get("frontend", {}).get("port", 8501)))
    API_BASE_URL: str = os.getenv("API_BASE_URL", _config.get("frontend", {}).get("api_base_url", "http://127.0.0.1:8000"))

    # Financial defaults
    RISK_FREE_RATE: float = float(os.getenv("RISK_FREE_RATE", _config.get("financial", {}).get("risk_free_rate", 0.065)))
    TRADING_DAYS_PER_YEAR: int = int(os.getenv("TRADING_DAYS_PER_YEAR", _config.get("financial", {}).get("trading_days_per_year", 252)))
    MAX_STOCK_WEIGHT: float = float(os.getenv("MAX_STOCK_WEIGHT", _config.get("financial", {}).get("max_stock_weight", 0.20)))
    MIN_STOCK_WEIGHT: float = float(os.getenv("MIN_STOCK_WEIGHT", _config.get("financial", {}).get("min_stock_weight", 0.0)))
    WEIGHT_THRESHOLD: float = float(_config.get("financial", {}).get("weight_threshold", 0.0001))
    MIN_COMMON_HISTORY_RATIO: float = float(_config.get("financial", {}).get("min_common_history_ratio", 0.80))

    # Directories
    BASE_DIR: Path = BASE_DIR
    RAW_DATA_DIR: Path = BASE_DIR / _config.get("data", {}).get("raw_dir", "data/raw")
    PROCESSED_DATA_DIR: Path = BASE_DIR / _config.get("data", {}).get("processed_dir", "data/processed")
    REPORTS_DIR: Path = BASE_DIR / _config.get("data", {}).get("reports_dir", "data/reports")
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", _config.get("logging", {}).get("level", "INFO"))
    LOG_FILE: Path = BASE_DIR / _config.get("logging", {}).get("log_file", "logs/stackit.log")

settings = Settings()
