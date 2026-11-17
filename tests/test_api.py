"""Tests for FastAPI backend routes using Starlette / HTTPX TestClient."""

import pytest
from starlette.testclient import TestClient
from app.backend.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["processed_data_ready"] is True

def test_dataset_summary_endpoint():
    res = client.get("/api/dataset/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["valid_stocks_count"] == 50

def test_stocks_list_endpoint():
    res = client.get("/api/dataset/stocks?search=TCS")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["stock"] == "TCS"

def test_portfolio_recommendation_endpoint():
    payload = {
        "investment_amount": 50000.0,
        "risk_appetite": "Moderate",
        "investment_horizon": "3–5 years",
        "investment_objective": "Balanced Growth",
        "max_stock_weight": 0.20
    }
    res = client.post("/api/portfolio/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    rec = data["data"]
    assert "recommended_portfolio" in rec
    assert rec["rupee_allocation"]["total_budget"] == 50000.0
    assert len(rec["explanations"]) > 0

def test_strategy_compare_endpoint():
    res = client.get("/api/portfolio/compare?max_weight=0.20")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "Minimum Variance" in data["data"]
    assert "Maximum Sharpe" in data["data"]
    assert "Markowitz Efficient" in data["data"]
