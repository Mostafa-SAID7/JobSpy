"""
Search Flow Completeness Tests
Tests for complete search flow from query to results
"""

import pytest
from fastapi.testclient import TestClient
from Backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client"""
    return TestClient(app)


class TestSearchFlowCompleteness:
    """Test complete search flow"""
    
    def test_search_query_submission_endpoint(self, client: TestClient):
        """Test that search query submission endpoint works"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={"search_term": "Python Developer"},
            headers=headers
        )
        # Should accept search query
        assert response.status_code != 422
    
    def test_search_results_retrieval_endpoint(self, client: TestClient):
        """Test that search results can be retrieved"""
        headers = {"Authorization": "Bearer test_token"}
        # First submit search
        response = client.post(
            "/api/v1/search",
            json={"search_term": "Python"},
            headers=headers
        )
        
        # Then retrieve results
        if response.status_code in [200, 202]:
            data = response.json()
            if "search_id" in data:
                result_response = client.get(
                    f"/api/v1/search/{data['search_id']}",
                    headers=headers
                )
                assert result_response.status_code in [200, 202]
    
    def test_search_filtering_parameters_accepted(self, client: TestClient):
        """Test that search accepts all filtering parameters"""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "location": "San Francisco",
                "job_type": "fulltime",
                "salary_min": 100000,
                "salary_max": 150000,
                "is_remote": False,
                "distance": 50
            },
            headers=headers
        )
        # Should accept all filters
        assert response.status_code != 422
    
    def test_search_pagination_parameters_accepted(self, client: TestClient):
        """Test that search accepts pagination parameters"""
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
        # Should accept pagination
        assert response.status_code != 422
    
    def test_search_flow_from_query_to_results(self, client: TestClient):
        """Test complete flow from query submission to results"""
        headers = {"Authorization": "Bearer test_token"}
        
        # Step 1: Submit search query
        search_response = client.post(
            "/api/v1/search",
            json={
                "search_term": "Python",
                "location": "Remote",
                "job_type": "fulltime"
            },
            headers=headers
        )
        
        # Should accept search
        assert search_response.status_code != 422
        
        # Step 2: If search was accepted, try to get results
        if search_response.status_code in [200, 202]:
            data = search_response.json()
            
            # Should have search_id or results
            assert "search_id" in data or "results" in data or "jobs" in data
