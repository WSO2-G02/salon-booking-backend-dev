"""
Pydantic Models for Service Management
Request and Response schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============================================================================
# Service Schemas
# ============================================================================

class ServiceCreate(BaseModel):
    """Request model for creating a new service"""
    name: str = Field(..., min_length=1, max_length=100, description="Service name")
    description: Optional[str] = Field(None, description="Service description")
    category: Optional[str] = Field(None, max_length=50, description="Service category")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Service price")
    duration_minutes: int = Field(..., gt=0, description="Service duration in minutes")
    
    @field_validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Service name cannot be empty')
        return v.strip()
    
    @field_validator('price')
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than zero')
        return v
    
    @field_validator('duration_minutes')
    def duration_positive(cls, v):
        if v <= 0:
            raise ValueError('Duration must be greater than zero')
        if v > 1440:  # 24 hours
            raise ValueError('Duration cannot exceed 24 hours (1440 minutes)')
        return v


class ServiceUpdate(BaseModel):
    """Request model for updating a service"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    
    @field_validator('price')
    def price_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than zero')
        return v
    
    @field_validator('duration_minutes')
    def duration_positive(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Duration must be greater than zero')
            if v > 1440:
                raise ValueError('Duration cannot exceed 24 hours (1440 minutes)')
        return v


class ServiceResponse(BaseModel):
    """Response model for service"""
    id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    price: Decimal
    duration_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


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