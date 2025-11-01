"""Test configuration and fixtures"""

import pytest
import pytest_asyncio
import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base, clear_mappers
from sqlalchemy import MetaData
from uuid import uuid4

# Set test environment BEFORE importing app modules
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Ensure app module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

# Clear settings cache to pick up test environment variables
from app.config import get_settings
get_settings.cache_clear()

# Import database models
from app.models.database import User, Case, Observation, Conflict, Report, AuditLog
from app.models.schemas import UserRole

# Pre-computed bcrypt hash for "testpass123" to avoid bcrypt initialization issues
# This hash was generated with: bcrypt.hashpw(b"testpass123", bcrypt.gensalt())
TEST_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQw8W8ZqW"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create test database with fresh metadata for each test"""
    from app.database import Base

    # Use in-memory database for speed
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        # Create all tables using the declarative Base metadata
        # Note: checkfirst=True prevents "index already exists" errors
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)

    async_session_local = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    session = async_session_local()

    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def test_user_analyst(test_db: AsyncSession):
    """Create test analyst user"""
    user = User(
        id=uuid4(),
        email="analyst@test.com",
        full_name="Test Analyst",
        hashed_password=TEST_PASSWORD_HASH,
        role=UserRole.ANALYST,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_lead(test_db: AsyncSession):
    """Create test lead partner user"""
    user = User(
        id=uuid4(),
        email="lead@test.com",
        full_name="Test Lead Partner",
        hashed_password=TEST_PASSWORD_HASH,
        role=UserRole.LEAD_PARTNER,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_admin(test_db: AsyncSession):
    """Create test admin user"""
    user = User(
        id=uuid4(),
        email="admin@test.com",
        full_name="Test Admin",
        hashed_password=TEST_PASSWORD_HASH,
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_case(test_db: AsyncSession, test_user_analyst):
    """Create test case"""
    test_case = Case(
        id=uuid4(),
        title="Test Case",
        description="Test case for unit tests",
        company_name="Test Company",
        sector="Technology",
        created_by=test_user_analyst.id,
        extra_data={},
    )
    test_db.add(test_case)
    await test_db.commit()
    await test_db.refresh(test_case)
    return test_case
