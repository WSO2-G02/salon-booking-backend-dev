"""
Configuration Management for Staff Service
Loads and validates environment variables
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings loaded from environment variables"""
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
        # JWT Configuration (must match User Service for token validation)
    # JWT_SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Service Configuration
    SERVICE_NAME: str = "staff_service"
    SERVICE_PORT: int = 8003
    HOST: str = "0.0.0.0"
    

    
    # Database Configuration (Single AWS RDS MySQL Database)
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str = "salon-db"  # Single database with all tables
    DB_USER: str
    DB_PASSWORD: str
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Notification Service URL
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_allowed_origins(self) -> List[str]:
        """Parse CORS allowed origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance
    Using lru_cache ensures we only load settings once
    """
    return Settings()