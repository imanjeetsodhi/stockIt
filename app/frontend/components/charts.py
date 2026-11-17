"""Interactive Plotly chart components for financial visualizations."""

from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

DARK_LAYOUT = dict(
    paper_bgcolor="#0e1117",
    plot_bgcolor="#161b22",
    font=dict(color="#f0f6fc", family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto"),
    margin=dict(l=40, r=40, t=40, b=40)
)

def create_allocation_donut_chart(allocations: Dict[str, float]) -> go.Figure:
    """Creates a clean donut chart of portfolio allocations."""
    labels = list(allocations.keys())
    values = [round(v * 100, 2) for v in allocations.values()]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                textinfo="label+percent",
                marker=dict(line=dict(color="#0e1117", width=2)),
                hoverinfo="label+value+percent"
            )
        ]
    )
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="Portfolio Weights Allocation", font=dict(size=15)),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    return fig

def create_allocation_bar_chart(allocations: Dict[str, float]) -> go.Figure:
    """Creates a horizontal bar chart of portfolio weights."""
    sorted_items = sorted(allocations.items(), key=lambda x: x[1], reverse=True)
    tickers = [item[0] for item in sorted_items]
    weights = [round(item[1] * 100, 2) for item in sorted_items]

    fig = go.Figure(
        data=[
            go.Bar(
                x=weights,
                y=tickers,
                orientation="h",
                marker=dict(color="#58a6ff", line=dict(color="#1f6feb", width=1)),
                text=[f"{w:.1f}%" for w in weights],
                textposition="auto"
            )
        ]
    )
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="Stock Allocation Percentage", font=dict(size=15)),
        xaxis=dict(title="Allocation Weight (%)", gridcolor="#30363d"),
        yaxis=dict(autorange="reversed", gridcolor="#30363d")
    )
    return fig

def create_correlation_heatmap(corr_df: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
    """Creates a clean correlation matrix heatmap."""
    fig = go.Figure(
        data=go.Heatmap(
            z=corr_df.values,
            x=list(corr_df.columns),
            y=list(corr_df.index),
            colorscale="Viridis",
            zmin=-1.0,
            zmax=1.0,
            colorbar=dict(title="Corr", tickvals=[-1, -0.5, 0, 0.5, 1])
        )
    )
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text=title, font=dict(size=15)),
        xaxis=dict(tickangle=-45, gridcolor="#30363d"),
        yaxis=dict(gridcolor="#30363d")
    )
    return fig

def create_efficient_frontier_chart(
    frontier_points: List[Dict[str, float]],
    strategies: Dict[str, Any],
    selected_strategy_name: Optional[str] = None
) -> go.Figure:
    """Plots the Efficient Frontier curve with highlighted strategy portfolios."""
    fig = go.Figure()

    # Efficient frontier line
    if frontier_points:
        df_f = pd.DataFrame(frontier_points)
        fig.add_trace(
            go.Scatter(
                x=df_f["volatility"] * 100,
                y=df_f["return"] * 100,
                mode="lines",
                name="Efficient Frontier",
                line=dict(color="#58a6ff", width=2.5)
            )
        )

    # Strategy points
    colors = {
        "Minimum Variance": "#3fb950",
        "Markowitz Efficient": "#d29922",
        "Maximum Sharpe": "#bc8cff"
    }

    for name, s in strategies.items():
        ret = s.get("expected_annual_return", 0) * 100
        vol = s.get("annual_volatility", 0) * 100
        sharpe = s.get("sharpe_ratio", 0)
        is_selected = (name == selected_strategy_name)

        fig.add_trace(
            go.Scatter(
                x=[vol],
                y=[ret],
                mode="markers+text",
                name=name,
                text=[f"  <b>{name}</b><br>  (Ret: {ret:.1f}%, Vol: {vol:.1f}%, Sharpe: {sharpe:.2f})"],
                textposition="top right",
                marker=dict(
                    size=14 if is_selected else 10,
                    color=colors.get(name, "#f0f6fc"),
                    symbol="star" if is_selected else "circle",
                    line=dict(color="#ffffff", width=2 if is_selected else 1)
                )
            )
        )

    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="Markowitz Efficient Frontier & Strategy Positions", font=dict(size=15)),
        xaxis=dict(title="Annualized Volatility (%)", gridcolor="#30363d"),
        yaxis=dict(title="Expected Annual Return (%)", gridcolor="#30363d"),
        showlegend=True
    )
    return fig

def create_backtest_cumulative_chart(cumulative_curves: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
    """Plots historical out-of-sample cumulative portfolio performance."""
    fig = go.Figure()
    palette = {
        "Minimum Variance": "#3fb950",
        "Markowitz Efficient": "#d29922",
        "Maximum Sharpe": "#bc8cff",
        "Equal-Weight Benchmark": "#8b949e"
    }

    for name, series in cumulative_curves.items():
        dates = [pt["date"] for pt in series]
        values = [(pt["value"] - 1.0) * 100 for pt in series]  # Percentage gain/loss

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines",
                name=name,
                line=dict(color=palette.get(name, "#58a6ff"), width=2)
            )
        )

    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="Out-of-Sample Cumulative Portfolio Growth (%)", font=dict(size=15)),
        xaxis=dict(title="Date", gridcolor="#30363d"),
        yaxis=dict(title="Cumulative Return (%)", gridcolor="#30363d"),
        showlegend=True
    )
    return fig

def create_price_and_returns_chart(history_points: List[Dict[str, Any]], ticker: str) -> go.Figure:
    """Creates historical price and return chart for a specific stock."""
    df = pd.DataFrame(history_points)
    df["date"] = pd.to_datetime(df["date"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["adj_close"],
            mode="lines",
            name="Adjusted Close (₹)",
            line=dict(color="#58a6ff", width=2)
        )
    )
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text=f"{ticker} Historical Adjusted Close Price (₹)", font=dict(size=15)),
        xaxis=dict(title="Date", gridcolor="#30363d"),
        yaxis=dict(title="Price (₹)", gridcolor="#30363d")
    )
    return fig
