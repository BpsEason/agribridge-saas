import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.main import app, get_db, Base, create_access_token, settings
from api.models import Tenant, Farmer, Product, Order
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
def setup_order_data():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create mock tenant if not exists
    tenant = db.query(Tenant).filter(Tenant.id == 1).first()
    if not tenant:
        tenant = Tenant(id=1, name="Test Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    # Ensure a product exists for orders
    product = db.query(Product).filter(Product.id == 1001, Product.tenant_id == 1).first()
    if not product:
        product = Product(id=1001, tenant_id=1, name="Test Product for Order", price=10.0, farmer_id=1)
        db.add(product)
        db.commit()
        db.refresh(product)

    # Clean up and add test orders
    db.query(Order).filter(Order.tenant_id == 1).delete()
    db.add_all([
        Order(id=1, tenant_id=1, product_id=1001, quantity=5, total_price=50.0, buyer_id=10, status="pending"),
        Order(id=2, tenant_id=1, product_id=1001, quantity=10, total_price=100.0, buyer_id=11, status="completed"),
    ])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def auth_headers():
    token = create_access_token(data={"sub": "testuser", "tenant_id": 1}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

def test_create_order(setup_order_data, auth_headers):
    response = client.post(
        "/api/v1/orders",
        json={"product_id": 1001, "quantity": 3, "buyer_id": 12},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["product_id"] == 1001
    assert response.json()["quantity"] == 3
    assert response.json()["total_price"] == 30.0 # 3 * 10.0
    assert response.json()["status"] == "pending"
    assert response.json()["tenant_id"] == 1

def test_create_order_product_not_found(setup_order_data, auth_headers):
    response = client.post(
        "/api/v1/orders",
        json={"product_id": 9999, "quantity": 1, "buyer_id": 13},
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]

def test_get_orders(setup_order_data, auth_headers):
    response = client.get("/api/v1/orders", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2
    assert any(o["id"] == 1 for o in response.json())

def test_get_orders_pagination(setup_order_data, auth_headers):
    response = client.get("/api/v1/orders?limit=1&offset=0", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1

# Test multi-tenancy for orders
@pytest.fixture(scope="module")
def other_tenant_auth_headers_for_orders():
    token = create_access_token(data={"sub": "otheruser", "tenant_id": 2}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

def test_order_multi_tenancy_isolation(setup_order_data, other_tenant_auth_headers_for_orders):
    # Try to get orders owned by tenant 1 with tenant 2's token
    response = client.get("/api/v1/orders", headers=other_tenant_auth_headers_for_orders)
    assert response.status_code == 200
    assert len(response.json()) == 0 # Tenant 2 should have no orders by default
