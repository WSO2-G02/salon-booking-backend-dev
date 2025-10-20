from fastapi import APIRouter, Depends, HTTPException, status
from core.security import get_current_user, get_current_admin_user
from db import crud
from db.models import User as DBUser
from schemas.user import UserCreate, UserPublic
from db.session import get_db

router = APIRouter()

@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: DBUser = Depends(get_current_user)):
    """

    Get current user's profile.
    """
    return current_user

@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user_in: UserCreate,
    db=Depends(get_db),
    current_admin: DBUser = Depends(get_current_admin_user)
):
    """
    Create a new user (can be admin or user). Admin only.
    """
    user = await crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = await crud.user.create(db, obj_in=user_in)
    return new_user
