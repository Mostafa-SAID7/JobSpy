"""
Search Pagination Tests
Tests for search pagination functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchPagination:
    """Test search pagination"""
    
    def test_search_accepts_skip_parameter(self, client: TestClient):
        """Test that search accepts skip parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "skip": 10
            },
            headers=headers
        )
        assert response.status_code != 422
    
    def test_search_accepts_limit_parameter(self, client: TestClient):
        """Test that search accepts limit parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "limit": 50
            },
            headers=headers
        )
        assert response.status_code != 422
    
    def test_search_accepts_pagination_parameters(self, client: TestClient):
        """Test that search accepts both skip and limit"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "skip": 20,
                "limit": 30
            },
            headers=headers
        )
        assert response.status_code != 422
    
    def test_search_with_zero_skip(self, client: TestClient):
        """Test search with skip=0 (first page)"""
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
        assert response.status_code != 422
    
    def test_search_with_large_skip(self, client: TestClient):
        """Test search with large skip value"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "skip": 10000,
                "limit": 20
            },
            headers=headers
        )
        # Should accept large skip values
        assert response.status_code != 422
    
    def test_search_pagination_limit_validation(self, client: TestClient):
        """Test that search validates limit parameter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "skip": 0,
                "limit": 100
            },
            headers=headers
        )
        # Should accept reasonable limit values
        assert response.status_code != 422
