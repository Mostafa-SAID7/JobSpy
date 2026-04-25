"""
Stress Test: Gradual Ramp-up to 200 Concurrent Users
Tests system behavior with gradual increase in load
"""

import pytest
import time
from stress_test import StressTester


@pytest.mark.performance
@pytest.mark.stress
def test_stress_gradual_rampup_200_users():
    """Test gradual ramp-up to 200 concurrent users"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Gradual Ramp-up to 200 Users",
        concurrent_users=200,
        duration_seconds=60
    )
    
    # Assertions
    assert metrics.total_requests > 0, "Should have made requests"
    assert metrics.successful_requests > 0, "Should have successful requests"
    assert metrics.error_rate < 0.15, "Error rate should be < 15%"
    assert metrics.avg_response_time_ms < 3000, "Avg response time should be < 3s"
    assert metrics.throughput_rps > 0.5, "Throughput should be > 0.5 req/s"


@pytest.mark.performance
@pytest.mark.stress
def test_stress_gradual_rampup_response_times():
    """Test response time distribution during gradual ramp-up"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Gradual Ramp-up - Response Times",
        concurrent_users=200,
        duration_seconds=60
    )
    
    # Response time assertions
    assert metrics.p50_response_time_ms < 1000, "P50 response time should be < 1s"
    assert metrics.p95_response_time_ms < 2000, "P95 response time should be < 2s"
    assert metrics.p99_response_time_ms < 3000, "P99 response time should be < 3s"
    assert metrics.max_response_time_ms < 5000, "Max response time should be < 5s"


@pytest.mark.performance
@pytest.mark.stress
def test_stress_gradual_rampup_no_breaking_point():
    """Test that gradual ramp-up doesn't reach breaking point"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Gradual Ramp-up - No Breaking Point",
        concurrent_users=200,
        duration_seconds=60
    )
    
    # Should not reach breaking point at 200 users
    assert not metrics.breaking_point_reached, \
        f"Should not reach breaking point at 200 users: {metrics.breaking_point_reason}"
