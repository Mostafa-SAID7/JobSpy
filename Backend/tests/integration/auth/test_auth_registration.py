"""
Authentication User Registration Tests

Tests for user registration flow and validation.

**Validates: Requirements 4.2**
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


class TestUserRegistration:
    """Test user registration flow."""
    
    def test_register_with_valid_credentials(self, test_client: TestClient):
        """
        Property: Users can register with valid credentials
        
        For any valid email and password, registration should succeed
        and return user data.
        
        **Validates: Requirements 4.2**
        """
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        
        response = test_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "user_id" in data
        assert "created_at" in data
    
    def test_register_duplicate_email(self, test_client: TestClient):
        """
        Property: Email must be unique
        
        For any email already registered, registration should fail
        with appropriate error.
        
        **Validates: Requirements 4.2**
        """
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        
        # First registration should succeed
        response1 = test_client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        response2 = test_client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    def test_register_invalid_email(self, test_client: TestClient):
        """
        Property: Email validation is enforced
        
        For any invalid email format, registration should fail.
        """
        user_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        
        response = test_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error
