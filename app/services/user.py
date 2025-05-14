# app/services/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional

def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user"""
    db_user = User(
        email=user_in.email,
        user_name=user_in.user_name,
        password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        department=user_in.department,
        tech_stack=user_in.tech_stack,
        profile_photo_url=user_in.profile_photo_url,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username"""
    return db.query(User).filter(User.user_name == username).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return None
    return user

def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """Update user data"""
    # Update user attributes
    for field, value in user_in.dict(exclude_unset=True).items():
        if field == "password" and value:
            # Hash password if provided
            setattr(user, field, get_password_hash(value))
        else:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def activate_user(db: Session, user: User) -> User:
    """Activate a user account"""
    user.active = True
    db.commit()
    db.refresh(user)
    return user
