from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Time,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
import sys
sys.path.append('../../')
from common.database import Base


class Staff(Base):
    """Staff model representing salon employees."""

    __tablename__ = "staff"

    # Auto-increment primary key for internal use (DO NOT REMOVE)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)


    # Main identifier used in API (user service mapping)
    user_id = Column(Integer, index=True, nullable=False, unique=True)


    # Internal staff employee code (unique)
    employee_id = Column(String, unique=True, index=True, nullable=False)


    # Professional details
    specialties = Column(String, nullable=True) 
    position = Column(String, nullable=False)
    experience_years = Column(Integer, default=0)


    # Employment status
    is_active = Column(Boolean, default=True)
    hire_date = Column(Date, nullable=True)


    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationship to availability
    availability_slots = relationship(
        "StaffAvailability",
        back_populates="staff",
        cascade="all, delete-orphan",
        passive_deletes=True  
    )

    def __repr__(self):
        return f"<Staff(user_id={self.user_id}, employee_id='{self.employee_id}', position='{self.position}')>"


class StaffAvailability(Base):
    """Staff availability slots."""
    __tablename__ = "staff_availability"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Correct FK link to Staff internal ID (id)
    staff_id = Column(
        Integer,
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Availability details must align with azure column types
    slot_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    availability_type = Column(String, nullable=False, default="work")


    # Relationship back to Staff
    staff = relationship("Staff", back_populates="availability_slots")

    def __repr__(self):
        return (
            f"<StaffAvailability(staff_id={self.staff_id}, slot_date={self.slot_date}, "
            f"{self.start_time}-{self.end_time})>"
        )
