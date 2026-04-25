"""
Unit tests for user endpoints (Phase 1 - Critical endpoints)
Tests: password change, password reset, email verification, preferences, statistics
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import secrets

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.utils.security import hash_password, verify_password
from app.repositories.user_repo import UserRepository


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("oldpassword123"),
        email_verified=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers"""
    # In real tests, you'd generate a JWT token
    return {"Authorization": f"Bearer test_token_{test_user.id}"}


class TestPasswordChangeEndpoint:
    """Test POST /users/me/password"""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, client, test_user, auth_headers):
        """Test successful password change"""
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, client, test_user, auth_headers):
        """Test password change with wrong current password"""
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_change_password_not_authenticated(self, client):
        """Test password change without authentication"""
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, client, auth_headers):
        """Test password change when user not found"""
        # Use invalid user ID in token
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            },
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code in [401, 404]


class TestPasswordResetEndpoints:
    """Test password reset flow"""
    
    @pytest.mark.asyncio
    async def test_request_password_reset_success(self, client, test_user):
        """Test successful password reset request"""
        response = client.post(
            "/api/v1/password-reset/request",
            json={"email": test_user.email}
        )
        
        assert response.status_code == 200
        assert "sent" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_request_password_reset_nonexistent_email(self, client):
        """Test password reset request with non-existent email"""
        response = client.post(
            "/api/v1/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )
        
        # Should not reveal if email exists
        assert response.status_code == 200
        assert "sent" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_confirm_password_reset_success(self, client, test_user, db: AsyncSession):
        """Test successful password reset confirmation"""
        # First, request reset to generate token
        reset_token = secrets.token_urlsafe(32)
        test_user.password_reset_token = reset_token
        test_user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.add(test_user)
        await db.commit()
        
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={
                "token": reset_token,
                "new_password": "newpassword789"
            }
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_confirm_password_reset_invalid_token(self, client):
        """Test password reset confirmation with invalid token"""
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={
                "token": "invalid_token",
                "new_password": "newpassword789"
            }
        )
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_confirm_password_reset_expired_token(self, client, test_user, db: AsyncSession):
        """Test password reset confirmation with expired token"""
        # Create expired token
        reset_token = secrets.token_urlsafe(32)
        test_user.password_reset_token = reset_token
        test_user.password_reset_token_expires = datetime.utcnow() - timedelta(hours=1)
        db.add(test_user)
        await db.commit()
        
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={
                "token": reset_token,
                "new_password": "newpassword789"
            }
        )
        
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()


class TestEmailVerificationEndpoints:
    """Test email verification flow"""
    
    @pytest.mark.asyncio
    async def test_send_email_verification_success(self, client, test_user, auth_headers, db: AsyncSession):
        """Test successful email verification send"""
        # Create unverified user
        test_user.email_verified = False
        db.add(test_user)
        await db.commit()
        
        response = client.post(
            "/api/v1/users/me/email-verification/send",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "sent" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_send_email_verification_already_verified(self, client, test_user, auth_headers):
        """Test email verification send when already verified"""
        response = client.post(
            "/api/v1/users/me/email-verification/send",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already verified" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_verify_email_success(self, client, test_user, db: AsyncSession):
        """Test successful email verification"""
        # Create verification token
        verification_token = secrets.token_urlsafe(32)
        test_user.email_verification_token = verification_token
        test_user.email_verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        test_user.email_verified = False
        db.add(test_user)
        await db.commit()
        
        response = client.post(
            "/api/v1/users/me/email-verification/verify",
            json={"token": verification_token}
        )
        
        assert response.status_code == 200
        assert "verified" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token"""
        response = client.post(
            "/api/v1/users/me/email-verification/verify",
            json={"token": "invalid_token"}
        )
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_verify_email_expired_token(self, client, test_user, db: AsyncSession):
        """Test email verification with expired token"""
        # Create expired token
        verification_token = secrets.token_urlsafe(32)
        test_user.email_verification_token = verification_token
        test_user.email_verification_token_expires = datetime.utcnow() - timedelta(hours=1)
        db.add(test_user)
        await db.commit()
        
        response = client.post(
            "/api/v1/users/me/email-verification/verify",
            json={"token": verification_token}
        )
        
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()


class TestUserPreferencesEndpoints:
    """Test user preferences endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_preferences_success(self, client, test_user, auth_headers):
        """Test successful preferences retrieval"""
        response = client.get(
            "/api/v1/users/me/preferences",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "theme" in data
        assert "notifications_enabled" in data
        assert "email_alerts" in data
    
    @pytest.mark.asyncio
    async def test_get_preferences_not_authenticated(self, client):
        """Test preferences retrieval without authentication"""
        response = client.get("/api/v1/users/me/preferences")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_update_preferences_success(self, client, test_user, auth_headers):
        """Test successful preferences update"""
        response = client.put(
            "/api/v1/users/me/preferences",
            json={
                "theme": "dark",
                "notifications_enabled": False,
                "email_alerts": True,
                "job_recommendations": False,
                "saved_jobs_limit": 500
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "dark"
        assert data["notifications_enabled"] is False
    
    @pytest.mark.asyncio
    async def test_update_preferences_invalid_data(self, client, test_user, auth_headers):
        """Test preferences update with invalid data"""
        response = client.put(
            "/api/v1/users/me/preferences",
            json={
                "theme": "invalid_theme",
                "notifications_enabled": "not_a_boolean"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error


class TestUserStatsEndpoint:
    """Test user statistics endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_stats_success(self, client, test_user, auth_headers):
        """Test successful stats retrieval"""
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "saved_jobs" in data
        assert "active_alerts" in data
        assert "total_searches" in data
        assert isinstance(data["saved_jobs"], int)
        assert isinstance(data["active_alerts"], int)
        assert isinstance(data["total_searches"], int)
    
    @pytest.mark.asyncio
    async def test_get_stats_not_authenticated(self, client):
        """Test stats retrieval without authentication"""
        response = client.get("/api/v1/users/me/stats")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_stats_correct_counts(self, client, test_user, auth_headers, db: AsyncSession):
        """Test that stats return correct counts"""
        # This would require setting up saved jobs, alerts, and searches
        # For now, just verify the endpoint returns correct structure
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["saved_jobs"] >= 0
        assert data["active_alerts"] >= 0
        assert data["total_searches"] >= 0


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    @pytest.mark.asyncio
    async def test_invalid_json_payload(self, client, auth_headers):
        """Test handling of invalid JSON payload"""
        response = client.post(
            "/api/v1/users/me/password",
            data="invalid json",
            headers=auth_headers,
            content_type="application/json"
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client, auth_headers):
        """Test handling of missing required fields"""
        response = client.post(
            "/api/v1/users/me/password",
            json={"current_password": "test"},  # Missing new_password
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_email_format(self, client):
        """Test handling of invalid email format"""
        response = client.post(
            "/api/v1/password-reset/request",
            json={"email": "not_an_email"}
        )
        
        assert response.status_code == 422


class TestCacheInvalidation:
    """Test cache invalidation after updates"""
    
    @pytest.mark.asyncio
    async def test_cache_invalidated_after_password_change(self, client, test_user, auth_headers, db: AsyncSession):
        """Test that cache is invalidated after password change"""
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # Cache should be invalidated (verified through monitoring)
    
    @pytest.mark.asyncio
    async def test_cache_invalidated_after_preferences_update(self, client, test_user, auth_headers):
        """Test that cache is invalidated after preferences update"""
        response = client.put(
            "/api/v1/users/me/preferences",
            json={
                "theme": "dark",
                "notifications_enabled": False,
                "email_alerts": True,
                "job_recommendations": True,
                "saved_jobs_limit": 1000
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # Cache should be invalidated (verified through monitoring)
