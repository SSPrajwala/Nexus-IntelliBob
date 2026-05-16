"""
Auth Service - Main API Entry Point
Handles authentication, authorization, and token management
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime, timedelta
import logging
import jwt
import bcrypt

from db.session import get_db_session
from middleware.token_validator import TokenValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auth Service", version="1.0.0")

# Initialize token validator
token_validator = TokenValidator()

# RISK: Hardcoded secret key in production-like code
JWT_SECRET = "super_secret_key_12345"  # RISK: Should be in env var
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(
    login_req: LoginRequest,
    db_session=Depends(get_db_session)
):
    """
    Authenticate user and return JWT token
    
    RISK: No rate limiting on login attempts
    RISK: No account lockout after failed attempts
    """
    from db.session import User
    
    try:
        # Query user (RISK: no index on username)
        user = db_session.query(User).filter(
            User.username == login_req.username
        ).first()
        
        if not user:
            # RISK: Generic error message reveals if user exists
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not bcrypt.checkpw(
            login_req.password.encode('utf-8'),
            user.password_hash.encode('utf-8')
        ):
            logger.warning(f"Failed login attempt for user {login_req.username}")
            # RISK: No tracking of failed attempts
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate JWT token
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        }
        
        access_token = jwt.encode(
            token_data,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        # Update last login (RISK: session not properly managed)
        user.last_login = datetime.utcnow()
        db_session.commit()
        
        logger.info(f"User {login_req.username} logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            expires_in=TOKEN_EXPIRY_HOURS * 3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@app.post("/api/v1/auth/register")
async def register(
    user_reg: UserRegistration,
    db_session=Depends(get_db_session)
):
    """
    Register a new user
    
    RISK: No email verification
    RISK: Weak password policy
    """
    from db.session import User
    import uuid
    
    try:
        # Check if user exists (RISK: race condition possible)
        existing_user = db_session.query(User).filter(
            (User.username == user_reg.username) | (User.email == user_reg.email)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # RISK: No password strength validation
        if len(user_reg.password) < 6:
            raise HTTPException(status_code=400, detail="Password too short")
        
        # Hash password
        password_hash = bcrypt.hashpw(
            user_reg.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            username=user_reg.username,
            email=user_reg.email,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        
        db_session.add(user)
        db_session.commit()
        
        logger.info(f"New user registered: {user_reg.username}")
        
        return {
            "user_id": user.id,
            "username": user.username,
            "message": "Registration successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/api/v1/auth/validate")
async def validate_token(
    authorization: Optional[str] = Header(None)
):
    """
    Validate JWT token
    
    RISK: No token revocation mechanism
    RISK: No refresh token support
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    
    try:
        # Decode and validate token
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        
        # RISK: No check if user still exists or is active
        return {
            "valid": True,
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "exp": payload.get("exp")
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/api/v1/auth/logout")
async def logout(
    authorization: Optional[str] = Header(None)
):
    """
    Logout user
    
    RISK: No actual token invalidation (stateless JWT)
    RISK: Token remains valid until expiry
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    
    # RISK: Cannot actually invalidate JWT without token blacklist
    logger.info("Logout requested (token still valid until expiry)")
    
    return {
        "message": "Logged out successfully",
        "note": "Token will remain valid until expiry"
    }


@app.get("/api/v1/users/{user_id}")
async def get_user(
    user_id: str,
    authorization: Optional[str] = Header(None),
    db_session=Depends(get_db_session)
):
    """
    Get user information
    
    RISK: No authorization check (any authenticated user can view any user)
    """
    from db.session import User
    
    # Validate token (RISK: minimal validation)
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = db_session.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # RISK: Returning sensitive information
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,  # RISK: Email exposed
        "created_at": user.created_at,
        "last_login": user.last_login
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

# Made with Bob
