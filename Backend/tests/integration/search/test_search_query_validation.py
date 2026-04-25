"""
Search Query Validation Tests
Tests for search endpoint query parameter validation
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchQueryValidation:
    """Test search query validation"""
    
    def test_search_requires_authentication(self, client: TestClient):
        """Test that search endpoint requires authentication"""
        response = client.post("/api/v1/search", json={"search_term": "Python"})
        assert response.status_code == 401
    
    def test_search_with_invalid_token(self, client: TestClient):
        """Test search with invalid JWT token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post(
            "/api/v1/search",
            json={"search_term": "Python"},
            headers=headers
        )
        assert response.status_code == 401
    
    def test_search_endpoint_exists(self, client: TestClient):
        """Test that search endpoint exists"""
        # Without auth, should return 401 not 404
        response = client.post("/api/v1/search", json={"search_term": "Python"})
        assert response.status_code in [401, 422]  # 401 auth or 422 validation
    
    def test_search_with_empty_query_validation(self, client: TestClient):
        """Test search with empty query string"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={"search_term": ""},
            headers=headers
        )
        # Should reject empty search term
        assert response.status_code in [400, 422]
    
    def test_search_with_missing_query_parameter(self, client: TestClient):
        """Test search with missing required query parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={},
            headers=headers
        )
        # Should reject missing search_term
        assert response.status_code in [400, 422]
