"""Health and system status routes."""

from fastapi import APIRouter
from app.backend.core.config import settings
from app.backend.api.schemas.response_schema import StandardResponse

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=StandardResponse[dict])
def check_health():
    """Returns application health status, version, and data directories."""
    data_ready = (settings.PROCESSED_DATA_DIR / "stock_statistics.csv").exists()
    return StandardResponse(
        success=True,
        message="Stackit API is running healthy",
        data={
            "app_name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "processed_data_ready": data_ready,
            "risk_free_rate": settings.RISK_FREE_RATE,
            "trading_days": settings.TRADING_DAYS_PER_YEAR
        }
    )
