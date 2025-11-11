from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List, Optional
from datetime import datetime, date, time
import json


# STAFF BASE SCHEMA
class StaffBase(BaseModel):
    """Base schema shared by create and response."""
    user_id: int = Field(..., description="Reference to user service")
    employee_id: str = Field(..., description="Internal employee code")
    position: str
    specialties: Optional[List[str]] = Field(default_factory=list) 
    experience_years: int = 0
    hire_date: Optional[date] = None
    is_active: bool = True

    # VALIDATORS
    @field_validator("employee_id")
    def employee_id_format(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee ID cannot be empty")
        return v.strip().upper()

    @field_validator("experience_years")
    def experience_positive(cls, v):
        if v < 0:
            raise ValueError("Experience years cannot be negative")
        return v



# STAFF CREATE SCHEMA
class StaffCreate(StaffBase):
    """Schema for creating new staff."""
    pass



# STAFF UPDATE SCHEMA
class StaffUpdate(BaseModel):
    """Fields that can be updated."""
    position: Optional[str] = None
    specialties: Optional[List[str]] = None
    experience_years: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("experience_years")
    def experience_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("Experience years cannot be negative")
        return v



# STAFF RESPONSE SCHEMA

class StaffResponse(StaffBase):
    """Returned to client."""
    id: int  
    created_at: datetime
    updated_at: Optional[datetime]

    @field_validator("specialties", mode="before")
    def parse_specialties(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)  
            except:
                return []  
        return v

    class Config:
        from_attributes = True  # Works with SQLAlchemy ORM



# AVAILABILITY BASE SCHEMA
class AvailabilityBase(BaseModel):
    staff_id: int
    slot_date: date
    start_time: time
    end_time: time
    availability_type: str = "work"

    
    
    @field_validator("end_time")
    def validate_end_time(cls, v, info: ValidationInfo):
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
          raise ValueError("End time must be after start time")
        return v


class AvailabilityCreate(AvailabilityBase):
    """Used to create availability."""
    pass


class AvailabilityResponse(AvailabilityBase):
    id: int

    class Config:
        from_attributes = True



# AVAILABILITY SLOT SCHEMA
class TimeSlot(BaseModel):
    start_time: time
    end_time: time
    duration_minutes: int


class StaffAvailabilityResponse(BaseModel):
    staff_id: int
    slot_date: date
    available_slots: List[TimeSlot]
    total_available_minutes: int

