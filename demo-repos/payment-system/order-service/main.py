"""
Order Service - Main API Entry Point
Handles order creation, updates, and fulfillment
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime
import logging
import requests

from db.connection import get_db_session
from services.order_handler import OrderHandler
from services.inventory import InventoryService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Service", version="1.0.0")

# Initialize services
order_handler = OrderHandler()
inventory_service = InventoryService()

# RISK: Hardcoded service URLs without service discovery
PAYMENT_SERVICE_URL = "http://payment-service:8001"
AUTH_SERVICE_URL = "http://auth-service:8003"


class OrderRequest(BaseModel):
    customer_id: str
    items: List[dict]
    shipping_address: dict
    payment_method: str


class OrderResponse(BaseModel):
    order_id: str
    status: str
    total_amount: float
    created_at: datetime


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "order-service"}


@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(
    order_req: OrderRequest,
    background_tasks: BackgroundTasks,
    db_session=Depends(get_db_session)
):
    """
    Create a new order
    
    RISK: Synchronous calls to multiple services without timeout
    RISK: No compensation logic if payment fails after inventory reservation
    """
    try:
        logger.info(f"Creating order for customer {order_req.customer_id}")
        
        # Calculate total amount
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) 
                          for item in order_req.items)
        
        # Step 1: Reserve inventory (RISK: synchronous blocking call)
        inventory_reserved = inventory_service.reserve_inventory(
            order_req.items
        )
        
        if not inventory_reserved:
            raise HTTPException(
                status_code=400, 
                detail="Insufficient inventory"
            )
        
        # Step 2: Create order record
        order = order_handler.create_order(
            db_session=db_session,
            customer_id=order_req.customer_id,
            items=order_req.items,
            total_amount=total_amount,
            shipping_address=order_req.shipping_address
        )
        
        db_session.commit()
        
        # Step 3: Process payment (RISK: synchronous call without timeout)
        try:
            payment_response = requests.post(
                f"{PAYMENT_SERVICE_URL}/api/v1/payments",
                json={
                    "order_id": order.id,
                    "amount": total_amount,
                    "customer_id": order_req.customer_id,
                    "payment_method": order_req.payment_method
                }
                # RISK: No timeout specified
            )
            
            payment_response.raise_for_status()
            payment_data = payment_response.json()
            
            # Update order with payment info
            order_handler.update_order_payment(
                db_session,
                order.id,
                payment_data.get("transaction_id")
            )
            
            db_session.commit()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment failed: {str(e)}")
            # RISK: Inventory already reserved but payment failed
            # No compensation/rollback logic
            order_handler.update_order_status(db_session, order.id, "payment_failed")
            db_session.commit()
            raise HTTPException(
                status_code=500,
                detail="Payment processing failed"
            )
        
        # Schedule fulfillment in background
        background_tasks.add_task(
            process_fulfillment,
            order.id
        )
        
        return OrderResponse(
            order_id=order.id,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        logger.error(f"Order creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")


@app.get("/api/v1/orders/{order_id}")
async def get_order(
    order_id: str,
    db_session=Depends(get_db_session)
):
    """Get order details"""
    order = order_handler.get_order(db_session, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "items": order.items,
        "created_at": order.created_at
    }


@app.put("/api/v1/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    db_session=Depends(get_db_session)
):
    """
    Cancel an order
    
    RISK: No distributed transaction handling
    RISK: Synchronous refund call without timeout
    """
    order = order_handler.get_order(db_session, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status in ["shipped", "delivered"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel order in current status"
        )
    
    try:
        # Release inventory
        inventory_service.release_inventory(order.items)
        
        # Process refund if payment was made (RISK: no timeout)
        if order.payment_transaction_id:
            refund_response = requests.post(
                f"{PAYMENT_SERVICE_URL}/api/v1/refunds",
                json={
                    "transaction_id": order.payment_transaction_id,
                    "reason": "Order cancelled by customer"
                }
                # RISK: No timeout specified
            )
            refund_response.raise_for_status()
        
        # Update order status
        order_handler.update_order_status(db_session, order_id, "cancelled")
        db_session.commit()
        
        return {"status": "cancelled", "order_id": order_id}
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"Order cancellation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Cancellation failed"
        )


@app.get("/api/v1/orders")
async def list_orders(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db_session=Depends(get_db_session)
):
    """
    List orders with optional filtering
    
    RISK: No pagination offset
    RISK: Large limit without proper controls
    """
    orders = order_handler.list_orders(
        db_session,
        customer_id=customer_id,
        status=status,
        limit=limit
    )
    
    return {
        "orders": [
            {
                "order_id": o.id,
                "customer_id": o.customer_id,
                "status": o.status,
                "total_amount": o.total_amount,
                "created_at": o.created_at
            }
            for o in orders
        ]
    }


def process_fulfillment(order_id: str):
    """
    Background task to process order fulfillment
    
    RISK: No error handling or retry logic
    RISK: Database session management in background task
    """
    from db.connection import get_db_context
    
    try:
        with get_db_context() as db:
            order = order_handler.get_order(db, order_id)
            
            if order and order.status == "pending":
                # Simulate fulfillment processing
                logger.info(f"Processing fulfillment for order {order_id}")
                order_handler.update_order_status(db, order_id, "processing")
                
    except Exception as e:
        logger.error(f"Fulfillment processing failed for order {order_id}: {str(e)}")
        # RISK: No retry mechanism


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

# Made with Bob
