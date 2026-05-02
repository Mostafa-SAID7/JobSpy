"""
Pytest configuration and fixtures
"""
import sys
import os
from pathlib import Path
import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient
import fakeredis.aioredis

# ---------------------------------------------------------------------------
# Patch passlib's bcrypt detect_wrap_bug BEFORE any import of pwd_context.
# bcrypt>=4.0 refuses passwords >72 bytes; passlib's initialization probe
# uses a 73-byte secret which raises ValueError on modern bcrypt.
# ---------------------------------------------------------------------------
try:
    import passlib.handlers.bcrypt as _passlib_bcrypt
    _passlib_bcrypt.detect_wrap_bug = lambda ident: False  # type: ignore[attr-defined]
except Exception:
    pass

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Add the Backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.infrastructure.persistence.sqlalchemy.database import Base, get_db
from app.domain.entities.user import User
from app.shared.security.security import hash_password


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session backed by in-memory SQLite."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create a standard test user (hashed with bcrypt via patched passlib)."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=hash_password("secret99"),  # <=72 bytes, safe
        email_verified=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for a test user."""
    from app.config.settings import settings
    from jose import jwt

    token = jwt.encode(
        {"sub": str(test_user.id)},
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create HTTP test client with the test DB injected."""
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def mock_redis():
    """Replace redis with fakeredis for every test."""
    from app.infrastructure.cache.redis import redis_client

    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    redis_client.redis = fake_redis

    yield fake_redis

    await fake_redis.aclose()
