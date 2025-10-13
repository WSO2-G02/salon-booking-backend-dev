"""
SQLAlchemy models for Staff Management.
Defines staff members and their availability schedules.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
sys.path.append('../../')
from common.database import Base

class Staff(Base):
    """
    Staff model representing salon employees.
    
    This table stores information about stylists, beauticians, and other staff members.
    """
    __tablename__ = "staff"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Staff identification (links to User service)
    user_id = Column(Integer, index=True, nullable=False)  # Reference to User service
    employee_id = Column(String, unique=True, index=True)  # Internal employee ID
    
    # Professional details
    position = Column(String, nullable=False)  # e.g., "Senior Stylist", "Beautician"
    specialties = Column(JSON)  # List of specialties (e.g., ["Haircut", "Color", "Highlights"])
    experience_years = Column(Integer, default=0)
    
    # Employment status
    is_active = Column(Boolean, default=True)
    hire_date = Column(Date)
    
    # Contact and emergency information
    phone = Column(String)
    emergency_contact = Column(String)
    emergency_phone = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to availability
    availability_slots = relationship("StaffAvailability", back_populates="staff")
    
    def __repr__(self):
        return f"<Staff(id={self.id}, employee_id='{self.employee_id}', position='{self.position}')>"

class StaffAvailability(Base):
    """
    Staff availability model for managing work schedules.
    
    This table defines when staff members are available to work.
    It supports both regular weekly schedules and specific date overrides.
    """
    __tablename__ = "staff_availability"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to staff
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    
    # Date and time information
    date = Column(Date, nullable=False, index=True)  # Specific date for this availability
    start_time = Column(Time, nullable=False)  # Start time (e.g., 09:00)
    end_time = Column(Time, nullable=False)    # End time (e.g., 17:00)
    
    # Availability type and status
    availability_type = Column(String, default="work")  # "work", "break", "leave", "sick"
    is_available = Column(Boolean, default=True)  # Whether staff is available during this time
    
    # Optional notes
    notes = Column(String)  # e.g., "Lunch break", "Training session"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship back to staff
    staff = relationship("Staff", back_populates="availability_slots")
    
    def __repr__(self):
        return f"<StaffAvailability(staff_id={self.staff_id}, date={self.date}, {self.start_time}-{self.end_time})>"