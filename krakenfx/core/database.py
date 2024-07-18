# krakenfx/core/database.py
import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from krakenfx.core.config import Settings
from krakenfx.repository.models import Base

logger = logging.getLogger(__name__)


class DatabaseFactory:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._async_engine = None
        self._sync_engine = None
        self._async_session_factory = None
        self._sync_session_factory = None

    def get_async_engine(self):
        if not self._async_engine:
            try:
                self._async_engine = create_async_engine(
                    self._settings.DATABASE_URL.unicode_string(), future=True, echo=True
                )
                logger.info("Async database engine created successfully.")
            except SQLAlchemyError as e:
                logger.error(f"Error creating async database engine: {e}")
                raise
        return self._async_engine

    def get_sync_engine(self):
        if not self._sync_engine:
            try:
                self._sync_engine = create_engine(
                    self._settings.DATABASE_URL.unicode_string(), future=True, echo=True
                )
                logger.info("Sync database engine created successfully.")
            except SQLAlchemyError as e:
                logger.error(f"Error creating sync database engine: {e}")
                raise
        return self._sync_engine

    def get_async_session_factory(self):
        if not self._async_session_factory:
            try:
                async_engine = self.get_async_engine()
                self._async_session_factory = sessionmaker(
                    bind=async_engine, class_=AsyncSession, expire_on_commit=False
                )
                logger.info("Async session factory created successfully.")
            except SQLAlchemyError as e:
                logger.error(f"Error creating async session factory: {e}")
                raise
        return self._async_session_factory

    def get_sync_session_factory(self):
        if not self._sync_session_factory:
            try:
                sync_engine = self.get_sync_engine()
                self._sync_session_factory = sessionmaker(
                    bind=sync_engine, class_=Session, expire_on_commit=False
                )
                logger.info("Sync session factory created successfully.")
            except SQLAlchemyError as e:
                logger.error(f"Error creating sync session factory: {e}")
                raise
        return self._sync_session_factory

    def get_async_session(self):
        async_session_factory = self.get_async_session_factory()
        return async_session_factory()

    def get_sync_session(self):
        sync_session_factory = self.get_sync_session_factory()
        return sync_session_factory()


# Create a global factory instance
db_factory = DatabaseFactory(Settings())


def get_async_postgresql_session(*, force_new=False):
    if force_new:
        new_factory = DatabaseFactory(Settings())
        return new_factory.get_async_session()
    return db_factory.get_async_session()


def get_sync_postgresql_session(*, force_new=False):
    if force_new:
        new_factory = DatabaseFactory(Settings())
        return new_factory.get_sync_session()
    return db_factory.get_sync_session()


# Expose session, base, and engine
__all__ = [
    "get_async_postgresql_session",
    "get_sync_postgresql_session",
    "Base",
    "db_factory",
]
