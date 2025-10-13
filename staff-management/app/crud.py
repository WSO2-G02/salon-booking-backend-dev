"""
CRUD operations for Staff Management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from . import models, schemas
from typing import List, Optional
from datetime import datetime, date, time, timedelta
import requests

def get_staff_member(db: Session, staff_id: int) -> Optional[models.Staff]:
    """Get staff member by ID"""
    return db.query(models.Staff).filter(models.Staff.id == staff_id).first()

def get_staff_by_employee_id(db: Session, employee_id: str) -> Optional[models.Staff]:
    """Get staff member by employee ID"""
    return db.query(models.Staff).filter(models.Staff.employee_id == employee_id).first()

def get_staff_members(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True,
    position: Optional[str] = None
) -> List[models.Staff]:
    """
    Get list of staff members with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Only return active staff
        position: Filter by position
    
    Returns:
        List of staff models
    """
    query = db.query(models.Staff)
    
    if active_only:
        query = query.filter(models.Staff.is_active == True)
    
    if position:
        query = query.filter(models.Staff.position == position)
    
    return query.offset(skip).limit(limit).all()

def create_staff_member(db: Session, staff: schemas.StaffCreate) -> models.Staff:
    """
    Create a new staff member.
    
    Args:
        db: Database session
        staff: Staff creation data
    
    Returns:
        Created staff model
    
    Raises:
        ValueError: If employee ID already exists or user doesn't exist
    """
    # Check if employee ID already exists
    existing_staff = get_staff_by_employee_id(db, staff.employee_id)
    if existing_staff:
        raise ValueError("Employee ID already exists")
    
    # TODO: In production, verify user_id exists in User Service
    # This would require an API call to the User Service
    
    db_staff = models.Staff(**staff.dict())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

def update_staff_member(
    db: Session, 
    staff_id: int, 
    staff_update: schemas.StaffUpdate
) -> Optional[models.Staff]:
    """Update staff member information"""
    db_staff = get_staff_member(db, staff_id)
    if not db_staff:
        return None
    
    update_data = staff_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_staff, field, value)
    
    db.commit()
    db.refresh(db_staff)
    return db_staff

def create_availability(db: Session, availability: schemas.AvailabilityCreate) -> models.StaffAvailability:
    """
    Create a new availability slot for a staff member.
    
    Args:
        db: Database session
        availability: Availability data
    
    Returns:
        Created availability model
    """
    db_availability = models.StaffAvailability(**availability.dict())
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

def get_staff_availability(
    db: Session, 
    staff_id: int, 
    target_date: date
) -> List[models.StaffAvailability]:
    """
    Get staff availability for a specific date.
    
    Args:
        db: Database session
        staff_id: Staff member ID
        target_date: Date to check availability
    
    Returns:
        List of availability slots for the date
    """
    return db.query(models.StaffAvailability).filter(
        and_(
            models.StaffAvailability.staff_id == staff_id,
            models.StaffAvailability.date == target_date,
            models.StaffAvailability.is_available == True
        )
    ).all()

def calculate_available_time_slots(
    db: Session,
    staff_id: int,
    target_date: date,
    service_duration_minutes: int = 60
) -> schemas.StaffAvailabilityResponse:
    """
    Calculate available time slots for booking appointments.
    
    This function considers:
    1. Staff's working hours for the day
    2. Existing appointments (would need to call Appointment Service)
    3. Service duration requirements
    
    Args:
        db: Database session
        staff_id: Staff member ID
        target_date: Date to check
        service_duration_minutes: Required service duration
    
    Returns:
        Available time slots
    """
    # Get staff availability for the date
    availability_slots = get_staff_availability(db, staff_id, target_date)
    
    if not availability_slots:
        return schemas.StaffAvailabilityResponse(
            staff_id=staff_id,
            date=target_date,
            available_slots=[],
            total_available_minutes=0
        )
    
    # TODO: In production, call Appointment Service to get existing appointments
    # existing_appointments = get_existing_appointments(staff_id, target_date)
    existing_appointments = []  # Placeholder
    
    available_slots = []
    total_minutes = 0
    
    for availability in availability_slots:
        # Convert times to datetime for easier calculation
        start_datetime = datetime.combine(target_date, availability.start_time)
        end_datetime = datetime.combine(target_date, availability.end_time)
        
        # Generate time slots based on service duration
        current_time = start_datetime
        while current_time + timedelta(minutes=service_duration_minutes) <= end_datetime:
            slot_end = current_time + timedelta(minutes=service_duration_minutes)
            
            # Check if this slot conflicts with existing appointments
            is_available = True
            for appointment in existing_appointments:
                # TODO: Implement appointment conflict checking logic
                pass
            
            if is_available:
                available_slots.append(schemas.TimeSlot(
                    start_time=current_time.time(),
                    end_time=slot_end.time(),
                    duration_minutes=service_duration_minutes
                ))
                total_minutes += service_duration_minutes
            
            # Move to next possible slot (typically 15-30 minute intervals)
            current_time += timedelta(minutes=30)  # 30-minute intervals
    
    return schemas.StaffAvailabilityResponse(
        staff_id=staff_id,
        date=target_date,
        available_slots=available_slots,
        total_available_minutes=total_minutes
    )

def get_staff_by_specialty(db: Session, specialty: str) -> List[models.Staff]:
    """
    Get staff members who specialize in a specific service.
    
    Args:
        db: Database session
        specialty: Service specialty to search for
    
    Returns:
        List of staff members with the specialty
    """
    return db.query(models.Staff).filter(
        and_(
            models.Staff.specialties.contains([specialty]),
            models.Staff.is_active == True
        )
    ).all()