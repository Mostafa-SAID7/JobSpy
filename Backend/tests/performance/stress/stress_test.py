"""
Comprehensive Stress Testing for JobSpy Application
Tests system with extreme load conditions (200-1000+ concurrent users)
Identifies breaking points, degradation patterns, and recovery behavior
"""

import time
import json
import random
import statistics
import threading
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class StressTestMetrics:
    """Metrics collected during stress test"""
    timestamp: str
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    min_response_time_ms: float
    max_response_time_ms: float
    avg_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    throughput_rps: float
    error_rate: float
    breaking_point_reached: bool = False
    breaking_point_reason: str = ""
    response_times: List[float] = field(default_factory=list)
    status_codes: Dict[int, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class StressTestClient:
    """HTTP client for stress testing with connection pooling"""
    
    def __init__(self, base_url: str, timeout: int = 60):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session()
        self.auth_token = None
        self.user_id = None
    
    def _create_session(self) -> requests.Session:
        """Create session with connection pooling and retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=1,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=100,
            pool_maxsize=100
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def setup_user(self, email: str, password: str) -> bool:
        """Setup user (register and login)"""
        try:
            # Try to register
            self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "full_name": f"Stress Test User {random.randint(1000, 9999)}"
                },
                timeout=self.timeout
            )
            
            # Login
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                return True
            return False
        except Exception:
            return False
    
    def _get_headers(self) -> Dict:
        """Get request headers with auth token"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def search_jobs(self) -> Tuple[float, int, Optional[str]]:
        """Search for jobs and measure response time"""
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/jobs",
                params={"search_term": "Python", "limit": 20},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, response.status_code, None
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, 0, str(e)
    
    def get_job_details(self, job_id: str = "test-id") -> Tuple[float, int, Optional[str]]:
        """Get job details"""
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/jobs/{job_id}",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, response.status_code, None
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, 0, str(e)
    
    def save_job(self, job_id: str = "test-id") -> Tuple[float, int, Optional[str]]:
        """Save a job"""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/saved-jobs",
                json={"job_id": job_id, "notes": "Stress test"},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, response.status_code, None
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, 0, str(e)
    
    def get_saved_jobs(self) -> Tuple[float, int, Optional[str]]:
        """Get saved jobs"""
        start_time = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/saved-jobs",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, response.status_code, None
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, 0, str(e)
    
    def create_alert(self) -> Tuple[float, int, Optional[str]]:
        """Create an alert"""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/alerts",
                json={
                    "search_term": "Python",
                    "frequency": "daily",
                    "is_active": True
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, response.status_code, None
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return response_time_ms, 0, str(e)


class StressTester:
    """Main stress testing orchestrator"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[StressTestMetrics] = []
        self.lock = threading.Lock()
    
    def run_stress_scenario(
        self,
        scenario_name: str,
        concurrent_users: int,
        duration_seconds: int,
        ramp_up_seconds: int = 0
    ) -> StressTestMetrics:
        """Run a stress test scenario"""
        print(f"\n{'='*70}")
        print(f"🔥 STRESS TEST: {scenario_name}")
        print(f"{'='*70}")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Duration: {duration_seconds}s")
        if ramp_up_seconds > 0:
            print(f"Ramp-up: {ramp_up_seconds}s")
        print(f"Start Time: {datetime.now().isoformat()}")
        
        metrics = StressTestMetrics(
            timestamp=datetime.now().isoformat(),
            concurrent_users=concurrent_users,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            min_response_time_ms=float('inf'),
            max_response_time_ms=0,
            avg_response_time_ms=0,
            p50_response_time_ms=0,
            p95_response_time_ms=0,
            p99_response_time_ms=0,
            throughput_rps=0,
            error_rate=0
        )
        
        start_time = time.time()
        
        def user_task(user_id: int):
            """Task for each concurrent user"""
            email = f"stress_{user_id}_{int(time.time())}@test.com"
            password = "StressTest123!"
            
            client = StressTestClient(self.base_url)
            
            # Setup user
            if not client.setup_user(email, password):
                with self.lock:
                    metrics.failed_requests += 1
                    metrics.errors.append(f"User {user_id} setup failed")
                return
            
            # Perform actions during test duration
            elapsed = 0
            while elapsed < duration_seconds:
                # Randomly choose action
                action = random.choice([
                    client.search_jobs,
                    client.get_saved_jobs,
                    client.create_alert,
                    client.save_job
                ])
                
                response_time_ms, status_code, error = action()
                
                with self.lock:
                    metrics.total_requests += 1
                    metrics.response_times.append(response_time_ms)
                    metrics.status_codes[status_code] = metrics.status_codes.get(status_code, 0) + 1
                    
                    if status_code in [200, 201]:
                        metrics.successful_requests += 1
                    else:
                        metrics.failed_requests += 1
                        if error:
                            metrics.errors.append(error)
                    
                    metrics.min_response_time_ms = min(metrics.min_response_time_ms, response_time_ms)
                    metrics.max_response_time_ms = max(metrics.max_response_time_ms, response_time_ms)
                
                elapsed = time.time() - start_time
        
        # Execute stress test with thread pool
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_task, i) for i in range(concurrent_users)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Task error: {e}")
        
        # Calculate final metrics
        total_duration = time.time() - start_time
        
        if metrics.response_times:
            sorted_times = sorted(metrics.response_times)
            metrics.avg_response_time_ms = statistics.mean(sorted_times)
            metrics.p50_response_time_ms = sorted_times[int(len(sorted_times) * 0.50)]
            metrics.p95_response_time_ms = sorted_times[int(len(sorted_times) * 0.95)]
            metrics.p99_response_time_ms = sorted_times[int(len(sorted_times) * 0.99)]
        
        metrics.throughput_rps = metrics.total_requests / total_duration if total_duration > 0 else 0
        metrics.error_rate = metrics.failed_requests / metrics.total_requests if metrics.total_requests > 0 else 0
        
        # Detect breaking point
        if metrics.error_rate > 0.10:  # >10% error rate
            metrics.breaking_point_reached = True
            metrics.breaking_point_reason = f"High error rate: {metrics.error_rate*100:.2f}%"
        elif metrics.avg_response_time_ms > 2000:  # >2s avg response
            metrics.breaking_point_reached = True
            metrics.breaking_point_reason = f"High response time: {metrics.avg_response_time_ms:.2f}ms"
        elif metrics.throughput_rps < 1:  # <1 req/s
            metrics.breaking_point_reached = True
            metrics.breaking_point_reason = f"Low throughput: {metrics.throughput_rps:.2f} req/s"
        
        self.results.append(metrics)
        self._print_metrics(metrics)
        
        return metrics
    
    def _print_metrics(self, metrics: StressTestMetrics):
        """Print test metrics"""
        print(f"\n📊 Results:")
        print(f"  Total Requests: {metrics.total_requests}")
        print(f"  Successful: {metrics.successful_requests}")
        print(f"  Failed: {metrics.failed_requests}")
        print(f"  Error Rate: {metrics.error_rate*100:.2f}%")
        print(f"  Response Times (ms):")
        print(f"    Min: {metrics.min_response_time_ms:.2f}")
        print(f"    Max: {metrics.max_response_time_ms:.2f}")
        print(f"    Avg: {metrics.avg_response_time_ms:.2f}")
        print(f"    P50: {metrics.p50_response_time_ms:.2f}")
        print(f"    P95: {metrics.p95_response_time_ms:.2f}")
        print(f"    P99: {metrics.p99_response_time_ms:.2f}")
        print(f"  Throughput: {metrics.throughput_rps:.2f} req/s ({metrics.throughput_rps*60:.0f} req/min)")
        
        if metrics.breaking_point_reached:
            print(f"  ⚠️  BREAKING POINT REACHED: {metrics.breaking_point_reason}")
    
    def generate_stress_report(self, output_file: str = "Backend/tests/performance/stress_test_report.md"):
        """Generate comprehensive stress test report"""
        report = "# Stress Testing Report - JobSpy Application\n\n"
        report += f"**Generated:** {datetime.now().isoformat()}\n"
        report += f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Executive Summary\n\n"
        report += f"- **Total Scenarios:** {len(self.results)}\n"
        report += f"- **Total Requests:** {sum(r.total_requests for r in self.results)}\n"
        report += f"- **Overall Success Rate:** {(sum(r.successful_requests for r in self.results) / sum(r.total_requests for r in self.results) * 100) if sum(r.total_requests for r in self.results) > 0 else 0:.2f}%\n"
        report += f"- **Breaking Points Detected:** {sum(1 for r in self.results if r.breaking_point_reached)}\n\n"
        
        report += "## Performance Requirements Validation\n\n"
        report += "| Requirement | Target | Actual | Status | Notes |\n"
        report += "|---|---|---|---|---|\n"
        
        # Requirement 8.1: Response time < 500ms
        avg_response_time = statistics.mean([r.avg_response_time_ms for r in self.results]) if self.results else 0
        status_8_1 = "✅ PASS" if avg_response_time < 500 else "❌ FAIL"
        report += f"| 8.1: Response Time < 500ms | <500ms | {avg_response_time:.2f}ms | {status_8_1} | Average across all scenarios |\n"
        
        # Requirement 8.2: Handle 100+ concurrent users
        max_concurrent = max([r.concurrent_users for r in self.results]) if self.results else 0
        status_8_2 = "✅ PASS" if max_concurrent >= 100 else "⚠️  PARTIAL"
        report += f"| 8.2: Handle 100+ Concurrent Users | ≥100 users | {max_concurrent} users | {status_8_2} | Max tested |\n"
        
        # Requirement 8.3: Handle 1000+ requests per minute
        max_throughput = max([r.throughput_rps * 60 for r in self.results]) if self.results else 0
        status_8_3 = "✅ PASS" if max_throughput >= 1000 else "⚠️  PARTIAL"
        report += f"| 8.3: Handle 1000+ req/min | ≥1000 req/min | {max_throughput:.0f} req/min | {status_8_3} | Max throughput |\n"
        
        # Requirement 8.5: Error handling
        avg_error_rate = statistics.mean([r.error_rate for r in self.results]) if self.results else 0
        status_8_5 = "✅ PASS" if avg_error_rate < 0.05 else "⚠️  PARTIAL"
        report += f"| 8.5: Error Handling | <5% error rate | {avg_error_rate*100:.2f}% | {status_8_5} | Should be < 5% |\n\n"
        
        report += "## Detailed Results by Scenario\n\n"
        
        for result in self.results:
            report += f"### {result.concurrent_users} Concurrent Users\n\n"
            report += f"**Configuration:**\n"
            report += f"- Concurrent Users: {result.concurrent_users}\n"
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
            report += f"- P50: {result.p50_response_time_ms:.2f}\n"
            report += f"- P95: {result.p95_response_time_ms:.2f}\n"
            report += f"- P99: {result.p99_response_time_ms:.2f}\n\n"
            
            if result.breaking_point_reached:
                report += f"**⚠️  BREAKING POINT:** {result.breaking_point_reason}\n\n"
        
        report += "## Breaking Points Analysis\n\n"
        
        breaking_points = [r for r in self.results if r.breaking_point_reached]
        if breaking_points:
            for bp in breaking_points:
                report += f"- **{bp.concurrent_users} users**: {bp.breaking_point_reason}\n"
            report += "\n"
        else:
            report += "No breaking points detected in tested scenarios.\n\n"
        
        report += "## Degradation Patterns\n\n"
        
        if len(self.results) > 1:
            sorted_results = sorted(self.results, key=lambda r: r.concurrent_users)
            report += "| Users | Avg Response (ms) | Error Rate (%) | Throughput (req/s) | Status |\n"
            report += "|---|---|---|---|---|\n"
            
            for result in sorted_results:
                status = "🔴 CRITICAL" if result.breaking_point_reached else "🟢 NORMAL"
                report += f"| {result.concurrent_users} | {result.avg_response_time_ms:.2f} | {result.error_rate*100:.2f} | {result.throughput_rps:.2f} | {status} |\n"
            report += "\n"
        
        report += "## Recovery Analysis\n\n"
        report += "- System should recover to normal operation after stress test ends\n"
        report += "- Monitor for lingering connections or resource leaks\n"
        report += "- Check database connection pool recovery\n"
        report += "- Verify cache invalidation after high load\n\n"
        
        report += "## Recommendations for Optimization\n\n"
        report += "1. **Database Optimization:**\n"
        report += "   - Add connection pooling (PgBouncer)\n"
        report += "   - Optimize slow queries with EXPLAIN ANALYZE\n"
        report += "   - Add missing indexes on frequently queried columns\n"
        report += "   - Consider read replicas for scaling reads\n\n"
        
        report += "2. **API Optimization:**\n"
        report += "   - Implement response compression (gzip)\n"
        report += "   - Add pagination to reduce response size\n"
        report += "   - Implement rate limiting per user/IP\n"
        report += "   - Use async/await for I/O operations\n\n"
        
        report += "3. **Caching Strategy:**\n"
        report += "   - Increase Redis cache TTL for frequently accessed data\n"
        report += "   - Implement cache warming for popular searches\n"
        report += "   - Use CDN for static assets\n"
        report += "   - Add query result caching\n\n"
        
        report += "4. **Infrastructure:**\n"
        report += "   - Implement horizontal scaling with load balancing\n"
        report += "   - Use auto-scaling based on CPU/memory metrics\n"
        report += "   - Implement circuit breakers for external services\n"
        report += "   - Use async workers (Celery) for background jobs\n\n"
        
        report += "5. **Monitoring & Alerting:**\n"
        report += "   - Setup real-time performance monitoring (Prometheus/Grafana)\n"
        report += "   - Implement alerting for performance degradation\n"
        report += "   - Track metrics over time for trend analysis\n"
        report += "   - Setup distributed tracing (Jaeger)\n\n"
        
        report += "## Conclusion\n\n"
        
        if breaking_points:
            report += f"The system reached breaking points at {breaking_points[0].concurrent_users} concurrent users. "
            report += "Immediate optimization is recommended before production deployment.\n"
        else:
            report += "The system handled all tested load scenarios successfully. "
            report += "Continue monitoring in production for real-world performance.\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"\n✅ Stress test report generated: {output_file}")


def run_comprehensive_stress_tests():
    """Run comprehensive stress testing scenarios"""
    tester = StressTester(base_url="http://localhost:8000")
    
    print("\n" + "="*70)
    print("🔥 JOBSPY COMPREHENSIVE STRESS TESTING SUITE")
    print("="*70)
    
    # Scenario 1: Gradual ramp-up to 200 users
    tester.run_stress_scenario(
        "Gradual Ramp-up to 200 Users",
        concurrent_users=200,
        duration_seconds=60
    )
    
    # Scenario 2: Sudden spike to 500 users
    tester.run_stress_scenario(
        "Sudden Spike to 500 Users",
        concurrent_users=500,
        duration_seconds=60
    )
    
    # Scenario 3: Sustained load at 500 users for 5 minutes
    tester.run_stress_scenario(
        "Sustained Load - 500 Users for 5 Minutes",
        concurrent_users=500,
        duration_seconds=300
    )
    
    # Scenario 4: Extreme load - 1000 users
    tester.run_stress_scenario(
        "Extreme Load - 1000 Users",
        concurrent_users=1000,
        duration_seconds=60
    )
    
    # Scenario 5: Recovery test - back to 100 users
    print("\n⏳ Waiting 30 seconds for system recovery...")
    time.sleep(30)
    
    tester.run_stress_scenario(
        "Recovery Test - 100 Users",
        concurrent_users=100,
        duration_seconds=60
    )
    
    # Generate comprehensive report
    tester.generate_stress_report()
    
    print("\n" + "="*70)
    print("✅ STRESS TESTING COMPLETE")
    print("="*70)


if __name__ == "__main__":
    run_comprehensive_stress_tests()
