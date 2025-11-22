"""
Authentication Utilities for Notification Service
Validates JWT tokens issued by User Service
"""
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class JWTValidator:
    """JWT token validation utilities"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def decode_token(self, token: str) -> Optional[Dict]:
        """
        Decode and validate a JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload dictionary or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def verify_token_type(self, payload: Dict, expected_type: str) -> bool:
        """Verify that a token payload has the expected type"""
        return payload.get("type") == expected_type
    
    def verify_admin_role(self, payload: Dict) -> bool:
        """Verify that the user has admin privileges"""
        return payload.get("user_type") == "admin"