"""
Pydantic models for Staff Management API.
"""
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal

class StaffBase(BaseModel):
    """Base staff schema"""
    user_id: int
    employee_id: str
    position: str
    specialties: Optional[List[str]] = []
    experience_years: int = 0
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    hire_date: Optional[date] = None
    is_active: bool = True
    
    @validator('employee_id')
    def employee_id_format(cls, v):
        if not v.strip():
            raise ValueError('Employee ID cannot be empty')
        return v.strip().upper()
    
    @validator('experience_years')
    def experience_positive(cls, v):
        if v < 0:
            raise ValueError('Experience years cannot be negative')
        return v

class StaffCreate(StaffBase):
    """Schema for creating new staff members"""
    pass

class StaffUpdate(BaseModel):
    """Schema for updating staff information"""
    position: Optional[str] = None
    specialties: Optional[List[str]] = None
    experience_years: Optional[int] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    is_active: Optional[bool] = None

class StaffResponse(StaffBase):
    """Schema for staff responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AvailabilityBase(BaseModel):
    """Base availability schema"""
    staff_id: int
    date: date
    start_time: time
    end_time: time
    availability_type: str = "work"
    is_available: bool = True
    notes: Optional[str] = None
    
    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class AvailabilityCreate(AvailabilityBase):
    """Schema for creating availability slots"""
    pass

class AvailabilityResponse(AvailabilityBase):
    """Schema for availability responses"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TimeSlot(BaseModel):
    """Schema for available time slots"""
    start_time: time
    end_time: time
    duration_minutes: int

class StaffAvailabilityResponse(BaseModel):
    """Schema for staff availability on a specific date"""
    staff_id: int
    date: date
    available_slots: List[TimeSlot]
    total_available_minutes: int