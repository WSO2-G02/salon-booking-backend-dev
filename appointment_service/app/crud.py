"""
CRUD operations for Appointment Service.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from . import models, schemas
from typing import List, Optional
from datetime import datetime, date
import requests
import json

# Configuration for other services
STAFF_SERVICE_URL = "http://staff-service:8003"
SERVICE_MANAGEMENT_URL = "http://service-management:8002"
USER_SERVICE_URL = "http://user-service:8001"

def get_appointment(db: Session, appointment_id: int) -> Optional[models.Appointment]:
    """Get appointment by ID"""
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def get_user_appointments(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None
) -> List[models.Appointment]:
    """
    Get appointments for a specific user.
    
    Args:
        db: Database session
        user_id: Customer ID
        skip: Pagination skip
        limit: Pagination limit
        status_filter: Filter by appointment status
    
    Returns:
        List of user's appointments
    """
    query = db.query(models.Appointment).filter(models.Appointment.user_id == user_id)
    
    if status_filter:
        query = query.filter(models.Appointment.status == status_filter)
    
    return query.offset(skip).limit(limit).all()

def get_staff_appointments(
    db: Session,
    staff_id: int,
    target_date: Optional[date] = None
) -> List[models.Appointment]:
    """
    Get appointments for a specific staff member.
    
    Args:
        db: Database session
        staff_id: Staff member ID
        target_date: Optional date filter
    
    Returns:
        List of staff's appointments
    """
    query = db.query(models.Appointment).filter(models.Appointment.staff_id == staff_id)
    
    if target_date:
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        query = query.filter(
            and_(
                models.Appointment.appointment_datetime >= start_datetime,
                models.Appointment.appointment_datetime <= end_datetime
            )
        )
    
    return query.all()

async def verify_booking_availability(
    staff_id: int,
    appointment_datetime: datetime,
    duration_minutes: int
) -> bool:
    """
    Verify that a staff member is available for booking.
    
    This function calls the Staff Management Service to check availability.
    
    Args:
        staff_id: Staff member ID
        appointment_datetime: Requested appointment time
        duration_minutes: Service duration
    
    Returns:
        True if available, False otherwise
    """
    try:
        # Call Staff Management Service to check availability
        response = requests.get(
            f"{STAFF_SERVICE_URL}/api/v1/staff/{staff_id}/availability",
            params={
                "date": appointment_datetime.date().isoformat(),
                "service_duration": duration_minutes
            }
        )
        
        if response.status_code == 200:
            availability_data = response.json()
            
            # Check if requested time slot is available
            requested_time = appointment_datetime.time()
            for slot in availability_data.get("available_slots", []):
                slot_start = datetime.strptime(slot["start_time"], "%H:%M:%S").time()
                slot_end = datetime.strptime(slot["end_time"], "%H:%M:%S").time()
                
                if slot_start <= requested_time < slot_end:
                    return True
            
        return False
    except requests.RequestException:
        # If Staff Service is unavailable, reject the booking for safety
        return False

async def get_service_details(service_id: int) -> Optional[dict]:
    """
    Get service details from Service Management Service.
    
    Args:
        service_id: Service ID
    
    Returns:
        Service details or None if not found
    """
    try:
        response = requests.get(f"{SERVICE_MANAGEMENT_URL}/api/v1/services/{service_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None

def create_appointment(db: Session, appointment: schemas.AppointmentCreate) -> models.Appointment:
    """
    Create a new appointment.
    
    Args:
        db: Database session
        appointment: Appointment creation data
    
    Returns:
        Created appointment model
    """
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def update_appointment_status(
    db: Session,
    appointment_id: int,
    status: schemas.AppointmentStatus,
    staff_notes: Optional[str] = None
) -> Optional[models.Appointment]:
    """
    Update appointment status.
    
    Args:
        db: Database session
        appointment_id: Appointment ID
        status: New status
        staff_notes: Optional staff notes
    
    Returns:
        Updated appointment or None if not found
    """
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        return None
    
    appointment.status = status
    if staff_notes:
        appointment.staff_notes = staff_notes
    
    # Set timestamp fields based on status
    if status == schemas.AppointmentStatus.CONFIRMED:
        appointment.confirmed_at = datetime.now()
    elif status == schemas.AppointmentStatus.COMPLETED:
        appointment.completed_at = datetime.now()
    
    db.commit()
    db.refresh(appointment)
    return appointment

def reschedule_appointment(
    db: Session,
    appointment_id: int,
    new_datetime: datetime
) -> Optional[models.Appointment]:
    """
    Reschedule an appointment to a new time.
    
    Args:
        db: Database session
        appointment_id: Appointment ID
        new_datetime: New appointment time
    
    Returns:
        Updated appointment or None if not found
    """
    appointment = get_appointment(db, appointment_id)
    if not appointment:
        return None
    
    appointment.appointment_datetime = new_datetime
    appointment.status = schemas.AppointmentStatus.PENDING  # Reset to pending for re-confirmation
    
    db.commit()
    db.refresh(appointment)
    return appointment