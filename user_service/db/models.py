from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.mssql import BIT
from sqlalchemy.orm import relationship

from .session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    user_type = Column(String(10), nullable=False, default='user')
    is_active = Column(BIT, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # EAGER LOADING CONFIGURATION:
    # This tells SQLAlchemy to always fetch related sessions when a user is fetched.
    sessions = relationship(
        "Session", 
        back_populates="user", 
        cascade="all, delete-orphan", 
        lazy="selectin"
    )


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # EAGER LOADING CONFIGURATION:
    # This tells SQLAlchemy to always fetch the related user when a session is fetched.
    user = relationship(
        "User", 
        back_populates="sessions", 
        lazy="selectin"
    )