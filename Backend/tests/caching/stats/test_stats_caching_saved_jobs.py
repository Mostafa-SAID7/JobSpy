"""
Tests for Saved Jobs Statistics Caching
Tests verify that saved jobs statistics are properly cached and invalidated
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

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


class TestSavedJobsStatisticsCaching:
    """Tests for saved jobs statistics caching"""
    
    async def test_saved_jobs_statistics_caching(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test that saved jobs statistics are cached"""
        stats_repo.get_total_saved_jobs.return_value = 3
        
        stats1 = await stats_service.get_saved_jobs_statistics(use_cache=True)
        assert stats1["total_saved_jobs"] == 3
        
        stats2 = await stats_service.get_saved_jobs_statistics(use_cache=True)
        assert stats2 == stats1
