# Stackit: API Documentation

The Stackit FastAPI backend runs on `http://127.0.0.1:8000`.
Interactive Swagger UI is accessible at `/docs` and ReDoc at `/redoc`.

---

## 1. System Health
### `GET /api/health`
Returns system status, active version, and preprocessing pipeline state.

**Response:**
```json
{
  "success": true,
  "message": "Stackit API is running healthy",
  "data": {
    "app_name": "Stackit",
    "version": "1.0.0",
    "processed_data_ready": true,
    "risk_free_rate": 0.065,
    "trading_days": 252
  }
}
```

---

## 2. Dataset Endpoints
### `GET /api/dataset/summary`
Returns dataset ingestion counts, date ranges, and quality report.

### `GET /api/dataset/stocks`
Returns list of all analyzed stocks with computed statistics.
- **Query Params:** `search` (optional string filter).

### `GET /api/dataset/stocks/{ticker}`
Returns detailed time series and summary metrics for a specific stock.

### `GET /api/dataset/correlation`
Returns Pearson correlation matrix.
- **Query Params:** `stocks` (optional comma-separated list of symbols).

### `POST /api/dataset/reload`
Forces complete regeneration of preprocessed matrices from raw CSVs.

---

## 3. Portfolio Optimization Endpoints
### `POST /api/portfolio/recommend`
Generates a complete portfolio recommendation matched to an investor profile.

**Request Body:**
```json
{
  "investment_amount": 100000.0,
  "risk_appetite": "Moderate",
  "investment_horizon": "3–5 years",
  "investment_objective": "Balanced Growth",
  "max_stock_weight": 0.20,
  "risk_free_rate": 0.065
}
```

**Response Data Structure:**
- `selected_strategy`: Name of chosen model.
- `selection_rationale`: Grounded explanation text.
- `recommended_portfolio`: PortfolioResult (expected return, volatility, Sharpe, allocations).
- `rupee_allocation`: Whole-share order breakdown, actual invested, and unallocated cash.
- `explanations`: List of per-stock qualitative and quantitative justification cards.
- `all_strategies`: Dictionary containing results for all three models for side-by-side comparison.
- `efficient_frontier`: List of points tracing the Markowitz curve.

### `POST /api/portfolio/optimize`
Runs a standalone optimization technique (`Minimum Variance`, `Markowitz Efficient`, or `Maximum Sharpe`).

### `GET /api/portfolio/compare`
Runs all 3 strategies under identical parameters.
- **Query Params:** `max_weight` (default `0.20`), `risk_free_rate` (default `0.065`).

### `GET /api/portfolio/frontier`
Traces the Efficient Frontier curve.
- **Query Params:** `max_weight` (default `0.20`), `points` (default `35`).

---

## 4. Backtesting Endpoints
### `POST /api/backtesting/run`
Executes an out-of-sample chronological backtest.

**Request Body:**
```json
{
  "train_ratio": 0.70,
  "transaction_cost_pct": 0.001,
  "max_stock_weight": 0.20
}
```
