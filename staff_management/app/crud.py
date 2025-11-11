from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, cast, String
from . import models, schemas
from typing import List, Optional
from datetime import datetime, date, timedelta
import json


def _decode_specialties(staff_obj):
    if staff_obj and isinstance(staff_obj.specialties, str):
        try:
            staff_obj.specialties = json.loads(staff_obj.specialties)
        except:
            staff_obj.specialties = []
    return staff_obj


# GET STAFF BY user_id
async def get_staff_member(db: AsyncSession, user_id: int) -> Optional[models.Staff]:
    """Fetch staff record using user_id instead of internal id"""
    result = await db.execute(
        select(models.Staff).filter(models.Staff.user_id == user_id)
    )
    staff = result.scalars().first()
    return _decode_specialties(staff)

    #return result.scalars().first()


# GET STAFF BY employee_id
async def get_staff_by_employee_id(db: AsyncSession, employee_id: str):
    result = await db.execute(
        select(models.Staff).filter(models.Staff.employee_id == employee_id)
    )
    staff = result.scalars().first()
    return _decode_specialties(staff) 

    #return result.scalars().first()



# GET STAFF LIST (with MSSQL fix)
async def get_staff_members(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    position: Optional[str] = None
):
    query = select(models.Staff)

    if active_only:
        query = query.filter(models.Staff.is_active == True)

    if position:
        query = query.filter(models.Staff.position == position)

    query = query.order_by(models.Staff.user_id)

    result = await db.execute(query.offset(skip).limit(limit))
    staff_list = result.scalars().all()
    return [_decode_specialties(s) for s in staff_list]



# CREATE STAFF
async def create_staff_member(db: AsyncSession, staff: schemas.StaffCreate) -> models.Staff:
    existing = await get_staff_by_employee_id(db, staff.employee_id)
    if existing:
        raise ValueError("Employee ID already exists")
    
    data = staff.dict()

    # convert Python list → JSON 
    data["specialties"] = json.dumps(data["specialties"])

    db_staff = models.Staff(**data)

    db.add(db_staff)
    await db.commit()
    await db.refresh(db_staff)

    return _decode_specialties(db_staff)



# UPDATE by user_id
async def update_staff_member(
    db: AsyncSession,
    user_id: int,
    staff_update: schemas.StaffUpdate
):
    db_staff = await get_staff_member(db, user_id)
    if not db_staff:
        return None

    update_data = staff_update.dict(exclude_unset=True)

    if "specialties" in update_data:
        update_data["specialties"] = json.dumps(update_data["specialties"])

    for field, value in update_data.items():
        setattr(db_staff, field, value)

    await db.commit()
    await db.refresh(db_staff)

    return _decode_specialties(db_staff)



# CREATE AVAILABILITY
async def create_availability(db: AsyncSession, availability: schemas.AvailabilityCreate):
    """
    IMPORTANT: construct the object using the exact Azure DB column names
    (slot_date, start_time, end_time, availability_type).
    """
    db_availability = models.StaffAvailability(
        staff_id=availability.staff_id,
        slot_date=availability.slot_date,
        start_time=availability.start_time,
        end_time=availability.end_time,
        availability_type=availability.availability_type
    )
    db.add(db_availability)
    await db.commit()
    await db.refresh(db_availability)
    return db_availability

#async def create_availability(db: AsyncSession, availability: schemas.AvailabilityCreate):
#    db_availability = models.StaffAvailability(**availability.dict())
#    db.add(db_availability)
#    await db.commit()
#    await db.refresh(db_availability)
#    return db_availability



# Availability by staff_id
async def get_staff_availability(db: AsyncSession, staff_id: int, target_date: date):
    """
    Query uses slot_date (the actual column in Azure DB) and DOES NOT use
    is_available / notes / created_at because they don't exist in the DB.
    """
    result = await db.execute(
        select(models.StaffAvailability).filter(
            and_(
                models.StaffAvailability.staff_id == staff_id,
                models.StaffAvailability.slot_date == target_date
            )
        )
    )
    return result.scalars().all()


  

#  CALCULATE AVAILABLE TIME SLOTS
async def calculate_available_time_slots(
    db: AsyncSession,
    staff_id: int,
    target_date: date,
    service_duration_minutes: int = 60
):
    availability_slots = await get_staff_availability(db, staff_id, target_date)

    if not availability_slots:
        return schemas.StaffAvailabilityResponse(
            staff_id=staff_id,
            slot_date=target_date,
            available_slots=[],
            total_available_minutes=0
        )

    available_slots = []
    total_minutes = 0

    for availability in availability_slots:
        # availability.slot_date / start_time / end_time come from DB
        start_dt = datetime.combine(target_date, availability.start_time)
        end_dt = datetime.combine(target_date, availability.end_time)
        current = start_dt

        while current + timedelta(minutes=service_duration_minutes) <= end_dt:
            slot_end = current + timedelta(minutes=service_duration_minutes)

            available_slots.append(
                schemas.TimeSlot(
                    start_time=current.time(),
                    end_time=slot_end.time(),
                    duration_minutes=service_duration_minutes
                )
            )
            total_minutes += service_duration_minutes

            current += timedelta(minutes=30)

    return schemas.StaffAvailabilityResponse(
        staff_id=staff_id,
        slot_date=target_date,
        available_slots=available_slots,
        total_available_minutes=total_minutes
    )



# GET STAFF BY SPECIALTY
async def get_staff_by_specialty(db: AsyncSession, specialty: str):
    result = await db.execute(
        select(models.Staff).filter(
            and_(
                cast(models.Staff.specialties, String).like(f"%{specialty}%"),
                models.Staff.is_active == True
            )
        )
    )
    staff_list = result.scalars().all()
    return [_decode_specialties(s) for s in staff_list]



# DELETE by user_id
async def delete_staff_member(db: AsyncSession, user_id: int) -> bool:
    staff = await get_staff_member(db, user_id)
    if not staff:
        return False

    await db.delete(staff)
    await db.commit()
    return True
