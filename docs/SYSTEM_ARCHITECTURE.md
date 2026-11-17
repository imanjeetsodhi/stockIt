# Stackit: System Architecture

## 1. Architectural Principles
Stackit follows a strict separation of concerns, ensuring high cohesion, modularity, and clean testability:

- **Frontend (Streamlit):** Minimal, professional dark-first UI with Plotly charts. Contains zero business or optimization logic. Communicates with the backend via REST API or local service fallback.
- **Backend (FastAPI):** High-performance asynchronous REST API powered by Pydantic schema validation.
- **Optimization Layer:** Pure mathematical classes deriving from `BaseOptimizer`, decoupling solvers from web frameworks.
- **Data Ingestion & Feature Engineering:** Reproducible ETL pipeline taking raw CSV files and outputting clean matrices.

```
                          ┌────────────────────────┐
                          │   Streamlit Frontend   │
                          │   (app/frontend/)      │
                          └───────────┬────────────┘
                                      │ HTTP / Direct
                                      ▼
                          ┌────────────────────────┐
                          │     FastAPI Backend    │
                          │     (app/backend/)     │
                          └───────────┬────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Portfolio Service│        │ Alloc / Explains │        │ Backtest Service │
│ (Optimizers)     │        │ Services         │        │ (Out-of-sample)  │
└─────────┬────────┘        └─────────┬────────┘        └─────────┬────────┘
          └───────────────────────────┼───────────────────────────┘
                                      ▼
                        ┌──────────────────────────┐
                        │   Feature Engineering    │
                        │   & Aligned Matrices     │
                        └─────────────┬────────────┘
                                      ▼
                        ┌──────────────────────────┐
                        │   Raw NIFTY 50 CSVs      │
                        │   (data/raw/)            │
                        └──────────────────────────┘
```

---

## 2. Component Breakdown

### A. Data Layer (`app/backend/services/`)
- `DataLoader`: Reads raw CSVs, enforces positive price checks, sanitizes columns, removes duplicate dates.
- `PreprocessingPipeline`: Inner-joins on common trading dates across constituents, producing aligned matrices.
- `FeatureEngineeringService`: Calculates annualized return, annualized volatility, Sharpe ratio, covariance, and correlation matrices.

### B. Mathematical Optimization (`app/backend/optimization/`)
- `BaseOptimizer`: Abstract class enforcing common constraints ($\sum w_i = 1$, $0 \le w_i \le w_{\max}$), weight cleaning, and marginal risk contribution calculations.
- `MinimumVarianceOptimizer`: Minimizes $\mathbf{w}^T \mathbf{\Sigma} \mathbf{w}$.
- `MarkowitzOptimizer`: Solves quadratic utility and traces the Efficient Frontier.
- `MaximumSharpeOptimizer`: Solves for the tangency portfolio maximizing excess return over risk-free rate.

### C. Execution & Explanation Layer
- `AllocationService`: Integer floor allocation and cash drag analysis.
- `ExplanationService`: Generates deterministic per-stock explanations.
- `RecommendationService`: Evaluates investor profiles and selects optimal strategies.

### D. Out-of-Sample Backtesting (`BacktestService`)
- Chronological train/test split.
- Transaction friction simulation (10 bps).
- Comparison against equal-weighted benchmark.
