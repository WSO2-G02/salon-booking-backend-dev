"""
Staff Service API Routes
Implements all REST API endpoints for the Staff Service
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Optional
from datetime import date
import logging

from app.schemas import (
    StaffCreate, StaffUpdate, StaffResponse,
    AvailabilityCreate, AvailabilityResponse,
    StaffAvailabilityResponse, TimeSlot,
    SuccessResponse, PaginatedResponse
)
from app.services import StaffService
from app.database import get_db_manager, DatabaseManager
from app.dependencies import get_current_admin, get_authenticated_user

router = APIRouter(prefix="/api/v1", tags=["Staff Service"])
logger = logging.getLogger(__name__)


def get_staff_service(db: DatabaseManager = Depends(get_db_manager)) -> StaffService:
    """Dependency to get StaffService instance"""
    return StaffService(db)


# ============================================================================
# Staff Management Endpoints (Admin Only)
# ============================================================================

@router.post("/staff", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_member(
    staff_data: StaffCreate,
    current_admin: Dict = Depends(get_current_admin),
    staff_service: StaffService = Depends(get_staff_service)
):
    """
    Create a new staff member (Admin only)
    
    - **user_id**: Reference to user in user_db
    - **employee_id**: Unique employee identifier
    - **position**: Job position
    - **specialties**: Comma-separated specialties (optional)
    - **experience_years**: Years of experience (optional)
    - **hire_date**: Date of hire (optional)
    
    Requires: Admin access token
    """
    try:
        staff = staff_service.create_staff_member(
            user_id=staff_data.user_id,
            employee_id=staff_data.employee_id,
            position=staff_data.position,
            specialties=staff_data.specialties,
            experience_years=staff_data.experience_years,
            hire_date=staff_data.hire_date
        )
        
        return SuccessResponse(
            status="success",
            data={"staff": StaffResponse(**staff).dict()},
            message="Staff member created successfully"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Staff creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Staff creation failed"
        )


@router.get("/staff", response_model=List[StaffResponse])
async def get_staff_members(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(True, description="Filter active staff only"),
    position: Optional[str] = Query(None, description="Filter by position"),
    current_user: Dict = Depends(get_authenticated_user),
    staff_service: StaffService = Depends(get_staff_service)
):
    """
    Get list of all staff members (Authenticated users)
    
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 10, max: 100)
    - **active_only**: Filter active staff (default: true)
    - **position**: Filter by position (optional)
    
    Requires: Valid access token
    """
    try:
        staff_list, total = staff_service.get_all_staff(
            page=page,
            limit=limit,
            active_only=active_only,
            position=position
        )
        
        return [StaffResponse(**staff) for staff in staff_list]
    
    except Exception as e:
        logger.error(f"Error fetching staff: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch staff"
        )


@router.get("/staff/{staff_id}", response_model=StaffResponse)
async def get_staff_member(
    staff_id: int,
    current_user: Dict = Depends(get_authenticated_user),
    staff_service: StaffService = Depends(get_staff_service)
):
    """
    Get details for a specific staff member (Authenticated users)
    
    - **staff_id**: Internal staff ID
    
    Requires: Valid access token
    """
    staff = staff_service.get_staff_by_id(staff_id)
    
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    return StaffResponse(**staff)


@router.put("/staff/{staff_id}", response_model=StaffResponse)
async def update_staff_member(
    staff_id: int,
    staff_update: StaffUpdate,
    current_admin: Dict = Depends(get_current_admin),
    staff_service: StaffService = Depends(get_staff_service)
):
    """
    Update a staff member's profile (Admin only)
    
    - **staff_id**: Internal staff ID
    - **position**: New position (optional)
    - **specialties**: New specialties (optional)
    - **experience_years**: New experience years (optional)
    - **hire_date**: New hire date (optional)
    - **is_active**: Active status (optional)
    
    Requires: Admin access token
    """
    try:
        staff = staff_service.update_staff_member(
            staff_id=staff_id,
            position=staff_update.position,
            specialties=staff_update.specialties,
            experience_years=staff_update.experience_years,
            hire_date=staff_update.hire_date,
            is_active=staff_update.is_active
        )
        
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff member not found"
            )
        
        return StaffResponse(**staff)
    
    except Exception as e:
        logger.error(f"Staff update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Staff update failed"
        )


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_member(
    staff_id: int,
    current_admin: Dict = Depends(get_current_admin),
    staff_service: StaffService = Depends(get_staff_service)
):
    """
    Deactivate a staff member (soft delete) (Admin only)
    
    - **staff_id**: Internal staff ID
    
    Requires: Admin access token
    """
    success = staff_service.delete_staff_member(staff_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    return None


# ============================================================================
# Staff Availability Endpoints
# ============================================================================

@router.post("/staff/{staff_id}/availability", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_availability(
    staff_id: int,
    availability: AvailabilityCreate,
    current_admin: Dict = Depends(get_current_admin),
    staff_service: StaffService = Depends(get_staff_service)
):
    """
    Create a single availability slot for a staff member (Admin only)
    
    - **staff_id**: Internal staff ID
    - **slot_date**: Date of availability
    - **start_time**: Start time
    - **end_time**: End time
    - **availability_type**: Type (work, break, unavailable)
    
    Requires: Admin access token
    """
    # Verify staff exists
    staff = staff_service.get_staff_by_id(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    try:
        # Override staff_id from URL parameter
        availability_data = staff_service.create_availability(
            staff_id=staff_id,
            slot_date=availability.slot_date,
            start_time=availability.start_time,
            end_time=availability.end_time,
            availability_type=availability.availability_type
        )
        
        return AvailabilityResponse(**availability_data)
    
    except Exception as e:
        logger.error(f"Availability creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Availability creation failed"
        )


@router.get("/staff/{staff_id}/availability", response_model=StaffAvailabilityResponse)
async def get_staff_availability(
    staff_id: int,
    slot_date: date = Query(..., description="Date in YYYY-MM-DD format"),
    service_duration: int = Query(60, ge=15, le=480, description="Service duration in minutes"),
    current_user: Dict = Depends(get_authenticated_user),
    staff_service: StaffService = Depends(get_staff_service)
):
    """
    Get available time slots for a staff member on a specific date (Authenticated users)
    
    - **staff_id**: Internal staff ID
    - **slot_date**: Date to check (YYYY-MM-DD)
    - **service_duration**: Duration of service in minutes (default: 60)
    
    Returns calculated booking slots based on availability
    
    Requires: Valid access token
    """
    # Verify staff exists
    staff = staff_service.get_staff_by_id(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    try:
        result = staff_service.calculate_available_time_slots(
            staff_id=staff_id,
            slot_date=slot_date,
            service_duration_minutes=service_duration
        )
        
        # Convert to response model
        return StaffAvailabilityResponse(
            staff_id=result['staff_id'],
            slot_date=result['slot_date'],
            available_slots=[TimeSlot(**slot) for slot in result['available_slots']],
            total_available_minutes=result['total_available_minutes']
        )
    
    except Exception as e:
        logger.error(f"Error calculating availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate availability"
        )


# ============================================================================
# Search/Filter Endpoints
# ============================================================================

@router.get("/staff/specialty/{specialty}", response_model=List[StaffResponse])
async def get_staff_by_specialty(
    specialty: str,
    current_user: Dict = Depends(get_authenticated_user),
    staff_service: StaffService = Depends(get_staff_service)
):
    """
    Get staff members by specialty (Authenticated users)
    
    - **specialty**: Specialty to search for
    
    Requires: Valid access token
    """
    try:
        staff_list = staff_service.get_staff_by_specialty(specialty)
        return [StaffResponse(**staff) for staff in staff_list]
    
    except Exception as e:
        logger.error(f"Error searching staff by specialty: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
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
        "service": "staff_service",
        "database": "connected" if db_healthy else "disconnected"
    }