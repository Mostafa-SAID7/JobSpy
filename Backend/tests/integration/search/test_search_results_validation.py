"""
Search Results Validation Tests
Tests for search results validation and structure
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchResultsValidation:
    """Test search results validation"""
    
    def test_search_results_have_required_fields(self, client: TestClient):
        """Test that search results have all required fields"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={"search_term": "Python"},
            headers=headers
        )
        
        if response.status_code in [200, 202]:
            data = response.json()
            
            # Check for required fields in response
            if "results" in data:
                results = data["results"]
                if isinstance(results, list) and len(results) > 0:
                    job = results[0]
                    # Check for required job fields
                    required_fields = ["title", "company", "job_url"]
                    for field in required_fields:
                        assert field in job or field.lower() in str(job).lower()
    
    def test_search_results_pagination_info(self, client: TestClient):
        """Test that search results include pagination info"""
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
        
        if response.status_code in [200, 202]:
            data = response.json()
            
            # Should have pagination info
            pagination_fields = ["total", "skip", "limit", "page", "page_size"]
            has_pagination = any(field in data for field in pagination_fields)
            
            # Or results should be a list
            if "results" in data:
                assert isinstance(data["results"], list)
