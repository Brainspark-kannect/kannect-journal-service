# app/utils/jwt.py
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import jwt
from app.config.settings import settings

def create_access_token(subject: str, roles: List[str] = None, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token matching Spring Boot's implementation
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": subject,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "roles": roles or []
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify JWT token from Spring Boot
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
