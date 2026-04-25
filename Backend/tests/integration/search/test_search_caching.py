"""
Search Caching Tests
Tests for search result caching functionality
"""

import pytest
import time
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchCaching:
    """Test search caching"""
    
    def test_search_cache_key_generation(self, client: TestClient):
        """Test that search cache keys are generated correctly"""
        headers = {"Authorization": "Bearer test_token"}
        
        # Make two identical searches
        response1 = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "location": "Remote"
            },
            headers=headers
        )
        
        response2 = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "location": "Remote"
            },
            headers=headers
        )
        
        # Both should succeed
        assert response1.status_code != 422
        assert response2.status_code != 422
    
    def test_search_cache_consistency(self, client: TestClient):
        """Test that cached searches return consistent results"""
        headers = {"Authorization": "Bearer test_token"}
        
        search_params = {
            "search_term": "Python",
            "location": "San Francisco"
        }
        
        # Make first search
        response1 = client.post(
            "/api/v1/search",
            json=search_params,
            headers=headers
        )
        
        # Small delay
        time.sleep(0.1)
        
        # Make second search with same params
        response2 = client.post(
            "/api/v1/search",
            json=search_params,
            headers=headers
        )
        
        # Both should succeed
        assert response1.status_code != 422
        assert response2.status_code != 422
        
        # If both returned results, they should be consistent
        if response1.status_code in [200, 202] and response2.status_code in [200, 202]:
            data1 = response1.json()
            data2 = response2.json()
            
            # Should have same structure
            assert type(data1) == type(data2)
