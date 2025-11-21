"""
Pydantic Models for Staff Service
Request and Response schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, date, time
import json


# ============================================================================
# Staff Schemas
# ============================================================================

class StaffCreate(BaseModel):
    """Request model for creating a new staff member"""
    user_id: int = Field(..., description="Reference to user service user ID")
    employee_id: str = Field(..., description="Unique employee identifier")
    position: str = Field(..., description="Job position/title")
    specialties: Optional[str] = Field(None, max_length=1000, description="Comma-separated specialties")
    experience_years: Optional[int] = Field(None, ge=0, description="Years of experience")
    hire_date: Optional[date] = Field(None, description="Date of hire")
    
    @field_validator('employee_id')
    def employee_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Employee ID cannot be empty')
        return v.strip().upper()
    
    @field_validator('position')
    def position_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Position cannot be empty')
        return v.strip()


class StaffUpdate(BaseModel):
    """Request model for updating staff member"""
    position: Optional[str] = None
    specialties: Optional[str] = Field(None, max_length=1000)
    experience_years: Optional[int] = Field(None, ge=0)
    hire_date: Optional[date] = None
    is_active: Optional[bool] = None
    
    @field_validator('experience_years')
    def experience_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('Experience years cannot be negative')
        return v


class StaffResponse(BaseModel):
    """Response model for staff member"""
    id: int
    user_id: int
    employee_id: str
    position: str
    specialties: Optional[str]
    experience_years: Optional[int]
    hire_date: Optional[date]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Staff Availability Schemas
# ============================================================================

class AvailabilityCreate(BaseModel):
    """Request model for creating availability slot"""
    staff_id: int
    slot_date: date = Field(..., description="Date of availability")
    start_time: time = Field(..., description="Start time of slot")
    end_time: time = Field(..., description="End time of slot")
    availability_type: str = Field(default="work", description="Type: work, break, unavailable")
    
    @field_validator('availability_type')
    def validate_type(cls, v):
        allowed_types = ['work', 'break', 'unavailable']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {", ".join(allowed_types)}')
        return v
    
    @field_validator('end_time')
    def end_after_start(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v


class AvailabilityResponse(BaseModel):
    """Response model for availability slot"""
    id: int
    staff_id: int
    slot_date: date
    start_time: time
    end_time: time
    availability_type: str
    
    class Config:
        from_attributes = True


class TimeSlot(BaseModel):
    """Time slot for available booking times"""
    start_time: time
    end_time: time
    duration_minutes: int


class StaffAvailabilityResponse(BaseModel):
    """Response with calculated available time slots"""
    staff_id: int
    slot_date: date
    available_slots: List[TimeSlot]
    total_available_minutes: int


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