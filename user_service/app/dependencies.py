"""
FastAPI Dependencies for Authentication and Authorization
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import logging

from app.auth import jwt_manager
from app.database import get_db_manager, DatabaseManager

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db_manager)
) -> dict:
    """
    Dependency to get the current authenticated user from JWT token
    
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
    payload = jwt_manager.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Verify token type
    if not jwt_manager.verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # Fetch user from database
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


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: DatabaseManager = Depends(get_db_manager)
) -> Optional[dict]:
    """
    Dependency to optionally get current user (doesn't raise if no token)
    Used for endpoints that work differently for authenticated users
    
    Args:
        authorization: Authorization header with Bearer token
        db: Database manager instance
    
    Returns:
        User dictionary if authenticated, None otherwise
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, db)
    except HTTPException:
        return None