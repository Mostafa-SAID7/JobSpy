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

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Add the Backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.utils.security import hash_password


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
    """Create test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
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
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("password123"),
        is_email_verified=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers"""
    from app.core.config import settings
    from jose import jwt
    
    token = jwt.encode(
        {"sub": str(test_user.id)},
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    async def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
