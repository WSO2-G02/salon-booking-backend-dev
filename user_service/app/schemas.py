"""
Pydantic Models for User Service
Request and Response schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime
import re


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    """Request model for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric with underscores only')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginRequest(BaseModel):
    """Request model for user login"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response model for token issuance"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class RefreshTokenRequest(BaseModel):
    """Request model for refreshing access token"""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Response model for access token refresh"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================================================
# User Profile Schemas
# ============================================================================

class UserProfileResponse(BaseModel):
    """Response model for user profile"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    user_type: Literal['user', 'admin']
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class PasswordChangeRequest(BaseModel):
    """Request model for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


# ============================================================================
# Admin User Management Schemas
# ============================================================================

class UserCreateRequest(BaseModel):
    """Request model for admin to create a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    user_type: Literal['user', 'admin'] = 'user'
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric with underscores only')
        return v


class UserListResponse(BaseModel):
    """Response model for single user in list"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    user_type: Literal['user', 'admin']
    is_active: bool
    created_at: datetime


class PaginationParams(BaseModel):
    """Query parameters for pagination"""
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)


# ============================================================================
# Standard API Response Schemas
# ============================================================================

class SuccessResponse(BaseModel):
    """Standard success response"""
    status: str = "success"
    data: Optional[dict] = None
    message: str = "Operation completed successfully"


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    status: str = "success"
    data: list
    pagination: dict
    
    @staticmethod
    def create(data: list, total: int, page: int, limit: int):
        """Helper to create paginated response"""
        total_pages = (total + limit - 1) // limit
        return PaginatedResponse(
            status="success",
            data=data,
            pagination={
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages
            }
        )