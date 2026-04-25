"""Endurance tests for concurrent operations and error recovery"""

import pytest
import time
import statistics
import threading
from typing import List, Dict
import requests


class TestEnduranceConcurrentOps:
    """Concurrent operations and error recovery endurance tests"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client"""
        return requests.Session()
    
    @pytest.fixture
    def base_url(self):
        """Get base URL"""
        return "http://localhost:8000"
    
    def test_error_recovery_after_failures(self, api_client, base_url):
        """Test system recovery after encountering errors"""
        successful_requests = 0
        failed_requests = 0
        
        # Make requests that might fail
        for i in range(100):
            try:
                response = api_client.post(
                    f"{base_url}/api/v1/search",
                    json={
                        "search_term": "Python",
                        "location": "Remote",
                        "results_wanted": 50
                    },
                    timeout=30
                )
                
                if response.status_code in [200, 202]:
                    successful_requests += 1
                else:
                    failed_requests += 1
            except Exception:
                failed_requests += 1
        
        # System should recover and maintain reasonable success rate
        success_rate = (successful_requests / (successful_requests + failed_requests) * 100)
        assert success_rate > 80, f"Success rate {success_rate}% is below 80%"
    
    def test_concurrent_different_operations(self, api_client, base_url):
        """Test system with concurrent different operations"""
        duration_seconds = 300  # 5 minutes
        concurrent_users = 30
        
        response_times: List[float] = []
        errors = 0
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def user_worker(user_id: int):
            nonlocal errors
            operation_count = 0
            
            while time.time() < end_time:
                try:
                    operation = operation_count % 3
                    request_start = time.time()
                    
                    if operation == 0:
                        # Search operation
                        response = api_client.post(
                            f"{base_url}/api/v1/search",
                            json={
                                "search_term": "Python",
                                "location": "Remote",
                                "results_wanted": 50
                            },
                            timeout=30
                        )
                    elif operation == 1:
                        # Get saved jobs
                        response = api_client.get(
                            f"{base_url}/api/v1/saved-jobs?page=1&page_size=20",
                            timeout=30
                        )
                    else:
                        # Get alerts
                        response = api_client.get(
                            f"{base_url}/api/v1/alerts",
                            timeout=30
                        )
                    
                    response_time = (time.time() - request_start) * 1000
                    
                    if response.status_code in [200, 202]:
                        response_times.append(response_time)
                    else:
                        errors += 1
                    
                    operation_count += 1
                except Exception:
                    errors += 1
        
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
    
    def test_throughput_consistency(self, api_client, base_url):
        """Test that throughput remains consistent over time"""
        duration_seconds = 600  # 10 minutes
        concurrent_users = 20
        
        # Track requests per minute
        minute_counts: Dict[int, int] = {}
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def user_worker(user_id: int):
            while time.time() < end_time:
                try:
                    current_minute = int((time.time() - start_time) / 60)
                    
                    response = api_client.get(
                        f"{base_url}/api/v1/jobs?page=1&page_size=20",
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        minute_counts[current_minute] = minute_counts.get(current_minute, 0) + 1
                except Exception:
                    pass
                
                time.sleep(0.5)
        
        threads = []
        for i in range(concurrent_users):
            thread = threading.Thread(target=user_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        # Check consistency
        if len(minute_counts) > 1:
            counts = list(minute_counts.values())
            avg_count = statistics.mean(counts)
            std_dev = statistics.stdev(counts) if len(counts) > 1 else 0
            
            # Standard deviation should be less than 20% of average
            cv = (std_dev / avg_count * 100) if avg_count > 0 else 0
            assert cv < 20, f"Coefficient of variation {cv}% exceeds 20% threshold"
