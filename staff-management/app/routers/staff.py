"""
Staff Management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from .. import crud, schemas
import sys
sys.path.append('../../../')
from common.database import get_db

router = APIRouter(prefix="/api/v1/staff", tags=["staff"])

@router.post("/", response_model=schemas.StaffResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_member(
    staff: schemas.StaffCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new staff member.
    
    Args:
        staff: Staff creation data
        db: Database session
    
    Returns:
        Created staff member information
    """
    try:
        return crud.create_staff_member(db=db, staff=staff)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.get("/", response_model=List[schemas.StaffResponse])
async def get_staff_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    position: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of staff members with optional filtering"""
    return crud.get_staff_members(
        db=db,
        skip=skip,
        limit=limit,
        active_only=active_only,
        position=position
    )

@router.get("/{staff_id}", response_model=schemas.StaffResponse)
async def get_staff_member(
    staff_id: int,
    db: Session = Depends(get_db)
):
    """Get specific staff member by ID"""
    staff = crud.get_staff_member(db=db, staff_id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    return staff

@router.put("/{staff_id}", response_model=schemas.StaffResponse)
async def update_staff_member(
    staff_id: int,
    staff_update: schemas.StaffUpdate,
    db: Session = Depends(get_db)
):
    """Update staff member information"""
    staff = crud.update_staff_member(db=db, staff_id=staff_id, staff_update=staff_update)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    return staff

@router.post("/{staff_id}/availability", response_model=schemas.AvailabilityResponse)
async def create_availability(
    staff_id: int,
    availability: schemas.AvailabilityCreate,
    db: Session = Depends(get_db)
):
    """
    Create availability slot for staff member.
    
    Args:
        staff_id: Staff member ID
        availability: Availability data
        db: Database session
    
    Returns:
        Created availability information
    """
    # Ensure staff_id in URL matches the one in request body
    availability.staff_id = staff_id
    
    # Verify staff member exists
    staff = crud.get_staff_member(db=db, staff_id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    return crud.create_availability(db=db, availability=availability)

@router.get("/{staff_id}/availability", response_model=schemas.StaffAvailabilityResponse)
async def get_staff_availability(
    staff_id: int,
    date: date = Query(..., description="Date to check availability (YYYY-MM-DD)"),
    service_duration: int = Query(60, ge=15, le=480, description="Service duration in minutes"),
    db: Session = Depends(get_db)
):
    """
    Get available time slots for a staff member on a specific date.
    
    This is the most important endpoint for the booking system.
    It calculates when a staff member is available for appointments.
    
    Args:
        staff_id: Staff member ID
        date: Date to check availability
        service_duration: Required service duration in minutes
        db: Database session
    
    Returns:
        Available time slots for booking
    """
    # Verify staff member exists
    staff = crud.get_staff_member(db=db, staff_id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    return crud.calculate_available_time_slots(
        db=db,
        staff_id=staff_id,
        target_date=date,
        service_duration_minutes=service_duration
    )

@router.get("/specialty/{specialty}", response_model=List[schemas.StaffResponse])
async def get_staff_by_specialty(
    specialty: str,
    db: Session = Depends(get_db)
):
    """
    Get staff members who specialize in a specific service.
    
    Args:
        specialty: Service specialty (e.g., "Haircut", "Color")
        db: Database session
    
    Returns:
        List of qualified staff members
    """
    return crud.get_staff_by_specialty(db=db, specialty=specialty)