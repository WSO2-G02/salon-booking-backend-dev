"""
Pydantic models for request/response validation.
These models define the API contract - what data comes in and goes out.
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """
    Base user schema with common fields.
    This is inherited by other schemas to avoid duplication.
    """
    email: EmailStr  # Automatically validates email format
    username: str
    full_name: str
    phone: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username contains only alphanumeric characters and underscores"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v
    
    @validator('phone')
    def phone_format(cls, v):
        """Basic phone number validation"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, +, -, and spaces')
        return v

class UserCreate(UserBase):
    """
    Schema for user registration.
    Includes password field which is not stored directly.
    """
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        """Enforce password strength requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    """Schema for user login requests"""
    username: str  # Can be username or email
    password: str

class UserResponse(UserBase):
    """
    Schema for user data in responses.
    Excludes sensitive information like password hash.
    """
    id: int
    is_active: bool
    is_staff: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True  # Allow creation from SQLAlchemy models

class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None