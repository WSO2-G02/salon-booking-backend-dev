from typing import Optional
from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    phone: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str
    user_type: str = "user"

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

# Properties stored in DB
class UserInDB(UserBase):
    id: int
    username: str
    password_hash: str
    user_type: str
    
    class Config:
        orm_mode = True

# Properties to return to client
class UserPublic(UserBase):
    id: int
    username: str
    user_type: str

    class Config:
        orm_mode = True