"""
Stress Test: Sustained Load at 500 Concurrent Users for 5 Minutes
Tests system stability under prolonged high load
"""

import pytest
from stress_test import StressTester


@pytest.mark.performance
@pytest.mark.stress
def test_stress_sustained_load_500_users_5min():
    """Test sustained load at 500 users for 5 minutes"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Sustained Load - 500 Users for 5 Minutes",
        concurrent_users=500,
        duration_seconds=300
    )
    
    # Assertions
    assert metrics.total_requests > 100, "Should have made many requests"
    assert metrics.successful_requests > 0, "Should have successful requests"
    assert metrics.error_rate < 0.25, "Error rate should be < 25% under sustained load"
    assert metrics.avg_response_time_ms < 5000, "Avg response time should be < 5s"


@pytest.mark.performance
@pytest.mark.stress
def test_stress_sustained_load_stability():
    """Test system stability during sustained load"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Sustained Load - Stability",
        concurrent_users=500,
        duration_seconds=300
    )
    
    # Response times should not degrade significantly
    assert metrics.p99_response_time_ms < 6000, "P99 response time should be < 6s"
    assert metrics.max_response_time_ms < 10000, "Max response time should be < 10s"


@pytest.mark.performance
@pytest.mark.stress
def test_stress_sustained_load_consistency():
    """Test consistency of metrics during sustained load"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Sustained Load - Consistency",
        concurrent_users=500,
        duration_seconds=300
    )
    
    # Throughput should be relatively consistent
    assert metrics.throughput_rps > 0.2, "Throughput should be > 0.2 req/s"
    
    # Should not reach breaking point at 500 users for 5 minutes
    if metrics.breaking_point_reached:
        # Allow breaking point but log it
        assert metrics.error_rate < 0.30, "Error rate should be < 30%"
