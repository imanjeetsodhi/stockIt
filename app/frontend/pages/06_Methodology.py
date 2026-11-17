"""06 Methodology — Mathematical Foundations, Models, and Financial Disclaimers."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

st.title("📚 Quantitative Methodology & Mathematical Models")
st.markdown("Detailed reference documentation explaining the mathematical foundations of Stackit.")

st.markdown("---")

st.markdown("### **1. The Portfolio Optimization Problem**")
st.write(
    """
    Modern Portfolio Theory (MPT), pioneered by Nobel laureate Harry Markowitz in 1952, demonstrates that an investor can 
    construct an optimal portfolio maximizing expected return for a given level of market risk through diversification.
    
    Rather than picking stocks in isolation, MPT evaluates how securities interact with one another through their **covariance**.
    """
)

st.markdown("---")

st.markdown("### **2. Mathematical Formulation of the Three Models**")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("#### **A. Minimum Variance**")
    st.latex(r"\min_{\mathbf{w}} \mathbf{w}^T \mathbf{\Sigma} \mathbf{w}")
    st.write(
        """
        **Subject to:**
        - $\sum_{i=1}^N w_i = 1$ (100% allocation)
        - $0 \le w_i \le w_{\max}$ (Long-only, no short selling)
        
        **Purpose:** Finds the asset combination that delivers the mathematically lowest historical variance $\sigma_p^2$. 
        Does not seek high returns; prioritizes defense.
        """
    )

with c2:
    st.markdown("#### **B. Markowitz Efficient**")
    st.latex(r"\max_{\mathbf{w}} \left( \mathbf{w}^T \mathbf{\mu} - \frac{\lambda}{2} \mathbf{w}^T \mathbf{\Sigma} \mathbf{w} \right)")
    st.write(
        """
        **Subject to:**
        - $\sum_{i=1}^N w_i = 1$
        - $0 \le w_i \le w_{\max}$
        
        **Purpose:** Balances expected arithmetic return $\mathbf{\mu}$ against risk penalty weighted by risk-aversion coefficient $\lambda$.
        Traces the boundary of the Efficient Frontier.
        """
    )

with c3:
    st.markdown("#### **C. Maximum Sharpe Ratio**")
    st.latex(r"\max_{\mathbf{w}} \frac{\mathbf{w}^T \mathbf{\mu} - R_f}{\sqrt{\mathbf{w}^T \mathbf{\Sigma} \mathbf{w}}}")
    st.write(
        """
        **Subject to:**
        - $\sum_{i=1}^N w_i = 1$
        - $0 \le w_i \le w_{\max}$
        
        **Purpose:** Maximizes historical excess return above the risk-free rate $R_f$ per unit of total volatility. 
        Identifies the optimal Tangency Portfolio.
        """
    )

st.markdown("---")

st.markdown("### **3. Financial Formulas & Conventions**")
st.write(
    """
    - **Daily Return:** $R_t = \\frac{P_t}{P_{t-1}} - 1$ where $P_t$ is the Adjusted Close price.
    - **Annualized Return:** $\\bar{R}_{\\text{ann}} = \\bar{R}_{\\text{daily}} \\times 252$
    - **Annualized Volatility:** $\\sigma_{\\text{ann}} = \\sigma_{\\text{daily}} \\times \\sqrt{252}$
    - **Annualized Covariance Matrix:** $\\mathbf{\\Sigma}_{\\text{ann}} = \\mathbf{\\Sigma}_{\\text{daily}} \\times 252$
    - **Sharpe Ratio:** $\\text{Sharpe} = \\frac{\\bar{R}_{\\text{ann}} - R_f}{\\sigma_{\\text{ann}}}$
    - **Marginal Risk Contribution:** $\\text{RC}_i = \\frac{w_i (\\mathbf{\\Sigma} \\mathbf{w})_i}{\\sigma_p^2}$
    """
)

st.markdown("---")

st.markdown("### **4. Assumptions and Real-World Limitations**")
st.warning(
    """
    1. **Survivorship Bias:** The historical dataset consists of the current NIFTY 50 constituent list. Companies that were removed from the index in past years are not reflected.
    2. **Stationarity Assumption:** Historical returns and covariances are used as proxies for future expectations. In live markets, covariance matrices and asset returns are non-stationary and regime-dependent.
    3. **Execution Slippage & Whole Shares:** Fractional shares are not supported in standard Indian depository accounts (CDSL/NSDL). Stackit rounds to whole integer shares, producing minor unallocated cash drag.
    4. **Transaction Costs:** Real portfolio rebalancing incurs brokerage, STT (Securities Transaction Tax), GST, stamp duty, and exchange turnover charges (~10–15 bps).
    """
)

st.markdown("---")
st.caption("Educational Project Disclaimer: Stackit is an academic portfolio optimization and decision-support system. It is not an automated broker or SEBI-registered investment advisor.")
