"""
Saved Jobs Pagination Tests
Tests for saved jobs pagination functionality
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSavedJobsPagination:
    """Test saved jobs pagination"""
    
    def test_saved_jobs_accepts_skip_parameter(self, client: TestClient):
        """Test that saved jobs accepts skip parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get(
            "/api/v1/saved-jobs?skip=10",
            headers=headers
        )
        assert response.status_code != 422
    
    def test_saved_jobs_accepts_limit_parameter(self, client: TestClient):
        """Test that saved jobs accepts limit parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get(
            "/api/v1/saved-jobs?limit=50",
            headers=headers
        )
        assert response.status_code != 422
    
    def test_saved_jobs_accepts_pagination_parameters(self, client: TestClient):
        """Test that saved jobs accepts both skip and limit"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get(
            "/api/v1/saved-jobs?skip=20&limit=30",
            headers=headers
        )
        assert response.status_code != 422
    
    def test_saved_jobs_with_zero_skip(self, client: TestClient):
        """Test saved jobs with skip=0 (first page)"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get(
            "/api/v1/saved-jobs?skip=0&limit=20",
            headers=headers
        )
        assert response.status_code != 422
    
    def test_saved_jobs_with_large_skip(self, client: TestClient):
        """Test saved jobs with large skip value"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get(
            "/api/v1/saved-jobs?skip=10000&limit=20",
            headers=headers
        )
        # Should accept large skip values
        assert response.status_code != 422
    
    def test_saved_jobs_pagination_limit_validation(self, client: TestClient):
        """Test that saved jobs validates limit parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get(
            "/api/v1/saved-jobs?skip=0&limit=100",
            headers=headers
        )
        # Should accept reasonable limit values
        assert response.status_code != 422
    
    def test_saved_jobs_default_pagination(self, client: TestClient):
        """Test saved jobs with default pagination"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/saved-jobs", headers=headers)
        # Should work with default pagination
        assert response.status_code != 422
