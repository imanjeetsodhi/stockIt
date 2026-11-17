"""FastAPI main application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.backend.core.config import settings
from app.backend.core.logging import logger
from app.backend.core.exceptions import StackitException
from app.backend.api.routes import health, dataset, portfolio, backtesting

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Quantitative Financial Portfolio Optimization & Investment Recommendation System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging & timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time-Sec"] = f"{process_time:.4f}"
        return response
    except Exception as exc:
        process_time = time.time() - start_time
        logger.error(f"Unhandled error in {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error occurred",
                "error": str(exc),
                "path": request.url.path
            }
        )

# Global custom exception handler
@app.exception_handler(StackitException)
async def stackit_exception_handler(request: Request, exc: StackitException):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(dataset.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(backtesting.router, prefix="/api")

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
