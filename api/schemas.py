from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class FarmerCreate(BaseModel):
    name: str
    location: str

class FarmerResponse(BaseModel):
    id: int
    name: str
    location: str
    esg_score: float
    total_sales: float

    class Config:
        from_attributes = True

class ESGReportResponse(BaseModel):
    farmer_name: str
    esg_score: float
    social_impact: Dict[str, Any]
    environmental_impact: Dict[str, Any]

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

# --- New Schemas for Products and Orders ---
class ProductCreate(BaseModel):
    name: str = Field(..., example="有機蘋果")
    price: float = Field(..., example=50.0)
    farmer_id: int = Field(..., example=1)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    farmer_id: int
    tenant_id: int # Include tenant_id in response

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    product_id: int = Field(..., example=101)
    quantity: int = Field(..., example=10)
    buyer_id: int = Field(..., example=101)

class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_price: float
    buyer_id: int
    status: str
    tenant_id: int # Include tenant_id in response

    class Config:
        from_attributes = True

# --- New Schemas for Financial Ledger ---
class PaymentRequest(BaseModel):
    order_id: int
    amount: float
    currency: str
    payment_method: str # e.g., "stripe", "newebpay"

class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    currency: str
    order_id: int

# --- New Schemas for IoT Data ---
class IoTData(BaseModel):
    device_id: str
    timestamp: datetime # Use datetime object for better handling
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil_moisture: Optional[float] = None
    light_intensity: Optional[float] = None

class IoTDataResponse(BaseModel):
    message: str
    data: IoTData

# --- New Schemas for Blockchain (Mock) ---
class BlockchainTransaction(BaseModel):
    sender: str
    receiver: str
    amount: float
    data: Optional[str] = None
    # Add fields for mock blockchain response
    hash: Optional[str] = None
    timestamp: Optional[datetime] = None
    block_id: Optional[int] = None
