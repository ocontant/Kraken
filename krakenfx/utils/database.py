import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from krakenfx.repository.models import Base
from krakenfx.utils.config import Settings


class DatabaseFactory:
    _instance = None
    _initialized = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        settings: Settings,
        logger: logging.Logger,
    ):
        if not self._initialized:
            self._settings = settings
            self._logger = logger
            self._async_engine = None
            self._sync_engine = None
            self._async_session_factory = None
            self._sync_session_factory = None
            self._sqlite_memory_async_engine = None
            self._sqlite_memory_sync_engine = None
            self._sqlite_memory_async_session_factory = None
            self._sqlite_memory_sync_session_factory = None
            self._initialized = True

    # PostgreSQL methods
    async def get_async_engine(self):
        if not self._async_engine:
            try:
                self._async_engine = create_async_engine(
                    self._settings.DATABASE_URL.unicode_string(), future=True, echo=True
                )
                self._logger.info(
                    "Async PostgreSQL database engine created successfully."
                )
            except SQLAlchemyError as e:
                self._logger.error(
                    f"Error creating async PostgreSQL database engine: %{e}"
                )
                raise
        return self._async_engine

    def get_sync_engine(self):
        if not self._sync_engine:
            try:
                self._sync_engine = create_engine(
                    self._settings.DATABASE_URL.unicode_string(), future=True, echo=True
                )
                self._logger.info(
                    "Sync PostgreSQL database engine created successfully."
                )
            except SQLAlchemyError as e:
                self._logger.error(
                    f"Error creating sync PostgreSQL database engine: {e}"
                )
                raise
        return self._sync_engine

    async def get_async_session_factory(self):
        if not self._async_session_factory:
            try:
                async_engine = self.get_async_engine()
                self._async_session_factory = sessionmaker(
                    bind=async_engine, class_=AsyncSession, expire_on_commit=False
                )
                self._logger.info(
                    "Async PostgreSQL session factory created successfully."
                )
            except SQLAlchemyError as e:
                self._logger.error(
                    f"Error creating async PostgreSQL session factory: {e}"
                )
                raise
        return self._async_session_factory

    def get_sync_session_factory(self):
        if not self._sync_session_factory:
            try:
                sync_engine = self.get_sync_engine()
                self._sync_session_factory = sessionmaker(
                    bind=sync_engine, class_=Session, expire_on_commit=False
                )
                self._logger.info(
                    "Sync PostgreSQL session factory created successfully."
                )
            except SQLAlchemyError as e:
                self._logger.error(
                    f"Error creating sync PostgreSQL session factory: {e}"
                )
                raise
        return self._sync_session_factory

    async def get_async_session(self):
        async_session_factory = self.get_async_session_factory()
        return async_session_factory()

    def get_sync_session(self):
        sync_session_factory = self.get_sync_session_factory()
        return sync_session_factory()

    # SQLite methods
    async def get_sqlite_memory_async_engine(self):
        if not self._sqlite_memory_async_engine:
            try:
                self._sqlite_memory_async_engine = create_async_engine(
                    "sqlite+aiosqlite:///:memory:", future=True, echo=True
                )
                self._logger.info(
                    "SQLite memory async database engine created successfully."
                )
            except SQLAlchemyError as e:
                self._logger.error(
                    f"Error creating SQLite memory async database engine: {e}"
                )
                raise
        return self._sqlite_memory_async_engine

    def get_sqlite_memory_sync_engine(self):
        if not self._sqlite_memory_sync_engine:
            try:
                self._sqlite_memory_sync_engine = create_engine(
                    "sqlite:///:memory:", future=True, echo=True
                )
                self._logger.info(
                    "SQLite memory sync database engine created successfully."
                )
            except SQLAlchemyError as e:
                self._logger.error(
                    f"Error creating SQLite memory sync database engine: {e}"
                )
                raise
        return self._sqlite_memory_sync_engine

    async def create_async_tables(self, engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def create_sync_tables(self, engine):
        with engine.begin() as conn:
            Base.metadata.create_all(conn)

    async def get_sqlite_memory_async_session_factory(self):
        if not self._sqlite_memory_async_session_factory:
            try:
                sqlite_memory_async_engine = await self.get_sqlite_memory_async_engine()
                await self.create_async_tables(sqlite_memory_async_engine)
                self._sqlite_memory_async_session_factory = sessionmaker(
                    bind=sqlite_memory_async_engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                )
                self._logger.info(
                    "SQLite memory async session factory created successfully."
                )
            except SQLAlchemyError as e:
                self._logger.error(
                    f"Error creating SQLite memory async session factory: {e}"
                )
                raise
        return self._sqlite_memory_async_session_factory

    def get_sqlite_memory_sync_session_factory(self):
        if not self._sqlite_memory_sync_session_factory:
            try:
                sqlite_memory_sync_engine = self.get_sqlite_memory_sync_engine()
                self.create_sync_tables(sqlite_memory_sync_engine)
                self._sqlite_memory_sync_session_factory = sessionmaker(
                    bind=sqlite_memory_sync_engine,
                    class_=Session,
                    expire_on_commit=False,
                )
                self._logger.info(
                    "SQLite memory sync session factory created successfully."
                )
            except SQLAlchemyError as e:
                self._logger.error(
                    f"Error creating SQLite memory sync session factory: {e}"
                )
                raise
        return self._sqlite_memory_sync_session_factory

    async def get_sqlite_memory_async_session(self):
        sqlite_memory_async_session_factory = (
            await self.get_sqlite_memory_async_session_factory()
        )
        return sqlite_memory_async_session_factory()

    def get_sqlite_memory_sync_session(self):
        sqlite_memory_sync_session_factory = (
            self.get_sqlite_memory_sync_session_factory()
        )
        return sqlite_memory_sync_session_factory()
