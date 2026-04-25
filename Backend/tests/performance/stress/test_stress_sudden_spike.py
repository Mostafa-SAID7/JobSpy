"""
Stress Test: Sudden Spike to 500 Concurrent Users
Tests system behavior with sudden load increase
"""

import pytest
from .stress_test import StressTester


@pytest.mark.performance
@pytest.mark.stress
def test_stress_sudden_spike_500_users():
    """Test sudden spike to 500 concurrent users"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Sudden Spike to 500 Users",
        concurrent_users=500,
        duration_seconds=60
    )
    
    # Assertions
    assert metrics.total_requests > 0, "Should have made requests"
    assert metrics.successful_requests > 0, "Should have successful requests"
    assert metrics.error_rate < 0.20, "Error rate should be < 20% under spike"
    assert metrics.avg_response_time_ms < 4000, "Avg response time should be < 4s"


@pytest.mark.performance
@pytest.mark.stress
def test_stress_sudden_spike_throughput():
    """Test throughput during sudden spike"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Sudden Spike - Throughput",
        concurrent_users=500,
        duration_seconds=60
    )
    
    # Throughput should be maintained
    assert metrics.throughput_rps > 0.3, "Throughput should be > 0.3 req/s"
    assert metrics.throughput_rps * 60 > 20, "Should handle > 20 req/min"


@pytest.mark.performance
@pytest.mark.stress
def test_stress_sudden_spike_error_handling():
    """Test error handling during sudden spike"""
    tester = StressTester(base_url="http://localhost:8000")
    
    metrics = tester.run_stress_scenario(
        "Sudden Spike - Error Handling",
        concurrent_users=500,
        duration_seconds=60
    )
    
    # Should handle errors gracefully
    assert len(metrics.errors) < metrics.total_requests * 0.5, \
        "Should not have excessive errors"
    assert metrics.status_codes.get(500, 0) < metrics.total_requests * 0.1, \
        "Should not have many 500 errors"
