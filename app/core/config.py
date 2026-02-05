"""
Core Configuration
Environment variables and app settings
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    PROJECT_NAME: str = "FastAPI JWT RBAC"
    VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Clean Architecture FastAPI with JWT & RBAC"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app/siswa.db"
    
    # JWT Settings
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
