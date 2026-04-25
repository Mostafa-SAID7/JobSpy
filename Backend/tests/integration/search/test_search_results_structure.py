"""
Search Results Structure Tests
Tests for search response format and structure
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchResultsStructure:
    """Test search results structure and format"""
    
    def test_search_response_format_without_auth(self, client: TestClient):
        """Test that search endpoint returns proper error format without auth"""
        response = client.post("/api/v1/search", json={"search_term": "Python"})
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data or "error" in data
    
    def test_search_endpoint_accepts_query_parameter(self, client: TestClient):
        """Test that search endpoint accepts search_term parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={"search_term": "Python Developer"},
            headers=headers
        )
        # Should not return 422 (validation error)
        assert response.status_code != 422
    
    def test_search_endpoint_accepts_pagination_parameters(self, client: TestClient):
        """Test that search endpoint accepts pagination parameters"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "skip": 0,
                "limit": 20
            },
            headers=headers
        )
        # Should not return 422 (validation error)
        assert response.status_code != 422
    
    def test_search_endpoint_accepts_filter_parameters(self, client: TestClient):
        """Test that search endpoint accepts filter parameters"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "location": "San Francisco",
                "job_type": "fulltime",
                "is_remote": False
            },
            headers=headers
        )
        # Should not return 422 (validation error)
        assert response.status_code != 422
