# Stackit: Data Dictionary

## 1. Raw Dataset Format
Raw files are located in `data/raw/*.csv`. Each CSV represents one constituent of the NIFTY 50 index.

| Column | Type | Description |
|---|---|---|
| `Stock` | String | NSE Ticker symbol (e.g. `RELIANCE`, `TCS`, `INFY`) |
| `Date` | Date (YYYY-MM-DD) | Historical trading session date |
| `Open` | Float | Opening price in INR (₹) |
| `High` | Float | Intra-day highest price in INR (₹) |
| `Low` | Float | Intra-day lowest price in INR (₹) |
| `Close` | Float | Unadjusted daily closing price in INR (₹) |
| `Adj Close` | Float | Adjusted closing price accounting for splits, dividends, and corporate actions |
| `Volume` | Integer | Total number of shares traded during the session |

---

## 2. Processed Matrices & Files
Located in `data/processed/`:

- **`combined_stock_data.csv`**: Consolidated, chronologically sorted records of all valid stocks.
- **`adjusted_close_prices.csv`**: Date-indexed matrix where each column is a stock's Adjusted Close series.
- **`daily_returns.csv`**: Daily percentage price changes: $R_t = (P_t / P_{t-1}) - 1$.
- **`covariance_matrix.csv`**: Annualized $50 \times 50$ covariance matrix ($\mathbf{\Sigma}_{\text{daily}} \times 252$).
- **`correlation_matrix.csv`**: Pearson correlation matrix ($\mathbf{\rho}_{i,j} \in [-1, 1]$).
- **`stock_statistics.csv`**: Summary table of metrics per stock:
  - `Average_Daily_Return`: Arithmetic mean of daily returns.
  - `Annualized_Return`: Mean daily return $\times 252$.
  - `CAGR`: Compounded Annual Growth Rate: $(P_{\text{end}} / P_{\text{start}})^{1/years} - 1$.
  - `Annualized_Volatility`: Daily return sample standard deviation $\times \sqrt{252}$.
  - `Daily_Variance`: Daily return variance.
  - `Annualized_Variance`: Daily variance $\times 252$.
  - `Maximum_Drawdown`: Maximum peak-to-trough drop over historical series.
  - `Sharpe_Ratio`: $(\text{Annualized Return} - R_f) / \text{Annualized Volatility}$.
  - `Average_Daily_Volume`: Mean trading volume.
  - `Latest_Price`: Most recent Adjusted Close price.
  - `Total_Observations`: Count of valid aligned trading sessions.
