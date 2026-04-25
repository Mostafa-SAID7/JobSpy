"""Endurance tests for memory and cache stability"""

import pytest
import time
import statistics
from typing import List
import requests


class TestEnduranceMemoryCache:
    """Memory and cache stability endurance tests"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client"""
        return requests.Session()
    
    @pytest.fixture
    def base_url(self):
        """Get base URL"""
        return "http://localhost:8000"
    
    def test_memory_stability_repeated_searches(self, api_client, base_url):
        """Test memory stability with repeated search operations"""
        num_iterations = 1000
        response_times: List[float] = []
        errors = 0
        
        for i in range(num_iterations):
            try:
                request_start = time.time()
                response = api_client.post(
                    f"{base_url}/api/v1/search",
                    json={
                        "search_term": "Python",
                        "location": "San Francisco",
                        "results_wanted": 50
                    },
                    timeout=30
                )
                response_time = (time.time() - request_start) * 1000
                
                if response.status_code in [200, 202]:
                    response_times.append(response_time)
                else:
                    errors += 1
            except Exception:
                errors += 1
        
        error_rate = (errors / num_iterations * 100)
        assert error_rate < 5, f"Error rate {error_rate}% exceeds 5% threshold"
        
        # Check for response time degradation (sign of memory leak)
        first_100 = response_times[:100]
        last_100 = response_times[-100:]
        
        first_avg = statistics.mean(first_100)
        last_avg = statistics.mean(last_100)
        
        degradation = ((last_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        # Allow up to 20% degradation
        assert degradation < 20, f"Response time degradation {degradation}% exceeds 20% threshold"
    
    def test_cache_effectiveness_repeated_queries(self, api_client, base_url):
        """Test cache effectiveness with repeated identical queries"""
        search_params = {
            "search_term": "Python",
            "location": "Remote",
            "results_wanted": 50
        }
        
        response_times: List[float] = []
        
        # First request (cache miss)
        request_start = time.time()
        response1 = api_client.post(
            f"{base_url}/api/v1/search",
            json=search_params,
            timeout=30
        )
        first_response_time = (time.time() - request_start) * 1000
        
        assert response1.status_code in [200, 202], "First request failed"
        
        # Repeated requests (should hit cache)
        for i in range(10):
            request_start = time.time()
            response = api_client.post(
                f"{base_url}/api/v1/search",
                json=search_params,
                timeout=30
            )
            response_time = (time.time() - request_start) * 1000
            response_times.append(response_time)
            
            assert response.status_code in [200, 202], f"Request {i} failed"
        
        # Cached requests should be faster
        cached_avg = statistics.mean(response_times)
        
        # Cached requests should be at least 50% faster
        speedup = (first_response_time - cached_avg) / first_response_time * 100
        assert speedup > 50, f"Cache speedup {speedup}% is less than 50%"
