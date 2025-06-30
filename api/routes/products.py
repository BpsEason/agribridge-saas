from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.main import get_db, get_current_user
from api.models import Product
from api.schemas import ProductCreate, ProductResponse

router = APIRouter()

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Create a new product for the current tenant."""
    tenant_id = current_user.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID not found in token.")
    
    db_product = Product(**product.dict(), tenant_id=tenant_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), limit: int = 10, offset: int = 0):
    """Retrieve a list of products with pagination, respecting tenant isolation."""
    tenant_id = current_user.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID not found in token.")
    
    return db.query(Product).filter(Product.tenant_id == tenant_id).offset(offset).limit(limit).all()

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Retrieve a specific product by ID, respecting tenant isolation."""
    tenant_id = current_user.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID not found in token.")
    
    product = db.query(Product).filter(Product.id == product_id, Product.tenant_id == tenant_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
