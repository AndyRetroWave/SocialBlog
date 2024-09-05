from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

if settings.MODE != "TEST":
    DATABASE_PARAM: dict = {}
    DATABASE_URL: str = settings.DB_URL
elif settings.MODE == "TEST":
    DATABASE_PARAM: dict = {"poolclass": NullPool}
    DATABASE_URL: str = settings.TEST_DB_URL


engine = create_async_engine(DATABASE_URL, **DATABASE_PARAM)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
