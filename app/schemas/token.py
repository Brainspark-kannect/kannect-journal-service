# app/schemas/token.py
from typing import List, Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: int
    roles: Optional[List[str]] = []

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []
