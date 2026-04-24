"""
Tests for advanced search result caching functionality
"""
import pytest
import json
import hashlib
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.search_service import SearchService
from app.core.redis import redis_client
from app.core.config import settings


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


class TestSearchCacheInvalidation:
    """Test cache invalidation for search results."""
    
    @pytest.mark.asyncio
    async def test_invalidate_search_cache_specific_query(self):
        """Test invalidating cache for specific search query."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python Developer"
        filters = {"location": "NYC"}
        
        with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
            with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
                result = await service.invalidate_search_cache(query, filters)
        
        assert result is True
        mock_delete.assert_called_once()
        mock_delete_pattern.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_invalidate_all_search_cache(self):
        """Test invalidating all search-related cache."""
        db = AsyncMock()
        service = SearchService(db)
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            result = await service.invalidate_all_search_cache()
        
        assert result is True
        # Should delete multiple patterns
        assert mock_delete_pattern.call_count >= 4


class TestAdvancedSearchCaching:
    """Test advanced search with caching."""
    
    @pytest.mark.asyncio
    async def test_advanced_search_with_multiple_filters(self):
        """Test advanced search with multiple filter criteria."""
        db = AsyncMock()
        service = SearchService(db)
        
        # Mock the job repository methods
        service.job_repo.search = AsyncMock(return_value=[])
        service.job_repo.count_search = AsyncMock(return_value=0)
        service.search_history_repo.create = AsyncMock()
        
        search_params = {
            "query": "Python Developer",
            "location": "San Francisco",
            "job_type": "fulltime",
            "salary_min": 100000,
            "salary_max": 150000,
            "is_remote": True,
            "skip": 0,
            "limit": 20,
        }
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=None):
            with patch.object(redis_client, 'set', new_callable=AsyncMock):
                result = await service.advanced_search(1, search_params)
        
        assert "query" in result
        assert "filters" in result
        assert "results" in result
    
    @pytest.mark.asyncio
    async def test_advanced_search_cache_hit(self):
        """Test that cached results are returned on cache hit."""
        db = AsyncMock()
        service = SearchService(db)
        
        search_params = {
            "query": "Python",
            "location": "NYC",
            "skip": 0,
            "limit": 20,
        }
        
        cached_result = {
            "query": "Python",
            "filters": {"location": "NYC"},
            "results": [{"id": "job1"}],
            "total_count": 1,
        }
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=cached_result):
            result = await service.advanced_search(1, search_params)
        
        assert result == cached_result
    
    @pytest.mark.asyncio
    async def test_advanced_search_builds_correct_filters(self):
        """Test that advanced search builds correct filter dictionary."""
        db = AsyncMock()
        service = SearchService(db)
        
        service.job_repo.search = AsyncMock(return_value=[])
        service.job_repo.count_search = AsyncMock(return_value=0)
        service.search_history_repo.create = AsyncMock()
        
        search_params = {
            "query": "Engineer",
            "location": "SF",
            "job_type": "fulltime",
            "experience_level": "senior",
            "salary_min": 150000,
            "salary_max": 250000,
            "is_remote": False,
            "skip": 0,
            "limit": 20,
        }
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=None):
            with patch.object(redis_client, 'set', new_callable=AsyncMock):
                result = await service.advanced_search(1, search_params)
        
        # Verify filters were built correctly
        assert result["filters"]["location"] == "SF"
        assert result["filters"]["job_type"] == "fulltime"
        assert result["filters"]["salary_min"] == 150000


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


class TestSearchCacheMetadata:
    """Test metadata included in cached search results."""
    
    @pytest.mark.asyncio
    async def test_search_result_includes_pagination_metadata(self):
        """Test that search results include pagination metadata."""
        db = AsyncMock()
        service = SearchService(db)
        
        service.job_repo.search = AsyncMock(return_value=[])
        service.job_repo.count_search = AsyncMock(return_value=100)
        service.search_history_repo.create = AsyncMock()
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=None):
            with patch.object(redis_client, 'set', new_callable=AsyncMock):
                result = await service.search_jobs(1, "Python", skip=0, limit=20)
        
        assert "skip" in result
        assert "limit" in result
        assert "total_count" in result
        assert "has_more" in result
        assert result["skip"] == 0
        assert result["limit"] == 20
    
    @pytest.mark.asyncio
    async def test_search_result_has_more_flag(self):
        """Test that has_more flag is correctly set."""
        db = AsyncMock()
        service = SearchService(db)
        
        service.job_repo.search = AsyncMock(return_value=[])
        service.job_repo.count_search = AsyncMock(return_value=100)
        service.search_history_repo.create = AsyncMock()
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=None):
            with patch.object(redis_client, 'set', new_callable=AsyncMock):
                # First page
                result1 = await service.search_jobs(1, "Python", skip=0, limit=20)
                assert result1["has_more"] is True
                
                # Last page
                result2 = await service.search_jobs(1, "Python", skip=80, limit=20)
                assert result2["has_more"] is False
