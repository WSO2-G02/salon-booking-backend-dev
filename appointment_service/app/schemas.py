"""
Pydantic Models for Appointment Service
Request and Response schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============================================================================
# Appointment Schemas
# ============================================================================

class AppointmentCreate(BaseModel):
    """Request model for creating a new appointment"""
    user_id: int = Field(..., description="Customer user ID")
    staff_id: int = Field(..., description="Staff member ID")
    service_id: int = Field(..., description="Service ID")
    appointment_datetime: datetime = Field(..., description="Appointment date and time")
    customer_notes: Optional[str] = Field(None, max_length=500, description="Customer notes or requests")
    
    @field_validator('appointment_datetime')
    def datetime_not_past(cls, v):
        if v < datetime.now():
            raise ValueError('Appointment datetime cannot be in the past')
        return v


class AppointmentUpdate(BaseModel):
    """Request model for updating an appointment"""
    staff_id: Optional[int] = None
    service_id: Optional[int] = None
    appointment_datetime: Optional[datetime] = None
    status: Optional[str] = None
    customer_notes: Optional[str] = Field(None, max_length=500)
    staff_notes: Optional[str] = Field(None, max_length=500)
    cancellation_reason: Optional[str] = Field(None, max_length=500)
    
    @field_validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'no-show']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    @field_validator('appointment_datetime')
    def datetime_not_past(cls, v):
        if v is not None and v < datetime.now():
            raise ValueError('Appointment datetime cannot be in the past')
        return v


class AppointmentResponse(BaseModel):
    """Response model for appointment"""
    id: int
    user_id: int
    staff_id: int
    service_id: int
    appointment_datetime: datetime
    duration_minutes: int
    service_price: Decimal
    status: str
    customer_notes: Optional[str]
    staff_notes: Optional[str]
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class AppointmentDetailResponse(BaseModel):
    """Detailed appointment response with related information"""
    id: int
    user_id: int
    user_name: Optional[str]
    user_email: Optional[str]
    user_phone: Optional[str]
    staff_id: int
    staff_name: Optional[str]
    staff_position: Optional[str]
    service_id: int
    service_name: Optional[str]
    appointment_datetime: datetime
    duration_minutes: int
    service_price: Decimal
    status: str
    customer_notes: Optional[str]
    staff_notes: Optional[str]
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
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