"""
Tests for Dashboard Statistics Caching
Tests verify that dashboard statistics are properly cached and timestamped
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from app.repositories.stats_repo import StatsRepository
from app.services.stats_service import StatsService


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
    from uuid import uuid4
    return [
        {"id": uuid4(), "email": "user1@example.com"},
        {"id": uuid4(), "email": "user2@example.com"},
    ]


@pytest.fixture
async def sample_saved_jobs():
    """Create sample saved jobs data"""
    from uuid import uuid4
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


class TestStatsServiceCaching:
    """Tests for statistics service caching"""
    
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
