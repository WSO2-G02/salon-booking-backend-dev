"""
Appointment Service API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from .. import crud, schemas, messaging
import sys
sys.path.append('../../../')
from common.database import get_db
import datetime

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])

@router.post("/book", response_model=schemas.BookingResponse, status_code=status.HTTP_202_ACCEPTED)
async def book_appointment(
    booking_request: schemas.BookingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Book a new appointment (Saga Pattern Implementation).
    
    This endpoint implements the booking saga:
    1. Verify service exists and get details
    2. Check staff availability
    3. Create appointment with PENDING status
    4. Publish AppointmentBooked event
    5. Return 202 Accepted (async processing)
    
    Args:
        booking_request: Booking request data
        background_tasks: FastAPI background tasks
        db: Database session
    
    Returns:
        Booking response with appointment ID and status
    """
    try:
        # Step 1: Get service details
        service_details = await crud.get_service_details(booking_request.service_id)
        if not service_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Step 2: Check staff availability
        is_available = await crud.verify_booking_availability(
            staff_id=booking_request.staff_id,
            appointment_datetime=booking_request.appointment_datetime,
            duration_minutes=service_details["duration_minutes"]
        )
        
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Staff member is not available at the requested time"
            )
        
        # Step 3: Create appointment
        appointment_data = schemas.AppointmentCreate(
            user_id=1,  # TODO: Get from authenticated user context
            staff_id=booking_request.staff_id,
            service_id=booking_request.service_id,
            appointment_datetime=booking_request.appointment_datetime,
            duration_minutes=service_details["duration_minutes"],
            service_price=service_details["price"],
            customer_notes=booking_request.customer_notes
        )
        
        appointment = crud.create_appointment(db=db, appointment=appointment_data)
        
        # Step 4: Publish event (background task)
        background_tasks.add_task(
            messaging.publish_appointment_booked,
            schemas.AppointmentResponse.from_orm(appointment)
        )
        
        return schemas.BookingResponse(
            appointment_id=appointment.id,
            status="accepted",
            message="Appointment request received and is being processed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process booking request"
        )

@router.get("/{appointment_id}", response_model=schemas.AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Get appointment by ID"""
    appointment = crud.get_appointment(db=db, appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment

@router.get("/user/{user_id}", response_model=List[schemas.AppointmentResponse])
async def get_user_appointments(
    user_id: int,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get appointments for a specific user"""
    return crud.get_user_appointments(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        status_filter=status_filter
    )

@router.get("/staff/{staff_id}", response_model=List[schemas.AppointmentResponse])
async def get_staff_appointments(
    staff_id: int,
    date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get appointments for a specific staff member"""
    return crud.get_staff_appointments(
        db=db,
        staff_id=staff_id,
        target_date=date
    )

@router.put("/{appointment_id}/confirm", response_model=schemas.AppointmentResponse)
async def confirm_appointment(
    appointment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Confirm a pending appointment.
    
    Args:
        appointment_id: Appointment ID to confirm
        background_tasks: For publishing events
        db: Database session
    
    Returns:
        Updated appointment
    """
    appointment = crud.update_appointment_status(
        db=db,
        appointment_id=appointment_id,
        status=schemas.AppointmentStatus.CONFIRMED
    )
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Publish confirmation event
    background_tasks.add_task(
        messaging.publish_appointment_confirmed,
        schemas.AppointmentResponse.from_orm(appointment)
    )
    
    return appointment

@router.put("/{appointment_id}/reschedule", response_model=schemas.AppointmentResponse)
async def reschedule_appointment(
    appointment_id: int,
    new_datetime: datetime,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Reschedule an appointment to a new time.
    
    Args:
        appointment_id: Appointment ID to reschedule
        new_datetime: New appointment datetime
        background_tasks: For publishing events
        db: Database session
    
    Returns:
        Updated appointment
    """
    # First verify the appointment exists
    existing_appointment = crud.get_appointment(db=db, appointment_id=appointment_id)
    if not existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check new time availability
    is_available = await crud.verify_booking_availability(
        staff_id=existing_appointment.staff_id,
        appointment_datetime=new_datetime,
        duration_minutes=existing_appointment.duration_minutes
    )
    
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Staff member is not available at the new requested time"
        )
    
    # Reschedule the appointment
    appointment = crud.reschedule_appointment(
        db=db,
        appointment_id=appointment_id,
        new_datetime=new_datetime
    )
    
    # Publish reschedule event
    background_tasks.add_task(
        messaging.publish_appointment_booked,  # Treat as new booking
        schemas.AppointmentResponse.from_orm(appointment)
    )
    
    return appointment

@router.delete("/{appointment_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: int,
    cancellation_reason: Optional[str] = None,
    # background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cancel an appointment.
    
    Args:
        appointment_id: Appointment ID to cancel
        cancellation_reason: Optional reason for cancellation
        background_tasks: For publishing events
        db: Database session
    """
    appointment = crud.update_appointment_status(
        db=db,
        appointment_id=appointment_id,
        status=schemas.AppointmentStatus.CANCELLED,
        staff_notes=f"Cancelled: {cancellation_reason}" if cancellation_reason else "Cancelled"
    )
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Publish cancellation event
    # background_tasks.add_task(
    #     messaging.publish_appointment_cancelled,
    #     schemas.AppointmentResponse.from_orm(appointment),
    #     cancellation_reason
    # )