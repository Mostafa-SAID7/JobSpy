"""
Search Error Handling Tests
Tests for search error handling and validation
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchErrorHandling:
    """Test search error handling"""
    
    def test_search_handles_missing_query(self, client: TestClient):
        """Test that search handles missing query gracefully"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={},
            headers=headers
        )
        # Should return validation error, not 500
        assert response.status_code in [400, 422]
    
    def test_search_handles_invalid_skip(self, client: TestClient):
        """Test that search handles invalid skip parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "skip": -1
            },
            headers=headers
        )
        # Should handle negative skip
        assert response.status_code in [400, 422, 200]
    
    def test_search_handles_invalid_limit(self, client: TestClient):
        """Test that search handles invalid limit parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "limit": -1
            },
            headers=headers
        )
        # Should handle negative limit
        assert response.status_code in [400, 422, 200]
    
    def test_search_handles_invalid_salary_min(self, client: TestClient):
        """Test that search handles invalid salary_min parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "salary_min": -1000
            },
            headers=headers
        )
        # Should handle negative salary
        assert response.status_code in [400, 422, 200]
