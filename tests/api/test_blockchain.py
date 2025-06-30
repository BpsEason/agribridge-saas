import pytest
from fastapi.testclient import TestClient
from api.main import app, create_access_token
from datetime import timedelta
from api.services.blockchain_mock import mock_blockchain_ledger # For direct inspection
from api.schemas import BlockchainTransaction

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def clear_blockchain_ledger():
    # Clear the mock ledger for all tenants before each test
    mock_blockchain_ledger.clear()
    yield

@pytest.fixture(scope="module")
def auth_headers_tenant1():
    token = create_access_token(data={"sub": "user1", "tenant_id": 1}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def auth_headers_tenant2():
    token = create_access_token(data={"sub": "user2", "tenant_id": 2}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

def test_create_blockchain_transaction(auth_headers_tenant1):
    transaction_data = {
        "sender": "Alice",
        "receiver": "Bob",
        "amount": 100.0,
        "data": "Organic produce sale"
    }
    response = client.post(
        "/api/v1/blockchain/transactions",
        json=transaction_data,
        headers=auth_headers_tenant1
    )
    assert response.status_code == 201
    assert response.json()["sender"] == "Alice"
    assert "hash" in response.json()
    assert len(mock_blockchain_ledger[1]) == 1 # Check if stored for tenant 1

def test_get_blockchain_transactions(auth_headers_tenant1):
    # Add a few transactions for tenant 1
    client.post("/api/v1/blockchain/transactions", json={"sender": "A", "receiver": "B", "amount": 10.0}, headers=auth_headers_tenant1)
    client.post("/api/v1/blockchain/transactions", json={"sender": "C", "receiver": "D", "amount": 20.0}, headers=auth_headers_tenant1)
    
    response = client.get("/api/v1/blockchain/transactions", headers=auth_headers_tenant1)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["amount"] == 20.0 # Should be most recent first
    assert response.json()[1]["amount"] == 10.0

def test_get_blockchain_transactions_limit(auth_headers_tenant1):
    client.post("/api/v1/blockchain/transactions", json={"sender": "A", "receiver": "B", "amount": 10.0}, headers=auth_headers_tenant1)
    client.post("/api/v1/blockchain/transactions", json={"sender": "C", "receiver": "D", "amount": 20.0}, headers=auth_headers_tenant1)
    client.post("/api/v1/blockchain/transactions", json={"sender": "E", "receiver": "F", "amount": 30.0}, headers=auth_headers_tenant1)

    response = client.get("/api/v1/blockchain/transactions?limit=1", headers=auth_headers_tenant1)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["amount"] == 30.0

def test_blockchain_multi_tenancy_isolation(auth_headers_tenant1, auth_headers_tenant2):
    # Tenant 1 adds a transaction
    client.post("/api/v1/blockchain/transactions", json={"sender": "T1-Alice", "receiver": "T1-Bob", "amount": 100.0}, headers=auth_headers_tenant1)
    
    # Tenant 2 tries to get transactions
    response_tenant2 = client.get("/api/v1/blockchain/transactions", headers=auth_headers_tenant2)
    assert response_tenant2.status_code == 200
    assert len(response_tenant2.json()) == 0 # Tenant 2 should see no transactions initially

    # Tenant 2 adds its own transaction
    client.post("/api/v1/blockchain/transactions", json={"sender": "T2-Charlie", "receiver": "T2-David", "amount": 50.0}, headers=auth_headers_tenant2)
    
    # Tenant 2 gets its own transactions
    response_tenant2_after = client.get("/api/v1/blockchain/transactions", headers=auth_headers_tenant2)
    assert response_tenant2_after.status_code == 200
    assert len(response_tenant2_after.json()) == 1
    assert response_tenant2_after.json()[0]["sender"] == "T2-Charlie"

    # Tenant 1 still only sees its own
    response_tenant1_after = client.get("/api/v1/blockchain/transactions", headers=auth_headers_tenant1)
    assert response_tenant1_after.status_code == 200
    assert len(response_tenant1_after.json()) == 1
    assert response_tenant1_after.json()[0]["sender"] == "T1-Alice"
