"""
Authentication API endpoints.
Handles user registration, login, and profile management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import crud, models, schemas
import sys
sys.path.append('../../../')
from common.database import get_db
from common.security import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Create router instance
router = APIRouter(prefix="/api/v1", tags=["authentication"])

# Security scheme for JWT token authentication
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency to get current authenticated user from JWT token.
    This function is used to protect endpoints that require authentication.
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
    
    Returns:
        User model of authenticated user
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Verify and decode token
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    This endpoint creates a new user in the system with the provided information.
    The password is automatically hashed before storage for security.
    
    Args:
        user: User registration data (email, username, password, etc.)
        db: Database session (automatically injected)
    
    Returns:
        Created user information (excluding password)
    
    Raises:
        HTTPException 409: If email or username already exists
        HTTPException 422: If validation fails
    """
    try:
        # Attempt to create new user
        db_user = crud.create_user(db=db, user=user)
        return db_user
    except ValueError as e:
        # Handle duplicate email/username errors
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

@router.post("/login", response_model=dict)
async def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    
    This endpoint verifies user credentials and returns a JWT token
    that can be used to access protected endpoints.
    
    Args:
        user_credentials: Login data (username/email and password)
        db: Database session (automatically injected)
    
    Returns:
        Dictionary containing access token and user information
    
    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Authenticate user
    user = crud.authenticate_user(
        db, user_credentials.username, user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_staff": user.is_staff
        }
    }

@router.get("/profile", response_model=schemas.UserResponse)
async def get_user_profile(current_user: models.User = Depends(get_current_user)):
    """
    Get current user's profile information.
    
    This is a protected endpoint that requires authentication.
    Returns the profile of the currently logged-in user.
    
    Args:
        current_user: Authenticated user (automatically injected)
    
    Returns:
        User profile information
    """
    return current_user

@router.get("/profile/{user_id}", response_model=schemas.UserResponse)
async def get_user_profile_by_id(
    user_id: int, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user profile by ID.
    
    This endpoint allows getting any user's profile.
    In production, you might want to add authorization checks
    to ensure users can only access appropriate profiles.
    
    Args:
        user_id: ID of user to retrieve
        current_user: Authenticated user (for authorization)
        db: Database session
    
    Returns:
        User profile information
    
    Raises:
        HTTPException 404: If user not found
    """
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/profile", response_model=schemas.UserResponse)
async def update_user_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Allows authenticated users to update their own profile information.
    Only provided fields will be updated.
    
    Args:
        user_update: Updated user data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated user profile
    """
    updated_user = crud.update_user(db, current_user.id, user_update)
    return updated_user