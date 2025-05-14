# app/core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
import jwt
from app.db.session import get_db
from app.models.user import User, Role
from app.schemas.token import TokenData
from app.utils.jwt import decode_token
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """
    Get the current authenticated user based on the JWT token from Spring Boot
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        roles = payload.get("roles", [])
        token_data = TokenData(username=username, roles=roles)
    except jwt.JWTError:
        raise credentials_exception
    
    # Try to find user by email first, then by username if email not found
    user = db.query(User).filter(User.email == token_data.username).first()
    if user is None:
        user = db.query(User).filter(User.user_name == token_data.username).first()
        if user is None:
            raise credentials_exception
    
    try:
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Get or create roles from the token
        db_roles = []
        for role_name in token_data.roles:
            # Try to find existing role
            role = db.query(Role).filter(Role.role_name == role_name).first()
            if role is None:
                # Create role if it doesn't exist
                role = Role(role_name=role_name)
                db.add(role)
            db_roles.append(role)
        
        # Update user's roles
        user.roles = db_roles
        db.commit()
        
    except Exception as e:
        logger.error(f"Error updating user roles: {str(e)}")
        db.rollback()
        # Don't fail the request if role update fails
        pass
    
    return user

async def get_active_user(
    current_user: User = Depends(get_current_user),
):
    """
    Check if the current user is active
    """
    if not current_user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
