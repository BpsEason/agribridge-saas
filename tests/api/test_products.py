import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.main import app, get_db, Base, create_access_token, settings
from api.models import Tenant, Farmer, Product
from datetime import timedelta

# Test database configuration
SQLALCHEMY_TEST_DATABASE_URL = "mysql+pymysql://agriuser:agripassword@127.0.0.1:3306/agribridge_db_test"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_product_data():
    Base.metadata.create_all(bind=engine) # Ensure tables exist
    db = TestingSessionLocal()
    
    # Create mock tenant if not exists
    tenant = db.query(Tenant).filter(Tenant.id == 1).first()
    if not tenant:
        tenant = Tenant(id=1, name="Test Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    # Create a mock farmer for the tenant
    farmer = db.query(Farmer).filter(Farmer.id == 1).first()
    if not farmer:
        farmer = Farmer(id=1, tenant_id=1, name="Test Farmer", location="Test Location")
        db.add(farmer)
        db.commit()
        db.refresh(farmer)

    # Clean up and add test products
    db.query(Product).filter(Product.tenant_id == 1).delete()
    db.add_all([
        Product(id=101, tenant_id=1, name="Test Apple", price=25.5, farmer_id=1),
        Product(id=102, tenant_id=1, name="Test Orange", price=30.0, farmer_id=1),
        Product(id=103, tenant_id=1, name="Test Banana", price=15.0, farmer_id=1),
    ])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine) # Clean up after tests

@pytest.fixture(scope="module")
def auth_headers():
    # Generate a test token for tenant_id = 1
    token = create_access_token(data={"sub": "testuser", "tenant_id": 1}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

def test_create_product(setup_product_data, auth_headers):
    response = client.post(
        "/api/v1/products",
        json={"name": "New Grape", "price": 40.0, "farmer_id": 1},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "New Grape"
    assert response.json()["tenant_id"] == 1

def test_get_products(setup_product_data, auth_headers):
    response = client.get("/api/v1/products", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 3 # Expecting initial 3 + potentially one from create test
    assert any(p["name"] == "Test Apple" for p in response.json())

def test_get_products_pagination(setup_product_data, auth_headers):
    response = client.get("/api/v1/products?limit=1&offset=0", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_product_by_id(setup_product_data, auth_headers):
    response = client.get("/api/v1/products/101", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Apple"
    assert response.json()["id"] == 101

def test_get_product_by_id_not_found(setup_product_data, auth_headers):
    response = client.get("/api/v1/products/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

# Test multi-tenancy for products (e.g., trying to access other tenant's product)
@pytest.fixture(scope="module")
def other_tenant_auth_headers():
    # Generate a test token for tenant_id = 2
    token = create_access_token(data={"sub": "otheruser", "tenant_id": 2}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

def test_product_multi_tenancy_isolation(setup_product_data, other_tenant_auth_headers):
    # Try to get product ID 101 (owned by tenant 1) with tenant 2's token
    response = client.get("/api/v1/products/101", headers=other_tenant_auth_headers)
    assert response.status_code == 404 # Should be not found for tenant 2
