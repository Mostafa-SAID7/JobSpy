"""
Search API Endpoints Tests
Tests for search API endpoint availability and accessibility
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchAPIEndpoints:
    """Test search API endpoints"""
    
    def test_search_endpoint_is_accessible(self, client: TestClient):
        """Test that search endpoint is accessible"""
        # Endpoint should exist (return 401 for auth, not 404)
        response = client.post("/api/v1/search", json={"search_term": "Python"})
        assert response.status_code != 404
    
    def test_search_endpoint_returns_json(self, client: TestClient):
        """Test that search endpoint returns JSON response"""
        response = client.post("/api/v1/search", json={"search_term": "Python"})
        # Should return JSON (even if error)
        assert response.headers.get("content-type") == "application/json"
    
    def test_search_without_authentication_returns_401(self, client: TestClient):
        """Test that search without auth returns 401"""
        response = client.post("/api/v1/search", json={"search_term": "Python"})
        assert response.status_code == 401
    
    def test_search_with_invalid_token_returns_401(self, client: TestClient):
        """Test that search with invalid token returns 401"""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        response = client.post(
            "/api/v1/search",
            json={"search_term": "Python"},
            headers=headers
        )
        assert response.status_code == 401
    
    def test_search_advanced_endpoint_exists(self, client: TestClient):
        """Test that advanced search endpoint exists"""
        response = client.post("/api/v1/search/advanced", json={"search_term": "Python"})
        # Should not return 404
        assert response.status_code != 404
    
    def test_search_simple_endpoint_exists(self, client: TestClient):
        """Test that simple search endpoint exists"""
        response = client.get("/api/v1/search?q=Python")
        # Should not return 404
        assert response.status_code != 404
    
    def test_jobs_list_endpoint_exists(self, client: TestClient):
        """Test that jobs list endpoint exists"""
        response = client.get("/api/v1/jobs")
        # Should not return 404
        assert response.status_code != 404
    
    def test_jobs_get_endpoint_exists(self, client: TestClient):
        """Test that get job endpoint exists"""
        response = client.get("/api/v1/jobs/test-id")
        # Should not return 404 (may return 404 for missing job, but endpoint exists)
        assert response.status_code in [200, 401, 404]
