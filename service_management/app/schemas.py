"""
Pydantic models for Service Management API.
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ServiceBase(BaseModel):
    """Base service schema"""
    name: str
    description: Optional[str] = None
    category: str
    price: Decimal
    duration_minutes: int
    is_active: bool = True
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Service name cannot be empty')
        return v.strip()
    
    @validator('price')
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('duration_minutes')
    def duration_positive(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        if v > 480:  # 8 hours max
            raise ValueError('Duration cannot exceed 8 hours (480 minutes)')
        return v

class ServiceCreate(ServiceBase):
    """Schema for creating new services"""
    pass

class ServiceUpdate(BaseModel):
    """Schema for updating services"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class ServiceResponse(ServiceBase):
    """Schema for service responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True