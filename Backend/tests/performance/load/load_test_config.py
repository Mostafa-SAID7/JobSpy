"""
Load Testing Configuration
Defines test scenarios and parameters
"""

from dataclasses import dataclass
from typing import List, Callable


@dataclass
class LoadTestScenario:
    """Configuration for a load test scenario"""
    name: str
    concurrent_users: int
    duration_seconds: int
    requests_per_user: int
    description: str


# Test Scenarios
SCENARIOS = {
    "light": LoadTestScenario(
        name="Light Load - 10 Users",
        concurrent_users=10,
        duration_seconds=30,
        requests_per_user=5,
        description="Light load test with 10 concurrent users"
    ),
    "moderate": LoadTestScenario(
        name="Moderate Load - 50 Users",
        concurrent_users=50,
        duration_seconds=30,
        requests_per_user=3,
        description="Moderate load test with 50 concurrent users"
    ),
    "heavy": LoadTestScenario(
        name="Heavy Load - 100 Users",
        concurrent_users=100,
        duration_seconds=30,
        requests_per_user=2,
        description="Heavy load test with 100 concurrent users"
    ),
    "stress": LoadTestScenario(
        name="Stress Test - 500 Users",
        concurrent_users=500,
        duration_seconds=60,
        requests_per_user=1,
        description="Stress test with 500 concurrent users"
    ),
    "endurance": LoadTestScenario(
        name="Endurance Test - 50 Users 5 Minutes",
        concurrent_users=50,
        duration_seconds=300,
        requests_per_user=10,
        description="Endurance test with 50 users for 5 minutes"
    ),
}

# Performance Requirements
PERFORMANCE_REQUIREMENTS = {
    "response_time_avg_ms": 500,  # Requirement 8.1
    "response_time_p95_ms": 1000,
    "response_time_p99_ms": 1500,
    "concurrent_users": 100,  # Requirement 8.2
    "throughput_rpm": 1000,  # Requirement 8.3 (1000+ requests per minute)
    "uptime_percentage": 99.9,  # Requirement 8.4
    "error_rate_percentage": 5,  # Requirement 8.5 (< 5%)
    "success_rate_percentage": 95,
}

# Endpoints to Test
ENDPOINTS = {
    "search_jobs": {
        "method": "GET",
        "path": "/api/v1/jobs",
        "params": {"search_term": "Python", "limit": 20},
        "requires_auth": True,
        "description": "Search for jobs"
    },
    "get_job_details": {
        "method": "GET",
        "path": "/api/v1/jobs/{job_id}",
        "requires_auth": True,
        "description": "Get job details"
    },
    "login": {
        "method": "POST",
        "path": "/api/v1/auth/login",
        "requires_auth": False,
        "description": "User login"
    },
    "save_job": {
        "method": "POST",
        "path": "/api/v1/saved-jobs",
        "requires_auth": True,
        "description": "Save a job"
    },
    "get_saved_jobs": {
        "method": "GET",
        "path": "/api/v1/saved-jobs",
        "requires_auth": True,
        "description": "Get saved jobs"
    },
    "create_alert": {
        "method": "POST",
        "path": "/api/v1/alerts",
        "requires_auth": True,
        "description": "Create an alert"
    },
    "get_alerts": {
        "method": "GET",
        "path": "/api/v1/alerts",
        "requires_auth": True,
        "description": "Get alerts"
    },
}

# Test Profiles
TEST_PROFILES = {
    "quick": {
        "scenarios": ["light"],
        "duration_minutes": 1,
        "description": "Quick smoke test"
    },
    "standard": {
        "scenarios": ["light", "moderate", "heavy"],
        "duration_minutes": 3,
        "description": "Standard load test"
    },
    "comprehensive": {
        "scenarios": ["light", "moderate", "heavy", "stress"],
        "duration_minutes": 5,
        "description": "Comprehensive load test"
    },
    "endurance": {
        "scenarios": ["endurance"],
        "duration_minutes": 5,
        "description": "Endurance test"
    },
}

# Thresholds for Alerts
ALERT_THRESHOLDS = {
    "response_time_warning_ms": 400,
    "response_time_critical_ms": 600,
    "error_rate_warning_percentage": 3,
    "error_rate_critical_percentage": 10,
    "throughput_warning_rpm": 800,
    "throughput_critical_rpm": 500,
}

# Retry Configuration
RETRY_CONFIG = {
    "max_retries": 3,
    "backoff_factor": 0.5,
    "status_forcelist": [429, 500, 502, 503, 504],
}

# Timeout Configuration
TIMEOUT_CONFIG = {
    "connection_timeout_seconds": 10,
    "read_timeout_seconds": 30,
    "total_timeout_seconds": 60,
}

# Report Configuration
REPORT_CONFIG = {
    "output_format": "markdown",  # markdown, html, json
    "include_charts": True,
    "include_recommendations": True,
    "include_raw_data": False,
}


def get_scenario(scenario_name: str) -> LoadTestScenario:
    """Get scenario by name"""
    return SCENARIOS.get(scenario_name)


def get_profile(profile_name: str) -> dict:
    """Get test profile by name"""
    return TEST_PROFILES.get(profile_name)


def validate_requirements(metrics: dict) -> dict:
    """Validate metrics against requirements"""
    results = {
        "requirement_8_1": metrics.get("avg_response_time_ms", 0) < PERFORMANCE_REQUIREMENTS["response_time_avg_ms"],
        "requirement_8_2": metrics.get("concurrent_users", 0) >= PERFORMANCE_REQUIREMENTS["concurrent_users"],
        "requirement_8_3": metrics.get("throughput_rpm", 0) >= PERFORMANCE_REQUIREMENTS["throughput_rpm"],
        "requirement_8_4": metrics.get("uptime_percentage", 0) >= PERFORMANCE_REQUIREMENTS["uptime_percentage"],
        "requirement_8_5": metrics.get("error_rate_percentage", 100) <= PERFORMANCE_REQUIREMENTS["error_rate_percentage"],
    }
    return results


def get_alert_level(metric_name: str, value: float) -> str:
    """Determine alert level for a metric"""
    if metric_name == "response_time_ms":
        if value >= ALERT_THRESHOLDS["response_time_critical_ms"]:
            return "CRITICAL"
        elif value >= ALERT_THRESHOLDS["response_time_warning_ms"]:
            return "WARNING"
    elif metric_name == "error_rate_percentage":
        if value >= ALERT_THRESHOLDS["error_rate_critical_percentage"]:
            return "CRITICAL"
        elif value >= ALERT_THRESHOLDS["error_rate_warning_percentage"]:
            return "WARNING"
    elif metric_name == "throughput_rpm":
        if value <= ALERT_THRESHOLDS["throughput_critical_rpm"]:
            return "CRITICAL"
        elif value <= ALERT_THRESHOLDS["throughput_warning_rpm"]:
            return "WARNING"
    
    return "OK"
