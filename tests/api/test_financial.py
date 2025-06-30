import pytest
from fastapi.testclient import TestClient
from api.main import app, create_access_token, settings
from datetime import timedelta
import os

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    token = create_access_token(data={"sub": "testuser", "tenant_id": 1}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

def test_process_payment_stripe_success(auth_headers, monkeypatch):
    monkeypatch.setenv("STRIPE_API_KEY", "pk_test_valid_stripe_key")
    response = client.post(
        "/api/v1/payments",
        json={"order_id": 1, "amount": 50.0, "currency": "TWD", "payment_method": "stripe"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert "transaction_id" in response.json()
    assert response.json()["order_id"] == 1

def test_process_payment_newebpay_success(auth_headers, monkeypatch):
    monkeypatch.setenv("NEWEPAY_API_KEY", "valid_newebpay_key")
    response = client.post(
        "/api/v1/payments",
        json={"order_id": 2, "amount": 120.0, "currency": "TWD", "payment_method": "newebpay"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert "transaction_id" in response.json()
    assert response.json()["order_id"] == 2

def test_process_payment_unsupported_method(auth_headers):
    response = client.post(
        "/api/v1/payments",
        json={"order_id": 3, "amount": 10.0, "currency": "TWD", "payment_method": "unsupported"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported payment method"

def test_get_transactions(auth_headers):
    response = client.get("/api/v1/ledger/transactions", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0 # Expect mock data

def test_get_transactions_pagination(auth_headers):
    response = client.get("/api/v1/ledger/transactions?limit=1&offset=0", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    # Check for a known mock transaction ID or pattern from financial.py
    assert response.json()[0]["transaction_id"].startswith("mock_txn_A") or \
           response.json()[0]["transaction_id"].startswith("mock_txn_B")
