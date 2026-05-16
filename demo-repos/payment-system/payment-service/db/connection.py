"""
Database Connection Management
Handles SQLAlchemy session creation and connection pooling
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://payment_user:payment_pass@localhost:5432/payment_db"
)

# RISK: Small connection pool size can lead to exhaustion under load
# RISK: No overflow pool configured
engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # RISK: Only 5 connections in pool
    max_overflow=0,  # RISK: No overflow connections allowed
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session() -> Session:
    """
    Dependency function for FastAPI to get database session
    
    Risk: Session might not be properly closed if exception occurs
    Risk: No timeout on session acquisition
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
    Use this for background tasks or non-FastAPI code
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
    logger.info("Database tables initialized")


def get_connection_pool_status():
    """
    Get current connection pool status for monitoring
    Useful for detecting pool exhaustion
    """
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }


class Transaction(Base):
    """Transaction model"""
    __tablename__ = "transactions"
    
    from sqlalchemy import Column, String, Float, DateTime, Integer
    from datetime import datetime
    
    id = Column(String, primary_key=True)
    order_id = Column(String, nullable=False, index=True)
    customer_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, nullable=False)
    payment_method = Column(String)
    gateway_transaction_id = Column(String, unique=True)
    idempotency_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Refund(Base):
    """Refund model"""
    __tablename__ = "refunds"
    
    from sqlalchemy import Column, String, Float, DateTime, ForeignKey
    from datetime import datetime
    
    id = Column(String, primary_key=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String)
    status = Column(String, nullable=False)
    gateway_refund_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Made with Bob
