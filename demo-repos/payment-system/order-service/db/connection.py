"""
Database Connection Management for Order Service
"""
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://order_user:order_pass@localhost:5432/order_db"
)

# RISK: Small connection pool size
# RISK: No max_overflow means no buffer for traffic spikes
engine = create_engine(
    DATABASE_URL,
    pool_size=8,  # RISK: Small pool for high-traffic service
    max_overflow=0,  # RISK: No overflow connections
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session() -> Session:
    """
    Dependency function for FastAPI to get database session
    
    RISK: Long-running queries can hold connections
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions
    Use for background tasks
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Order database tables initialized")


class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    items = Column(JSON, nullable=False)  # RISK: Storing JSON in relational DB
    shipping_address = Column(JSON)
    payment_transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrderEvent(Base):
    """Order event log for audit trail"""
    __tablename__ = "order_events"
    
    id = Column(String, primary_key=True)
    order_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# Made with Bob
