"""
Authentication User Login Tests

Tests for user login flow and credential validation.

**Validates: Requirements 4.4, 4.5**
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData, Table, Column, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.infrastructure.persistence.sqlalchemy.database import get_db


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client with in-memory database."""
    # Use synchronous SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Create only the User table for testing
    metadata = MetaData()
    users_table = Table(
        'users',
        metadata,
        Column('id', String, primary_key=True, default=lambda: str(uuid4())),
        Column('email', String, unique=True, nullable=False),
        Column('hashed_password', String, nullable=False),
        Column('full_name', String),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    
    metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()


class TestUserLogin:
    """Test user login flow."""
    
    def test_login_with_correct_credentials(self, test_client: TestClient):
        """
        Property: Users can login with correct credentials
        
        For any registered user with correct email and password,
        login should succeed and return access and refresh tokens.
        
        **Validates: Requirements 4.4**
        """
        # Register user first
        user_data = {
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        # Login with correct credentials
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600
    
    def test_login_with_invalid_credentials(self, test_client: TestClient):
        """
        Property: Invalid credentials are rejected
        
        For any registered user with incorrect password,
        login should fail.
        
        **Validates: Requirements 4.5**
        """
        # Register user first
        user_data = {
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        # Login with wrong password
        login_data = {
            "email": user_data["email"],
            "password": "WrongPassword123!"
        }
        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, test_client: TestClient):
        """
        Property: Login fails for non-existent users
        
        For any email not registered, login should fail.
        """
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
