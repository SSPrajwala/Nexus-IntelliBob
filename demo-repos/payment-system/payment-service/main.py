"""
Payment Service - Main API Entry Point
Handles payment processing, refunds, and transaction management
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime
import logging

from db.connection import get_db_session
from services.payment_processor import PaymentProcessor
from services.external_api import ExternalPaymentGateway

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Service", version="1.0.0")

# Initialize services
payment_processor = PaymentProcessor()
payment_gateway = ExternalPaymentGateway()


class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    currency: str = "USD"
    customer_id: str
    payment_method: str
    idempotency_key: Optional[str] = None


class RefundRequest(BaseModel):
    transaction_id: str
    amount: Optional[float] = None
    reason: str


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    timestamp: datetime


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "payment-service"}


@app.post("/api/v1/payments", response_model=PaymentResponse)
async def process_payment(
    payment_req: PaymentRequest,
    db_session=Depends(get_db_session)
):
    """
    Process a payment transaction
    
    Risk: Synchronous call to external gateway without timeout
    Risk: No circuit breaker for downstream failures
    """
    try:
        logger.info(f"Processing payment for order {payment_req.order_id}")
        
        # Validate payment request
        if payment_req.amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        # Check for duplicate transaction using idempotency key
        if payment_req.idempotency_key:
            existing = payment_processor.check_idempotency(
                db_session, 
                payment_req.idempotency_key
            )
            if existing:
                return existing
        
        # Call external payment gateway (RISK: no timeout, no circuit breaker)
        gateway_response = payment_gateway.charge(
            amount=payment_req.amount,
            currency=payment_req.currency,
            payment_method=payment_req.payment_method,
            customer_id=payment_req.customer_id
        )
        
        # Store transaction in database
        transaction = payment_processor.create_transaction(
            db_session=db_session,
            order_id=payment_req.order_id,
            amount=payment_req.amount,
            currency=payment_req.currency,
            customer_id=payment_req.customer_id,
            gateway_response=gateway_response,
            idempotency_key=payment_req.idempotency_key
        )
        
        db_session.commit()
        
        return PaymentResponse(
            transaction_id=transaction.id,
            status=transaction.status,
            amount=transaction.amount,
            timestamp=transaction.created_at
        )
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"Payment processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")


@app.post("/api/v1/refunds")
async def process_refund(
    refund_req: RefundRequest,
    db_session=Depends(get_db_session)
):
    """
    Process a refund for a previous transaction
    
    Risk: Retry logic without exponential backoff
    """
    try:
        # Fetch original transaction
        transaction = payment_processor.get_transaction(
            db_session, 
            refund_req.transaction_id
        )
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        refund_amount = refund_req.amount or transaction.amount
        
        # Retry logic for refund (RISK: no exponential backoff)
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                refund_response = payment_gateway.refund(
                    transaction_id=transaction.gateway_transaction_id,
                    amount=refund_amount
                )
                break
            except Exception as e:
                retry_count += 1
                logger.warning(f"Refund attempt {retry_count} failed: {str(e)}")
                if retry_count >= max_retries:
                    raise
                # RISK: Fixed delay, no exponential backoff
                import time
                time.sleep(1)
        
        # Record refund
        refund = payment_processor.create_refund(
            db_session=db_session,
            transaction_id=transaction.id,
            amount=refund_amount,
            reason=refund_req.reason,
            gateway_response=refund_response
        )
        
        db_session.commit()
        
        return {
            "refund_id": refund.id,
            "status": "completed",
            "amount": refund_amount
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        logger.error(f"Refund processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Refund failed: {str(e)}")


@app.get("/api/v1/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    db_session=Depends(get_db_session)
):
    """Get transaction details"""
    transaction = payment_processor.get_transaction(db_session, transaction_id)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "transaction_id": transaction.id,
        "order_id": transaction.order_id,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "status": transaction.status,
        "created_at": transaction.created_at
    }


@app.get("/api/v1/transactions")
async def list_transactions(
    customer_id: Optional[str] = None,
    limit: int = 100,
    db_session=Depends(get_db_session)
):
    """List transactions with optional filtering"""
    transactions = payment_processor.list_transactions(
        db_session,
        customer_id=customer_id,
        limit=limit
    )
    
    return {
        "transactions": [
            {
                "transaction_id": t.id,
                "order_id": t.order_id,
                "amount": t.amount,
                "status": t.status,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

# Made with Bob
