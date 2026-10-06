from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker

from auth_service.config import settings


class Base(DeclarativeBase):
    pass


url_db = settings.db_asyncurl
engine = create_async_engine(url_db, echo=True)

SessionMaker = async_sessionmaker(engine)
