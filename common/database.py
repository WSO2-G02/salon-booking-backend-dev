"""
Database configuration shared across all services.
This file provides database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os

class DatabaseSettings(BaseSettings):
    """
    Database configuration using environment variables.
    This allows easy configuration changes without code modification.
    """
    postgres_user: str = "salon_user"
    postgres_password: str = "salon_password"
    postgres_server: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "salon_booking"
    
    @property
    def database_url(self) -> str:
        """Constructs the complete database URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

# Initialize database settings
db_settings = DatabaseSettings()

# Create SQLAlchemy engine
# echo=True enables SQL query logging for debugging
engine = create_engine(db_settings.database_url, echo=True)

# Create session factory
# autocommit=False: transactions need explicit commit
# autoflush=False: don't automatically flush changes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session.
    This function is used with FastAPI's dependency injection system.
    It ensures proper session cleanup after each request.
    """
    db = SessionLocal()
    try:
        yield db  # Provide session to the endpoint
    finally:
        db.close()  # Always close session, even if error occurs