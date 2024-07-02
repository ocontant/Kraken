# my_project/core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from krakenfx.core.config import Settings

Base = declarative_base()

def get_postgresql_session(settings: Settings, *, force_new=False):
    if force_new:
        engine = create_async_engine(settings.DATABASE_URL.unicode_string(), future=True, echo=True)
        SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        return SessionLocal
    
# Expose session, base, and engine
__all__ = ['engine', 'get_postgresql_session']