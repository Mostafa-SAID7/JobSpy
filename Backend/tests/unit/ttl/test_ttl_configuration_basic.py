"""
TTL Configuration Tests - Basic Configuration
Verifies that TTL configuration is working correctly for different cache types
"""

import pytest
from app.core.redis import redis_client
from app.core.config import settings


class TestTTLConfiguration:
    """Test TTL configuration for different cache types"""
    
    @pytest.mark.asyncio
    async def test_cache_ttl_jobs_configuration(self):
        """Verify jobs cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("jobs")
        assert ttl == settings.CACHE_TTL_JOBS
        assert ttl == 3600  # 1 hour
    
    @pytest.mark.asyncio
    async def test_cache_ttl_search_results_configuration(self):
        """Verify search results cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("search_results")
        assert ttl == settings.CACHE_TTL_SEARCH_RESULTS
        assert ttl == 1800  # 30 minutes
    
    @pytest.mark.asyncio
    async def test_cache_ttl_statistics_configuration(self):
        """Verify statistics cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("statistics")
        assert ttl == settings.CACHE_TTL_STATISTICS
        assert ttl == 3600  # 1 hour
    
    @pytest.mark.asyncio
    async def test_cache_ttl_users_configuration(self):
        """Verify users cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("users")
        assert ttl == settings.CACHE_TTL_USERS
        assert ttl == 86400  # 24 hours
    
    @pytest.mark.asyncio
    async def test_cache_ttl_search_history_configuration(self):
        """Verify search history cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("search_history")
        assert ttl == settings.CACHE_TTL_SEARCH_HISTORY
        assert ttl == 3600  # 1 hour
    
    @pytest.mark.asyncio
    async def test_cache_ttl_recommendations_configuration(self):
        """Verify recommendations cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("recommendations")
        assert ttl == settings.CACHE_TTL_RECOMMENDATIONS
        assert ttl == 21600  # 6 hours
    
    @pytest.mark.asyncio
    async def test_cache_ttl_trending_searches_configuration(self):
        """Verify trending searches cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("trending_searches")
        assert ttl == settings.CACHE_TTL_TRENDING_SEARCHES
        assert ttl == 43200  # 12 hours
    
    @pytest.mark.asyncio
    async def test_default_ttl_for_unknown_cache_type(self):
        """Verify default TTL is used for unknown cache types"""
        ttl = redis_client.get_ttl_for_cache_type("unknown_type")
        assert ttl == settings.REDIS_CACHE_TTL
        assert ttl == 3600  # Default 1 hour
