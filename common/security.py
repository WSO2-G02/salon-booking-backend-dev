"""
Security utilities for authentication and authorization.
Handles JWT token creation/verification and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

# Configuration - Use environment variables in production
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    """Response model for authentication endpoints"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Data structure for JWT token payload"""
    username: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.
    Uses bcrypt's built-in verification which includes salt checking.
    
    Args:
        plain_password: The plain text password from login
        hashed_password: The stored hash from database
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    Automatically generates a unique salt for each password.
    
    Args:
        password: Plain text password to hash
    
    Returns:
        str: Bcrypt hash of the password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing user information (user_id, email, role)
        expires_delta: Custom expiration time, defaults to 30 minutes
    
    Returns:
        str: Encoded JWT token
    
    Example:
        token = create_access_token({
            "user_id": 1,
            "email": "admin@salon.com",
            "role": "admin"
        })
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration to token payload
    to_encode.update({"exp": expire})
    
    # Encode and return JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Dictionary containing user information (user_id, email, role)
        expires_delta: Custom expiration time, defaults to 7 days
    
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    # Set expiration time (longer than access token)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Add expiration and token type to payload
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    # Encode and return JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    Returns the full payload including user_id, email, and role.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload if valid, None if invalid
        
    Example return:
        {
            "user_id": 1,
            "email": "admin@salon.com",
            "role": "admin",
            "exp": 1234567890
        }
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Return the full payload
        return payload
        
    except JWTError as e:
        # Token is invalid, expired, or malformed
        print(f"Token verification failed: {str(e)}")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error in token verification: {str(e)}")
        return None

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verification (for debugging).
    DO NOT USE THIS IN PRODUCTION - use verify_token instead.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload (unverified)
    """
    try:
        # Decode without verification
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        print(f"Token decode failed: {str(e)}")
        return None