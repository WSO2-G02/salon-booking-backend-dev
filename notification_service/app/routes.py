"""
Notification Service API Routes
Implements all REST API endpoints for sending email notifications
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
import logging

from app.schemas import (
    RegisterUserEmail, ResetPasswordEmail, CreateStaffEmail,
    CreateAppointmentEmail, UpdateAppointmentEmail, CancelAppointmentEmail,
    EmailResponse
)
from app.services import get_email_service, EmailService
from app.database import get_db_manager, DatabaseManager
from app.dependencies import get_authenticated_user, get_current_admin

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)


# ============================================================================
# Email Notification Endpoints
# ============================================================================

@router.post("/email/register-user", response_model=EmailResponse)
async def send_register_user_email(
    email_data: RegisterUserEmail,
    email_service: EmailService = Depends(get_email_service)
):
    """
    Send welcome email to newly registered user
    
    - **email**: Recipient email address
    - **full_name**: User's full name
    - **username**: User's username
    
    Note: This endpoint is typically called internally by User Service
    """
    try:
        result = email_service.send_register_user_email(
            email=email_data.email,
            full_name=email_data.full_name,
            username=email_data.username
        )
        return EmailResponse(**result)
    
    except ValueError as e:
        logger.error(f"Failed to send registration email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


@router.post("/email/reset-password", response_model=EmailResponse)
async def send_reset_password_email(
    email_data: ResetPasswordEmail,
    email_service: EmailService = Depends(get_email_service)
):
    """
    Send password reset email
    
    - **email**: Recipient email address
    - **full_name**: User's full name
    - **reset_token**: Password reset token/link
    - **expiry_minutes**: Token expiry time (default: 30)
    
    Note: This endpoint is typically called internally by User Service
    """
    try:
        result = email_service.send_reset_password_email(
            email=email_data.email,
            full_name=email_data.full_name,
            reset_token=email_data.reset_token,
            expiry_minutes=email_data.expiry_minutes
        )
        return EmailResponse(**result)
    
    except ValueError as e:
        logger.error(f"Failed to send password reset email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


@router.post("/email/create-staff", response_model=EmailResponse)
async def send_create_staff_email(
    email_data: CreateStaffEmail,
    current_admin: Dict = Depends(get_current_admin),
    email_service: EmailService = Depends(get_email_service)
):
    """
    Send welcome email to new staff member (Admin only)
    
    - **email**: Staff email address
    - **full_name**: Staff full name
    - **position**: Staff position
    - **username**: Staff username
    - **temporary_password**: Temporary password (optional)
    
    Requires: Admin access token
    """
    try:
        result = email_service.send_create_staff_email(
            email=email_data.email,
            full_name=email_data.full_name,
            position=email_data.position,
            username=email_data.username,
            temporary_password=email_data.temporary_password
        )
        return EmailResponse(**result)
    
    except ValueError as e:
        logger.error(f"Failed to send staff welcome email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


@router.post("/email/create-appointment", response_model=EmailResponse)
async def send_create_appointment_email(
    email_data: CreateAppointmentEmail,
    current_user: Dict = Depends(get_authenticated_user),
    email_service: EmailService = Depends(get_email_service)
):
    """
    Send appointment confirmation email (Authenticated users)
    
    - **email**: Customer email address
    - **customer_name**: Customer name
    - **service_name**: Service booked
    - **staff_name**: Staff member name
    - **appointment_datetime**: Appointment date and time
    - **duration_minutes**: Service duration
    - **price**: Service price
    - **appointment_id**: Appointment ID
    
    Requires: Valid access token
    """
    try:
        result = email_service.send_create_appointment_email(
            email=email_data.email,
            customer_name=email_data.customer_name,
            service_name=email_data.service_name,
            staff_name=email_data.staff_name,
            appointment_datetime=email_data.appointment_datetime,
            duration_minutes=email_data.duration_minutes,
            price=email_data.price,
            appointment_id=email_data.appointment_id
        )
        return EmailResponse(**result)
    
    except ValueError as e:
        logger.error(f"Failed to send appointment confirmation email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


@router.post("/email/update-appointment", response_model=EmailResponse)
async def send_update_appointment_email(
    email_data: UpdateAppointmentEmail,
    current_user: Dict = Depends(get_authenticated_user),
    email_service: EmailService = Depends(get_email_service)
):
    """
    Send appointment update notification email (Authenticated users)
    
    - **email**: Customer email address
    - **customer_name**: Customer name
    - **service_name**: Service name
    - **staff_name**: Staff member name
    - **old_datetime**: Previous appointment datetime
    - **new_datetime**: New appointment datetime
    - **appointment_id**: Appointment ID
    - **change_reason**: Reason for change (optional)
    
    Requires: Valid access token
    """
    try:
        result = email_service.send_update_appointment_email(
            email=email_data.email,
            customer_name=email_data.customer_name,
            service_name=email_data.service_name,
            staff_name=email_data.staff_name,
            old_datetime=email_data.old_datetime,
            new_datetime=email_data.new_datetime,
            appointment_id=email_data.appointment_id,
            change_reason=email_data.change_reason
        )
        return EmailResponse(**result)
    
    except ValueError as e:
        logger.error(f"Failed to send appointment update email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


@router.post("/email/cancel-appointment", response_model=EmailResponse)
async def send_cancel_appointment_email(
    email_data: CancelAppointmentEmail,
    current_user: Dict = Depends(get_authenticated_user),
    email_service: EmailService = Depends(get_email_service)
):
    """
    Send appointment cancellation email (Authenticated users)
    
    - **email**: Customer email address
    - **customer_name**: Customer name
    - **service_name**: Service name
    - **staff_name**: Staff member name
    - **appointment_datetime**: Original appointment datetime
    - **appointment_id**: Appointment ID
    - **cancellation_reason**: Reason for cancellation (optional)
    
    Requires: Valid access token
    """
    try:
        result = email_service.send_cancel_appointment_email(
            email=email_data.email,
            customer_name=email_data.customer_name,
            service_name=email_data.service_name,
            staff_name=email_data.staff_name,
            appointment_datetime=email_data.appointment_datetime,
            appointment_id=email_data.appointment_id,
            cancellation_reason=email_data.cancellation_reason
        )
        return EmailResponse(**result)
    
    except ValueError as e:
        logger.error(f"Failed to send appointment cancellation email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get("/health")
async def health_check(db: DatabaseManager = Depends(get_db_manager)):
    """
    Health check endpoint to verify service and database status
    """
    db_healthy = db.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "notification_service",
        "database": "connected" if db_healthy else "disconnected",
        "smtp_configured": bool(get_email_service().smtp_user)
    }