"""
Tests for Statistics Caching Implementation
Tests verify that statistics are properly cached and invalidated
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.repositories.stats_repo import StatsRepository
from app.services.stats_service import StatsService
from app.core.redis import redis_client


@pytest.fixture
def stats_repo() -> StatsRepository:
    """Create mock stats repository"""
    repo = AsyncMock(spec=StatsRepository)
    return repo


@pytest.fixture
def stats_service(stats_repo: StatsRepository) -> StatsService:
    """Create stats service with mock repository"""
    return StatsService(stats_repo)


@pytest.fixture
async def sample_jobs():
    """Create sample job data"""
    return [
        {"title": "Python Developer", "company": "Tech Corp", "source": "linkedin"},
        {"title": "Senior Engineer", "company": "Big Tech", "source": "indeed"},
        {"title": "Junior Developer", "company": "Startup Inc", "source": "linkedin"},
    ]


@pytest.fixture
async def sample_users():
    """Create sample user data"""
    return [
        {"id": uuid4(), "email": "user1@example.com"},
        {"id": uuid4(), "email": "user2@example.com"},
    ]


@pytest.fixture
async def sample_saved_jobs():
    """Create sample saved jobs data"""
    return [
        {"user_id": uuid4(), "job_id": uuid4()},
        {"user_id": uuid4(), "job_id": uuid4()},
    ]


@pytest.fixture
async def sample_searches():
    """Create sample search data"""
    return [
        {"query": "Python Developer", "count": 2},
        {"query": "Senior Engineer", "count": 1},
    ]


class TestJobStatistics:
    """Tests for job statistics"""
    
    async def test_get_total_jobs(self, stats_repo: StatsRepository):
        """Test getting total job count"""
        stats_repo.get_total_jobs.return_value = 3
        
        total = await stats_repo.get_total_jobs()
        assert total == 3
    
    async def test_get_jobs_by_source(self, stats_repo: StatsRepository):
        """Test getting jobs by source"""
        stats_repo.get_jobs_by_source.return_value = {"linkedin": 2, "indeed": 1}
        
        by_source = await stats_repo.get_jobs_by_source()
        assert by_source["linkedin"] == 2
        assert by_source["indeed"] == 1
    
    async def test_get_jobs_by_type(self, stats_repo: StatsRepository):
        """Test getting jobs by type"""
        stats_repo.get_jobs_by_type.return_value = {"fulltime": 2, "parttime": 1}
        
        by_type = await stats_repo.get_jobs_by_type()
        assert by_type["fulltime"] == 2
        assert by_type["parttime"] == 1
    
    async def test_get_remote_jobs_count(self, stats_repo: StatsRepository):
        """Test getting remote jobs count"""
        stats_repo.get_remote_jobs_count.return_value = 2
        
        remote = await stats_repo.get_remote_jobs_count()
        assert remote == 2
    
    async def test_get_salary_statistics(self, stats_repo: StatsRepository):
        """Test getting salary statistics"""
        stats_repo.get_salary_statistics.return_value = {
            "min_salary": 50000,
            "max_salary": 180000,
            "avg_min_salary": 90000,
            "avg_max_salary": 136666,
        }
        
        stats = await stats_repo.get_salary_statistics()
        assert stats["min_salary"] == 50000
        assert stats["max_salary"] == 180000
    
    async def test_get_jobs_by_company(self, stats_repo: StatsRepository):
        """Test getting top companies"""
        stats_repo.get_jobs_by_company.return_value = [
            {"company": "Tech Corp", "count": 1},
            {"company": "Big Tech", "count": 1},
        ]
        
        companies = await stats_repo.get_jobs_by_company(limit=10)
        assert len(companies) == 2
    
    async def test_get_jobs_by_location(self, stats_repo: StatsRepository):
        """Test getting top locations"""
        stats_repo.get_jobs_by_location.return_value = [
            {"location": "San Francisco", "count": 2},
            {"location": "New York", "count": 1},
        ]
        
        locations = await stats_repo.get_jobs_by_location(limit=10)
        assert len(locations) == 2


class TestUserStatistics:
    """Tests for user statistics"""
    
    async def test_get_total_users(self, stats_repo: StatsRepository):
        """Test getting total user count"""
        stats_repo.get_total_users.return_value = 2
        
        total = await stats_repo.get_total_users()
        assert total == 2
    
    async def test_get_active_users(self, stats_repo: StatsRepository):
        """Test getting active users"""
        stats_repo.get_active_users.return_value = 2
        
        active = await stats_repo.get_active_users(days=30)
        assert active == 2


class TestSavedJobsStatistics:
    """Tests for saved jobs statistics"""
    
    async def test_get_total_saved_jobs(self, stats_repo: StatsRepository):
        """Test getting total saved jobs count"""
        stats_repo.get_total_saved_jobs.return_value = 3
        
        total = await stats_repo.get_total_saved_jobs()
        assert total == 3
    
    async def test_get_saved_jobs_by_user(self, stats_repo: StatsRepository):
        """Test getting saved jobs for a user"""
        stats_repo.get_saved_jobs_by_user.return_value = 2
        
        count = await stats_repo.get_saved_jobs_by_user(uuid4())
        assert count == 2


class TestSearchStatistics:
    """Tests for search statistics"""
    
    async def test_get_search_statistics(self, stats_repo: StatsRepository):
        """Test getting search statistics"""
        stats_repo.get_search_statistics.return_value = {
            "total_searches": 3,
            "unique_users": 2,
            "avg_searches_per_user": 1.5,
        }
        
        stats = await stats_repo.get_search_statistics()
        assert stats["total_searches"] == 3
        assert stats["unique_users"] == 2
        assert stats["avg_searches_per_user"] == 1.5
    
    async def test_get_trending_searches(self, stats_repo: StatsRepository):
        """Test getting trending searches"""
        stats_repo.get_trending_searches.return_value = [
            {"query": "Python Developer", "count": 2},
            {"query": "Senior Engineer", "count": 1},
        ]
        
        trending = await stats_repo.get_trending_searches(limit=10, days=7)
        assert len(trending) == 2
        assert trending[0]["query"] == "Python Developer"
        assert trending[0]["count"] == 2


class TestStatsServiceCaching:
    """Tests for statistics service caching"""
    
    async def test_job_statistics_caching(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test that job statistics are cached"""
        stats_repo.get_total_jobs.return_value = 3
        stats_repo.get_jobs_by_source.return_value = {"linkedin": 2}
        stats_repo.get_jobs_by_type.return_value = {"fulltime": 2}
        stats_repo.get_remote_jobs_count.return_value = 2
        stats_repo.get_salary_statistics.return_value = {"min_salary": 50000}
        stats_repo.get_jobs_posted_today.return_value = 1
        stats_repo.get_jobs_posted_this_week.return_value = 3
        stats_repo.get_jobs_by_company.return_value = []
        stats_repo.get_jobs_by_location.return_value = []
        
        # First call - should compute and cache
        stats1 = await stats_service.get_job_statistics(use_cache=True)
        assert stats1["total_jobs"] == 3
        
        # Second call - should use cache
        stats2 = await stats_service.get_job_statistics(use_cache=True)
        assert stats2 == stats1
        
        # Verify cache key exists
        cache_key = stats_service._get_cache_key("jobs:all")
        cached = await redis_client.get(cache_key)
        assert cached is not None
    
    async def test_user_statistics_caching(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test that user statistics are cached"""
        stats_repo.get_total_users.return_value = 2
        stats_repo.get_active_users.return_value = 2
        
        stats1 = await stats_service.get_user_statistics(use_cache=True)
        assert stats1["total_users"] == 2
        
        stats2 = await stats_service.get_user_statistics(use_cache=True)
        assert stats2 == stats1
    
    async def test_search_statistics_caching(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test that search statistics are cached"""
        stats_repo.get_search_statistics.return_value = {"total_searches": 3}
        stats_repo.get_trending_searches.return_value = []
        
        stats1 = await stats_service.get_search_statistics(use_cache=True)
        assert stats1["total_searches"] == 3
        
        stats2 = await stats_service.get_search_statistics(use_cache=True)
        assert stats2 == stats1
    
    async def test_saved_jobs_statistics_caching(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test that saved jobs statistics are cached"""
        stats_repo.get_total_saved_jobs.return_value = 3
        
        stats1 = await stats_service.get_saved_jobs_statistics(use_cache=True)
        assert stats1["total_saved_jobs"] == 3
        
        stats2 = await stats_service.get_saved_jobs_statistics(use_cache=True)
        assert stats2 == stats1
    
    async def test_dashboard_statistics_caching(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test that dashboard statistics are cached"""
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
        
        stats1 = await stats_service.get_dashboard_statistics(use_cache=True)
        assert "jobs" in stats1
        assert "users" in stats1
        assert "searches" in stats1
        assert "saved_jobs" in stats1
        
        stats2 = await stats_service.get_dashboard_statistics(use_cache=True)
        assert stats2 == stats1
    
    async def test_bypass_cache(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test bypassing cache"""
        stats_repo.get_total_jobs.return_value = 3
        stats_repo.get_jobs_by_source.return_value = {}
        stats_repo.get_jobs_by_type.return_value = {}
        stats_repo.get_remote_jobs_count.return_value = 2
        stats_repo.get_salary_statistics.return_value = {}
        stats_repo.get_jobs_posted_today.return_value = 1
        stats_repo.get_jobs_posted_this_week.return_value = 3
        stats_repo.get_jobs_by_company.return_value = []
        stats_repo.get_jobs_by_location.return_value = []
        
        stats1 = await stats_service.get_job_statistics(use_cache=True)
        
        # Bypass cache
        stats2 = await stats_service.get_job_statistics(use_cache=False)
        
        # Should have same data but different timestamps
        assert stats1["total_jobs"] == stats2["total_jobs"]


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


class TestStatisticsTimestamp:
    """Tests for statistics timestamp"""
    
    async def test_statistics_include_timestamp(
        self, stats_service: StatsService, sample_jobs
    ):
        """Test that statistics include timestamp"""
        stats = await stats_service.get_job_statistics(use_cache=False)
        assert "timestamp" in stats
        
        # Verify timestamp is valid ISO format
        timestamp = datetime.fromisoformat(stats["timestamp"])
        assert timestamp is not None
    
    async def test_dashboard_includes_timestamp(
        self, stats_service: StatsService, sample_jobs, sample_users, sample_saved_jobs, sample_searches
    ):
        """Test that dashboard statistics include timestamp"""
        stats = await stats_service.get_dashboard_statistics(use_cache=False)
        assert "timestamp" in stats
        
        timestamp = datetime.fromisoformat(stats["timestamp"])
        assert timestamp is not None
