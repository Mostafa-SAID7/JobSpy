"""
Tests for Statistics Cache Invalidation
Tests verify that statistics cache is properly invalidated
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.infrastructure.cache.redis import redis_client
from app.domain.interfaces.repositories import IStatsRepository as StatsRepository
from app.application.services.stats_service import StatsService


@pytest.fixture
def stats_repo() -> StatsRepository:
    """Create mock stats repository"""
    repo = AsyncMock(spec=StatsRepository)
    return repo


@pytest.fixture
def stats_service(stats_repo: StatsRepository) -> StatsService:
    """Create stats service with mock repository"""
    return StatsService(stats_repo)


class TestCacheInvalidation:
    """Tests for cache invalidation"""
    
    async def test_invalidate_job_statistics(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test invalidating job statistics cache"""
        # Setup mocks
        stats_repo.get_total_jobs.return_value = 3
        stats_repo.get_jobs_by_source.return_value = {}
        stats_repo.get_jobs_by_type.return_value = {}
        stats_repo.get_remote_jobs_count.return_value = 2
        stats_repo.get_salary_statistics.return_value = {}
        stats_repo.get_jobs_posted_today.return_value = 1
        stats_repo.get_jobs_posted_this_week.return_value = 3
        stats_repo.get_jobs_by_company.return_value = []
        stats_repo.get_jobs_by_location.return_value = []
        
        # Cache statistics
        await stats_service.get_job_statistics(use_cache=True)
        
        # Verify cache exists
        cache_key = stats_service._get_cache_key("jobs:all")
        cached = await redis_client.get(cache_key)
        assert cached is not None
        
        # Invalidate
        success = await stats_service.invalidate_job_statistics()
        assert success
        
        # Verify cache is gone
        cached = await redis_client.get(cache_key)
        assert cached is None
    
    async def test_invalidate_user_statistics(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test invalidating user statistics cache"""
        stats_repo.get_total_users.return_value = 2
        stats_repo.get_active_users.return_value = 2
        
        await stats_service.get_user_statistics(use_cache=True)
        
        success = await stats_service.invalidate_user_statistics()
        assert success
        
        cache_key = stats_service._get_cache_key("users:all")
        cached = await redis_client.get(cache_key)
        assert cached is None
    
    async def test_invalidate_search_statistics(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test invalidating search statistics cache"""
        stats_repo.get_search_statistics.return_value = {}
        stats_repo.get_trending_searches.return_value = []
        
        await stats_service.get_search_statistics(use_cache=True)
        
        success = await stats_service.invalidate_search_statistics()
        assert success
        
        cache_key = stats_service._get_cache_key("searches:all")
        cached = await redis_client.get(cache_key)
        assert cached is None
    
    async def test_invalidate_saved_jobs_statistics(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test invalidating saved jobs statistics cache"""
        stats_repo.get_total_saved_jobs.return_value = 3
        
        await stats_service.get_saved_jobs_statistics(use_cache=True)
        
        success = await stats_service.invalidate_saved_jobs_statistics()
        assert success
        
        cache_key = stats_service._get_cache_key("saved_jobs:all")
        cached = await redis_client.get(cache_key)
        assert cached is None
    
    async def test_invalidate_all_statistics(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test invalidating all statistics cache"""
        # Setup all mocks
        stats_repo.get_total_jobs.return_value = 3
        stats_repo.get_jobs_by_source.return_value = {}
        stats_repo.get_jobs_by_type.return_value = {}
        stats_repo.get_remote_jobs_count.return_value = 2
        stats_repo.get_salary_statistics.return_value = {}
        stats_repo.get_jobs_posted_today.return_value = 1
        stats_repo.get_jobs_posted_this_week.return_value = 3
        stats_repo.get_jobs_by_company.return_value = []
        stats_repo.get_jobs_by_location.return_value = []
        stats_repo.get_total_users.return_value = 2
        stats_repo.get_active_users.return_value = 2
        stats_repo.get_search_statistics.return_value = {}
        stats_repo.get_trending_searches.return_value = []
        stats_repo.get_total_saved_jobs.return_value = 3
        
        # Cache all statistics
        await stats_service.get_job_statistics(use_cache=True)
        await stats_service.get_user_statistics(use_cache=True)
        await stats_service.get_search_statistics(use_cache=True)
        await stats_service.get_saved_jobs_statistics(use_cache=True)
        
        # Invalidate all
        success = await stats_service.invalidate_all_statistics()
        assert success
        
        # Verify all caches are gone
        assert await redis_client.get(stats_service._get_cache_key("jobs:all")) is None
        assert await redis_client.get(stats_service._get_cache_key("users:all")) is None
        assert await redis_client.get(stats_service._get_cache_key("searches:all")) is None
        assert await redis_client.get(stats_service._get_cache_key("saved_jobs:all")) is None


class TestCacheKeyGeneration:
    """Tests for cache key generation"""
    
    async def test_cache_key_format(self, stats_service: StatsService):
        """Test cache key format"""
        key = stats_service._get_cache_key("jobs:all")
        assert key == "stats:jobs:all"
    
    async def test_cache_key_with_args(self, stats_service: StatsService):
        """Test cache key with arguments"""
        key = stats_service._get_cache_key("user", "123", "searches")
        assert key == "stats:user:123:searches"
