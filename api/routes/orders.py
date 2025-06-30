from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.main import get_db, get_current_user
from api.models import Order, Product
from api.schemas import OrderCreate, OrderResponse

router = APIRouter()

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Create a new order for the current tenant."""
    tenant_id = current_user.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID not found in token.")

    product = db.query(Product).filter(Product.id == order.product_id, Product.tenant_id == tenant_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or not owned by your tenant")
    
    total_price = product.price * order.quantity
    db_order = Order(
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price,
        buyer_id=order.buyer_id,
        status="pending",
        tenant_id=tenant_id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), limit: int = 10, offset: int = 0):
    """Retrieve a list of orders with pagination, respecting tenant isolation."""
    tenant_id = current_user.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID not found in token.")
        
    return db.query(Order).filter(Order.tenant_id == tenant_id).offset(offset).limit(limit).all()
