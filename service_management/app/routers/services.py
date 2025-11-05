"""
Service Management API endpoints with Admin Authentication.
All endpoints require valid admin token.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, parent_dir)

from app import crud, schemas
from app.auth import require_admin, TokenData
from common.database import get_db
# Create router instance
router = APIRouter(prefix="/api/v1/services", tags=["services"])

@router.post(
    "/", 
    response_model=schemas.ServiceResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create New Service",
    description="Create a new salon service. Requires admin privileges."
)
async def create_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Create a new salon service.
    
    **Admin Only** - Token validation applied (STEP 05)
    
    Args:
        service: Service creation data
        db: Database session
        current_user: Authenticated admin user
    
    Returns:
        Created service information
    """
    try:
        return crud.create_service(db=db, service=service)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service: {str(e)}"
        )

@router.get(
    "/", 
    response_model=List[schemas.ServiceResponse],
    summary="Get All Services",
    description="Retrieve list of salon services with filtering options."
)
async def get_services(
    skip: int = Query(0, ge=0, description="Number of services to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of services to return"),
    category: Optional[str] = Query(None, description="Filter by service category"),
    active_only: bool = Query(True, description="Only return active services"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Retrieve list of salon services.
    
    **Admin Only** - Token validation applied (STEP 05)
    
    Supports pagination and filtering by category.
    
    Args:
        skip: Number of services to skip (pagination)
        limit: Maximum number of services to return
        category: Filter by service category
        active_only: Whether to include only active services
        db: Database session
        current_user: Authenticated admin user
    
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

@router.get(
    "/{service_id}", 
    response_model=schemas.ServiceResponse,
    summary="Get Service by ID",
    description="Retrieve a specific service by its ID."
)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Get a specific service by ID.
    
    **Admin Only** - Token validation applied (STEP 05)
    
    Args:
        service_id: ID of the service to retrieve
        db: Database session
        current_user: Authenticated admin user
    
    Returns:
        Service information
    
    Raises:
        HTTPException 404: If service not found
    """
    service = crud.get_service(db=db, service_id=service_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found"
        )
    return service

@router.put(
    "/{service_id}", 
    response_model=schemas.ServiceResponse,
    summary="Update Service",
    description="Update an existing service. Requires admin privileges."
)
async def update_service(
    service_id: int,
    service_update: schemas.ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Update an existing service.
    
    **Admin Only** - Token validation applied (STEP 05)
    
    Allows updating service details like price, duration, etc.
    
    Args:
        service_id: ID of service to update
        service_update: Updated service data
        db: Database session
        current_user: Authenticated admin user
    
    Returns:
        Updated service information
    
    Raises:
        HTTPException 404: If service not found
    """
    service = crud.update_service(
        db=db, 
        service_id=service_id, 
        service_update=service_update
    )
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found"
        )
    return service

@router.delete(
    "/{service_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Service",
    description="Soft delete a service (sets is_active to False)."
)
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Delete a service (soft delete).
    
    **Admin Only** - Token validation applied (STEP 05)
    
    Performs a soft delete by setting is_active to False.
    This preserves historical data while removing the service from active use.
    
    Args:
        service_id: ID of service to delete
        db: Database session
        current_user: Authenticated admin user
    
    Raises:
        HTTPException 404: If service not found
    """
    success = crud.delete_service(db=db, service_id=service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found"
        )

@router.get(
    "/category/{category}", 
    response_model=List[schemas.ServiceResponse],
    summary="Get Services by Category",
    description="Retrieve all services in a specific category."
)
async def get_services_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Get all services in a specific category.
    
    **Admin Only** - Token validation applied (STEP 05)
    
    Args:
        category: Service category (e.g., "Hair", "Nails", "Skin")
        db: Database session
        current_user: Authenticated admin user
    
    Returns:
        List of services in the specified category
    """
    services = crud.get_services_by_category(db=db, category=category)
    return services