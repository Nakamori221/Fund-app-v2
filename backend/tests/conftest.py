"""Test configuration and fixtures"""

import pytest
import pytest_asyncio
import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4

# Set test environment BEFORE importing app modules
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Ensure app module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

# Clear settings cache to pick up test environment variables
from app.config import get_settings
get_settings.cache_clear()

from app.database import Base
from app.models.database import User
from app.models.schemas import UserRole
from app.core.security import AuthService


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create test database with fresh schema for each test"""
    import tempfile
    # Create a unique temporary database file for each test
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_url = f"sqlite+aiosqlite:///{temp_db.name}"
    temp_db.close()

    engine = create_async_engine(
        db_url,
        echo=False,
    )

    async with engine.begin() as conn:
        # Create schema (use checkfirst=True to avoid errors)
        await conn.run_sync(lambda conn_sync: Base.metadata.create_all(conn_sync, checkfirst=True))

    async_session_local = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    session = async_session_local()
    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

        # Clean up temporary database file
        import os
        try:
            os.unlink(temp_db.name)
        except Exception:
            pass


@pytest_asyncio.fixture
async def test_user_analyst(test_db: AsyncSession) -> User:
    """Create test analyst user"""
    user = User(
        id=uuid4(),
        email="analyst@test.com",
        full_name="Test Analyst",
        hashed_password=AuthService.hash_password("testpass123"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_lead(test_db: AsyncSession) -> User:
    """Create test lead partner user"""
    user = User(
        id=uuid4(),
        email="lead@test.com",
        full_name="Test Lead Partner",
        hashed_password=AuthService.hash_password("testpass123"),
        role=UserRole.LEAD_PARTNER,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_admin(test_db: AsyncSession) -> User:
    """Create test admin user"""
    user = User(
        id=uuid4(),
        email="admin@test.com",
        full_name="Test Admin",
        hashed_password=AuthService.hash_password("testpass123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user
