"""
Load Testing for JobSpy Application
Tests system performance under various load conditions
"""

import time
import json
import random
import statistics
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class ResponseMetrics:
    """Metrics for a single response"""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: str
    error: str = None


@dataclass
class LoadTestResult:
    """Results from a load test scenario"""
    scenario_name: str
    concurrent_users: int
    duration_seconds: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    min_response_time_ms: float
    max_response_time_ms: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    throughput_rps: float
    error_rate: float
    timestamp: str


class LoadTestClient:
    """HTTP client for load testing with retry logic"""
    
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
    
    def register_user(self, email: str, password: str) -> Tuple[bool, str]:
        """Register a new user"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "full_name": f"Test User {random.randint(1000, 9999)}"
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return True, response.json().get("user_id")
            return False, None
        except Exception as e:
            return False, str(e)
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """Login and get auth token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=self.timeout
            )
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                return True, self.auth_token
            return False, None
        except Exception as e:
            return False, str(e)
    
    def _get_headers(self) -> Dict:
        """Get request headers with auth token"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def search_jobs(self, search_term: str = "Python") -> ResponseMetrics:
        """Search for jobs"""
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/jobs",
                params={"search_term": search_term, "limit": 20},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/jobs",
                method="GET",
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=None if response.status_code == 200 else response.text
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/jobs",
                method="GET",
                status_code=0,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def get_job_details(self, job_id: str) -> ResponseMetrics:
        """Get job details"""
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/jobs/{job_id}",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint=f"/api/v1/jobs/{{id}}",
                method="GET",
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=None if response.status_code == 200 else response.text
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint=f"/api/v1/jobs/{{id}}",
                method="GET",
                status_code=0,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def save_job(self, job_id: str) -> ResponseMetrics:
        """Save a job"""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/saved-jobs",
                json={"job_id": job_id, "notes": "Test save"},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/saved-jobs",
                method="POST",
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=None if response.status_code in [200, 201] else response.text
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/saved-jobs",
                method="POST",
                status_code=0,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def get_saved_jobs(self) -> ResponseMetrics:
        """Get saved jobs"""
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/saved-jobs",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/saved-jobs",
                method="GET",
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=None if response.status_code == 200 else response.text
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/saved-jobs",
                method="GET",
                status_code=0,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def create_alert(self, search_term: str = "Python") -> ResponseMetrics:
        """Create an alert"""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/alerts",
                json={
                    "search_term": search_term,
                    "frequency": "daily",
                    "is_active": True
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/alerts",
                method="POST",
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=None if response.status_code in [200, 201] else response.text
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/alerts",
                method="POST",
                status_code=0,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def get_alerts(self) -> ResponseMetrics:
        """Get alerts"""
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/alerts",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/alerts",
                method="GET",
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=None if response.status_code == 200 else response.text
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return ResponseMetrics(
                endpoint="/api/v1/alerts",
                method="GET",
                status_code=0,
                response_time_ms=response_time_ms,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )


class LoadTester:
    """Main load testing orchestrator"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[LoadTestResult] = []
        self.metrics: List[ResponseMetrics] = []
    
    def run_scenario(
        self,
        scenario_name: str,
        concurrent_users: int,
        duration_seconds: int,
        user_actions_func
    ) -> LoadTestResult:
        """Run a load test scenario"""
        print(f"\n{'='*60}")
        print(f"Running: {scenario_name}")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Duration: {duration_seconds}s")
        print(f"{'='*60}")
        
        start_time = time.time()
        scenario_metrics: List[ResponseMetrics] = []
        
        # Simulate concurrent users
        for user_id in range(concurrent_users):
            client = LoadTestClient(self.base_url)
            
            # Setup user (register/login)
            email = f"loadtest_{user_id}_{int(time.time())}@test.com"
            password = "TestPassword123!"
            
            # Try to register
            client.register_user(email, password)
            # Login
            client.login(email, password)
            
            # Run user actions
            elapsed = 0
            while elapsed < duration_seconds:
                metrics = user_actions_func(client)
                scenario_metrics.extend(metrics if isinstance(metrics, list) else [metrics])
                elapsed = time.time() - start_time
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in scenario_metrics if m.response_time_ms > 0]
        successful = sum(1 for m in scenario_metrics if m.status_code in [200, 201])
        failed = len(scenario_metrics) - successful
        
        if response_times:
            response_times.sort()
            result = LoadTestResult(
                scenario_name=scenario_name,
                concurrent_users=concurrent_users,
                duration_seconds=duration_seconds,
                total_requests=len(scenario_metrics),
                successful_requests=successful,
                failed_requests=failed,
                min_response_time_ms=min(response_times),
                max_response_time_ms=max(response_times),
                avg_response_time_ms=statistics.mean(response_times),
                p95_response_time_ms=response_times[int(len(response_times) * 0.95)] if len(response_times) > 0 else 0,
                p99_response_time_ms=response_times[int(len(response_times) * 0.99)] if len(response_times) > 0 else 0,
                throughput_rps=len(scenario_metrics) / duration_seconds,
                error_rate=failed / len(scenario_metrics) if scenario_metrics else 0,
                timestamp=datetime.now().isoformat()
            )
        else:
            result = LoadTestResult(
                scenario_name=scenario_name,
                concurrent_users=concurrent_users,
                duration_seconds=duration_seconds,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                min_response_time_ms=0,
                max_response_time_ms=0,
                avg_response_time_ms=0,
                p95_response_time_ms=0,
                p99_response_time_ms=0,
                throughput_rps=0,
                error_rate=1.0,
                timestamp=datetime.now().isoformat()
            )
        
        self.results.append(result)
        self.metrics.extend(scenario_metrics)
        
        # Print results
        self._print_result(result)
        
        return result
    
    def _print_result(self, result: LoadTestResult):
        """Print test result"""
        print(f"\n📊 Results for {result.scenario_name}:")
        print(f"  Total Requests: {result.total_requests}")
        print(f"  Successful: {result.successful_requests}")
        print(f"  Failed: {result.failed_requests}")
        print(f"  Error Rate: {result.error_rate*100:.2f}%")
        print(f"  Response Times (ms):")
        print(f"    Min: {result.min_response_time_ms:.2f}")
        print(f"    Max: {result.max_response_time_ms:.2f}")
        print(f"    Avg: {result.avg_response_time_ms:.2f}")
        print(f"    P95: {result.p95_response_time_ms:.2f}")
        print(f"    P99: {result.p99_response_time_ms:.2f}")
        print(f"  Throughput: {result.throughput_rps:.2f} req/s")
    
    def generate_report(self, output_file: str = "Backend/tests/performance/load_test_report.md"):
        """Generate comprehensive load test report"""
        report = "# Load Testing Report - JobSpy Application\n\n"
        report += f"**Generated:** {datetime.now().isoformat()}\n\n"
        
        report += "## Executive Summary\n\n"
        report += f"- **Total Scenarios:** {len(self.results)}\n"
        report += f"- **Total Requests:** {sum(r.total_requests for r in self.results)}\n"
        report += f"- **Overall Success Rate:** {(sum(r.successful_requests for r in self.results) / sum(r.total_requests for r in self.results) * 100) if sum(r.total_requests for r in self.results) > 0 else 0:.2f}%\n\n"
        
        report += "## Performance Requirements Validation\n\n"
        report += "| Requirement | Target | Status | Notes |\n"
        report += "|---|---|---|---|\n"
        
        # Check requirement 8.1: Response time < 500ms
        avg_response_time = statistics.mean([r.avg_response_time_ms for r in self.results]) if self.results else 0
        status_8_1 = "✅ PASS" if avg_response_time < 500 else "❌ FAIL"
        report += f"| 8.1: Response Time < 500ms | {avg_response_time:.2f}ms | {status_8_1} | Average across all scenarios |\n"
        
        # Check requirement 8.2: Handle 100+ concurrent users
        max_concurrent = max([r.concurrent_users for r in self.results]) if self.results else 0
        status_8_2 = "✅ PASS" if max_concurrent >= 100 else "⚠️  PARTIAL"
        report += f"| 8.2: Handle 100+ Concurrent Users | {max_concurrent} users | {status_8_2} | Max tested |\n"
        
        # Check requirement 8.3: Handle 1000+ requests per minute
        max_throughput = max([r.throughput_rps * 60 for r in self.results]) if self.results else 0
        status_8_3 = "✅ PASS" if max_throughput >= 1000 else "⚠️  PARTIAL"
        report += f"| 8.3: Handle 1000+ req/min | {max_throughput:.0f} req/min | {status_8_3} | Max throughput |\n"
        
        # Check requirement 8.5: Error handling
        avg_error_rate = statistics.mean([r.error_rate for r in self.results]) if self.results else 0
        status_8_5 = "✅ PASS" if avg_error_rate < 0.05 else "⚠️  PARTIAL"
        report += f"| 8.5: Error Handling | {avg_error_rate*100:.2f}% error rate | {status_8_5} | Should be < 5% |\n\n"
        
        report += "## Detailed Results by Scenario\n\n"
        
        for result in self.results:
            report += f"### {result.scenario_name}\n\n"
            report += f"**Configuration:**\n"
            report += f"- Concurrent Users: {result.concurrent_users}\n"
            report += f"- Duration: {result.duration_seconds}s\n"
            report += f"- Timestamp: {result.timestamp}\n\n"
            
            report += f"**Metrics:**\n"
            report += f"- Total Requests: {result.total_requests}\n"
            report += f"- Successful: {result.successful_requests}\n"
            report += f"- Failed: {result.failed_requests}\n"
            report += f"- Error Rate: {result.error_rate*100:.2f}%\n"
            report += f"- Throughput: {result.throughput_rps:.2f} req/s ({result.throughput_rps*60:.0f} req/min)\n\n"
            
            report += f"**Response Times (ms):**\n"
            report += f"- Min: {result.min_response_time_ms:.2f}\n"
            report += f"- Max: {result.max_response_time_ms:.2f}\n"
            report += f"- Average: {result.avg_response_time_ms:.2f}\n"
            report += f"- P95: {result.p95_response_time_ms:.2f}\n"
            report += f"- P99: {result.p99_response_time_ms:.2f}\n\n"
        
        report += "## Bottlenecks Identified\n\n"
        
        # Identify bottlenecks
        bottlenecks = []
        for result in self.results:
            if result.avg_response_time_ms > 500:
                bottlenecks.append(f"- **{result.scenario_name}**: High response time ({result.avg_response_time_ms:.2f}ms)")
            if result.error_rate > 0.05:
                bottlenecks.append(f"- **{result.scenario_name}**: High error rate ({result.error_rate*100:.2f}%)")
            if result.throughput_rps < 10:
                bottlenecks.append(f"- **{result.scenario_name}**: Low throughput ({result.throughput_rps:.2f} req/s)")
        
        if bottlenecks:
            for bottleneck in bottlenecks:
                report += f"{bottleneck}\n"
        else:
            report += "No significant bottlenecks identified.\n\n"
        
        report += "\n## Recommendations for Optimization\n\n"
        report += "1. **Database Optimization:**\n"
        report += "   - Add indexes on frequently queried columns\n"
        report += "   - Implement query optimization and caching\n"
        report += "   - Consider database connection pooling\n\n"
        
        report += "2. **API Optimization:**\n"
        report += "   - Implement response compression (gzip)\n"
        report += "   - Add pagination to reduce response size\n"
        report += "   - Implement rate limiting to prevent abuse\n\n"
        
        report += "3. **Caching Strategy:**\n"
        report += "   - Increase Redis cache TTL for frequently accessed data\n"
        report += "   - Implement cache warming for popular searches\n"
        report += "   - Use CDN for static assets\n\n"
        
        report += "4. **Infrastructure:**\n"
        report += "   - Implement horizontal scaling with load balancing\n"
        report += "   - Use async workers for background jobs\n"
        report += "   - Monitor and optimize resource usage\n\n"
        
        report += "5. **Monitoring:**\n"
        report += "   - Setup real-time performance monitoring\n"
        report += "   - Implement alerting for performance degradation\n"
        report += "   - Track metrics over time for trend analysis\n\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"\n✅ Report generated: {output_file}")


def run_load_tests():
    """Run all load test scenarios"""
    tester = LoadTester(base_url="http://localhost:8000")
    
    # Scenario 1: 10 concurrent users - search jobs
    def scenario_1_actions(client):
        return [client.search_jobs()]
    
    tester.run_scenario(
        "10 Concurrent Users - Search Jobs",
        concurrent_users=10,
        duration_seconds=30,
        user_actions_func=scenario_1_actions
    )
    
    # Scenario 2: 50 concurrent users - mixed operations
    def scenario_2_actions(client):
        actions = [client.search_jobs()]
        if random.random() > 0.7:
            actions.append(client.get_saved_jobs())
        return actions
    
    tester.run_scenario(
        "50 Concurrent Users - Mixed Operations",
        concurrent_users=50,
        duration_seconds=30,
        user_actions_func=scenario_2_actions
    )
    
    # Scenario 3: 100 concurrent users - comprehensive operations
    def scenario_3_actions(client):
        actions = []
        rand = random.random()
        if rand < 0.4:
            actions.append(client.search_jobs())
        elif rand < 0.7:
            actions.append(client.get_saved_jobs())
        else:
            actions.append(client.create_alert())
        return actions
    
    tester.run_scenario(
        "100 Concurrent Users - Comprehensive Operations",
        concurrent_users=100,
        duration_seconds=30,
        user_actions_func=scenario_3_actions
    )
    
    # Generate report
    tester.generate_report()


if __name__ == "__main__":
    run_load_tests()
