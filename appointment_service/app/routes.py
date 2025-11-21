"""
Appointment Service API Routes
Implements all REST API endpoints for the Appointment Service
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Optional
from datetime import date, datetime
import logging

from app.schemas import (
    AppointmentCreate, AppointmentUpdate, AppointmentResponse,
    AppointmentDetailResponse, SuccessResponse
)
from app.services import AppointmentService
from app.database import get_db_manager, DatabaseManager
from app.dependencies import get_current_admin, get_authenticated_user

router = APIRouter(prefix="/api/v1", tags=["Appointment Service"])
logger = logging.getLogger(__name__)


def get_appointment_service(db: DatabaseManager = Depends(get_db_manager)) -> AppointmentService:
    """Dependency to get AppointmentService instance"""
    return AppointmentService(db)


# ============================================================================
# Appointment Management Endpoints
# ============================================================================

@router.post("/appointments", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: Dict = Depends(get_authenticated_user),
    appt_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Create a new appointment (Authenticated users)
    
    - **user_id**: Customer user ID
    - **staff_id**: Staff member ID
    - **service_id**: Service ID
    - **appointment_date**: Date of appointment (YYYY-MM-DD)
    - **appointment_time**: Time of appointment (HH:MM:SS)
    - **notes**: Special notes or requests (optional)
    
    Requires: Valid access token
    Note: Users can only book for themselves unless admin
    """
    # Non-admin users can only create appointments for themselves
    if current_user['user_type'] != 'admin' and appointment_data.user_id != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create appointments for yourself"
        )
    
    try:
        appointment = appt_service.create_appointment(
            user_id=appointment_data.user_id,
            staff_id=appointment_data.staff_id,
            service_id=appointment_data.service_id,
            appointment_datetime=appointment_data.appointment_datetime,
            customer_notes=appointment_data.customer_notes
        )
        
        return SuccessResponse(
            status="success",
            data={"appointment": AppointmentResponse(**appointment).dict()},
            message="Appointment created successfully"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Appointment creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Appointment creation failed"
        )


@router.get("/appointments", response_model=List[AppointmentResponse])
async def get_appointments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    from_datetime: Optional[datetime] = Query(None, description="From datetime"),
    current_admin: Dict = Depends(get_current_admin),
    appt_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Get list of all appointments (Admin only)
    
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 10, max: 100)
    - **status_filter**: Filter by status (pending/confirmed/completed/cancelled/no-show)
    - **from_datetime**: Get appointments from this datetime onwards
    
    Requires: Admin access token
    """
    try:
        appointments, total = appt_service.get_all_appointments(
            page=page,
            limit=limit,
            status=status_filter,
            from_datetime=from_datetime
        )
        
        return [AppointmentResponse(**appt) for appt in appointments]
    
    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch appointments"
        )


@router.get("/appointments/{appointment_id}", response_model=AppointmentDetailResponse)
async def get_appointment(
    appointment_id: int,
    current_user: Dict = Depends(get_authenticated_user),
    appt_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Get detailed appointment information (Authenticated users)
    
    - **appointment_id**: Appointment ID
    
    Requires: Valid access token
    Note: Users can only view their own appointments unless admin
    """
    appointment = appt_service.get_appointment_details(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Non-admin users can only view their own appointments
    if current_user['user_type'] != 'admin' and appointment['user_id'] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own appointments"
        )
    
    return AppointmentDetailResponse(**appointment)


@router.get("/users/{user_id}/appointments", response_model=List[AppointmentResponse])
async def get_user_appointments(
    user_id: int,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    from_datetime: Optional[datetime] = Query(None, description="From datetime"),
    current_user: Dict = Depends(get_authenticated_user),
    appt_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Get all appointments for a specific user (Authenticated users)
    
    - **user_id**: User ID
    - **status_filter**: Filter by status (optional)
    - **from_datetime**: From datetime onwards (optional)
    
    Requires: Valid access token
    Note: Users can only view their own appointments unless admin
    """
    # Non-admin users can only view their own appointments
    if current_user['user_type'] != 'admin' and user_id != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own appointments"
        )
    
    try:
        appointments = appt_service.get_user_appointments(
            user_id=user_id,
            status=status_filter,
            from_datetime=from_datetime
        )
        
        return [AppointmentResponse(**appt) for appt in appointments]
    
    except Exception as e:
        logger.error(f"Error fetching user appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch appointments"
        )


@router.get("/staff/{staff_id}/appointments", response_model=List[AppointmentResponse])
async def get_staff_appointments(
    staff_id: int,
    appointment_date: Optional[date] = Query(None, description="Filter by date"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: Dict = Depends(get_authenticated_user),
    appt_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Get all appointments for a specific staff member (Authenticated users)
    
    - **staff_id**: Staff ID
    - **appointment_date**: Filter by specific date (optional)
    - **status_filter**: Filter by status (optional)
    
    Requires: Valid access token
    """
    try:
        appointments = appt_service.get_staff_appointments(
            staff_id=staff_id,
            appointment_date=appointment_date,
            status=status_filter
        )
        
        return [AppointmentResponse(**appt) for appt in appointments]
    
    except Exception as e:
        logger.error(f"Error fetching staff appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch appointments"
        )


@router.get("/appointments/date/{appointment_date}", response_model=List[AppointmentResponse])
async def get_appointments_by_date(
    appointment_date: date,
    current_user: Dict = Depends(get_authenticated_user),
    appt_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Get all appointments for a specific date (Authenticated users)
    
    - **appointment_date**: Date to query (YYYY-MM-DD)
    
    Requires: Valid access token
    """
    try:
        appointments = appt_service.get_appointments_by_date(appointment_date)
        return [AppointmentResponse(**appt) for appt in appointments]
    
    except Exception as e:
        logger.error(f"Error fetching appointments by date: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch appointments"
        )


@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    current_user: Dict = Depends(get_authenticated_user),
    appt_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Update an appointment (Authenticated users)
    
    - **appointment_id**: Appointment ID
    - **staff_id**: New staff ID (optional)
    - **service_id**: New service ID (optional)
    - **appointment_date**: New date (optional)
    - **appointment_time**: New time (optional)
    - **status**: New status (optional)
    - **notes**: New notes (optional)
    
    Requires: Valid access token
    Note: Users can only update their own appointments unless admin
    """
    # Check if appointment exists and user has permission
    existing = appt_service.get_appointment_by_id(appointment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Non-admin users can only update their own appointments
    if current_user['user_type'] != 'admin' and existing['user_id'] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own appointments"
        )
    
    # Non-admin users cannot change status
    if current_user['user_type'] != 'admin' and appointment_update.status is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change appointment status"
        )
    
    try:
        appointment = appt_service.update_appointment(
            appointment_id=appointment_id,
            staff_id=appointment_update.staff_id,
            service_id=appointment_update.service_id,
            appointment_datetime=appointment_update.appointment_datetime,
            status=appointment_update.status,
            customer_notes=appointment_update.customer_notes,
            staff_notes=appointment_update.staff_notes,
            cancellation_reason=appointment_update.cancellation_reason
        )
        
        return AppointmentResponse(**appointment)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Appointment update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Appointment update failed"
        )


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: int,
    current_user: Dict = Depends(get_authenticated_user),
    appt_service: AppointmentService = Depends(get_appointment_service)
):
    """
    Cancel an appointment (Authenticated users)
    
    - **appointment_id**: Appointment ID
    
    Requires: Valid access token
    Note: Users can only cancel their own appointments unless admin
    """
    # Check if appointment exists and user has permission
    existing = appt_service.get_appointment_by_id(appointment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Non-admin users can only cancel their own appointments
    if current_user['user_type'] != 'admin' and existing['user_id'] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own appointments"
        )
    
    success = appt_service.cancel_appointment(appointment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    return None


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
        "service": "appointment_service",
        "database": "connected" if db_healthy else "disconnected"
    }