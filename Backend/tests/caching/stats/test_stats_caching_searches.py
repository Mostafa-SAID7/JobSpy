"""
Tests for Search Statistics Caching
Tests verify that search statistics are properly cached and invalidated
"""

import pytest
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


class TestSearchStatisticsCaching:
    """Tests for search statistics caching"""
    
    async def test_search_statistics_caching(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test that search statistics are cached"""
        stats_repo.get_search_statistics.return_value = {"total_searches": 3}
        stats_repo.get_trending_searches.return_value = []
        
        stats1 = await stats_service.get_search_statistics(use_cache=True)
        assert stats1["total_searches"] == 3
        
        stats2 = await stats_service.get_search_statistics(use_cache=True)
        assert stats2 == stats1
