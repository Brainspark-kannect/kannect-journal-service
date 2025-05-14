# app/core/security.py
from datetime import timedelta
from passlib.context import CryptContext
from app.config.settings import settings
from app.utils.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches the hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def generate_auth_token(email: str, roles: list = None) -> str:
    """Generate JWT authentication token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        subject=email, 
        roles=roles,
        expires_delta=access_token_expires
    )
