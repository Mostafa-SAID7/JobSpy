"""
Tests for Search Cache Key Generation
Tests cache key generation for search results
"""
import pytest
from unittest.mock import AsyncMock

from app.services.search_service import SearchService


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
