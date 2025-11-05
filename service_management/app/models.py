"""
SQLAlchemy models for Service Management.
Defines services offered by the salon.
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from common.database import Base

class Service(Base):
    """
    Service model representing salon services.
    
    This table stores all services offered by the salon including
    pricing, duration, and availability status.
    """
    __tablename__ = "services"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Service details
    name = Column(String, nullable=False, index=True)  # e.g., "Haircut", "Manicure"
    description = Column(String)  # Detailed service description
    category = Column(String, index=True)  # e.g., "Hair", "Nails", "Skin"
    
    # Pricing and duration
    price = Column(Numeric(10, 2), nullable=False)  # Price in decimal format (e.g., 25.00)
    duration_minutes = Column(Integer, nullable=False)  # Service duration in minutes
    
    # Service status
    is_active = Column(Boolean, default=True)  # Whether service is currently offered
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}', price={self.price})>"