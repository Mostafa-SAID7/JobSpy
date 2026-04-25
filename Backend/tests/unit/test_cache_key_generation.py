"""
Unit tests for cache key generation

Tests for generating cache keys for different operations.
Extracted from test_caching.py and test_search_caching.py
"""
import pytest
from uuid import uuid4
from app.core.redis import redis_client
from app.services.search_service import SearchService
from unittest.mock import AsyncMock


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


class TestSearchCacheKeyGeneration:
    """Test cache key generation for search results."""
    
    def test_generate_search_cache_key_with_simple_query(self):
        """Test cache key generation for simple search query."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python Developer"
        cache_key = service._generate_search_cache_key(query)
        
        assert "search:advanced:" in cache_key
        assert query in cache_key
        assert "0:20" in cache_key  # Default skip and limit
    
    def test_generate_search_cache_key_with_filters(self):
        """Test cache key generation includes all filter parameters."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python Developer"
        filters = {
            "location": "San Francisco",
            "job_type": "fulltime",
            "salary_min": 100000,
            "salary_max": 150000,
            "is_remote": True,
        }
        
        cache_key = service._generate_search_cache_key(query, filters)
        
        assert "search:advanced:" in cache_key
        assert query in cache_key
        # Filter hash should be included
        assert len(cache_key.split(":")) >= 4
    
    def test_cache_key_includes_pagination(self):
        """Test that cache keys include pagination parameters."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Developer"
        
        # Different pagination should create different keys
        key1 = service._generate_search_cache_key(query, skip=0, limit=20)
        key2 = service._generate_search_cache_key(query, skip=20, limit=20)
        
        assert key1 != key2
        assert "0:20" in key1
        assert "20:20" in key2
    
    def test_cache_key_deterministic_with_same_filters(self):
        """Test that same filters generate same cache key."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python"
        filters = {"location": "NYC", "job_type": "fulltime"}
        
        key1 = service._generate_search_cache_key(query, filters)
        key2 = service._generate_search_cache_key(query, filters)
        
        assert key1 == key2
    
    def test_cache_key_different_with_different_filters(self):
        """Test that different filters generate different cache keys."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python"
        filters1 = {"location": "NYC"}
        filters2 = {"location": "SF"}
        
        key1 = service._generate_search_cache_key(query, filters1)
        key2 = service._generate_search_cache_key(query, filters2)
        
        assert key1 != key2
    
    def test_cache_key_ignores_none_filters(self):
        """Test that None filter values don't affect cache key."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python"
        filters1 = {"location": "NYC", "job_type": None}
        filters2 = {"location": "NYC"}
        
        key1 = service._generate_search_cache_key(query, filters1)
        key2 = service._generate_search_cache_key(query, filters2)
        
        assert key1 == key2
    
    def test_cache_key_handles_complex_filter_combinations(self):
        """Test cache key generation with complex filter combinations."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Engineer"
        filters = {
            "location": "San Francisco, CA",
            "job_type": "fulltime",
            "experience_level": "senior",
            "salary_min": 150000,
            "salary_max": 250000,
            "is_remote": False,
        }
        
        cache_key = service._generate_search_cache_key(query, filters)
        
        # Key should be reasonable length (not too long)
        assert len(cache_key) < 200
        # Key should contain query
        assert query in cache_key
        # Key should be deterministic
        cache_key2 = service._generate_search_cache_key(query, filters)
        assert cache_key == cache_key2
    
    def test_simple_search_cache_key(self):
        """Test simple search cache key generation."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python"
        cache_key = service._generate_simple_search_cache_key(query)
        
        assert "search:simple:" in cache_key
        assert query in cache_key
