from typing import Dict, Any, List
import uuid
import datetime
from api.schemas import BlockchainTransaction

# Mock blockchain ledger (keyed by tenant_id)
mock_blockchain_ledger: Dict[int, List[BlockchainTransaction]] = {}

def record_transaction_on_mock_blockchain(tenant_id: int, sender: str, receiver: str, amount: float, data: str = None) -> BlockchainTransaction:
    """
    Mocks recording a transaction on a blockchain for a specific tenant.
    In a real scenario, this would interact with a blockchain node.
    """
    if tenant_id not in mock_blockchain_ledger:
        mock_blockchain_ledger[tenant_id] = []

    transaction_hash = str(uuid.uuid4()).replace("-", "")
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    
    transaction_record = BlockchainTransaction(
        hash=transaction_hash,
        timestamp=timestamp,
        sender=sender,
        receiver=receiver,
        amount=amount,
        data=data,
        block_id=len(mock_blockchain_ledger[tenant_id]) + 1 # Simple block ID mock
    )
    mock_blockchain_ledger[tenant_id].append(transaction_record)
    print(f"Tenant {tenant_id} Mock Blockchain: Recorded transaction {transaction_hash}")
    return transaction_record

def get_recent_transactions(tenant_id: int, limit: int = 5) -> List[BlockchainTransaction]:
    """Retrieves recent mock blockchain transactions for a specific tenant."""
    if tenant_id not in mock_blockchain_ledger:
        return []
    return mock_blockchain_ledger[tenant_id][-limit:][::-1] # Last 'limit' transactions, reversed
