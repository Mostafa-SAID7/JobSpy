"""
Endurance tests for sustained load scenarios
Tests system stability under prolonged load conditions
"""

import pytest
import time
import statistics
import threading
from typing import List
import requests


class TestEnduranceSustainedLoad:
    """Sustained load endurance tests"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client"""
        return requests.Session()
    
    @pytest.fixture
    def base_url(self):
        """Get base URL"""
        return "http://localhost:8000"
    
    def test_sustained_load_1_hour(self, api_client, base_url):
        """
        Test system under sustained load for 1 hour
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
        """
        duration_seconds = 3600  # 1 hour
        concurrent_users = 50
        requests_per_second = 10
        
        response_times: List[float] = []
        errors = 0
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # Simulate concurrent users
        def user_worker(user_id: int):
            nonlocal errors
            while time.time() < end_time:
                try:
                    request_start = time.time()
                    response = api_client.get(
                        f"{base_url}/api/v1/jobs?page=1&page_size=20",
                        timeout=30
                    )
                    response_time = (time.time() - request_start) * 1000
                    
                    if response.status_code == 200:
                        response_times.append(response_time)
                    else:
                        errors += 1
                except Exception:
                    errors += 1
                
                time.sleep(1 / requests_per_second)
        
        # Start worker threads
        threads = []
        for i in range(concurrent_users):
            thread = threading.Thread(target=user_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Validate results
        total_requests = len(response_times) + errors
        error_rate = (errors / total_requests * 100) if total_requests > 0 else 0
        
        assert error_rate < 5, f"Error rate {error_rate}% exceeds 5% threshold"
        assert len(response_times) > 0, "No successful requests"
        
        # Check response times
        avg_response_time = statistics.mean(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        
        assert avg_response_time < 500, f"Average response time {avg_response_time}ms exceeds 500ms"
        assert p95_response_time < 1000, f"P95 response time {p95_response_time}ms exceeds 1000ms"
    
    def test_sustained_load_30_minutes_high_concurrency(self, api_client, base_url):
        """
        Test system under high concurrency for 30 minutes
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
        """
        duration_seconds = 1800  # 30 minutes
        concurrent_users = 100
        requests_per_second = 20
        
        response_times: List[float] = []
        errors = 0
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def user_worker(user_id: int):
            nonlocal errors
            while time.time() < end_time:
                try:
                    request_start = time.time()
                    response = api_client.post(
                        f"{base_url}/api/v1/search",
                        json={
                            "search_term": "Python",
                            "location": "Remote",
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
                
                time.sleep(1 / requests_per_second)
        
        threads = []
        for i in range(concurrent_users):
            thread = threading.Thread(target=user_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        total_requests = len(response_times) + errors
        error_rate = (errors / total_requests * 100) if total_requests > 0 else 0
        
        assert error_rate < 10, f"Error rate {error_rate}% exceeds 10% threshold"
        assert len(response_times) > 0, "No successful requests"
        
        avg_response_time = statistics.mean(response_times)
        assert avg_response_time < 1000, f"Average response time {avg_response_time}ms exceeds 1000ms"
