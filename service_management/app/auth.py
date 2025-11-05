"""
Authentication and Authorization Module
Handles token validation and user verification.
"""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from common.database import get_db
from common.security import verify_token

class TokenData:
    """Token data structure"""
    def __init__(self, user_id: int, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> TokenData:
    """
    Validate access token.
    
    SIMPLIFIED VERSION FOR TESTING:
    - Validates JWT token signature and expiration
    - Extracts user information from token
    - TODO: Add session table validation once User Service is running
    
    Args:
        authorization: Authorization header containing Bearer token
        db: Database session
    
    Returns:
        TokenData: Authenticated user information
    
    Raises:
        HTTPException 401: If token is invalid or missing
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extract access token from Authorization header
    if not authorization:
        raise credentials_exception
    
    try:
        scheme, access_token = authorization.split()
        if scheme.lower() != 'bearer':
            raise credentials_exception
    except ValueError:
        raise credentials_exception
    
    # Decode and verify access token
    payload = verify_token(access_token)
    if not payload:
        raise credentials_exception
    
    user_id: int = payload.get("user_id")
    email: str = payload.get("email")
    role: str = payload.get("role")
    
    if user_id is None:
        raise credentials_exception
    
    # ============================================================
    # STEP 05 IMPLEMENTATION (Currently Disabled for Testing)
    # ============================================================
    # TODO: Enable this once User Service creates the session table
    #
    # from sqlalchemy import text
    # query = text("""
    #     SELECT refresh_token, user_id 
    #     FROM session 
    #     WHERE user_id = :user_id 
    #     AND is_active = true
    #     ORDER BY created_at DESC 
    #     LIMIT 1
    # """)
    # 
    # result = db.execute(query, {"user_id": user_id}).fetchone()
    # 
    # if not result:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="No active session found"
    #     )
    # 
    # refresh_token = result[0]
    # if not refresh_token:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid session"
    #     )
    # 
    # refresh_payload = verify_token(refresh_token)
    # if not refresh_payload:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Refresh token expired or invalid"
    #     )
    # 
    # if refresh_payload.get("user_id") != user_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Token mismatch"
    #     )
    # ============================================================
    
    print(f"✅ Authenticated user: {email} (user_id={user_id}, role={role})")
    
    return TokenData(user_id=user_id, email=email, role=role)


async def require_admin(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency to ensure only admin users can access endpoint.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        TokenData: User information if admin
    
    Raises:
        HTTPException 403: If user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    print(f"✅ Admin access granted for user_id={current_user.user_id}")
    
    return current_user