"""
Authentication Complete Flow Tests

Tests for the complete authentication flow end-to-end.

**Validates: Requirements 4.2, 4.3, 4.4, 4.5**
"""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData, Table, Column, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.core.database import get_db
from app.utils.security import create_access_token, decode_token


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


class TestCompleteAuthenticationFlow:
    """Test the complete authentication flow end-to-end."""
    
    def test_complete_flow_registration_to_token_refresh(
        self, test_client: TestClient
    ):
        """
        Property: Complete authentication flow works end-to-end
        
        For a new user, the complete flow from registration through
        login to token refresh should work correctly.
        
        **Validates: Requirements 4.2, 4.3, 4.4, 4.5**
        """
        # Step 1: Register new user
        user_data = {
            "email": "flowtest@example.com",
            "password": "SecurePass123!",
            "full_name": "Flow Test User"
        }
        
        register_response = test_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["user_id"]
        
        # Step 2: Login with registered credentials
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]
        
        # Step 3: Verify access token is valid
        payload = decode_token(access_token)
        assert payload["sub"] == user_id
        
        # Step 4: Refresh access token
        refresh_response = test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json()["access_token"]
        
        # Step 5: Verify new access token is valid
        new_payload = decode_token(new_access_token)
        assert new_payload["sub"] == user_id
    
    def test_flow_with_expired_token(self, test_client: TestClient):
        """
        Property: Expired tokens are properly rejected in the flow
        
        For any expired token, subsequent requests should fail.
        
        **Validates: Requirements 4.5**
        """
        # Register and login
        user_data = {
            "email": "expiredtest@example.com",
            "password": "SecurePass123!",
            "full_name": "Expired Test User"
        }
        test_client.post("/api/v1/auth/register", json=user_data)
        
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        
        # Create an expired token manually
        user_id = login_response.json()["access_token"]
        expired_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Trying to use expired token should fail
        with pytest.raises(Exception):
            decode_token(expired_token)
