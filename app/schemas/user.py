# app/schemas/user.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class RoleBase(BaseModel):
    role_name: str

class Role(RoleBase):
    id: int
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    user_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    tech_stack: Optional[str] = None
    profile_photo_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    active: bool
    wallet_balance: int
    last_login: Optional[datetime] = None
    roles: List[Role] = []
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password: str
