"""
User Service API Routes
Implements all REST API endpoints for the User Service
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict
import logging

from app.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse,
    RefreshTokenRequest, AccessTokenResponse, UserProfileResponse,
    UserProfileUpdateRequest, PasswordChangeRequest, UserCreateRequest,
    UserListResponse, PaginationParams, SuccessResponse, PaginatedResponse
)
from app.services import UserService
from app.database import get_db_manager, DatabaseManager
from app.dependencies import get_current_user, get_current_admin
from app.auth import jwt_manager
from app.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["User Service"])
settings = get_settings()
logger = logging.getLogger(__name__)


def get_user_service(db: DatabaseManager = Depends(get_db_manager)) -> UserService:
    """Dependency to get UserService instance"""
    return UserService(db)


# ============================================================================
# Public Authentication Endpoints
# ============================================================================

@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegisterRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Register a new customer account
    
    - **username**: Unique username (3-50 chars, alphanumeric + underscore)
    - **email**: Valid email address
    - **password**: Minimum 8 chars with uppercase, lowercase, and digit
    - **full_name**: Optional full name
    - **phone**: Optional phone number
    """
    try:
        user = user_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            phone=user_data.phone
        )
        
        return SuccessResponse(
            status="success",
            data={"user": UserProfileResponse(**user).dict()},
            message="User registered successfully"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Authenticate user and return access and refresh tokens
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT access token (15 min expiry) and refresh token (7 day expiry)
    """
    # Authenticate user
    user = user_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    token_data = {
        "user_id": user['id'],
        "username": user['username'],
        "user_type": user['user_type']
    }
    
    access_token = jwt_manager.create_access_token(token_data)
    refresh_token = jwt_manager.create_refresh_token({"user_id": user['id']})
    
    # Store refresh token in database
    user_service.create_session(user['id'], refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Refresh access token using a valid refresh token
    
    - **refresh_token**: Valid refresh token from login
    
    Returns new access token
    """
    # Validate refresh token
    user = user_service.validate_refresh_token(token_data.refresh_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    token_data = {
        "user_id": user['user_id'],
        "username": user['username'],
        "user_type": user['user_type']
    }
    
    access_token = jwt_manager.create_access_token(token_data)
    
    return AccessTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    token_data: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Logout user by invalidating refresh token
    
    - **refresh_token**: Refresh token to invalidate
    """
    success = user_service.logout_user(token_data.refresh_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    return SuccessResponse(
        status="success",
        message="Logged out successfully"
    )


# ============================================================================
# User Profile Endpoints (Authenticated Users)
# ============================================================================

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get current user's profile information
    
    Requires: Valid access token in Authorization header
    """
    return UserProfileResponse(**current_user)


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: Dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Update current user's profile information
    
    - **full_name**: New full name (optional)
    - **phone**: New phone number (optional)
    - **email**: New email address (optional)
    
    Requires: Valid access token in Authorization header
    """
    try:
        updated_user = user_service.update_user_profile(
            user_id=current_user['id'],
            full_name=profile_data.full_name,
            phone=profile_data.phone,
            email=profile_data.email
        )
        
        return UserProfileResponse(**updated_user)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.put("/profile/password", response_model=SuccessResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Change current user's password
    
    - **current_password**: Current password for verification
    - **new_password**: New password (min 8 chars with uppercase, lowercase, digit)
    
    Requires: Valid access token in Authorization header
    """
    try:
        user_service.change_password(
            user_id=current_user['id'],
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        return SuccessResponse(
            status="success",
            message="Password changed successfully"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


# ============================================================================
# Admin User Management Endpoints
# ============================================================================

@router.post("/users", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    current_admin: Dict = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
):
    """
    Create a new user account (Admin only)
    
    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Password
    - **user_type**: 'user' or 'admin'
    - **full_name**: Optional full name
    - **phone**: Optional phone number
    
    Requires: Admin access token
    """
    try:
        user = user_service.create_user_as_admin(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            user_type=user_data.user_type,
            full_name=user_data.full_name,
            phone=user_data.phone
        )
        
        return SuccessResponse(
            status="success",
            data={"user": UserProfileResponse(**user).dict()},
            message="User created successfully"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )


@router.get("/users", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_admin: Dict = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get paginated list of all users (Admin only)
    
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 10, max: 100)
    
    Requires: Admin access token
    """
    try:
        users, total = user_service.get_all_users(page=page, limit=limit)
        
        # Convert to response models
        user_list = [UserListResponse(**user).dict() for user in users]
        
        return PaginatedResponse.create(
            data=user_list,
            total=total,
            page=page,
            limit=limit
        )
    
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
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
        "service": "user_service",
        "database": "connected" if db_healthy else "disconnected"
    }