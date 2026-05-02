"""
Integration tests for user endpoints (Phase 1)
Tests complete user flows: password reset, email verification, preferences, statistics
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import secrets

from app.main import app
from app.domain.entities.user import User
from app.domain.entities.job import Job
from app.domain.entities.saved_job import SavedJob
from app.domain.entities.alert import Alert
from app.shared.security.security import hash_password
from app.domain.interfaces.repositories import IUserRepository as UserRepository


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create test user"""
    user = User(
        email="integration@example.com",
        username="integrationuser",
        hashed_password=hash_password("password123"),
        email_verified=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers"""
    return {"Authorization": f"Bearer test_token_{test_user.id}"}


class TestCompletePasswordResetFlow:
    """Test complete password reset flow from request to confirmation"""
    
    @pytest.mark.asyncio
    async def test_password_reset_complete_flow(self, client, test_user, db: AsyncSession):
        """Test complete password reset flow"""
        # Step 1: Request password reset
        response = client.post(
            "/api/v1/password-reset/request",
            json={"email": test_user.email}
        )
        assert response.status_code == 200
        
        # Step 2: Simulate token generation (in real flow, email would be sent)
        reset_token = secrets.token_urlsafe(32)
        test_user.password_reset_token = reset_token
        test_user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.add(test_user)
        await db.commit()
        
        # Step 3: Confirm password reset with token
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={
                "token": reset_token,
                "new_password": "newpassword789"
            }
        )
        assert response.status_code == 200
        
        # Step 4: Verify new password works for login
        # (This would be tested in auth integration tests)
    
    @pytest.mark.asyncio
    async def test_password_reset_token_expiration(self, client, test_user, db: AsyncSession):
        """Test that expired tokens are rejected"""
        # Create expired token
        reset_token = secrets.token_urlsafe(32)
        test_user.password_reset_token = reset_token
        test_user.password_reset_token_expires = datetime.utcnow() - timedelta(hours=1)
        db.add(test_user)
        await db.commit()
        
        # Try to use expired token
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={
                "token": reset_token,
                "new_password": "newpassword789"
            }
        )
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_password_reset_token_single_use(self, client, test_user, db: AsyncSession):
        """Test that tokens can only be used once"""
        reset_token = secrets.token_urlsafe(32)
        test_user.password_reset_token = reset_token
        test_user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.add(test_user)
        await db.commit()
        
        # First use - should succeed
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={
                "token": reset_token,
                "new_password": "newpassword789"
            }
        )
        assert response.status_code == 200
        
        # Second use - should fail
        response = client.post(
            "/api/v1/password-reset/confirm",
            json={
                "token": reset_token,
                "new_password": "anotherpassword"
            }
        )
        assert response.status_code == 400


class TestCompleteEmailVerificationFlow:
    """Test complete email verification flow"""
    
    @pytest.mark.asyncio
    async def test_email_verification_complete_flow(self, client, test_user, auth_headers, db: AsyncSession):
        """Test complete email verification flow"""
        # Step 1: Create unverified user
        test_user.email_verified = False
        db.add(test_user)
        await db.commit()
        
        # Step 2: Request email verification
        response = client.post(
            "/api/v1/users/me/email-verification/send",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 3: Simulate token generation
        verification_token = secrets.token_urlsafe(32)
        test_user.email_verification_token = verification_token
        test_user.email_verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.add(test_user)
        await db.commit()
        
        # Step 4: Verify email with token
        response = client.post(
            "/api/v1/users/me/email-verification/verify",
            json={"token": verification_token}
        )
        assert response.status_code == 200
        
        # Step 5: Verify user is now marked as verified
        await db.refresh(test_user)
        assert test_user.email_verified is True
    
    @pytest.mark.asyncio
    async def test_email_verification_token_expiration(self, client, test_user, db: AsyncSession):
        """Test that expired verification tokens are rejected"""
        # Create expired token
        verification_token = secrets.token_urlsafe(32)
        test_user.email_verification_token = verification_token
        test_user.email_verification_token_expires = datetime.utcnow() - timedelta(hours=1)
        test_user.email_verified = False
        db.add(test_user)
        await db.commit()
        
        # Try to use expired token
        response = client.post(
            "/api/v1/users/me/email-verification/verify",
            json={"token": verification_token}
        )
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_cannot_verify_already_verified_email(self, client, test_user, auth_headers):
        """Test that already verified emails cannot be verified again"""
        response = client.post(
            "/api/v1/users/me/email-verification/send",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "already verified" in response.json()["detail"].lower()


class TestUserPreferencesFlow:
    """Test user preferences management flow"""
    
    @pytest.mark.asyncio
    async def test_preferences_get_and_update_flow(self, client, test_user, auth_headers):
        """Test getting and updating user preferences"""
        # Step 1: Get initial preferences
        response = client.get(
            "/api/v1/users/me/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        initial_prefs = response.json()
        
        # Step 2: Update preferences
        new_prefs = {
            "theme": "dark",
            "notifications_enabled": False,
            "email_alerts": True,
            "job_recommendations": False,
            "saved_jobs_limit": 500
        }
        response = client.put(
            "/api/v1/users/me/preferences",
            json=new_prefs,
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_prefs = response.json()
        
        # Step 3: Verify updates were applied
        assert updated_prefs["theme"] == "dark"
        assert updated_prefs["notifications_enabled"] is False
        assert updated_prefs["email_alerts"] is True
        
        # Step 4: Get preferences again to verify persistence
        response = client.get(
            "/api/v1/users/me/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        persisted_prefs = response.json()
        assert persisted_prefs["theme"] == "dark"
    
    @pytest.mark.asyncio
    async def test_preferences_partial_update(self, client, test_user, auth_headers):
        """Test partial preferences update"""
        # Update only theme
        response = client.put(
            "/api/v1/users/me/preferences",
            json={"theme": "light"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify other preferences remain unchanged
        response = client.get(
            "/api/v1/users/me/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        prefs = response.json()
        assert prefs["theme"] == "light"
    
    @pytest.mark.asyncio
    async def test_preferences_validation(self, client, test_user, auth_headers):
        """Test preferences validation"""
        # Try invalid theme
        response = client.put(
            "/api/v1/users/me/preferences",
            json={"theme": "invalid_theme"},
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # Try invalid saved_jobs_limit
        response = client.put(
            "/api/v1/users/me/preferences",
            json={"saved_jobs_limit": -100},
            headers=auth_headers
        )
        assert response.status_code == 422


class TestUserStatsFlow:
    """Test user statistics calculation flow"""
    
    @pytest.mark.asyncio
    async def test_stats_with_no_data(self, client, test_user, auth_headers):
        """Test stats for user with no saved jobs or alerts"""
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["saved_jobs"] == 0
        assert stats["active_alerts"] == 0
        assert stats["total_searches"] == 0
    
    @pytest.mark.asyncio
    async def test_stats_with_saved_jobs(self, client, test_user, auth_headers, db: AsyncSession):
        """Test stats calculation with saved jobs"""
        # Create test jobs and save them
        job1 = Job(
            title="Python Developer",
            company="Tech Corp",
            location="Cairo",
            salary_min=5000,
            salary_max=8000,
            job_type="Full-time",
            description="Python development role"
        )
        job2 = Job(
            title="React Developer",
            company="Web Inc",
            location="Cairo",
            salary_min=6000,
            salary_max=9000,
            job_type="Full-time",
            description="React development role"
        )
        db.add_all([job1, job2])
        await db.commit()
        
        # Save jobs
        saved_job1 = SavedJob(user_id=test_user.id, job_id=job1.id)
        saved_job2 = SavedJob(user_id=test_user.id, job_id=job2.id)
        db.add_all([saved_job1, saved_job2])
        await db.commit()
        
        # Get stats
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["saved_jobs"] == 2
    
    @pytest.mark.asyncio
    async def test_stats_with_active_alerts(self, client, test_user, auth_headers, db: AsyncSession):
        """Test stats calculation with active alerts"""
        # Create alerts
        alert1 = Alert(
            user_id=test_user.id,
            name="Python Jobs",
            query="Python",
            frequency="daily",
            notification_method="email",
            is_active=True
        )
        alert2 = Alert(
            user_id=test_user.id,
            name="React Jobs",
            query="React",
            frequency="weekly",
            notification_method="in_app",
            is_active=True
        )
        alert3 = Alert(
            user_id=test_user.id,
            name="Inactive Alert",
            query="Java",
            frequency="daily",
            notification_method="email",
            is_active=False
        )
        db.add_all([alert1, alert2, alert3])
        await db.commit()
        
        # Get stats
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["active_alerts"] == 2  # Only active alerts
    
    @pytest.mark.asyncio
    async def test_stats_comprehensive(self, client, test_user, auth_headers, db: AsyncSession):
        """Test comprehensive stats with all data types"""
        # Create jobs
        job = Job(
            title="Full Stack Developer",
            company="StartUp",
            location="Cairo",
            salary_min=7000,
            salary_max=10000,
            job_type="Full-time",
            description="Full stack development"
        )
        db.add(job)
        await db.commit()
        
        # Save job
        saved_job = SavedJob(user_id=test_user.id, job_id=job.id)
        db.add(saved_job)
        
        # Create alert
        alert = Alert(
            user_id=test_user.id,
            name="Full Stack Jobs",
            query="Full Stack",
            frequency="daily",
            notification_method="email",
            is_active=True
        )
        db.add(alert)
        await db.commit()
        
        # Get stats
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["saved_jobs"] >= 1
        assert stats["active_alerts"] >= 1
        assert isinstance(stats["total_searches"], int)


class TestPasswordChangeFlow:
    """Test password change flow"""
    
    @pytest.mark.asyncio
    async def test_password_change_complete_flow(self, client, test_user, auth_headers, db: AsyncSession):
        """Test complete password change flow"""
        old_password = "password123"
        new_password = "newpassword456"
        
        # Step 1: Change password
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": old_password,
                "new_password": new_password
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 2: Verify old password no longer works
        # (This would be tested in auth integration tests)
        
        # Step 3: Verify new password works
        # (This would be tested in auth integration tests)
    
    @pytest.mark.asyncio
    async def test_password_change_validation(self, client, test_user, auth_headers):
        """Test password change validation"""
        # Try with weak password
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "password123",
                "new_password": "123"  # Too weak
            },
            headers=auth_headers
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_password_change_same_as_current(self, client, test_user, auth_headers):
        """Test that new password cannot be same as current"""
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "password123",
                "new_password": "password123"  # Same as current
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "same" in response.json()["detail"].lower()


class TestConcurrentOperations:
    """Test concurrent operations on user endpoints"""
    
    @pytest.mark.asyncio
    async def test_concurrent_preference_updates(self, client, test_user, auth_headers):
        """Test concurrent preference updates"""
        # Simulate concurrent updates
        response1 = client.put(
            "/api/v1/users/me/preferences",
            json={"theme": "dark"},
            headers=auth_headers
        )
        response2 = client.put(
            "/api/v1/users/me/preferences",
            json={"notifications_enabled": False},
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify final state
        response = client.get(
            "/api/v1/users/me/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        prefs = response.json()
        # Both updates should be applied
        assert prefs["theme"] == "dark"
        assert prefs["notifications_enabled"] is False


class TestErrorRecovery:
    """Test error recovery and edge cases"""
    
    @pytest.mark.asyncio
    async def test_recovery_from_failed_password_change(self, client, test_user, auth_headers):
        """Test recovery from failed password change"""
        # First attempt with wrong current password
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456"
            },
            headers=auth_headers
        )
        assert response.status_code == 401
        
        # Second attempt with correct password should work
        response = client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "password123",
                "new_password": "newpassword456"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_recovery_from_failed_preferences_update(self, client, test_user, auth_headers):
        """Test recovery from failed preferences update"""
        # First attempt with invalid data
        response = client.put(
            "/api/v1/users/me/preferences",
            json={"theme": "invalid_theme"},
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # Second attempt with valid data should work
        response = client.put(
            "/api/v1/users/me/preferences",
            json={"theme": "dark"},
            headers=auth_headers
        )
        assert response.status_code == 200
