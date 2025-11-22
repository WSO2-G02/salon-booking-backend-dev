"""
Pydantic Models for Notification Service
Request and Response schemas for email notifications
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ============================================================================
# Email Request Schemas
# ============================================================================

class RegisterUserEmail(BaseModel):
    """Request model for user registration email"""
    email: EmailStr = Field(..., description="Recipient email address")
    full_name: str = Field(..., description="User's full name")
    username: str = Field(..., description="User's username")


class ResetPasswordEmail(BaseModel):
    """Request model for password reset email"""
    email: EmailStr = Field(..., description="Recipient email address")
    full_name: str = Field(..., description="User's full name")
    reset_token: str = Field(..., description="Password reset token/link")
    expiry_minutes: int = Field(default=30, description="Token expiry in minutes")


class CreateStaffEmail(BaseModel):
    """Request model for new staff member notification email"""
    email: EmailStr = Field(..., description="Staff email address")
    full_name: str = Field(..., description="Staff full name")
    position: str = Field(..., description="Staff position")
    username: str = Field(..., description="Staff username")
    temporary_password: Optional[str] = Field(None, description="Temporary password if generated")


class CreateAppointmentEmail(BaseModel):
    """Request model for appointment creation email"""
    email: EmailStr = Field(..., description="Customer email address")
    customer_name: str = Field(..., description="Customer name")
    service_name: str = Field(..., description="Service booked")
    staff_name: str = Field(..., description="Staff member name")
    appointment_datetime: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(..., description="Service duration")
    price: float = Field(..., description="Service price")
    appointment_id: int = Field(..., description="Appointment ID")


class UpdateAppointmentEmail(BaseModel):
    """Request model for appointment update email"""
    email: EmailStr = Field(..., description="Customer email address")
    customer_name: str = Field(..., description="Customer name")
    service_name: str = Field(..., description="Service name")
    staff_name: str = Field(..., description="Staff member name")
    old_datetime: datetime = Field(..., description="Previous appointment datetime")
    new_datetime: datetime = Field(..., description="New appointment datetime")
    appointment_id: int = Field(..., description="Appointment ID")
    change_reason: Optional[str] = Field(None, description="Reason for change")


class CancelAppointmentEmail(BaseModel):
    """Request model for appointment cancellation email"""
    email: EmailStr = Field(..., description="Customer email address")
    customer_name: str = Field(..., description="Customer name")
    service_name: str = Field(..., description="Service name")
    staff_name: str = Field(..., description="Staff member name")
    appointment_datetime: datetime = Field(..., description="Original appointment datetime")
    appointment_id: int = Field(..., description="Appointment ID")
    cancellation_reason: Optional[str] = Field(None, description="Reason for cancellation")


# ============================================================================
# Response Schemas
# ============================================================================

class EmailResponse(BaseModel):
    """Response model for email operations"""
    status: str = "success"
    message: str
    email_sent_to: str
    email_type: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] = None