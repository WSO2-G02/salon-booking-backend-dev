"""
CRUD operations for Service Management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from . import models, schemas
from typing import List, Optional

def get_service(db: Session, service_id: int) -> Optional[models.Service]:
    """Get service by ID"""
    return db.query(models.Service).filter(models.Service.id == service_id).first()

def get_services(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    active_only: bool = True
) -> List[models.Service]:
    """
    Get list of services with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        category: Filter by service category
        active_only: Only return active services
    
    Returns:
        List of service models
    """
    query = db.query(models.Service)
    
    # Apply filters
    if active_only:
        query = query.filter(models.Service.is_active == True)
    
    if category:
        query = query.filter(models.Service.category == category)
    
    # Apply pagination and return results
    return query.offset(skip).limit(limit).all()

def create_service(db: Session, service: schemas.ServiceCreate) -> models.Service:
    """
    Create a new service.
    
    Args:
        db: Database session
        service: Service creation data
    
    Returns:
        Created service model
    """
    db_service = models.Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def update_service(
    db: Session, 
    service_id: int, 
    service_update: schemas.ServiceUpdate
) -> Optional[models.Service]:
    """
    Update an existing service.
    
    Args:
        db: Database session
        service_id: ID of service to update
        service_update: Updated service data
    
    Returns:
        Updated service model or None if not found
    """
    db_service = get_service(db, service_id)
    if not db_service:
        return None
    
    # Update only provided fields
    update_data = service_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_service, field, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int) -> bool:
    """
    Delete a service (soft delete by setting is_active to False).
    
    Args:
        db: Database session
        service_id: ID of service to delete
    
    Returns:
        True if deleted, False if not found
    """
    db_service = get_service(db, service_id)
    if not db_service:
        return False
    
    # Soft delete - set is_active to False instead of actual deletion
    db_service.is_active = False
    db.commit()
    return True

def get_services_by_category(db: Session, category: str) -> List[models.Service]:
    """Get all active services in a specific category"""
    return db.query(models.Service).filter(
        and_(
            models.Service.category == category,
            models.Service.is_active == True
        )
    ).all()