"""
Token Validator Middleware
Handles JWT token validation and user context
"""
import jwt
import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# RISK: Hardcoded secret should match main.py
JWT_SECRET = "super_secret_key_12345"
JWT_ALGORITHM = "HS256"


class TokenValidator:
    """
    Validates JWT tokens and extracts user information
    
    RISK: No token blacklist/revocation mechanism
    RISK: No refresh token support
    """
    
    def __init__(self):
        # RISK: In-memory cache without TTL or size limit
        self._validation_cache = {}
        self._blacklist = set()  # RISK: In-memory, lost on restart
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate JWT token and return payload
        
        RISK: Cache without expiry checking
        RISK: No rate limiting on validation attempts
        """
        # Check cache first (RISK: stale data possible)
        if token in self._validation_cache:
            cached_result = self._validation_cache[token]
            # RISK: Not checking if cached token has expired
            return cached_result
        
        # Check blacklist (RISK: in-memory only)
        if token in self._blacklist:
            logger.warning("Attempted use of blacklisted token")
            return None
        
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token expired")
                return None
            
            # Cache validation result (RISK: unbounded cache)
            self._validation_cache[token] = payload
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token signature expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
    
    def extract_user_id(self, token: str) -> Optional[str]:
        """
        Extract user ID from token
        
        RISK: No validation that user still exists
        """
        payload = self.validate_token(token)
        if payload:
            return payload.get("user_id")
        return None
    
    def extract_username(self, token: str) -> Optional[str]:
        """Extract username from token"""
        payload = self.validate_token(token)
        if payload:
            return payload.get("username")
        return None
    
    def blacklist_token(self, token: str):
        """
        Add token to blacklist
        
        RISK: In-memory blacklist lost on restart
        RISK: No distributed blacklist for multiple instances
        RISK: Blacklist grows unbounded
        """
        self._blacklist.add(token)
        
        # Remove from validation cache
        if token in self._validation_cache:
            del self._validation_cache[token]
        
        logger.info("Token added to blacklist")
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return token in self._blacklist
    
    def clear_cache(self):
        """
        Clear validation cache
        
        RISK: Manual cache clearing, no automatic expiry
        """
        self._validation_cache.clear()
        logger.info("Token validation cache cleared")
    
    def get_cache_size(self) -> int:
        """Get current cache size for monitoring"""
        return len(self._validation_cache)
    
    def get_blacklist_size(self) -> int:
        """Get current blacklist size for monitoring"""
        return len(self._blacklist)
    
    def validate_and_check_permissions(
        self,
        token: str,
        required_permission: str
    ) -> bool:
        """
        Validate token and check if user has required permission
        
        RISK: No actual permission checking implemented
        RISK: Always returns True if token is valid
        """
        payload = self.validate_token(token)
        
        if not payload:
            return False
        
        # RISK: No actual permission system implemented
        # Just checking if user is admin
        is_admin = payload.get("is_admin", False)
        
        # RISK: Simplified permission check
        if required_permission == "admin" and not is_admin:
            return False
        
        return True
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh an existing token
        
        RISK: Not implemented - just validates existing token
        RISK: No refresh token mechanism
        """
        payload = self.validate_token(token)
        
        if not payload:
            return None
        
        # RISK: Should generate new token with extended expiry
        # Currently just returns the same token
        logger.warning("Token refresh not properly implemented")
        return token

# Made with Bob
