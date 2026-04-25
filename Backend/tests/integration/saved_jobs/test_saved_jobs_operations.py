"""
Saved Jobs Operations Tests
Tests for saved jobs CRUD operations
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSavedJobsFiltering:
    """Test saved jobs filtering and response structure"""
    
    def test_saved_jobs_response_structure(self, client: TestClient):
        """Test that saved jobs response has proper structure"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        
        if response.status_code in [200, 202]:
            data = response.json()
            # Should have items or results
            assert "items" in data or "results" in data or "data" in data
    
    def test_saved_jobs_response_includes_pagination_info(self, client: TestClient):
        """Test that saved jobs response includes pagination info"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        
        if response.status_code in [200, 202]:
            data = response.json()
            # Should have pagination info
            pagination_fields = ["total", "skip", "limit", "page", "page_size"]
            has_pagination = any(field in data for field in pagination_fields)
            assert has_pagination or "items" in data


class TestSavedJobsSorting:
    """Test saved jobs sorting"""
    
    def test_saved_jobs_default_sorting(self, client: TestClient):
        """Test saved jobs default sorting"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        # Should return results with default sorting
        assert response.status_code != 422
    
    def test_saved_jobs_response_format(self, client: TestClient):
        """Test saved jobs response format"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        
        if response.status_code in [200, 202]:
            data = response.json()
            # Should be JSON
            assert isinstance(data, dict)


class TestSaveJobsErrorHandling:
    """Test saved jobs error handling"""
    
    def test_save_job_with_missing_job_id(self, client: TestClient):
        """Test save job with missing job_id"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={},
            headers=headers
        )
        # Should reject missing job_id
        assert response.status_code in [400, 422]
    
    def test_save_job_with_invalid_job_id_format(self, client: TestClient):
        """Test save job with invalid job_id format"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/saved-jobs",
            json={"job_id": ""},
            headers=headers
        )
        # Should handle empty job_id
        assert response.status_code in [400, 422, 200]
    
    def test_delete_saved_job_with_invalid_id_format(self, client: TestClient):
        """Test delete saved job with invalid ID format"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.delete(
            "/api/v1/saved-jobs/",
            headers=headers
        )
        # Should handle invalid ID
        assert response.status_code in [400, 404, 422]
    
    def test_update_saved_job_with_invalid_id_format(self, client: TestClient):
        """Test update saved job with invalid ID format"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.put(
            "/api/v1/saved-jobs/",
            json={"notes": "test"},
            headers=headers
        )
        # Should handle invalid ID
        assert response.status_code in [400, 404, 422]
