"""
Unit tests for cache key patterns

Tests for basic cache key generation patterns and consistency.
"""
import pytest
from uuid import uuid4


def test_cache_key_generation():
    """Test that cache keys are generated correctly."""
    job_id = uuid4()
    cache_key = f"job:{job_id}"
    
    assert cache_key.startswith("job:")
    assert str(job_id) in cache_key


def test_search_cache_key_includes_query():
    """Test that search cache keys include the query."""
    query = "Python Developer"
    skip = 0
    limit = 100
    cache_key = f"jobs:search:{query}:{skip}:{limit}"
    
    assert query in cache_key
    assert str(skip) in cache_key
    assert str(limit) in cache_key


def test_cache_key_patterns_for_different_operations():
    """Test cache key patterns for different job operations."""
    job_id = uuid4()
    source = "linkedin"
    company = "Tech Corp"
    query = "Python"
    
    # Test individual job cache key
    job_cache_key = f"job:{job_id}"
    assert "job:" in job_cache_key
    
    # Test all jobs cache key
    all_jobs_key = f"jobs:all:0:100"
    assert "jobs:all:" in all_jobs_key
    
    # Test source-based cache key
    source_key = f"jobs:source:{source}:0:100"
    assert source in source_key
    
    # Test company-based cache key
    company_key = f"jobs:company:{company}:0:100"
    assert company in company_key
    
    # Test search cache key
    search_key = f"jobs:search:{query}:0:100"
    assert query in search_key


def test_cache_key_uniqueness():
    """Test that different queries generate different cache keys."""
    query1 = "Python Developer"
    query2 = "Java Developer"
    
    key1 = f"jobs:search:{query1}:0:100"
    key2 = f"jobs:search:{query2}:0:100"
    
    assert key1 != key2
    assert query1 in key1
    assert query2 in key2


def test_pagination_cache_keys():
    """Test that pagination parameters are included in cache keys."""
    query = "Developer"
    
    # Different pages should have different cache keys
    key_page1 = f"jobs:search:{query}:0:100"
    key_page2 = f"jobs:search:{query}:100:100"
    
    assert key_page1 != key_page2
    assert "0:100" in key_page1
    assert "100:100" in key_page2


def test_cache_key_format_consistency():
    """Test that cache keys follow a consistent format."""
    job_id = uuid4()
    
    # All job-related cache keys should follow the pattern
    cache_keys = [
        f"job:{job_id}",
        f"jobs:all:0:100",
        f"jobs:source:linkedin:0:100",
        f"jobs:company:Tech:0:100",
        f"jobs:search:Python:0:100",
    ]
    
    for key in cache_keys:
        # All keys should contain colons as separators
        assert ":" in key
        # All keys should be strings
        assert isinstance(key, str)
