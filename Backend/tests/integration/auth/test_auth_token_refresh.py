"""
Authentication Token Refresh Tests

Tests for token refresh flow and validation.

**Validates: Requirements 4.5**
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData, Table, Column, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.core.database import get_db


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


class TestTokenRefresh:
    """Test token refresh flow."""
    
    def test_refresh_token_success(self, test_client: TestClient):
        """
        Property: Access token can be refreshed using refresh token
        
        For any valid refresh token, a new access token should be issued.
        
        **Validates: Requirements 4.5**
        """
        # Register and login
        user_data = {
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        refresh_response = test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600
    
    def test_refresh_with_invalid_token(self, test_client: TestClient):
        """
        Property: Invalid refresh tokens are rejected
        
        For any invalid refresh token, refresh should fail.
        """
        refresh_response = test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        
        assert refresh_response.status_code == 401
        assert "invalid" in refresh_response.json()["detail"].lower()
