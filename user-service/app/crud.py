"""
Database CRUD (Create, Read, Update, Delete) operations.
These functions handle all database interactions for users.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas
import sys
sys.path.append('../../')
from common.security import get_password_hash, verify_password
from typing import Optional

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Retrieve a user by ID.
    
    Args:
        db: Database session
        user_id: User's primary key
    
    Returns:
        User model or None if not found
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Retrieve a user by email address.
    
    Args:
        db: Database session
        email: User's email address
    
    Returns:
        User model or None if not found
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Retrieve a user by username.
    
    Args:
        db: Database session
        username: User's username
    
    Returns:
        User model or None if not found
    """
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_username_or_email(db: Session, identifier: str) -> Optional[models.User]:
    """
    Retrieve a user by username OR email (for login flexibility).
    
    Args:
        db: Database session
        identifier: Username or email
    
    Returns:
        User model or None if not found
    """
    return db.query(models.User).filter(
        or_(models.User.username == identifier, models.User.email == identifier)
    ).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user account.
    
    Args:
        db: Database session
        user: User creation data
    
    Returns:
        Created user model
    
    Raises:
        Exception: If email or username already exists
    """
    # Check if email or username already exists
    existing_email = get_user_by_email(db, user.email)
    if existing_email:
        raise ValueError("Email already registered")
    
    existing_username = get_user_by_username(db, user.username)
    if existing_username:
        raise ValueError("Username already taken")
    
    # Hash the password before storing
    hashed_password = get_password_hash(user.password)
    
    # Create new user instance
    db_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password,
        full_name=user.full_name,
        phone=user.phone
    )
    
    # Add to database
    db.add(db_user)
    db.commit()  # Save to database
    db.refresh(db_user)  # Refresh to get auto-generated fields like ID
    
    return db_user

def authenticate_user(db: Session, identifier: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user login attempt.
    
    Args:
        db: Database session
        identifier: Username or email
        password: Plain text password
    
    Returns:
        User model if authentication successful, None otherwise
    """
    # Find user by username or email
    user = get_user_by_username_or_email(db, identifier)
    if not user:
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    # Check if user account is active
    if not user.is_active:
        return None
    
    return user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """
    Update user profile information.
    
    Args:
        db: Database session
        user_id: User's ID
        user_update: Updated user data
    
    Returns:
        Updated user model or None if user not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user