"""
Order Handler Service
Core business logic for order management
"""
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderHandler:
    """
    Handles order business logic and database operations
    """
    
    def __init__(self):
        # RISK: Shared mutable state without thread safety
        self._order_cache = {}
        self._processing_orders = set()
    
    def create_order(
        self,
        db_session: Session,
        customer_id: str,
        items: List[dict],
        total_amount: float,
        shipping_address: dict
    ):
        """
        Create a new order
        
        RISK: No validation of items structure
        RISK: No check for duplicate order creation
        """
        from db.connection import Order, OrderEvent
        
        order_id = str(uuid.uuid4())
        
        # RISK: No validation that items list is not empty
        order = Order(
            id=order_id,
            customer_id=customer_id,
            status="pending",
            total_amount=total_amount,
            items=items,  # RISK: Storing complex JSON without schema validation
            shipping_address=shipping_address,
            created_at=datetime.utcnow()
        )
        
        db_session.add(order)
        
        # Create order event
        event = OrderEvent(
            id=str(uuid.uuid4()),
            order_id=order_id,
            event_type="order_created",
            event_data={
                "customer_id": customer_id,
                "total_amount": total_amount,
                "item_count": len(items)
            },
            created_at=datetime.utcnow()
        )
        
        db_session.add(event)
        
        # Add to processing set (RISK: not thread-safe)
        self._processing_orders.add(order_id)
        
        logger.info(f"Created order {order_id} for customer {customer_id}")
        return order
    
    def get_order(self, db_session: Session, order_id: str):
        """
        Retrieve order by ID
        
        RISK: Cache without TTL or invalidation
        """
        from db.connection import Order
        
        # Check cache first (RISK: stale data)
        if order_id in self._order_cache:
            cached_order = self._order_cache[order_id]
            # RISK: No check if cached data is stale
            return cached_order
        
        order = db_session.query(Order).filter(
            Order.id == order_id
        ).first()
        
        if order:
            # Cache the order (RISK: unbounded cache growth)
            self._order_cache[order_id] = order
        
        return order
    
    def update_order_status(
        self,
        db_session: Session,
        order_id: str,
        new_status: str
    ):
        """
        Update order status
        
        RISK: No state machine validation
        RISK: No optimistic locking
        """
        from db.connection import Order, OrderEvent
        
        order = db_session.query(Order).filter(
            Order.id == order_id
        ).first()
        
        if order:
            old_status = order.status
            order.status = new_status
            order.updated_at = datetime.utcnow()
            
            # Log status change
            event = OrderEvent(
                id=str(uuid.uuid4()),
                order_id=order_id,
                event_type="status_changed",
                event_data={
                    "old_status": old_status,
                    "new_status": new_status
                },
                created_at=datetime.utcnow()
            )
            
            db_session.add(event)
            
            # Invalidate cache
            if order_id in self._order_cache:
                del self._order_cache[order_id]
            
            # Remove from processing set if completed
            if new_status in ["completed", "cancelled", "failed"]:
                self._processing_orders.discard(order_id)
            
            logger.info(f"Updated order {order_id} status: {old_status} -> {new_status}")
            return order
        
        return None
    
    def update_order_payment(
        self,
        db_session: Session,
        order_id: str,
        transaction_id: str
    ):
        """
        Update order with payment transaction ID
        """
        from db.connection import Order, OrderEvent
        
        order = db_session.query(Order).filter(
            Order.id == order_id
        ).first()
        
        if order:
            order.payment_transaction_id = transaction_id
            order.status = "paid"
            order.updated_at = datetime.utcnow()
            
            event = OrderEvent(
                id=str(uuid.uuid4()),
                order_id=order_id,
                event_type="payment_completed",
                event_data={
                    "transaction_id": transaction_id
                },
                created_at=datetime.utcnow()
            )
            
            db_session.add(event)
            
            # Invalidate cache
            if order_id in self._order_cache:
                del self._order_cache[order_id]
            
            logger.info(f"Updated order {order_id} with payment {transaction_id}")
            return order
        
        return None
    
    def list_orders(
        self,
        db_session: Session,
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List:
        """
        List orders with filtering
        
        RISK: No pagination offset
        RISK: Large limit without controls
        RISK: No query timeout
        """
        from db.connection import Order
        
        query = db_session.query(Order)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        # RISK: Could return huge result set
        orders = query.order_by(
            Order.created_at.desc()
        ).limit(limit).all()
        
        return orders
    
    def get_order_events(
        self,
        db_session: Session,
        order_id: str
    ) -> List:
        """
        Get event history for an order
        
        RISK: No limit on events returned
        """
        from db.connection import OrderEvent
        
        events = db_session.query(OrderEvent).filter(
            OrderEvent.order_id == order_id
        ).order_by(
            OrderEvent.created_at.asc()
        ).all()
        
        return events
    
    def get_processing_orders_count(self) -> int:
        """
        Get count of orders currently being processed
        Useful for monitoring
        """
        return len(self._processing_orders)

# Made with Bob
