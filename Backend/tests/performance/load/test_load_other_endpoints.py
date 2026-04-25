"""
Load tests for other endpoint performance
Tests saved jobs and alerts endpoints under load
"""

import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import requests


class PerformanceMetrics:
    """Collect and analyze performance metrics"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.status_codes: Dict[int, int] = {}
        self.errors: List[str] = []
        self.start_time = None
        self.end_time = None
    
    def add_response(self, response_time_ms: float, status_code: int, error: str = None):
        """Add a response metric"""
        self.response_times.append(response_time_ms)
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
        if error:
            self.errors.append(error)
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        if not self.response_times:
            return {}
        
        sorted_times = sorted(self.response_times)
        return {
            "total_requests": len(self.response_times),
            "min_ms": min(sorted_times),
            "max_ms": max(sorted_times),
            "avg_ms": statistics.mean(sorted_times),
            "median_ms": statistics.median(sorted_times),
            "p95_ms": sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0,
            "p99_ms": sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0,
            "status_codes": self.status_codes,
            "error_count": len(self.errors),
            "success_rate": (self.status_codes.get(200, 0) + self.status_codes.get(201, 0)) / len(self.response_times) * 100 if self.response_times else 0
        }


@pytest.fixture
def base_url():
    """Base URL for API"""
    return "http://localhost:8000"


@pytest.fixture
def test_user_credentials():
    """Test user credentials"""
    return {
        "email": f"loadtest_{int(time.time())}@test.com",
        "password": "TestPassword123!"
    }


class TestLoadOtherEndpoints:
    """Load performance tests for other endpoints"""
    
    def _make_request(self, method: str, url: str, headers: Dict = None, json: Dict = None, timeout: int = 30) -> tuple:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=json, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, response.status_code, None
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, 0, str(e)
    
    def _setup_user(self, base_url: str, email: str, password: str) -> str:
        """Setup user and return auth token"""
        # Register
        register_url = f"{base_url}/api/v1/auth/register"
        requests.post(register_url, json={
            "email": email,
            "password": password,
            "full_name": f"Test User {int(time.time())}"
        })
        
        # Login
        login_url = f"{base_url}/api/v1/auth/login"
        response = requests.post(login_url, json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    @pytest.mark.performance
    def test_saved_jobs_endpoint_load(self, base_url, test_user_credentials):
        """Test saved jobs endpoint under load"""
        metrics = PerformanceMetrics()
        num_users = 30
        
        def user_task(user_id):
            email = f"loadtest_{user_id}_{int(time.time())}@test.com"
            token = self._setup_user(base_url, email, test_user_credentials["password"])
            
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            
            for _ in range(5):
                url = f"{base_url}/api/v1/saved-jobs"
                response_time_ms, status_code, error = self._make_request("GET", url, headers=headers)
                metrics.add_response(response_time_ms, status_code, error)
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_task, i) for i in range(num_users)]
            for future in as_completed(futures):
                future.result()
        
        stats = metrics.get_stats()
        
        assert stats["avg_ms"] < 500, f"Saved jobs endpoint avg response time {stats['avg_ms']:.2f}ms exceeds 500ms"
        assert stats["success_rate"] > 90, f"Success rate {stats['success_rate']:.2f}% below 90%"
        
        print(f"\n✅ Saved Jobs Endpoint Test Results:")
        print(f"  Avg Response Time: {stats['avg_ms']:.2f}ms")
        print(f"  Success Rate: {stats['success_rate']:.2f}%")
    
    @pytest.mark.performance
    def test_alerts_endpoint_load(self, base_url, test_user_credentials):
        """Test alerts endpoint under load"""
        metrics = PerformanceMetrics()
        num_users = 30
        
        def user_task(user_id):
            email = f"loadtest_{user_id}_{int(time.time())}@test.com"
            token = self._setup_user(base_url, email, test_user_credentials["password"])
            
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            
            for _ in range(5):
                url = f"{base_url}/api/v1/alerts"
                response_time_ms, status_code, error = self._make_request("GET", url, headers=headers)
                metrics.add_response(response_time_ms, status_code, error)
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_task, i) for i in range(num_users)]
            for future in as_completed(futures):
                future.result()
        
        stats = metrics.get_stats()
        
        assert stats["avg_ms"] < 500, f"Alerts endpoint avg response time {stats['avg_ms']:.2f}ms exceeds 500ms"
        assert stats["success_rate"] > 90, f"Success rate {stats['success_rate']:.2f}% below 90%"
        
        print(f"\n✅ Alerts Endpoint Test Results:")
        print(f"  Avg Response Time: {stats['avg_ms']:.2f}ms")
        print(f"  Success Rate: {stats['success_rate']:.2f}%")
