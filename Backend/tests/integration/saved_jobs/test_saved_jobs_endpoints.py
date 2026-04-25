"""
Saved Jobs Endpoints Tests
Tests for saved jobs API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_job_id() -> str:
    """Sample job ID for testing"""
    return "test-job-id-123"


@pytest.fixture
def sample_user_id() -> str:
    """Sample user ID for testing"""
    return "test-user-id-456"


class TestSaveJobEndpoint:
    """Test save job endpoint"""
    
    def test_save_job_endpoint_exists(self, client: TestClient):
        """Test that save job endpoint exists"""
        response = client.post("/api/v1/saved-jobs", json={"job_id": "test-id"})
        # Should not return 404
        assert response.status_code != 404
    
    def test_save_job_requires_authentication(self, client: TestClient):
        """Test that save job requires authentication"""
        response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-id"}
        )
        assert response.status_code == 401
    
    def test_save_job_with_invalid_token(self, client: TestClient):
        """Test save job with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-id"},
            headers=headers
        )
        assert response.status_code == 401
    
    def test_save_job_accepts_job_id(self, client: TestClient):
        """Test that save job accepts job_id parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-job-id-123"},
            headers=headers
        )
        # Should not return 422 (validation error)
        assert response.status_code != 422
    
    def test_save_job_accepts_notes(self, client: TestClient):
        """Test that save job accepts notes parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={
                "job_id": "test-job-id-123",
                "notes": "Interesting position"
            },
            headers=headers
        )
        # Should not return 422 (validation error)
        assert response.status_code != 422


class TestGetSavedJobsEndpoint:
    """Test get saved jobs endpoint"""
    
    def test_get_saved_jobs_endpoint_exists(self, client: TestClient):
        """Test that get saved jobs endpoint exists"""
        response = client.get("/api/v1/saved-jobs")
        # Should not return 404
        assert response.status_code != 404
    
    def test_get_saved_jobs_requires_authentication(self, client: TestClient):
        """Test that get saved jobs requires authentication"""
        response = client.get("/api/v1/saved-jobs")
        assert response.status_code == 401
    
    def test_get_saved_jobs_with_invalid_token(self, client: TestClient):
        """Test get saved jobs with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        assert response.status_code == 401
    
    def test_get_saved_jobs_accepts_pagination(self, client: TestClient):
        """Test that get saved jobs accepts pagination parameters"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get(
            "/api/v1/saved-jobs?skip=0&limit=20",
            headers=headers
        )
        # Should not return 422 (validation error)
        assert response.status_code != 422
    
    def test_get_saved_jobs_returns_json(self, client: TestClient):
        """Test that get saved jobs returns JSON"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        # Should return JSON
        assert response.headers.get("content-type") == "application/json"


class TestDeleteSavedJobEndpoint:
    """Test delete saved job endpoint"""
    
    def test_delete_saved_job_endpoint_exists(self, client: TestClient):
        """Test that delete saved job endpoint exists"""
        response = client.delete("/api/v1/saved-jobs/test-id")
        # Should not return 404
        assert response.status_code != 404
    
    def test_delete_saved_job_requires_authentication(self, client: TestClient):
        """Test that delete saved job requires authentication"""
        response = client.delete("/api/v1/saved-jobs/test-id")
        assert response.status_code == 401
    
    def test_delete_saved_job_with_invalid_token(self, client: TestClient):
        """Test delete saved job with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.delete("/api/v1/saved-jobs/test-id", headers=headers)
        assert response.status_code == 401
    
    def test_delete_saved_job_by_job_id_endpoint_exists(self, client: TestClient):
        """Test that delete by job_id endpoint exists"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.delete(
            "/api/v1/saved-jobs/by-job/test-job-id",
            headers=headers
        )
        # Should not return 404
        assert response.status_code != 404


class TestUpdateSavedJobEndpoint:
    """Test update saved job endpoint"""
    
    def test_update_saved_job_endpoint_exists(self, client: TestClient):
        """Test that update saved job endpoint exists"""
        response = client.put(
            "/api/v1/saved-jobs/test-id",
            json={"notes": "Updated notes"}
        )
        # Should not return 404
        assert response.status_code != 404
    
    def test_update_saved_job_requires_authentication(self, client: TestClient):
        """Test that update saved job requires authentication"""
        response = client.put(
            "/api/v1/saved-jobs/test-id",
            json={"notes": "Updated notes"}
        )
        assert response.status_code == 401
    
    def test_update_saved_job_with_invalid_token(self, client: TestClient):
        """Test update saved job with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.put(
            "/api/v1/saved-jobs/test-id",
            json={"notes": "Updated notes"},
            headers=headers
        )
        assert response.status_code == 401
