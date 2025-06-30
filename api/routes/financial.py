from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from api.main import get_db, get_current_user
from api.schemas import PaymentRequest, PaymentResponse
import uuid
import os

router = APIRouter()

@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
def process_payment(payment_request: PaymentRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Mocks a payment processing endpoint.
    In a real application, this would integrate with Stripe/NewebPay.
    """
    tenant_id = current_user.get("tenant_id", 1)
    
    # Simulate payment gateway integration
    if payment_request.payment_method == "stripe":
        api_key = os.getenv("STRIPE_API_KEY")
        if not api_key or "mock" in api_key:
            print("Stripe API key not set or is mock key. Simulating success.")
        # Call Stripe API here
        transaction_status = "completed"
    elif payment_request.payment_method == "newebpay":
        api_key = os.getenv("NEWEPAY_API_KEY")
        if not api_key or "mock" in api_key:
            print("NewebPay API key not set or is mock key. Simulating success.")
        # Call NewebPay API here
        transaction_status = "completed"
    else:
        raise HTTPException(status_code=400, detail="Unsupported payment method")

    # In a real app, record transaction in DB
    transaction_id = str(uuid.uuid4())
    print(f"Tenant {tenant_id}: Processed payment for order {payment_request.order_id} - {payment_request.amount} {payment_request.currency}")
    
    return PaymentResponse(
        transaction_id=transaction_id,
        status=transaction_status,
        amount=payment_request.amount,
        currency=payment_request.currency,
        order_id=payment_request.order_id
    )

@router.get("/ledger/transactions", response_model=List[PaymentResponse])
def get_transactions(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), limit: int = 10, offset: int = 0):
    """Mocks retrieving financial transactions for the current tenant."""
    tenant_id = current_user.get("tenant_id", 1)
    # In a real app, fetch from a financial transactions table filtered by tenant_id
    mock_transactions = [
        {"transaction_id": f"mock_txn_A{i}_T{tenant_id}", "status": "completed", "amount": 100.0 + i, "currency": "TWD", "order_id": 100 + i} for i in range(5)
    ]
    mock_transactions.extend([
        {"transaction_id": f"mock_txn_B{i}_T{tenant_id}", "status": "pending", "amount": 50.0 + i, "currency": "USD", "order_id": 200 + i} for i in range(5)
    ])
    
    # Filter by tenant_id if it were a real DB query. For this mock, we just generate mock data with tenant_id.
    return mock_transactions[offset:offset+limit]
