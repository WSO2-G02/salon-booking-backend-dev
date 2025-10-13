"""
Service Management API endpoints.
Handles CRUD operations for salon services.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas
import sys
sys.path.append('../../../')
from common.database import get_db

# Create router instance
router = APIRouter(prefix="/api/v1/services", tags=["services"])

@router.post("/", response_model=schemas.ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new salon service.
    
    This endpoint allows adding new services to the salon's catalog.
    Only authenticated staff members should access this endpoint.
    
    Args:
        service: Service creation data
        db: Database session
    
    Returns:
        Created service information
    """
    try:
        return crud.create_service(db=db, service=service)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service"
        )

@router.get("/", response_model=List[schemas.ServiceResponse])
async def get_services(
    skip: int = Query(0, ge=0, description="Number of services to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of services to return"),
    category: Optional[str] = Query(None, description="Filter by service category"),
    active_only: bool = Query(True, description="Only return active services"),
    db: Session = Depends(get_db)
):
    """
    Retrieve list of salon services.
    
    This endpoint supports pagination and filtering by category.
    Used by both customers (to see available services) and staff (for management).
    
    Args:
        skip: Number of services to skip (pagination)
        limit: Maximum number of services to return
        category: Filter by service category
        active_only: Whether to include only active services
        db: Database session
    
    Returns:
        List of services matching criteria
    """
    services = crud.get_services(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        active_only=active_only
    )
    return services

@router.get("/{service_id}", response_model=schemas.ServiceResponse)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific service by ID.
    
    Args:
        service_id: ID of the service to retrieve
        db: Database session
    
    Returns:
        Service information
    
    Raises:
        HTTPException 404: If service not found
    """
    service = crud.get_service(db=db, service_id=service_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service

@router.put("/{service_id}", response_model=schemas.ServiceResponse)
async def update_service(
    service_id: int,
    service_update: schemas.ServiceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing service.
    
    This endpoint allows updating service details like price, duration, etc.
    Only authenticated staff members should access this endpoint.
    
    Args:
        service_id: ID of service to update
        service_update: Updated service data
        db: Database session
    
    Returns:
        Updated service information
    
    Raises:
        HTTPException 404: If service not found
    """
    service = crud.update_service(db=db, service_id=service_id, service_update=service_update)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a service (soft delete).
    
    This endpoint performs a soft delete by setting is_active to False.
    This preserves historical data while removing the service from active use.
    
    Args:
        service_id: ID of service to delete
        db: Database session
    
    Raises:
        HTTPException 404: If service not found
    """
    success = crud.delete_service(db=db, service_id=service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

@router.get("/category/{category}", response_model=List[schemas.ServiceResponse])
async def get_services_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    """
    Get all services in a specific category.
    
    Args:
        category: Service category (e.g., "Hair", "Nails", "Skin")
        db: Database session
    
    Returns:
        List of services in the specified category
    """
    services = crud.get_services_by_category(db=db, category=category)
    return services