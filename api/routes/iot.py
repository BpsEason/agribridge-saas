from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas import IoTData, IoTDataResponse
from typing import List, Dict
import datetime
from datetime import timedelta

router = APIRouter()

# In-memory store for mock IoT data (keyed by tenant_id, then device_id)
# This will store a history of IoT data for charting
mock_iot_data_store: Dict[int, Dict[str, List[IoTData]]] = {}

# Generate some historical mock data for charting
def _generate_mock_iot_data(tenant_id: int, device_id: str, num_points: int = 20):
    if tenant_id not in mock_iot_data_store:
        mock_iot_data_store[tenant_id] = {}
    if device_id not in mock_iot_data_store[tenant_id] or not mock_iot_data_store[tenant_id][device_id]:
        current_time = datetime.datetime.now(datetime.timezone.utc)
        for i in range(num_points):
            timestamp = current_time - timedelta(minutes=(num_points - 1 - i) * 5) # 5-minute intervals
            data_point = IoTData(
                device_id=device_id,
                timestamp=timestamp,
                temperature=round(20 + (i * 0.5) + (i % 3), 2), # Simulate fluctuating temp
                humidity=round(50 + (i * 0.3) + (i % 2), 2),    # Simulate fluctuating humidity
                soil_moisture=round(30 + (i * 0.2) + (i % 4), 2) # Simulate fluctuating soil moisture
            )
            mock_iot_data_store[tenant_id][device_id].append(data_point)

@router.post("/iot/data", response_model=IoTDataResponse, status_code=status.HTTP_201_CREATED)
def receive_iot_data(data: IoTData, current_user: dict = Depends(get_current_user)):
    """
    Receives mock IoT sensor data for the current tenant.
    In a real application, this would store data in a time-series DB.
    """
    tenant_id = current_user.get("tenant_id", 1)

    if tenant_id not in mock_iot_data_store:
        mock_iot_data_store[tenant_id] = {}
    if data.device_id not in mock_iot_data_store[tenant_id]:
        mock_iot_data_store[tenant_id][data.device_id] = []
    
    # Ensure timestamp is set if not provided by device
    if not data.timestamp:
        data.timestamp = datetime.datetime.now(datetime.timezone.utc)
        
    mock_iot_data_store[tenant_id][data.device_id].append(data)
    print(f"Tenant {tenant_id}: Received IoT data for device {data.device_id}: {data.dict()}")
    return IoTDataResponse(message="IoT data received successfully", data=data)

@router.get("/iot/data/{device_id}", response_model=List[IoTData], status_code=status.HTTP_200_OK)
def get_iot_data(device_id: str, current_user: dict = Depends(get_current_user), limit: int = 20):
    """Retrieves mock IoT sensor data for a specific device and current tenant."""
    tenant_id = current_user.get("tenant_id", 1)
    
    # Generate mock data if not already present for demonstration
    _generate_mock_iot_data(tenant_id, device_id)

    if tenant_id not in mock_iot_data_store or device_id not in mock_iot_data_store[tenant_id]:
        raise HTTPException(status_code=404, detail="No IoT data found for this device or tenant")
    
    # Return the latest 'limit' data points
    return mock_iot_data_store[tenant_id][device_id][-limit:]
