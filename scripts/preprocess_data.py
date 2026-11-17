"""Script to preprocess raw CSV data into clean matrices and statistical reports."""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.backend.services.preprocessing import PreprocessingPipeline
from app.backend.core.logging import logger

def main():
    print("\n" + "=" * 55)
    print("      STACKIT: DATA PREPROCESSING PIPELINE")
    print("=" * 55 + "\n")

    pipeline = PreprocessingPipeline()
    try:
        summary = pipeline.run_pipeline()
        print(f"Discovered stock files      : {summary['discovered_files']}")
        print(f"Valid stocks count          : {summary['valid_stocks_count']}")
        print(f"Stocks used in optimization : {summary['included_in_optimization']}")
        print(f"Rejected files count        : {summary['rejected_files_count']}")
        print(f"Aligned date range          : {summary['aligned_earliest_date']} to {summary['aligned_latest_date']}")
        print(f"Total common trading days   : {summary['total_common_trading_days']}")
        print(f"Risk-free rate              : {summary['risk_free_rate']:.2%}")
        print("\nGenerated files in data/processed/ and data/reports/:")
        for fn in summary['generated_files']:
            print(f"  - {fn}")
        print("\nPreprocessed pipeline completed successfully!\n")
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}", exc_info=True)
        print(f"\nPreprocessing failed: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
