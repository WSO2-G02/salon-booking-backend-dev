"""
SQLAlchemy models for User Service.
Defines the database schema for users table.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
import sys
sys.path.append('../../')
from common.database import Base

class User(Base):
    """
    User model representing customers and staff members.
    
    This table stores all user information including authentication credentials.
    The password is stored as a bcrypt hash for security.
    """
    __tablename__ = "users"

    # Primary key - auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True)
    
    # User identification - must be unique
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    
    # Authentication
    password_hash = Column(String, nullable=False)  # bcrypt hash, never store plain text
    
    # Profile information
    full_name = Column(String, nullable=False)
    phone = Column(String)
    
    # User status and role
    is_active = Column(Boolean, default=True)  # For account activation/deactivation
    is_staff = Column(Boolean, default=False)  # Differentiates customers from staff
    
    # Timestamps - automatically managed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"