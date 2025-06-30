import pytest
from fastapi.testclient import TestClient
from api.main import app, create_access_token
from datetime import timedelta
from api.routes.iot import mock_iot_data_store # Import the in-memory store for inspection

client = TestClient(app)

@pytest.fixture(scope="function")
def clear_iot_data_store():
    # Clear the mock store before each test function
    mock_iot_data_store.clear()
    yield

@pytest.fixture(scope="module")
def auth_headers():
    token = create_access_token(data={"sub": "testuser", "tenant_id": 1}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def other_tenant_auth_headers():
    token = create_access_token(data={"sub": "otheruser", "tenant_id": 2}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

def test_receive_iot_data(auth_headers, clear_iot_data_store):
    device_id = "sensor-001"
    iot_data = {
        "device_id": device_id,
        "timestamp": "2023-01-01T10:00:00Z",
        "temperature": 25.5,
        "humidity": 60.2
    }
    response = client.post(
        "/api/v1/iot/data",
        json=iot_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["message"] == "IoT data received successfully"
    assert response.json()["data"]["device_id"] == device_id
    
    # Verify data is stored in the mock store for the correct tenant
    assert 1 in mock_iot_data_store
    assert device_id in mock_iot_data_store[1]
    assert len(mock_iot_data_store[1][device_id]) == 1
    assert mock_iot_data_store[1][device_id][0].temperature == 25.5

def test_get_iot_data_for_device(auth_headers, clear_iot_data_store):
    device_id = "sensor-002"
    iot_data_1 = {"device_id": device_id, "timestamp": "2023-01-01T11:00:00Z", "temperature": 26.0}
    iot_data_2 = {"device_id": device_id, "timestamp": "2023-01-01T11:01:00Z", "humidity": 65.0}
    
    client.post("/api/v1/iot/data", json=iot_data_1, headers=auth_headers)
    client.post("/api/v1/iot/data", json=iot_data_2, headers=auth_headers)
    
    response = client.get(f"/api/v1/iot/data/{device_id}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["temperature"] == 26.0
    assert response.json()[1]["humidity"] == 65.0

def test_get_iot_data_device_not_found(auth_headers, clear_iot_data_store):
    response = client.get("/api/v1/iot/data/non-existent-device", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "No IoT data found for this device or tenant"

def test_iot_data_multi_tenancy_isolation(auth_headers, other_tenant_auth_headers, clear_iot_data_store):
    # Tenant 1 sends data for device-A
    client.post("/api/v1/iot/data", json={"device_id": "device-A", "timestamp": "2023-01-01T00:00:00Z", "temperature": 20.0}, headers=auth_headers)
    
    # Tenant 2 tries to access device-A
    response = client.get("/api/v1/iot/data/device-A", headers=other_tenant_auth_headers)
    assert response.status_code == 404 # Should not find tenant 1's device
    assert response.json()["detail"] == "No IoT data found for this device or tenant"

    # Tenant 2 sends data for device-B
    client.post("/api/v1/iot/data", json={"device_id": "device-B", "timestamp": "2023-01-01T00:00:00Z", "humidity": 50.0}, headers=other_tenant_auth_headers)
    
    # Tenant 2 accesses its own device-B
    response = client.get("/api/v1/iot/data/device-B", headers=other_tenant_auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["humidity"] == 50.0
