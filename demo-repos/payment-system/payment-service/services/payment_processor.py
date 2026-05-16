"""
Payment Processor Service
Core business logic for payment processing
"""
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """
    Handles payment transaction logic and database operations
    """
    
    def __init__(self):
        # RISK: Shared mutable cache without proper locking
        self._idempotency_cache = {}
        self._transaction_cache = {}
    
    def check_idempotency(self, db_session: Session, idempotency_key: str):
        """
        Check if transaction with this idempotency key already exists
        
        RISK: Cache without TTL can grow unbounded
        RISK: No thread-safe locking on cache access
        """
        # Check in-memory cache first (RISK: race condition possible)
        if idempotency_key in self._idempotency_cache:
            logger.info(f"Idempotency key {idempotency_key} found in cache")
            return self._idempotency_cache[idempotency_key]
        
        # Check database
        from db.connection import Transaction
        transaction = db_session.query(Transaction).filter(
            Transaction.idempotency_key == idempotency_key
        ).first()
        
        if transaction:
            # Store in cache (RISK: no cache size limit)
            self._idempotency_cache[idempotency_key] = {
                "transaction_id": transaction.id,
                "status": transaction.status,
                "amount": transaction.amount,
                "timestamp": transaction.created_at
            }
            return self._idempotency_cache[idempotency_key]
        
        return None
    
    def create_transaction(
        self,
        db_session: Session,
        order_id: str,
        amount: float,
        currency: str,
        customer_id: str,
        gateway_response: dict,
        idempotency_key: Optional[str] = None
    ):
        """
        Create a new payment transaction record
        
        RISK: No explicit transaction isolation level set
        """
        from db.connection import Transaction
        
        transaction_id = str(uuid.uuid4())
        
        transaction = Transaction(
            id=transaction_id,
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status=gateway_response.get("status", "pending"),
            payment_method=gateway_response.get("payment_method"),
            gateway_transaction_id=gateway_response.get("transaction_id"),
            idempotency_key=idempotency_key,
            created_at=datetime.utcnow()
        )
        
        db_session.add(transaction)
        # Note: Caller is responsible for commit
        
        # Update cache
        if idempotency_key:
            self._idempotency_cache[idempotency_key] = {
                "transaction_id": transaction.id,
                "status": transaction.status,
                "amount": transaction.amount,
                "timestamp": transaction.created_at
            }
        
        logger.info(f"Created transaction {transaction_id} for order {order_id}")
        return transaction
    
    def get_transaction(self, db_session: Session, transaction_id: str):
        """
        Retrieve transaction by ID
        
        RISK: No caching strategy, hits DB every time
        """
        from db.connection import Transaction
        
        # Check cache first (RISK: stale data possible)
        if transaction_id in self._transaction_cache:
            return self._transaction_cache[transaction_id]
        
        transaction = db_session.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        
        if transaction:
            # Cache the transaction (RISK: no invalidation strategy)
            self._transaction_cache[transaction_id] = transaction
        
        return transaction
    
    def list_transactions(
        self,
        db_session: Session,
        customer_id: Optional[str] = None,
        limit: int = 100
    ) -> List:
        """
        List transactions with optional filtering
        
        RISK: No pagination offset, could return too much data
        RISK: No query timeout set
        """
        from db.connection import Transaction
        
        query = db_session.query(Transaction)
        
        if customer_id:
            query = query.filter(Transaction.customer_id == customer_id)
        
        # RISK: Large limit without proper pagination
        transactions = query.order_by(
            Transaction.created_at.desc()
        ).limit(limit).all()
        
        return transactions
    
    def create_refund(
        self,
        db_session: Session,
        transaction_id: str,
        amount: float,
        reason: str,
        gateway_response: dict
    ):
        """
        Create a refund record
        """
        from db.connection import Refund
        
        refund_id = str(uuid.uuid4())
        
        refund = Refund(
            id=refund_id,
            transaction_id=transaction_id,
            amount=amount,
            reason=reason,
            status=gateway_response.get("status", "completed"),
            gateway_refund_id=gateway_response.get("refund_id"),
            created_at=datetime.utcnow()
        )
        
        db_session.add(refund)
        # Note: Caller is responsible for commit
        
        # Invalidate transaction cache (RISK: partial invalidation)
        if transaction_id in self._transaction_cache:
            del self._transaction_cache[transaction_id]
        
        logger.info(f"Created refund {refund_id} for transaction {transaction_id}")
        return refund
    
    def update_transaction_status(
        self,
        db_session: Session,
        transaction_id: str,
        new_status: str
    ):
        """
        Update transaction status
        
        RISK: No optimistic locking, race conditions possible
        """
        from db.connection import Transaction
        
        transaction = db_session.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        
        if transaction:
            transaction.status = new_status
            transaction.updated_at = datetime.utcnow()
            
            # Invalidate cache
            if transaction_id in self._transaction_cache:
                del self._transaction_cache[transaction_id]
            
            logger.info(f"Updated transaction {transaction_id} status to {new_status}")
            return transaction
        
        return None

# Made with Bob
