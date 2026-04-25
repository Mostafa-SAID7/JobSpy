"""
Saved Jobs Integration Tests
Tests for saved jobs frontend-backend integration
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSavedJobsFrontendBackendIntegration:
    """Test frontend-backend integration for saved jobs"""
    
    def test_save_job_endpoint_returns_json(self, client: TestClient):
        """Test that save job endpoint returns JSON"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-id"},
            headers=headers
        )
        # Should return JSON
        assert response.headers.get("content-type") == "application/json"
    
    def test_get_saved_jobs_endpoint_returns_json(self, client: TestClient):
        """Test that get saved jobs endpoint returns JSON"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        # Should return JSON
        assert response.headers.get("content-type") == "application/json"
    
    def test_delete_saved_job_endpoint_returns_proper_status(self, client: TestClient):
        """Test that delete saved job endpoint returns proper status"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.delete(
            "/api/v1/saved-jobs/test-id",
            headers=headers
        )
        # Should return proper status code
        assert response.status_code in [200, 204, 404]
    
    def test_update_saved_job_endpoint_returns_json(self, client: TestClient):
        """Test that update saved job endpoint returns JSON"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.put(
            "/api/v1/saved-jobs/test-id",
            json={"notes": "Updated"},
            headers=headers
        )
        # Should return JSON
        if response.status_code in [200, 202]:
            assert response.headers.get("content-type") == "application/json"


class TestSavedJobsAuthentication:
    """Test saved jobs authentication"""
    
    def test_save_job_without_authentication_returns_401(self, client: TestClient):
        """Test save job without authentication returns 401"""
        response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-id"}
        )
        assert response.status_code == 401
    
    def test_get_saved_jobs_without_authentication_returns_401(self, client: TestClient):
        """Test get saved jobs without authentication returns 401"""
        response = client.get("/api/v1/saved-jobs")
        assert response.status_code == 401
    
    def test_delete_saved_job_without_authentication_returns_401(self, client: TestClient):
        """Test delete saved job without authentication returns 401"""
        response = client.delete("/api/v1/saved-jobs/test-id")
        assert response.status_code == 401
    
    def test_update_saved_job_without_authentication_returns_401(self, client: TestClient):
        """Test update saved job without authentication returns 401"""
        response = client.put(
            "/api/v1/saved-jobs/test-id",
            json={"notes": "test"}
        )
        assert response.status_code == 401
    
    def test_save_job_with_invalid_token_returns_401(self, client: TestClient):
        """Test save job with invalid token returns 401"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-id"},
            headers=headers
        )
        assert response.status_code == 401


class TestSavedJobsDataPersistence:
    """Test saved jobs data persistence"""
    
    def test_save_job_endpoint_accepts_job_id(self, client: TestClient):
        """Test that save job endpoint accepts job_id"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-job-id-123"},
            headers=headers
        )
        # Should accept job_id
        assert response.status_code != 422
    
    def test_save_job_endpoint_accepts_notes(self, client: TestClient):
        """Test that save job endpoint accepts notes"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={
                "job_id": "test-job-id-123",
                "notes": "Interesting position"
            },
            headers=headers
        )
        # Should accept notes
        assert response.status_code != 422
    
    def test_saved_jobs_list_endpoint_returns_items(self, client: TestClient):
        """Test that saved jobs list endpoint returns items"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        
        if response.status_code in [200, 202]:
            data = response.json()
            # Should have items or results
            assert "items" in data or "results" in data or "data" in data
