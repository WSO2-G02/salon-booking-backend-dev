from datetime import datetime, timedelta, timezone
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.hash import get_password_hash
from db.models import Session, User
from db.session import Base
from schemas.user import UserCreate

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=UserCreate)


class CRUDBase(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()


class CRUDUser(CRUDBase[User, UserCreate]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        hashed_password = get_password_hash(obj_in.password)
        db_obj = self.model(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=hashed_password,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            user_type='user',
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


class CRUDSession:
    async def get_by_token(self, db: AsyncSession, *, refresh_token: str) -> Optional[Session]:
        result = await db.execute(
            select(Session).filter(Session.refresh_token == refresh_token)
        )
        session = result.scalars().first()

        # CORRECTED: Compare naive datetimes by getting the current UTC time
        # and then stripping the timezone info before comparison.
        if session and session.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
            await db.delete(session)
            await db.commit()
            return None
        
        return session

    async def create(self, db: AsyncSession, *, user_id: int, refresh_token: str) -> Session:
        # CORRECTED: Create a naive datetime object for UTC by stripping the
        # timezone info before saving to the database.
        expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).replace(tzinfo=None)
        db_obj = Session(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, db_obj: Session):
        await db.delete(db_obj)
        await db.commit()
        return db_obj


user = CRUDUser(User)
session = CRUDSession()
