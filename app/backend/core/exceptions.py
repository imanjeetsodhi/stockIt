"""Custom application exceptions."""

class StackitException(Exception):
    """Base exception for Stackit."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class DataIngestionError(StackitException):
    """Raised when data ingestion or reading fails."""
    pass

class DataPreprocessingError(StackitException):
    """Raised when data cleaning or alignment fails."""
    pass

class FinancialCalculationError(StackitException):
    """Raised when financial statistics cannot be computed."""
    pass

class OptimizationError(StackitException):
    """Raised when portfolio optimization fails or is infeasible."""
    pass

class InfeasibleConstraintsError(OptimizationError):
    """Raised when optimization constraints cannot be satisfied."""
    pass

class BacktestingError(StackitException):
    """Raised when backtesting encounters an error."""
    pass
