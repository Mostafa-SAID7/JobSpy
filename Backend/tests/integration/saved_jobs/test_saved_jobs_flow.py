"""
Saved Jobs Complete Flow Tests
Tests for complete saved jobs workflow
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestCompleteSaveJobsFlow:
    """Test complete save jobs flow"""
    
    def test_save_job_flow_endpoints_exist(self, client: TestClient):
        """Test that all save job flow endpoints exist"""
        headers = {"Authorization": "Bearer test_token"}
        
        # Test save endpoint
        response1 = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-id"},
            headers=headers
        )
        assert response1.status_code != 404
        
        # Test get endpoint
        response2 = client.get("/api/v1/saved-jobs", headers=headers)
        assert response2.status_code != 404
        
        # Test delete endpoint
        response3 = client.delete("/api/v1/saved-jobs/test-id", headers=headers)
        assert response3.status_code != 404
    
    def test_save_job_flow_with_pagination(self, client: TestClient):
        """Test save job flow with pagination"""
        headers = {"Authorization": "Bearer test_token"}
        
        # Get saved jobs with pagination
        response = client.get(
            "/api/v1/saved-jobs?skip=0&limit=20",
            headers=headers
        )
        
        # Should accept pagination
        assert response.status_code != 422
    
    def test_save_job_flow_with_multiple_operations(self, client: TestClient):
        """Test save job flow with multiple operations"""
        headers = {"Authorization": "Bearer test_token"}
        
        # Save a job
        save_response = client.post(
            "/api/v1/saved-jobs",
            json={
                "job_id": "test-job-1",
                "notes": "First job"
            },
            headers=headers
        )
        
        # Get saved jobs
        get_response = client.get("/api/v1/saved-jobs", headers=headers)
        
        # Both should succeed
        assert save_response.status_code != 422
        assert get_response.status_code != 422
    
    def test_save_job_flow_response_consistency(self, client: TestClient):
        """Test save job flow response consistency"""
        headers = {"Authorization": "Bearer test_token"}
        
        # Save job
        save_response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": "test-job-consistency"},
            headers=headers
        )
        
        # Get saved jobs
        get_response = client.get("/api/v1/saved-jobs", headers=headers)
        
        # Both should return JSON
        if save_response.status_code in [200, 202]:
            assert save_response.headers.get("content-type") == "application/json"
        
        if get_response.status_code in [200, 202]:
            assert get_response.headers.get("content-type") == "application/json"


class TestSavedJobsAPICompleteness:
    """Test saved jobs API completeness"""
    
    def test_save_job_endpoint_is_accessible(self, client: TestClient):
        """Test that save job endpoint is accessible"""
        response = client.post("/api/v1/saved-jobs", json={"job_id": "test"})
        # Should not return 404
        assert response.status_code != 404
    
    def test_get_saved_jobs_endpoint_is_accessible(self, client: TestClient):
        """Test that get saved jobs endpoint is accessible"""
        response = client.get("/api/v1/saved-jobs")
        # Should not return 404
        assert response.status_code != 404
    
    def test_delete_saved_job_endpoint_is_accessible(self, client: TestClient):
        """Test that delete saved job endpoint is accessible"""
        response = client.delete("/api/v1/saved-jobs/test-id")
        # Should not return 404
        assert response.status_code != 404
    
    def test_update_saved_job_endpoint_is_accessible(self, client: TestClient):
        """Test that update saved job endpoint is accessible"""
        response = client.put(
            "/api/v1/saved-jobs/test-id",
            json={"notes": "test"}
        )
        # Should not return 404
        assert response.status_code != 404
    
    def test_unsave_job_endpoint_is_accessible(self, client: TestClient):
        """Test that unsave job endpoint is accessible"""
        response = client.delete("/api/v1/saved-jobs/by-job/test-job-id")
        # Should not return 404
        assert response.status_code != 404
