from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings

# This is the critical line that was missing.
# It creates the base class that all ORM models will inherit from.
Base = declarative_base()

# Create an async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create a sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

async def get_db():
    """Dependency to get a database session."""
    async with SessionLocal() as session:
        yield session
