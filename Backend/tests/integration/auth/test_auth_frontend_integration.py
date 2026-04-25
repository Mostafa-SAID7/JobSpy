"""
Authentication Frontend Integration Tests

Tests for frontend and backend integration in authentication flow.

**Validates: Requirements 7.2, 8.5**
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


class TestFrontendBackendIntegration:
    """Test frontend and backend integration."""
    
    def test_frontend_registration_flow(self, test_client: TestClient):
        """
        Property: Frontend can successfully register users
        
        For any registration request from frontend with valid data,
        the backend should accept and return proper response.
        
        **Validates: Requirements 7.2, 8.5**
        """
        # Simulate frontend registration request
        user_data = {
            "email": "frontend@example.com",
            "password": "SecurePass123!",
            "full_name": "Frontend User"
        }
        
        response = test_client.post(
            "/api/v1/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response contains all required fields
        assert "user_id" in data
        assert "email" in data
        assert "full_name" in data
        assert "created_at" in data
        assert "is_active" in data
    
    def test_frontend_login_flow(self, test_client: TestClient):
        """
        Property: Frontend can successfully login users
        
        For any login request from frontend with valid credentials,
        the backend should return tokens.
        
        **Validates: Requirements 7.2, 8.5**
        """
        # Register user first
        user_data = {
            "email": "frontendlogin@example.com",
            "password": "SecurePass123!",
            "full_name": "Frontend Login User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        # Simulate frontend login request
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response contains all required fields
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
    
    def test_frontend_token_storage_and_refresh(self, test_client: TestClient):
        """
        Property: Frontend can store and refresh tokens
        
        For any tokens received from login, frontend should be able
        to use refresh token to get new access token.
        
        **Validates: Requirements 7.2, 8.5**
        """
        # Register and login
        user_data = {
            "email": "tokentest@example.com",
            "password": "SecurePass123!",
            "full_name": "Token Test User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        
        tokens = login_response.json()
        
        # Simulate frontend storing tokens and refreshing
        refresh_response = test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
            headers={"Content-Type": "application/json"}
        )
        
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
