"""
Database Session Management for Auth Service
"""
from sqlalchemy import create_engine, Column, String, DateTime, Boolean
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
    "postgresql://auth_user:auth_pass@localhost:5432/auth_db"
)

# RISK: Very small connection pool for authentication service
# RISK: Auth is critical path - small pool causes bottleneck
engine = create_engine(
    DATABASE_URL,
    pool_size=3,  # RISK: Only 3 connections for auth service
    max_overflow=0,  # RISK: No overflow buffer
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session() -> Session:
    """
    Dependency function for FastAPI to get database session
    
    RISK: Session leak if not properly closed
    RISK: No timeout on session acquisition
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # RISK: Close might not be called if exception occurs before yield
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions
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
    logger.info("Auth database tables initialized")


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(String, default="0")  # RISK: Stored as string
    
    # RISK: No indexes on commonly queried fields like last_login
    # RISK: No soft delete mechanism


class Session(Base):
    """
    Session tracking table
    
    RISK: Not actually used for JWT validation (stateless)
    RISK: Sessions accumulate without cleanup
    """
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String, nullable=False)  # RISK: Storing token hash but not using it
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # RISK: No cleanup job for expired sessions
    # RISK: Table grows unbounded


class LoginAttempt(Base):
    """
    Login attempt tracking
    
    RISK: Table exists but not used in login logic
    """
    __tablename__ = "login_attempts"
    
    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, index=True)
    ip_address = Column(String)
    success = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # RISK: No rate limiting based on this data
    # RISK: No cleanup of old attempts

# Made with Bob
