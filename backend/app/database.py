"""Database connection and session management"""

from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.config import get_settings


# ORM Base class for all models
Base = declarative_base()


class DatabaseManager:
    """Manage database connections and sessions"""

    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None

    def init_async(self):
        """Initialize async database engine and session factory"""
        settings = get_settings()

        # Create async SQLAlchemy engine with dialect-specific settings
        engine_kwargs = {
            "echo": settings.DATABASE_ECHO,
        }

        # SQLite doesn't support pool_pre_ping, pool_size, etc.
        if "sqlite" not in settings.DATABASE_URL.lower():
            engine_kwargs.update({
                "pool_pre_ping": True,  # Test connection before use
                "pool_size": 20,
                "max_overflow": 10,
                "pool_recycle": 3600,  # Recycle connections after 1 hour
                "pool_class": QueuePool,
            })
        # For SQLite, don't set any pool parameters

        self.async_engine = create_async_engine(
            settings.DATABASE_URL,
            **engine_kwargs
        )

        # Create async session factory
        self.async_session_factory = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        return self

    def init_sync(self):
        """Initialize sync database engine and session factory"""
        settings = get_settings()

        # Create sync SQLAlchemy engine (for migrations, admin tasks)
        sync_engine_kwargs = {
            "echo": settings.DATABASE_ECHO,
        }

        # SQLite doesn't support pool configuration
        if "sqlite" not in settings.DATABASE_URL.lower():
            sync_engine_kwargs.update({
                "pool_pre_ping": True,
                "pool_size": 10,
                "max_overflow": 5,
                "pool_recycle": 3600,
            })
        # For SQLite, don't set any pool parameters

        self.engine = create_engine(
            settings.DATABASE_URL,
            **sync_engine_kwargs
        )

        # Create sync session factory
        self.session_factory = sessionmaker(
            self.engine,
            autoflush=False,
            autocommit=False,
        )

        return self

    async def close_async(self):
        """Close async database connections"""
        if self.async_engine:
            await self.async_engine.dispose()

    def close_sync(self):
        """Close sync database connections"""
        if self.engine:
            self.engine.dispose()

    async def create_tables(self):
        """Create all database tables"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Drop all database tables (for testing)"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


# Global database manager instance
db_manager = DatabaseManager().init_async().init_sync()


# Dependency injection for async sessions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection"""
    async with db_manager.async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Context manager for manual session usage
class AsyncDBContext:
    """Async context manager for database sessions"""

    def __init__(self):
        self.session = None

    async def __aenter__(self) -> AsyncSession:
        """Enter async context"""
        self.session = db_manager.async_session_factory()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()


def get_sync_db():
    """Get sync database session (for migrations, scripts)"""
    session = db_manager.session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Connection pool status
async def get_connection_pool_status():
    """Get current connection pool status"""
    if db_manager.async_engine:
        pool = db_manager.async_engine.pool
        return {
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow(),
        }
    return None
