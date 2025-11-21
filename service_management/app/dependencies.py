"""
FastAPI Dependencies for Authentication and Authorization
Validates tokens from User Service database
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import logging

from app.auth import JWTValidator
from app.database import get_db_manager, DatabaseManager
from app.config import get_settings

logger = logging.getLogger(__name__)

# Load JWT settings from config (which loads from .env)
settings = get_settings()

# Initialize JWT validator
jwt_validator = JWTValidator(settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db_manager)
) -> dict:
    """
    Dependency to get the current authenticated user from JWT token
    Validates token and checks user exists in users table
    
    Args:
        authorization: Authorization header with Bearer token
        db: Database manager instance
    
    Returns:
        User dictionary with user details
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization:
        raise credentials_exception
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise credentials_exception
    
    token = parts[1]
    
    # Decode and validate token
    payload = jwt_validator.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Verify token type
    if not jwt_validator.verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # Fetch user from database to verify it still exists and is active
    query = """
        SELECT id, username, email, full_name, phone, user_type, is_active,
               created_at, updated_at
        FROM users
        WHERE id = %s AND is_active = 1
    """
    
    try:
        user = db.execute_query(query, (user_id,), fetch_one=True)
        if not user:
            raise credentials_exception
        
        return user
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise credentials_exception


async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure current user is an admin
    Service management requires admin privileges for write operations
    
    Args:
        current_user: Current authenticated user from get_current_user
    
    Returns:
        User dictionary if user is admin
    
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


async def get_authenticated_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency for endpoints that require authentication but not admin
    
    Args:
        current_user: Current authenticated user from get_current_user
    
    Returns:
        User dictionary
    """
    return current_user