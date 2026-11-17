# Stackit: Quantitative Methodology & Mathematical Foundations

## 1. Introduction for Final-Year Students & Evaluators
When investing in the stock market, picking single stocks based on gut feeling or recent news often leads to high risk. Even if you pick 5 good stocks, if they all drop at the same time during a market crash, your portfolio suffers heavy losses.

**Stackit** solves this problem using **Modern Portfolio Theory (MPT)**. Instead of looking at each stock individually, MPT looks at how stocks behave together. By combining stocks that do not move in lockstep, an investor can achieve **higher returns with lower total volatility**.

---

## 2. Core Mathematical Formulations

### A. Return and Risk Calculations
1. **Daily Return ($R_t$):**
   $$R_t = \frac{P_t - P_{t-1}}{P_{t-1}} = \frac{P_t}{P_{t-1}} - 1$$
   Where $P_t$ is the Adjusted Closing price on trading day $t$.

2. **Annualized Return ($\bar{R}_{\text{ann}}$):**
   Assuming 252 trading days per year:
   $$\bar{R}_{\text{ann}} = \bar{R}_{\text{daily}} \times 252$$

3. **Annualized Volatility ($\sigma_{\text{ann}}$):**
   Standard deviation measures the fluctuations/risk of daily returns:
   $$\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$$

4. **Covariance Matrix ($\mathbf{\Sigma}$):**
   Covariance measures how two stocks move together:
   $$\sigma_{i,j} = \frac{1}{T-1} \sum_{t=1}^T (R_{i,t} - \bar{R}_i)(R_{j,t} - \bar{R}_j)$$
   The annualized covariance matrix is:
   $$\mathbf{\Sigma}_{\text{ann}} = \mathbf{\Sigma}_{\text{daily}} \times 252$$

5. **Portfolio Variance and Volatility:**
   For a portfolio weight vector $\mathbf{w} = [w_1, w_2, \dots, w_N]^T$:
   $$\sigma_p^2 = \mathbf{w}^T \mathbf{\Sigma} \mathbf{w} = \sum_{i=1}^N \sum_{j=1}^N w_i w_j \sigma_{i,j}$$
   $$\sigma_p = \sqrt{\mathbf{w}^T \mathbf{\Sigma} \mathbf{w}}$$

6. **Sharpe Ratio:**
   Developed by Nobel laureate William Sharpe:
   $$\text{Sharpe} = \frac{\bar{R}_p - R_f}{\sigma_p}$$
   Where $R_f$ is the risk-free rate (6.5% Indian 10-Yr G-Sec proxy).

---

## 3. The Three Portfolio Optimization Techniques

### Technique 1: Minimum Variance Portfolio
- **Goal:** Find the combination of stocks with the lowest possible volatility.
- **Mathematical Problem:**
  $$\min_{\mathbf{w}} \mathbf{w}^T \mathbf{\Sigma} \mathbf{w}$$
  $$\text{Subject to: } \sum_{i=1}^N w_i = 1, \quad 0 \le w_i \le w_{\max}$$
- **Intuition:** Ideal for conservative investors who care primarily about capital preservation and sleep-well-at-night stability.

### Technique 2: Markowitz Mean-Variance Optimization
- **Goal:** Strike an optimal balance between expected return and risk penalty.
- **Mathematical Problem:**
  $$\max_{\mathbf{w}} \left( \mathbf{w}^T \mathbf{\mu} - \frac{\lambda}{2} \mathbf{w}^T \mathbf{\Sigma} \mathbf{w} \right)$$
  Where $\lambda$ is the investor's risk-aversion parameter.
- **Intuition:** Generates the **Efficient Frontier** — a curve showing the maximum possible return for every level of volatility. Ideal for moderate-risk investors seeking balanced growth.

### Technique 3: Maximum Sharpe Ratio Portfolio (Tangency Portfolio)
- **Goal:** Find the portfolio that delivers the maximum excess return per unit of volatility.
- **Mathematical Problem:**
  $$\max_{\mathbf{w}} \frac{\mathbf{w}^T \mathbf{\mu} - R_f}{\sqrt{\mathbf{w}^T \mathbf{\Sigma} \mathbf{w}}}$$
- **Intuition:** The most efficient point on the risk-return spectrum. Delivers the biggest "bang for the buck" in risk-adjusted performance.

---

## 4. Execution Engineering: Whole Share Rupee Allocations
In India, stocks trade on the NSE/BSE as whole integer shares (no fractional shares).
If the optimizer gives a 15% weight to a stock priced at ₹4,000 on a ₹1,00,000 budget:
$$\text{Target Amount} = ₹1,00,000 \times 0.15 = ₹15,000$$
$$\text{Whole Shares} = \lfloor 15,000 / 4,000 \rfloor = 3 \text{ shares}$$
$$\text{Actual Invested} = 3 \times ₹4,000 = ₹12,000$$
$$\text{Residual Cash Drag} = ₹15,000 - ₹12,000 = ₹3,000$$

Stackit calculates exact whole shares and transparently reports unallocated cash drag.

---

## 5. Marginal Risk Contribution
Stackit breaks down each asset's contribution to total portfolio risk:
$$\text{RC}_i = \frac{w_i (\mathbf{\Sigma} \mathbf{w})_i}{\sigma_p^2}$$
This lets investors see whether a high-volatility stock is dominating their portfolio's risk or whether diversification is successfully dampening it.

---

## 6. Assumptions and Limitations
1. **Survivorship Bias:** The historical dataset consists of the current 50 constituents of the NIFTY 50. Inactive or delisted firms are absent.
2. **Estimation Risk:** Future returns and covariances may diverge from historical averages due to economic regime shifts.
3. **Transaction Costs:** Real trading involves brokerage and statutory charges (~10 bps), which Stackit accounts for during backtesting.
