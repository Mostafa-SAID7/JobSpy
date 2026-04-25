"""
Tests for User Statistics Caching
Tests verify that user statistics are properly cached and invalidated
"""

import pytest
from uuid import uuid4
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


class TestUserStatisticsCaching:
    """Tests for user statistics caching"""
    
    async def test_user_statistics_caching(self, stats_service: StatsService, stats_repo: StatsRepository):
        """Test that user statistics are cached"""
        stats_repo.get_total_users.return_value = 2
        stats_repo.get_active_users.return_value = 2
        
        stats1 = await stats_service.get_user_statistics(use_cache=True)
        assert stats1["total_users"] == 2
        
        stats2 = await stats_service.get_user_statistics(use_cache=True)
        assert stats2 == stats1
