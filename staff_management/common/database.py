from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing in your .env file")


# Create async engine for Azure SQL Database
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Reconnect automatically if idle
    connect_args={"timeout": 30}
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Base class for ORM models
Base = declarative_base()


# Dependency for FastAPI routes
async def get_db():
    """Provide an async DB session for each request"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
