import pytest
from fastapi.testclient import TestClient
from api.main import app, settings, create_access_token
from datetime import timedelta, datetime, timezone
from jose import jwt

client = TestClient(app)

def test_login_success():
    response = client.post(
        "/api/v1/login",
        json={"username": "agribridge_user", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Decode token to verify payload
    token = response.json()["access_token"]
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "agribridge_user"
    assert "exp" in payload
    # Check if tenant_id is in the payload (mocked to 1)
    assert payload["tenant_id"] == 1 

def test_login_failure_invalid_password():
    response = client.post(
        "/api/v1/login",
        json={"username": "agribridge_user", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_failure_invalid_username():
    response = client.post(
        "/api/v1/login",
        json={"username": "non_existent_user", "password": "password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_protected_route_access_with_valid_token():
    # Simulate login to get a token with tenant_id
    access_token = create_access_token(
        data={"sub": "testuser", "tenant_id": 1},
        expires_delta=timedelta(minutes=1)
    )
    response = client.get(
        "/api/v1/protected",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "You have access to this protected resource!"

def test_protected_route_access_without_token():
    response = client.get("/api/v1/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" # FastAPI's default for missing token

def test_protected_route_access_with_invalid_token():
    response = client.get(
        "/api/v1/protected",
        headers={"Authorization": "Bearer invalid_jwt_token"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

def test_protected_route_access_with_expired_token():
    expired_token = create_access_token(
        data={"sub": "testuser", "tenant_id": 1},
        expires_delta=timedelta(minutes=-1) # Token expired 1 minute ago
    )
    response = client.get(
        "/api/v1/protected",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "Signature has expired" in response.json()["detail"]
