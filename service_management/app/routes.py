"""
Service Management API Routes
Implements all REST API endpoints for the Service Management Service
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Optional
from decimal import Decimal
import logging

from app.schemas import (
    ServiceCreate, ServiceUpdate, ServiceResponse,
    SuccessResponse
)
from app.services import ServiceManagementService
from app.database import get_db_manager, DatabaseManager
from app.dependencies import get_current_admin, get_authenticated_user

router = APIRouter(prefix="/api/v1", tags=["Service Management"])
logger = logging.getLogger(__name__)


def get_service_management_service(db: DatabaseManager = Depends(get_db_manager)) -> ServiceManagementService:
    """Dependency to get ServiceManagementService instance"""
    return ServiceManagementService(db)


# ============================================================================
# Service Management Endpoints
# ============================================================================

@router.post("/services", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    current_admin: Dict = Depends(get_current_admin),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Create a new salon service (Admin only)
    
    - **name**: Service name (unique, required)
    - **description**: Service description (optional)
    - **category**: Service category (optional)
    - **price**: Service price (required, must be > 0)
    - **duration_minutes**: Duration in minutes (required, must be > 0)
    
    Requires: Admin access token
    """
    try:
        service = service_mgmt.create_service(
            name=service_data.name,
            description=service_data.description,
            category=service_data.category,
            price=service_data.price,
            duration_minutes=service_data.duration_minutes
        )
        
        return SuccessResponse(
            status="success",
            data={"service": ServiceResponse(**service).dict()},
            message="Service created successfully"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Service creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service creation failed"
        )


@router.get("/services", response_model=List[ServiceResponse])
async def get_services(
    active_only: bool = Query(False, description="Filter active services only"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: Dict = Depends(get_authenticated_user),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Get list of all salon services (Authenticated users)
    
    - **active_only**: Filter active services (default: false)
    - **category**: Filter by category (optional)
    
    Requires: Valid access token
    """
    try:
        services = service_mgmt.get_all_services(
            active_only=active_only,
            category=category
        )
        
        return [ServiceResponse(**service) for service in services]
    
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch services"
        )

@router.get("/servicespub", response_model=List[ServiceResponse])
async def get_public_services(
    category: Optional[str] = Query(None, description="Filter by category"),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Public endpoint to fetch ACTIVE salon services (NO AUTH REQUIRED)

    - Only returns services where is_active = 1
    - Can be used on landing pages / before login
    """
    try:
        services = service_mgmt.get_all_services(
            active_only=True,  # only active services
            category=category
        )

        return [ServiceResponse(**service) for service in services]

    except Exception as e:
        logger.error(f"Error fetching public services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch public services"
        )


@router.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    current_user: Dict = Depends(get_authenticated_user),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Get details for a specific service (Authenticated users)
    
    - **service_id**: Service ID
    
    Requires: Valid access token
    """
    service = service_mgmt.get_service_by_id(service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return ServiceResponse(**service)


@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    current_admin: Dict = Depends(get_current_admin),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Update an existing service (Admin only)
    
    - **service_id**: Service ID
    - **name**: New name (optional)
    - **description**: New description (optional)
    - **category**: New category (optional)
    - **price**: New price (optional)
    - **duration_minutes**: New duration (optional)
    - **is_active**: Active status (optional)
    
    Requires: Admin access token
    """
    try:
        service = service_mgmt.update_service(
            service_id=service_id,
            name=service_update.name,
            description=service_update.description,
            category=service_update.category,
            price=service_update.price,
            duration_minutes=service_update.duration_minutes,
            is_active=service_update.is_active
        )
        
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        return ServiceResponse(**service)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Service update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service update failed"
        )


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    current_admin: Dict = Depends(get_current_admin),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Deactivate a service (soft delete) (Admin only)
    
    - **service_id**: Service ID
    
    Requires: Admin access token
    """
    success = service_mgmt.delete_service(service_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return None


# ============================================================================
# Additional Query Endpoints
# ============================================================================

@router.get("/services/category/{category}", response_model=List[ServiceResponse])
async def get_services_by_category(
    category: str,
    current_user: Dict = Depends(get_authenticated_user),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Get all active services in a specific category (Authenticated users)
    
    - **category**: Category name
    
    Requires: Valid access token
    """
    try:
        services = service_mgmt.get_services_by_category(category)
        return [ServiceResponse(**service) for service in services]
    
    except Exception as e:
        logger.error(f"Error fetching services by category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch services"
        )


@router.get("/services/price-range", response_model=List[ServiceResponse])
async def get_services_by_price_range(
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    current_user: Dict = Depends(get_authenticated_user),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Get services within a price range (Authenticated users)
    
    - **min_price**: Minimum price (optional)
    - **max_price**: Maximum price (optional)
    
    Requires: Valid access token
    """
    try:
        services = service_mgmt.get_services_by_price_range(min_price, max_price)
        return [ServiceResponse(**service) for service in services]
    
    except Exception as e:
        logger.error(f"Error fetching services by price range: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch services"
        )


@router.get("/categories", response_model=List[str])
async def get_categories(
    current_user: Dict = Depends(get_authenticated_user),
    service_mgmt: ServiceManagementService = Depends(get_service_management_service)
):
    """
    Get list of all service categories (Authenticated users)
    
    Requires: Valid access token
    """
    try:
        categories = service_mgmt.get_categories()
        return categories
    
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )


# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get("/health")
async def health_check(db: DatabaseManager = Depends(get_db_manager)):
    """
    Health check endpoint to verify service and database status
    """
    db_healthy = db.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "service_management",
        "database": "connected" if db_healthy else "disconnected"
    }