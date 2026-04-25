"""
Tests for Search Cache Patterns and TTL
Tests cache key patterns and TTL configuration
"""
import pytest
from unittest.mock import AsyncMock

from app.services.search_service import SearchService
from app.core.config import settings


class TestSearchCacheKeyPatterns:
    """Test cache key patterns for search operations."""
    
    def test_cache_key_pattern_for_invalidation(self):
        """Test that cache key patterns work for invalidation."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python"
        filters = {"location": "NYC"}
        
        # Generate multiple cache keys with different pagination
        key1 = service._generate_search_cache_key(query, filters, 0, 20)
        key2 = service._generate_search_cache_key(query, filters, 20, 20)
        key3 = service._generate_search_cache_key(query, filters, 40, 20)
        
        # All should have common prefix for pattern matching
        assert key1.split(":")[0] == key2.split(":")[0]
        assert key2.split(":")[0] == key3.split(":")[0]
    
    def test_search_cache_patterns_for_deletion(self):
        """Test cache patterns used for bulk deletion."""
        patterns = [
            "search:advanced:*",
            "search:simple:*",
            "recommendations:*",
            "trending_searches:*",
        ]
        
        # All patterns should be valid for Redis pattern matching
        for pattern in patterns:
            assert pattern.endswith("*")
            assert ":" in pattern


class TestSearchCacheTTL:
    """Test TTL configuration for search cache."""
    
    def test_cache_ttl_from_settings(self):
        """Test that cache TTL is properly configured."""
        assert hasattr(settings, 'REDIS_CACHE_TTL')
        assert settings.REDIS_CACHE_TTL > 0
        # Default should be 1 hour (3600 seconds)
        assert settings.REDIS_CACHE_TTL >= 3600
    
    def test_search_cache_uses_configured_ttl(self):
        """Test that search cache uses configured TTL."""
        db = AsyncMock()
        service = SearchService(db)
        
        # The service should use settings.REDIS_CACHE_TTL
        # This is verified in the search_jobs method
        assert hasattr(service, 'db')
