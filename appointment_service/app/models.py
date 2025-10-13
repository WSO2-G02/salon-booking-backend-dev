"""
SQLAlchemy models for Appointment Service.
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Numeric
from sqlalchemy.sql import func
from enum import Enum
import sys
sys.path.append('../../')
from common.database import Base

class AppointmentStatus(str, Enum):
    """Enumeration for appointment statuses"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class Appointment(Base):
    """
    Appointment model for booking system.
    
    This is the central table that ties together customers, staff, and services.
    """
    __tablename__ = "appointments"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys to other services (stored as IDs, not actual foreign keys)
    user_id = Column(Integer, nullable=False, index=True)      # Customer (User Service)
    staff_id = Column(Integer, nullable=False, index=True)     # Staff member (Staff Service)
    service_id = Column(Integer, nullable=False, index=True)   # Service (Service Management)
    
    # Appointment details
    appointment_datetime = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    
    # Pricing (captured at booking time to handle price changes)
    service_price = Column(Numeric(10, 2), nullable=False)
    
    # Status and notes
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.PENDING, index=True)
    customer_notes = Column(String)  # Special requests from customer
    staff_notes = Column(String)     # Internal notes from staff
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True))  # When appointment was confirmed
    completed_at = Column(DateTime(timezone=True))  # When service was completed
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, user_id={self.user_id}, status='{self.status}')>"