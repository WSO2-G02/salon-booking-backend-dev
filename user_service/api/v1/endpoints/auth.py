from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.config import settings
from core.security import create_access_token, create_refresh_token
from core.hash import verify_password
from db import crud
from schemas.token import Token, TokenRefresh
from schemas.user import UserCreate, UserPublic
from db.session import get_db

router = APIRouter()

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db=Depends(get_db)):
    """
    Register a new user.
    """
    user = await crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await crud.user.create(db, obj_in=user_in)
    return new_user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    db=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticate user and return tokens.
    """
    user = await crud.user.get_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    # Store refresh token in DB
    await crud.session.create(db, user_id=user.id, refresh_token=refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }

@router.post("/refresh", response_model=Token)
async def refresh_access_token(token_in: TokenRefresh, db=Depends(get_db)):
    """
    Get a new access token from a refresh token.
    """
    session = await crud.session.get_by_token(db, refresh_token=token_in.refresh_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    user = await crud.user.get(db, id=session.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Issue new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    # Delete old session and create new one
    await crud.session.delete(db, db_obj=session)
    await crud.session.create(db, user_id=user.id, refresh_token=new_refresh_token)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token,
    }

@router.post("/logout")
async def logout(token_in: TokenRefresh, db=Depends(get_db)):
    """
    Invalidate refresh token.
    """
    session = await crud.session.get_by_token(db, refresh_token=token_in.refresh_token)
    if session:
        await crud.session.delete(db, db_obj=session)
    return {"msg": "Successfully logged out"}
