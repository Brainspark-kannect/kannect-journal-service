# app/config/settings.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Journal API"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "dpg-d0a1571r0fns73e0melg-a.singapore-postgres.render.com:5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "pAdo1Zeme66SHatZmtFnpF9CFklo2Ugx")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "kannectdb")
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "2e23d7dc-3ab6-4fcd-b698-ede98aab8539")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: str = "8000"
    DEBUG: bool = True
    NLP_MODEL: str = "en_core_web_sm"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
