from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.main import get_current_user
from api.schemas import BlockchainTransaction
from api.services.blockchain_mock import record_transaction_on_mock_blockchain, get_recent_transactions

router = APIRouter()

@router.post("/blockchain/transactions", status_code=status.HTTP_201_CREATED, response_model=BlockchainTransaction)
def create_blockchain_transaction(
    transaction: BlockchainTransaction, 
    current_user: dict = Depends(get_current_user)
):
    """
    Mocks creating a new blockchain transaction for the current tenant.
    """
    tenant_id = current_user.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID not found in token.")
        
    record = record_transaction_on_mock_blockchain(
        tenant_id=tenant_id,
        sender=transaction.sender,
        receiver=transaction.receiver,
        amount=transaction.amount,
        data=transaction.data
    )
    return record

@router.get("/blockchain/transactions", response_model=List[BlockchainTransaction])
def get_blockchain_transactions(
    current_user: dict = Depends(get_current_user),
    limit: int = 5
):
    """
    Retrieves recent mock blockchain transactions for the current tenant.
    """
    tenant_id = current_user.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant ID not found in token.")
        
    transactions = get_recent_transactions(tenant_id, limit)
    return transactions
