# Stackit — Quantitative Portfolio Optimization & Investment Recommendation System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B.svg)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/tests-21%20passed-brightgreen.svg)]()

> A robust, mathematically defensible, Python-only financial engineering and portfolio decision-support system built using historical NIFTY 50 stock market data.

---

## 1. Project Introduction & Problem Statement
In Indian equity markets, retail and institutional participants often struggle with heuristic capital allocation, arbitrary diversification, and opaque "black-box" advisory tools. Traditional stock picking ignores inter-asset covariance and concentration risk, leading to suboptimal risk-adjusted performance. Furthermore, existing theoretical calculators frequently output fractional shares (e.g. 14.37 shares), which cannot be directly executed in Indian depository accounts (CDSL/NSDL).

**Stackit** solves this problem by providing an end-to-end, mathematically defensible portfolio engineering system. It cleans and aligns historical daily observations from NIFTY 50 equities, solves three core Modern Portfolio Theory optimization techniques, translates theoretical weights into actionable whole-share rupee allocations, and provides deterministic, metric-grounded explanations for every stock selection.

---

## 2. Project Objectives
- **Data Integrity:** Ingest and validate actual CSV market datasets across 50 NIFTY constituents over 760+ trading days without fabricating or interpolating missing points.
- **Three Quantitative Optimization Techniques:** Implement independent, reproducible mathematical optimizers:
  1. **Markowitz Mean-Variance Optimization**
  2. **Minimum Variance Portfolio**
  3. **Maximum Sharpe Ratio Portfolio**
- **Actionable Rupee Allocations:** Convert mathematical percentage weights into whole-share integer order quantities in Indian Rupees (₹), explicitly tracking residual cash drag.
- **Explainable Decisions:** Generate deterministic, metric-driven rationale for each selected asset based on historical return, volatility, drawdown, and marginal risk contribution.
- **Out-of-Sample Backtesting:** Chronologically evaluate model performance on held-out historical data without look-ahead bias.
- **Pure Python Architecture:** Build a modular system with a FastAPI REST backend and a dark-first Streamlit frontend.

---

## 3. Technology Stack
- **Language:** Python 3.9+
- **Frontend:** Streamlit, Custom Dark CSS, Plotly Interactive Visualizations
- **Backend API:** FastAPI, Pydantic v2, Uvicorn
- **Financial & Quantitative Optimization:** SciPy (SLSQP), PyPortfolioOpt, NumPy, Pandas
- **Testing:** Pytest, Starlette / HTTPX TestClient
- **Configuration:** PyYAML, Environment Variables

---

## 4. The Three Optimization Techniques

### A. Minimum Variance Portfolio
- **Objective:** Minimize total portfolio variance: $\min_{\mathbf{w}} \mathbf{w}^T \mathbf{\Sigma} \mathbf{w}$
- **Constraints:** $\sum_{i=1}^N w_i = 1$, $0 \le w_i \le w_{\max}$ (default 20% limit).
- **Profile Fit:** Capital preservation, low volatility tolerance.

### B. Markowitz Mean-Variance Optimization
- **Objective:** Maximize quadratic utility: $\max_{\mathbf{w}} \left(\mathbf{w}^T \mathbf{\mu} - \frac{\lambda}{2} \mathbf{w}^T \mathbf{\Sigma} \mathbf{w}\right)$
- **Constraints:** $\sum_{i=1}^N w_i = 1$, $0 \le w_i \le w_{\max}$.
- **Profile Fit:** Balanced growth, moderate risk appetite. Traces the Markowitz Efficient Frontier.

### C. Maximum Sharpe Ratio Portfolio (Tangency Portfolio)
- **Objective:** Maximize excess return per unit of volatility: $\max_{\mathbf{w}} \frac{\mathbf{w}^T \mathbf{\mu} - R_f}{\sqrt{\mathbf{w}^T \mathbf{\Sigma} \mathbf{w}}}$
- **Constraints:** $\sum_{i=1}^N w_i = 1$, $0 \le w_i \le w_{\max}$.
- **Profile Fit:** Growth / wealth creation, optimal risk-adjusted performance.

---

## 5. Folder Structure

```text
stockIt/
├── app/
│   ├── frontend/
│   │   ├── main.py                          # Streamlit application entrypoint
│   │   ├── pages/
│   │   │   ├── 01_Home.py                   # Dataset summary & overview
│   │   │   ├── 02_Dataset_Explorer.py       # Stock metrics & correlation heatmap
│   │   │   ├── 03_Portfolio_Builder.py      # Profile input & optimizer trigger
│   │   │   ├── 04_Portfolio_Results.py      # Allocations, charts & stock explanations
│   │   │   ├── 05_Strategy_Comparison.py    # Side-by-side comparison & backtests
│   │   │   └── 06_Methodology.py            # Mathematical foundations & formulas
│   │   ├── components/                      # Reusable UI widgets (metrics, charts, cards)
│   │   ├── styles/theme.css                 # Dark-first minimalist financial styling
│   │   └── utils/api_client.py              # Backend client with local fallback
│   ├── backend/
│   │   ├── main.py                          # FastAPI REST application
│   │   ├── api/routes/                      # Endpoints: health, dataset, portfolio, backtesting
│   │   ├── api/schemas/                     # Pydantic v2 validation models
│   │   ├── core/                            # Central config, logging, exceptions
│   │   ├── services/                        # Ingestion, preprocessor, portfolio, allocations
│   │   ├── optimization/                    # Markowitz, Minimum Variance, Max Sharpe optimizers
│   │   └── utils/                           # Pure mathematical calculations
│   └── shared/constants.py                  # Cross-tier enums & financial constants
├── config/settings.yaml                     # Application settings & financial defaults
├── data/
│   ├── raw/                                 # 50 NIFTY CSV market datasets
│   ├── processed/                           # Aligned prices, returns, statistics, covariance
│   └── reports/                             # Data quality reports (JSON/CSV)
├── docs/                                    # Architecture, methodology, API documentation
├── scripts/                                 # Preprocessing, statistics, backtesting CLIs
├── tests/                                   # 21 automated unit, integration, and API tests
├── requirements.txt                         # Pinned dependencies
├── run.py                                   # Unified dual-server startup script
└── README.md
```

---

## 6. Installation & Quick Start

### 1. Clone & Set Up Environment
```bash
# Navigate to project directory
cd stockIt

# Activate your python virtual environment
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Preprocess Market Data
Discovers all raw CSV files, aligns trading sessions, and computes financial statistics:
```bash
python scripts/preprocess_data.py
```

### 3. Launch the Application
Run both the FastAPI backend and Streamlit frontend concurrently:
```bash
python run.py
```
- **Streamlit Frontend Dashboard:** [http://localhost:8501](http://localhost:8501)
- **FastAPI Backend Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

*(Note: You can also run the servers independently)*
```bash
# Terminal 1: Backend
uvicorn app.backend.main:app --reload --port 8000

# Terminal 2: Frontend
streamlit run app/frontend/main.py
```

---

## 7. CLI Scripts

- **Preprocess Data:** `python scripts/preprocess_data.py`
- **View Stock Statistics:** `python scripts/generate_statistics.py`
- **Run Out-of-Sample Backtest:** `python scripts/run_backtest.py`

---

## 8. Running Automated Tests

Run the full automated test suite covering data validation, optimization solvers, allocation math, backtesting, and API endpoints:
```bash
pytest -v
```

All 21 test suites validate:
- Weight constraints ($\sum w_i = 1.0$, $0 \le w_i \le w_{\max}$).
- Zero negative or NaN allocations.
- Mathematical correctness of covariance, volatility, and Sharpe ratios.
- Whole-share integer allocations and cash drag.
- End-to-end API response schemas.

---

## 9. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & system status |
| `GET` | `/api/dataset/summary` | Ingestion metrics & quality summary |
| `GET` | `/api/dataset/stocks` | List stocks with financial metrics (supports search) |
| `GET` | `/api/dataset/stocks/{ticker}`| Detailed price history for a single stock |
| `GET` | `/api/dataset/correlation` | Pearson correlation matrix |
| `POST`| `/api/portfolio/recommend` | Full profile evaluation & portfolio recommendation |
| `POST`| `/api/portfolio/optimize` | Run a specific standalone optimization strategy |
| `GET` | `/api/portfolio/compare` | Compare all 3 strategies under identical parameters |
| `GET` | `/api/portfolio/frontier` | Generate Markowitz Efficient Frontier curve |
| `POST`| `/api/backtesting/run` | Execute out-of-sample chronological backtest |

---

## 10. Financial Assumptions & Limitations

1. **Constituent Survivorship Bias:** Historical data reflects current NIFTY 50 constituents. Companies removed from the index historically are not included.
2. **Estimation Risk:** In-sample historical returns and covariances are used as parameters for optimization. In live markets, asset dynamics are non-stationary.
3. **Execution Slippage:** Indian exchanges do not support fractional shares; whole share rounding introduces small residual cash balances.
4. **Transaction Costs:** Real portfolio rebalancing incurs brokerage, STT, and exchange turnover charges, which Stackit models during backtesting (~10 bps).

---

## 11. Educational Disclaimer
Stackit is an academic portfolio optimization and financial engineering project designed for educational demonstration. It is not a registered investment adviser or brokerage platform. Past historical performance is not a guarantee of future returns.
