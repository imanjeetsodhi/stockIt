"""API Client for interacting with the Stackit FastAPI backend with local fallback."""

from typing import Dict, List, Optional, Any
import httpx
from app.backend.core.config import settings
from app.backend.core.logging import logger

class APIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.API_BASE_URL).rstrip("/")
        self.timeout = 25.0

    def check_health(self) -> Dict[str, Any]:
        """Checks if backend API is responsive."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/health")
                if res.status_code == 200:
                    return {"online": True, **res.json().get("data", {})}
        except Exception:
            pass
        return {"online": False}

    def get_dataset_summary(self) -> Dict[str, Any]:
        """Fetches dataset summary metadata."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/api/dataset/summary")
                if res.status_code == 200:
                    return res.json().get("data", {})
        except Exception:
            pass
        # Fallback to direct service
        from app.backend.services.preprocessing import PreprocessingPipeline
        pipeline = PreprocessingPipeline()
        return pipeline.run_pipeline()

    def get_stocks(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetches list of all stocks with statistics."""
        params = {"search": search} if search else {}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/api/dataset/stocks", params=params)
                if res.status_code == 200:
                    return res.json().get("data", [])
        except Exception:
            pass
        from app.backend.services.portfolio_service import PortfolioService
        ps = PortfolioService()
        ps.ensure_data_loaded()
        df = ps.stock_statistics.reset_index()
        if search:
            df = df[df["Stock"].str.contains(search.strip().upper())]
        return [
            {
                "stock": row["Stock"],
                "annualized_return": round(float(row["Annualized_Return"]), 4),
                "cagr": round(float(row["CAGR"]), 4),
                "annualized_volatility": round(float(row["Annualized_Volatility"]), 4),
                "maximum_drawdown": round(float(row["Maximum_Drawdown"]), 4),
                "sharpe_ratio": round(float(row["Sharpe_Ratio"]), 2),
                "average_daily_volume": round(float(row["Average_Daily_Volume"]), 0),
                "latest_price": round(float(row["Latest_Price"]), 2),
                "total_observations": int(row["Total_Observations"])
            }
            for _, row in df.iterrows()
        ]

    def get_stock_detail(self, ticker: str) -> Dict[str, Any]:
        """Fetches detail and historical series for a single stock."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/api/dataset/stocks/{ticker}")
                if res.status_code == 200:
                    return res.json().get("data", {})
        except Exception:
            pass
        from app.backend.services.portfolio_service import PortfolioService
        ps = PortfolioService()
        ps.ensure_data_loaded()
        t = ticker.strip().upper()
        row = ps.stock_statistics.loc[t]
        prices = ps.prices[t]
        returns = ps.daily_returns[t]
        history = [
            {"date": d.strftime("%Y-%m-%d"), "adj_close": round(float(p), 2), "daily_return": round(float(returns.get(d, 0.0)), 4)}
            for d, p in prices.items()
        ]
        return {
            "stock": t,
            "metrics": {
                "stock": t,
                "annualized_return": round(float(row["Annualized_Return"]), 4),
                "annualized_volatility": round(float(row["Annualized_Volatility"]), 4),
                "sharpe_ratio": round(float(row["Sharpe_Ratio"]), 2),
                "maximum_drawdown": round(float(row["Maximum_Drawdown"]), 4),
                "latest_price": round(float(row["Latest_Price"]), 2)
            },
            "history": history
        }

    def get_correlation_matrix(self, stocks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetches correlation matrix."""
        params = {"stocks": ",".join(stocks)} if stocks else {}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/api/dataset/correlation", params=params)
                if res.status_code == 200:
                    return res.json().get("data", {})
        except Exception:
            pass
        from app.backend.services.portfolio_service import PortfolioService
        ps = PortfolioService()
        corr = ps.correlation_matrix
        if stocks:
            valid = [s for s in stocks if s in corr.columns]
            if valid:
                corr = corr.loc[valid, valid]
        return {
            "tickers": list(corr.columns),
            "matrix": [[round(float(v), 4) for v in row] for row in corr.values]
        }

    def recommend_portfolio(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calls recommendation endpoint."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/api/portfolio/recommend", json=payload)
                if res.status_code == 200:
                    return res.json().get("data", {})
        except Exception:
            pass
        from app.backend.services.recommendation_service import RecommendationService
        rec_service = RecommendationService()
        rec_out = rec_service.generate_recommendation(
            investment_amount=float(payload.get("investment_amount", 100000.0)),
            risk_appetite=payload.get("risk_appetite", "Moderate"),
            investment_horizon=payload.get("investment_horizon", "3–5 years"),
            investment_objective=payload.get("investment_objective", "Balanced Growth"),
            max_stock_weight=float(payload.get("max_stock_weight", 0.20)),
            risk_free_rate=payload.get("risk_free_rate")
        )
        return rec_out.model_dump()

    def compare_strategies(self, max_weight: float = 0.20) -> Dict[str, Any]:
        """Fetches side-by-side comparison of all 3 strategies."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/api/portfolio/compare", params={"max_weight": max_weight})
                if res.status_code == 200:
                    return res.json().get("data", {})
        except Exception:
            pass
        from app.backend.services.portfolio_service import PortfolioService
        ps = PortfolioService()
        strats = ps.run_all_strategies(max_weight=max_weight)
        return {k: v.model_dump() for k, v in strats.items()}

    def run_backtest(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calls out-of-sample backtesting endpoint."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/api/backtesting/run", json=payload)
                if res.status_code == 200:
                    return res.json().get("data", {})
        except Exception:
            pass
        from app.backend.services.portfolio_service import PortfolioService
        from app.backend.services.backtesting_service import BacktestService
        ps = PortfolioService()
        ps.ensure_data_loaded()
        bt = BacktestService(ps.prices, ps.daily_returns, ps.risk_free_rate)
        return bt.run_out_of_sample_backtest(
            split_date=payload.get("split_date"),
            train_ratio=float(payload.get("train_ratio", 0.70)),
            transaction_cost_pct=float(payload.get("transaction_cost_pct", 0.001)),
            max_stock_weight=float(payload.get("max_stock_weight", 0.20))
        )

api_client = APIClient()
