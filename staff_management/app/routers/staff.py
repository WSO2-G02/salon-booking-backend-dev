from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
from .. import crud, schemas
import sys
sys.path.append('../../../')
from common.database import get_db
from app.security.authentication import verify_user_session


router = APIRouter(prefix="/api/v1/staff", tags=["staff"])


# CREATE STAFF
@router.post("/", response_model=schemas.StaffResponse, status_code=status.HTTP_201_CREATED,dependencies=[Depends(verify_user_session)])
async def create_staff_member(
    staff: schemas.StaffCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await crud.create_staff_member(db=db, staff=staff)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


# GET STAFF LIST
@router.get("/", response_model=List[schemas.StaffResponse],dependencies=[Depends(verify_user_session)])
async def get_staff_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    position: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_staff_members(
        db=db, skip=skip, limit=limit,
        active_only=active_only, position=position
    )


# GET STAFF BY user_id 
@router.get("/{user_id}", response_model=schemas.StaffResponse,dependencies=[Depends(verify_user_session)])
async def get_staff_member(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    staff = await crud.get_staff_member(db=db, user_id=user_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    return staff


#  UPDATE STAFF BY user_id
@router.put("/{user_id}", response_model=schemas.StaffResponse,dependencies=[Depends(verify_user_session)])
async def update_staff_member(
    user_id: int,
    staff_update: schemas.StaffUpdate,
    db: AsyncSession = Depends(get_db)
):
    staff = await crud.update_staff_member(
        db=db, user_id=user_id, staff_update=staff_update
    )
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    return staff



# CREATE AVAILABILITY
@router.post("/{user_id}/availability", response_model=schemas.AvailabilityResponse,dependencies=[Depends(verify_user_session)])
async def create_availability(
    user_id: int,
    availability: schemas.AvailabilityCreate,
    db: AsyncSession = Depends(get_db)
):
    
    staff = await crud.get_staff_member(db=db, user_id=user_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

  
    availability.staff_id = staff.id

    return await crud.create_availability(db=db, availability=availability)
# staff_id here refers to the staff table's internal ID (FK)



# GET AVAILABILITY BY DATE
@router.get("/{user_id}/availability", response_model=schemas.StaffAvailabilityResponse,dependencies=[Depends(verify_user_session)])
async def get_staff_availability(
    user_id: int,
    slot_date: date = Query(..., description="Date in YYYY-MM-DD"),
    service_duration: int = Query(60, ge=15, le=480),
    db: AsyncSession = Depends(get_db)
):
    staff = await crud.get_staff_member(db=db, user_id=user_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    
    return await crud.calculate_available_time_slots(
        db=db,
        staff_id=staff.id,
        target_date=slot_date,
        service_duration_minutes=service_duration
    )



# GET STAFF BY SPECIALTY
@router.get("/specialty/{specialty}", response_model=List[schemas.StaffResponse],dependencies=[Depends(verify_user_session)])
async def get_staff_by_specialty(
    specialty: str,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_staff_by_specialty(db=db, specialty=specialty)



# DELETE STAFF BY user_id
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(verify_user_session)])
async def delete_staff_member(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await crud.delete_staff_member(db=db, user_id=user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Staff member not found")

    return {"message": "Staff deleted successfully"}


