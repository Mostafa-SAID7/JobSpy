"""
Stress Test: Recovery After Extreme Load
Tests system recovery to normal operation after stress
"""

import pytest
import time
from stress_test import StressTester


@pytest.mark.performance
@pytest.mark.stress
def test_stress_recovery_after_extreme_load():
    """Test system recovery after extreme load"""
    tester = StressTester(base_url="http://localhost:8000")
    
    # First, run extreme load
    extreme_metrics = tester.run_stress_scenario(
        "Recovery - Extreme Load Phase",
        concurrent_users=1000,
        duration_seconds=30
    )
    
    # Wait for recovery
    print("\n⏳ Waiting 30 seconds for system recovery...")
    time.sleep(30)
    
    # Then test recovery with normal load
    recovery_metrics = tester.run_stress_scenario(
        "Recovery - Normal Load Phase",
        concurrent_users=100,
        duration_seconds=60
    )
    
    # Recovery metrics should be better than extreme load
    assert recovery_metrics.error_rate < extreme_metrics.error_rate, \
        "Error rate should decrease after recovery"
    assert recovery_metrics.avg_response_time_ms < extreme_metrics.avg_response_time_ms, \
        "Response time should improve after recovery"


@pytest.mark.performance
@pytest.mark.stress
def test_stress_recovery_response_times():
    """Test response time recovery after extreme load"""
    tester = StressTester(base_url="http://localhost:8000")
    
    # Run extreme load
    tester.run_stress_scenario(
        "Recovery - Extreme Load",
        concurrent_users=1000,
        duration_seconds=30
    )
    
    # Wait for recovery
    time.sleep(30)
    
    # Test recovery
    recovery_metrics = tester.run_stress_scenario(
        "Recovery - Response Times",
        concurrent_users=100,
        duration_seconds=60
    )
    
    # Response times should be acceptable after recovery
    assert recovery_metrics.avg_response_time_ms < 2000, \
        "Response time should be < 2s after recovery"
    assert recovery_metrics.p95_response_time_ms < 3000, \
        "P95 response time should be < 3s after recovery"


@pytest.mark.performance
@pytest.mark.stress
def test_stress_recovery_no_resource_leaks():
    """Test that system doesn't have resource leaks after stress"""
    tester = StressTester(base_url="http://localhost:8000")
    
    # Run extreme load
    tester.run_stress_scenario(
        "Recovery - Resource Leak Check (Extreme)",
        concurrent_users=1000,
        duration_seconds=30
    )
    
    # Wait for recovery
    time.sleep(30)
    
    # Test recovery - should handle normal load without issues
    recovery_metrics = tester.run_stress_scenario(
        "Recovery - Resource Leak Check (Normal)",
        concurrent_users=100,
        duration_seconds=60
    )
    
    # Should not have excessive errors indicating resource exhaustion
    assert recovery_metrics.error_rate < 0.10, \
        "Error rate should be < 10% after recovery (no resource leaks)"
    assert recovery_metrics.successful_requests > recovery_metrics.failed_requests, \
        "Should have more successful than failed requests after recovery"
