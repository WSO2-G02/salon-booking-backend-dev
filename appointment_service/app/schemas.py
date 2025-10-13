"""
Pydantic models for Appointment Service.
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

class AppointmentStatus(str, Enum):
    """Appointment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class AppointmentBase(BaseModel):
    """Base appointment schema"""
    user_id: int
    staff_id: int
    service_id: int
    appointment_datetime: datetime
    duration_minutes: int
    service_price: Decimal
    customer_notes: Optional[str] = None
    
    @validator('appointment_datetime')
    def appointment_in_future(cls, v):
        if v <= datetime.now():
            raise ValueError('Appointment must be in the future')
        return v
    
    @validator('duration_minutes')
    def duration_positive(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        return v

class AppointmentCreate(AppointmentBase):
    """Schema for creating appointments"""
    pass

class AppointmentUpdate(BaseModel):
    """Schema for updating appointments"""
    appointment_datetime: Optional[datetime] = None
    customer_notes: Optional[str] = None
    staff_notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None

class AppointmentResponse(AppointmentBase):
    """Schema for appointment responses"""
    id: int
    status: AppointmentStatus
    staff_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BookingRequest(BaseModel):
    """Schema for booking requests"""
    service_id: int
    staff_id: int
    appointment_datetime: datetime
    customer_notes: Optional[str] = None

class BookingResponse(BaseModel):
    """Schema for booking responses"""
    appointment_id: int
    status: str
    message: str
    estimated_confirmation_time: Optional[datetime] = None

# Event schemas for RabbitMQ messaging
class AppointmentEvent(BaseModel):
    """Base schema for appointment events"""
    appointment_id: int
    user_id: int
    staff_id: int
    service_id: int
    appointment_datetime: datetime
    event_type: str
    timestamp: datetime = datetime.now()

class AppointmentBookedEvent(AppointmentEvent):
    """Event published when appointment is booked"""
    event_type: str = "appointment_booked"
    service_price: Decimal
    customer_notes: Optional[str] = None

class AppointmentConfirmedEvent(AppointmentEvent):
    """Event published when appointment is confirmed"""
    event_type: str = "appointment_confirmed"
    confirmed_at: datetime

class AppointmentCancelledEvent(AppointmentEvent):
    """Event published when appointment is cancelled"""
    event_type: str = "appointment_cancelled"
    cancelled_at: datetime
    cancellation_reason: Optional[str] = None