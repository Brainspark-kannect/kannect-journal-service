# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user import authenticate_user, create_user, get_user_by_email, get_user_by_username
from app.schemas.token import Token
from app.schemas.user import User, UserCreate
from app.core.security import generate_auth_token
from app.config.settings import settings

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=User)
async def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email exists
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    if get_user_by_username(db, user_in.user_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    return create_user(db, user_in)

@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login and get access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token with user roles
    token = generate_auth_token(user.email, roles=["user"])  # Add roles as needed
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }
