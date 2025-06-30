from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import redis
import os
from typing import Annotated
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
load_dotenv()

# --- 3.10.1 Settings and Configuration ---
class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret_key: str
    algorithm: str = "HS256"
    line_channel_access_token: str = "your_line_channel_access_token"
    line_channel_secret: str = "your_line_channel_secret"
    line_user_id: str = "Udeadbeefdeadbeefdeadbeefdeadbeef" # Default mock ID
    stripe_api_key: str = "sk_test_mock_stripe_key_12345"
    newebpay_api_key: str = "mock_newebpay_key_ABCDE"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Ensure required environment variables are set
try:
    settings = Settings()
    # Basic validation for JWT secret
    if settings.jwt_secret_key == "super-secret-key-that-you-should-change-in-production":
        print("WARNING: JWT_SECRET_KEY is still default. Please change it in your .env file for production!")
    if "your_line_channel_access_token" in settings.line_channel_access_token or \
       "your_line_channel_secret" in settings.line_channel_secret:
        print("WARNING: LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_SECRET is still default. Please update your .env file for LINE integration!")
    if "mock_stripe_key" in settings.stripe_api_key:
        print("WARNING: STRIPE_API_KEY is still a mock key. Please update your .env file for actual payment processing!")
    if "mock_newebpay_key" in settings.newebpay_api_key:
        print("WARNING: NEWEPAY_API_KEY is still a mock key. Please update your .env file for actual payment processing!")

except Exception as e:
    raise RuntimeError(f"Missing or invalid environment variables. Please check your .env file. Error: {e}")

app = FastAPI(
    title="AgriBridge API",
    description="A SaaS platform for sustainable agriculture, integrating FinTech and ESG.",
    version="1.0.0",
)

# --- 3.10.2 CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3.10.3 Database Configuration ---
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from api.models import Base, Tenant, Farmer, Product, Order # Import all models for initial data

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3.10.4 Caching with Redis ---
redis_client = redis.Redis.from_url(settings.redis_url)

# --- 3.10.5 JWT Token Dependency for Multi-tenancy ---
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30) # Default expiry
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        tenant_id: int = payload.get("tenant_id") # Get tenant_id from token
        if username is None or tenant_id is None:
            raise credentials_exception
        # In a real app, you would verify against the DB:
        # user = db.query(User).filter(User.username == username, User.tenant_id == tenant_id).first()
        # if user is None:
        #    raise credentials_exception
        return {"username": username, "tenant_id": tenant_id}
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {e}",
        )

# --- 3.10.6 Import and include API Routers ---
from api.routes import farmers, auth, products, orders, financial, iot, blockchain
from notification.line_bot_service import router as line_router
# This mock router is for frontend to trigger LINE notifications easily for demo
from api.routes.notifications_mock_for_frontend import router as notifications_mock_router 


app.include_router(farmers.router, prefix="/api/v1", tags=["Farmers", "ESG"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(orders.router, prefix="/api/v1", tags=["Orders"])
app.include_router(financial.router, prefix="/api/v1", tags=["Financial Ledger"])
app.include_router(iot.router, prefix="/api/v1", tags=["IoT"])
app.include_router(blockchain.router, prefix="/api/v1", tags=["Blockchain"])
app.include_router(line_router, prefix="/api/v1", tags=["Notifications"])
app.include_router(notifications_mock_router, prefix="/api/v1", tags=["Notifications (Mock)"]) # Mock for frontend


# --- 3.11 Health Check Endpoint ---
@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    try:
        # Check database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        # Check Redis connection
        redis_client.ping()
        return {"status": "ok", "message": "All services are running"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Service unavailable: {e}")

# --- 3.12 Initial Data Setup on Startup ---
@app.on_event("startup")
def create_initial_data():
    db = SessionLocal()
    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)

        # Check if default tenant exists
        default_tenant = db.query(Tenant).filter(Tenant.id == 1).first()
        if not default_tenant:
            print("Creating default tenant, farmer, products, and orders data...")
            tenant1 = Tenant(id=1, name="AgriBridge Default Tenant")
            db.add(tenant1)
            db.commit()
            db.refresh(tenant1)

            # Create a default farmer for the default tenant
            farmer1 = Farmer(id=1, tenant_id=1, name="AgriBridge Demo Farm", location="Taiwan", esg_score=75.5, total_sales=5000.0)
            db.add(farmer1)
            db.commit()
            db.refresh(farmer1)
            print("Default farmer created for default tenant.")

            # Create some default products for the default tenant and farmer
            product1 = Product(id=101, tenant_id=1, name="有機蔬菜包", price=120.0, farmer_id=1)
            product2 = Product(id=102, tenant_id=1, name="高山水果禮盒", price=500.0, farmer_id=1)
            product3 = Product(id=103, tenant_id=1, name="新鮮雞蛋 (10入)", price=80.0, farmer_id=1)
            db.add_all([product1, product2, product3])
            db.commit()
            db.refresh(product1)
            db.refresh(product2)
            db.refresh(product3)
            print("Default products created.")

            # Create some default orders for the default tenant
            order1 = Order(id=1, tenant_id=1, product_id=101, quantity=2, total_price=product1.price * 2, buyer_id=101, status="completed")
            order2 = Order(id=2, tenant_id=1, product_id=102, quantity=1, total_price=product2.price * 1, buyer_id=102, status="pending")
            db.add_all([order1, order2])
            db.commit()
            print("Default orders created.")
        else:
            print("Default tenant, farmer, products, and orders already exist. Skipping initial data creation.")
    except Exception as e:
        print(f"Error during initial data setup: {e}")
    finally:
        db.close()


# --- 3.13 Main execution ---
if __name__ == "__main__":
    import uvicorn
    # Initial data setup is now part of the startup event
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
