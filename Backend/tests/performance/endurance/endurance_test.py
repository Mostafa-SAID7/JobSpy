"""
Endurance Testing for JobSpy Application
Tests system stability and performance over extended periods (hours)
Identifies memory leaks, resource exhaustion, and degradation patterns
"""

import time
import json
import random
import statistics
import threading
import psutil
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class SystemMetrics:
    """System resource metrics at a point in time"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    open_files: int
    thread_count: int


@dataclass
class EnduranceTestResult:
    """Results from an endurance test scenario"""
    scenario_name: str
    duration_minutes: int
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    throughput_rps: float
    error_rate: float
    
    # Resource metrics
    initial_memory_mb: float
    peak_memory_mb: float
    final_memory_mb: float
    memory_growth_mb: float
    memory_growth_percent: float
    
    initial_cpu_percent: float
    avg_cpu_percent: float
    peak_cpu_percent: float
    
    # Degradation analysis
    first_hour_avg_response_ms: float
    last_hour_avg_response_ms: float
    response_time_degradation_percent: float
    
    # Stability metrics
    error_rate_trend: str  # "stable", "increasing", "decreasing"
    memory_trend: str  # "stable", "increasing", "decreasing"
    
    timestamp: str
    system_metrics: List[SystemMetrics] = field(default_factory=list)


class EnduranceTestClient:
    """HTTP client for endurance testing"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session()
        self.auth_token = None
    
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def login(self, email: str, password: str) -> bool:
        """Login and get auth token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=self.timeout
            )
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                return True
            return False
        except Exception:
            return False
    
    def search_jobs(self) -> Tuple[bool, float]:
        """Perform a job search and return success and response time"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        search_params = {
            "search_term": random.choice(["Python", "JavaScript", "Java", "DevOps", "Data Science"]),
            "location": random.choice(["San Francisco", "New York", "Remote", "London", "Toronto"]),
            "job_type": random.choice(["fulltime", "parttime", "contract"]),
            "results_wanted": 50,
            "hours_old": 24,
            "site_names": ["linkedin", "indeed"]
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/v1/search",
                json=search_params,
                headers=headers,
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return response.status_code == 200, response_time_ms
        except Exception:
            return False, 0
    
    def get_saved_jobs(self) -> Tuple[bool, float]:
        """Get saved jobs and return success and response time"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/api/v1/saved-jobs?page=1&page_size=20",
                headers=headers,
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return response.status_code == 200, response_time_ms
        except Exception:
            return False, 0
    
    def get_alerts(self) -> Tuple[bool, float]:
        """Get alerts and return success and response time"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/api/v1/alerts",
                headers=headers,
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return response.status_code == 200, response_time_ms
        except Exception:
            return False, 0


class SystemMonitor:
    """Monitor system resources during test"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.metrics: List[SystemMetrics] = []
    
    def capture_metrics(self):
        """Capture current system metrics"""
        try:
            metric = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=self.process.cpu_percent(interval=0.1),
                memory_percent=self.process.memory_percent(),
                memory_mb=self.process.memory_info().rss / 1024 / 1024,
                open_files=len(self.process.open_files()),
                thread_count=self.process.num_threads()
            )
            self.metrics.append(metric)
            return metric
        except Exception:
            return None
    
    def get_summary(self) -> Dict:
        """Get summary of metrics"""
        if not self.metrics:
            return {}
        
        memory_values = [m.memory_mb for m in self.metrics]
        cpu_values = [m.cpu_percent for m in self.metrics]
        
        return {
            "initial_memory_mb": memory_values[0],
            "peak_memory_mb": max(memory_values),
            "final_memory_mb": memory_values[-1],
            "memory_growth_mb": memory_values[-1] - memory_values[0],
            "initial_cpu_percent": cpu_values[0],
            "avg_cpu_percent": statistics.mean(cpu_values),
            "peak_cpu_percent": max(cpu_values),
        }


class EnduranceTestRunner:
    """Run endurance tests"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[EnduranceTestResult] = []
    
    def run_sustained_load_test(
        self,
        duration_minutes: int = 60,
        concurrent_users: int = 50,
        requests_per_user_per_minute: int = 10
    ) -> EnduranceTestResult:
        """
        Run sustained load test for extended period
        Tests system stability under constant load
        """
        print(f"\n{'='*80}")
        print(f"Starting Endurance Test: Sustained Load")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Requests/User/Minute: {requests_per_user_per_minute}")
        print(f"{'='*80}\n")
        
        scenario_name = f"Sustained Load - {concurrent_users} users for {duration_minutes}m"
        monitor = SystemMonitor()
        
        response_times: List[float] = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Initialize clients for each user
        clients = []
        for i in range(concurrent_users):
            client = EnduranceTestClient(self.base_url)
            # Login with test user
            email = f"test_user_{i}@example.com"
            password = "test_password_123"
            client.login(email, password)
            clients.append(client)
        
        # Track metrics by hour
        hourly_response_times: Dict[int, List[float]] = {}
        hourly_errors: Dict[int, int] = {}
        
        request_count = 0
        current_hour = 0
        
        # Run test for specified duration
        while time.time() < end_time:
            current_time = time.time()
            elapsed_minutes = (current_time - start_time) / 60
            current_hour = int(elapsed_minutes // 60)
            
            if current_hour not in hourly_response_times:
                hourly_response_times[current_hour] = []
                hourly_errors[current_hour] = 0
            
            # Distribute requests across users
            for user_idx in range(concurrent_users):
                client = clients[user_idx]
                
                # Randomly choose operation
                operation = random.choice(["search", "saved_jobs", "alerts"])
                
                try:
                    if operation == "search":
                        success, response_time = client.search_jobs()
                    elif operation == "saved_jobs":
                        success, response_time = client.get_saved_jobs()
                    else:
                        success, response_time = client.get_alerts()
                    
                    if success:
                        response_times.append(response_time)
                        hourly_response_times[current_hour].append(response_time)
                        successful_requests += 1
                    else:
                        failed_requests += 1
                        hourly_errors[current_hour] += 1
                    
                    request_count += 1
                    
                except Exception:
                    failed_requests += 1
                    hourly_errors[current_hour] += 1
            
            # Capture system metrics every 30 seconds
            if request_count % 100 == 0:
                monitor.capture_metrics()
                elapsed = time.time() - start_time
                print(f"Progress: {elapsed/60:.1f}m | Requests: {request_count} | "
                      f"Success: {successful_requests} | Failed: {failed_requests}")
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.1)
        
        # Calculate results
        total_requests = successful_requests + failed_requests
        duration_seconds = time.time() - start_time
        throughput_rps = total_requests / duration_seconds
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate response time statistics
        if response_times:
            response_times.sort()
            avg_response_time = statistics.mean(response_times)
            p95_response_time = response_times[int(len(response_times) * 0.95)]
            p99_response_time = response_times[int(len(response_times) * 0.99)]
        else:
            avg_response_time = p95_response_time = p99_response_time = 0
        
        # Analyze degradation
        first_hour_times = hourly_response_times.get(0, [])
        last_hour_times = hourly_response_times.get(current_hour, [])
        
        first_hour_avg = statistics.mean(first_hour_times) if first_hour_times else 0
        last_hour_avg = statistics.mean(last_hour_times) if last_hour_times else 0
        
        degradation_percent = 0
        if first_hour_avg > 0:
            degradation_percent = ((last_hour_avg - first_hour_avg) / first_hour_avg) * 100
        
        # Analyze trends
        error_rates_by_hour = [
            (hourly_errors.get(h, 0) / max(len(hourly_response_times.get(h, [])), 1)) * 100
            for h in sorted(hourly_response_times.keys())
        ]
        
        error_trend = self._analyze_trend(error_rates_by_hour)
        
        # Get system metrics summary
        system_summary = monitor.get_summary()
        memory_trend = self._analyze_memory_trend(monitor.metrics)
        
        result = EnduranceTestResult(
            scenario_name=scenario_name,
            duration_minutes=duration_minutes,
            concurrent_users=concurrent_users,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            throughput_rps=throughput_rps,
            error_rate=error_rate,
            initial_memory_mb=system_summary.get("initial_memory_mb", 0),
            peak_memory_mb=system_summary.get("peak_memory_mb", 0),
            final_memory_mb=system_summary.get("final_memory_mb", 0),
            memory_growth_mb=system_summary.get("memory_growth_mb", 0),
            memory_growth_percent=(
                (system_summary.get("memory_growth_mb", 0) / 
                 max(system_summary.get("initial_memory_mb", 1), 1)) * 100
            ),
            initial_cpu_percent=system_summary.get("initial_cpu_percent", 0),
            avg_cpu_percent=system_summary.get("avg_cpu_percent", 0),
            peak_cpu_percent=system_summary.get("peak_cpu_percent", 0),
            first_hour_avg_response_ms=first_hour_avg,
            last_hour_avg_response_ms=last_hour_avg,
            response_time_degradation_percent=degradation_percent,
            error_rate_trend=error_trend,
            memory_trend=memory_trend,
            timestamp=datetime.now().isoformat(),
            system_metrics=monitor.metrics
        )
        
        self.results.append(result)
        self._print_result(result)
        return result
    
    def run_memory_leak_test(
        self,
        duration_minutes: int = 30,
        concurrent_users: int = 20
    ) -> EnduranceTestResult:
        """
        Run test specifically designed to detect memory leaks
        Performs repeated operations and monitors memory growth
        """
        print(f"\n{'='*80}")
        print(f"Starting Endurance Test: Memory Leak Detection")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"{'='*80}\n")
        
        scenario_name = f"Memory Leak Test - {concurrent_users} users for {duration_minutes}m"
        monitor = SystemMonitor()
        
        response_times: List[float] = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Initialize clients
        clients = []
        for i in range(concurrent_users):
            client = EnduranceTestClient(self.base_url)
            email = f"test_user_{i}@example.com"
            password = "test_password_123"
            client.login(email, password)
            clients.append(client)
        
        request_count = 0
        
        # Run test - focus on search operations which may leak memory
        while time.time() < end_time:
            for user_idx in range(concurrent_users):
                client = clients[user_idx]
                
                try:
                    # Perform search operation multiple times
                    for _ in range(5):
                        success, response_time = client.search_jobs()
                        if success:
                            response_times.append(response_time)
                            successful_requests += 1
                        else:
                            failed_requests += 1
                        request_count += 1
                    
                except Exception:
                    failed_requests += 1
            
            # Capture metrics every 30 seconds
            if request_count % 50 == 0:
                monitor.capture_metrics()
                elapsed = time.time() - start_time
                print(f"Progress: {elapsed/60:.1f}m | Requests: {request_count} | "
                      f"Memory: {monitor.metrics[-1].memory_mb:.1f}MB")
            
            time.sleep(0.1)
        
        # Calculate results
        total_requests = successful_requests + failed_requests
        duration_seconds = time.time() - start_time
        throughput_rps = total_requests / duration_seconds
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        if response_times:
            response_times.sort()
            avg_response_time = statistics.mean(response_times)
            p95_response_time = response_times[int(len(response_times) * 0.95)]
            p99_response_time = response_times[int(len(response_times) * 0.99)]
        else:
            avg_response_time = p95_response_time = p99_response_time = 0
        
        system_summary = monitor.get_summary()
        memory_trend = self._analyze_memory_trend(monitor.metrics)
        
        result = EnduranceTestResult(
            scenario_name=scenario_name,
            duration_minutes=duration_minutes,
            concurrent_users=concurrent_users,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            throughput_rps=throughput_rps,
            error_rate=error_rate,
            initial_memory_mb=system_summary.get("initial_memory_mb", 0),
            peak_memory_mb=system_summary.get("peak_memory_mb", 0),
            final_memory_mb=system_summary.get("final_memory_mb", 0),
            memory_growth_mb=system_summary.get("memory_growth_mb", 0),
            memory_growth_percent=(
                (system_summary.get("memory_growth_mb", 0) / 
                 max(system_summary.get("initial_memory_mb", 1), 1)) * 100
            ),
            initial_cpu_percent=system_summary.get("initial_cpu_percent", 0),
            avg_cpu_percent=system_summary.get("avg_cpu_percent", 0),
            peak_cpu_percent=system_summary.get("peak_cpu_percent", 0),
            first_hour_avg_response_ms=avg_response_time,
            last_hour_avg_response_ms=avg_response_time,
            response_time_degradation_percent=0,
            error_rate_trend="stable",
            memory_trend=memory_trend,
            timestamp=datetime.now().isoformat(),
            system_metrics=monitor.metrics
        )
        
        self.results.append(result)
        self._print_result(result)
        return result
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analyze if values are increasing, decreasing, or stable"""
        if len(values) < 2:
            return "stable"
        
        # Calculate trend using simple linear regression
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        change_percent = ((second_half - first_half) / max(first_half, 0.1)) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_memory_trend(self, metrics: List[SystemMetrics]) -> str:
        """Analyze memory trend"""
        if len(metrics) < 2:
            return "stable"
        
        memory_values = [m.memory_mb for m in metrics]
        first_half = statistics.mean(memory_values[:len(memory_values)//2])
        second_half = statistics.mean(memory_values[len(memory_values)//2:])
        
        change_percent = ((second_half - first_half) / max(first_half, 1)) * 100
        
        if change_percent > 15:
            return "increasing"
        elif change_percent < -15:
            return "decreasing"
        else:
            return "stable"
    
    def _print_result(self, result: EnduranceTestResult):
        """Print test result"""
        print(f"\n{'='*80}")
        print(f"Endurance Test Result: {result.scenario_name}")
        print(f"{'='*80}")
        print(f"Duration: {result.duration_minutes} minutes")
        print(f"Concurrent Users: {result.concurrent_users}")
        print(f"\nRequest Statistics:")
        print(f"  Total Requests: {result.total_requests}")
        print(f"  Successful: {result.successful_requests}")
        print(f"  Failed: {result.failed_requests}")
        print(f"  Error Rate: {result.error_rate:.2f}%")
        print(f"  Throughput: {result.throughput_rps:.2f} req/s")
        print(f"\nResponse Time:")
        print(f"  Average: {result.avg_response_time_ms:.2f}ms")
        print(f"  P95: {result.p95_response_time_ms:.2f}ms")
        print(f"  P99: {result.p99_response_time_ms:.2f}ms")
        print(f"\nMemory Usage:")
        print(f"  Initial: {result.initial_memory_mb:.2f}MB")
        print(f"  Peak: {result.peak_memory_mb:.2f}MB")
        print(f"  Final: {result.final_memory_mb:.2f}MB")
        print(f"  Growth: {result.memory_growth_mb:.2f}MB ({result.memory_growth_percent:.2f}%)")
        print(f"  Trend: {result.memory_trend}")
        print(f"\nCPU Usage:")
        print(f"  Initial: {result.initial_cpu_percent:.2f}%")
        print(f"  Average: {result.avg_cpu_percent:.2f}%")
        print(f"  Peak: {result.peak_cpu_percent:.2f}%")
        print(f"\nDegradation Analysis:")
        print(f"  First Hour Avg Response: {result.first_hour_avg_response_ms:.2f}ms")
        print(f"  Last Hour Avg Response: {result.last_hour_avg_response_ms:.2f}ms")
        print(f"  Degradation: {result.response_time_degradation_percent:.2f}%")
        print(f"  Error Rate Trend: {result.error_rate_trend}")
        print(f"{'='*80}\n")
    
    def save_results(self, filename: str = "endurance_test_results.json"):
        """Save test results to file"""
        results_data = [asdict(r) for r in self.results]
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        print(f"Results saved to {filename}")


if __name__ == "__main__":
    runner = EnduranceTestRunner("http://localhost:8000")
    
    # Run sustained load test (1 hour)
    runner.run_sustained_load_test(
        duration_minutes=60,
        concurrent_users=50,
        requests_per_user_per_minute=10
    )
    
    # Run memory leak test (30 minutes)
    runner.run_memory_leak_test(
        duration_minutes=30,
        concurrent_users=20
    )
    
    # Save results
    runner.save_results("Backend/tests/performance/endurance_test_results.json")
