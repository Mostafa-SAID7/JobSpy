"""
Search Filtering Tests
Tests for search filtering functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchFiltering:
    """Test search filtering capabilities"""
    
    def test_search_accepts_location_filter(self, client: TestClient):
        """Test that search accepts location filter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "location": "San Francisco"
            },
            headers=headers
        )
        assert response.status_code != 422
    
    def test_search_accepts_job_type_filter(self, client: TestClient):
        """Test that search accepts job_type filter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "job_type": "fulltime"
            },
            headers=headers
        )
        assert response.status_code != 422
    
    def test_search_accepts_salary_filters(self, client: TestClient):
        """Test that search accepts salary range filters"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "salary_min": 100000,
                "salary_max": 150000
            },
            headers=headers
        )
        assert response.status_code != 422
    
    def test_search_accepts_remote_filter(self, client: TestClient):
        """Test that search accepts remote filter"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "is_remote": True
            },
            headers=headers
        )
        assert response.status_code != 422
    
    def test_search_accepts_multiple_filters(self, client: TestClient):
        """Test that search accepts multiple filters simultaneously"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "location": "San Francisco",
                "job_type": "fulltime",
                "salary_min": 100000,
                "salary_max": 150000,
                "is_remote": False
            },
            headers=headers
        )
        assert response.status_code != 422
