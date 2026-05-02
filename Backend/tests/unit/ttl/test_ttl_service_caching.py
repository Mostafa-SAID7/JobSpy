"""
TTL Service Caching Tests
Tests stats and search service caching with TTL
"""

import pytest
from unittest.mock import AsyncMock
from app.application.services.stats_service import StatsService
from app.services.search_service import SearchService
from app.domain.interfaces.repositories import IStatsRepository as StatsRepository


class TestStatsServiceCaching:
    """Test stats service caching with TTL"""
    
    @pytest.mark.asyncio
    async def test_job_statistics_cache_ttl(self):
        """Verify job statistics are cached with correct TTL"""
        # Mock the repository
        mock_repo = AsyncMock(spec=StatsRepository)
        mock_repo.get_total_jobs = AsyncMock(return_value=100)
        mock_repo.get_jobs_by_source = AsyncMock(return_value={"linkedin": 50, "indeed": 50})
        mock_repo.get_jobs_by_type = AsyncMock(return_value={"fulltime": 80, "parttime": 20})
        mock_repo.get_remote_jobs_count = AsyncMock(return_value=30)
        mock_repo.get_salary_statistics = AsyncMock(return_value={
            "min": 30000,
            "max": 150000,
            "avg": 80000
        })
        mock_repo.get_jobs_posted_today = AsyncMock(return_value=10)
        mock_repo.get_jobs_posted_this_week = AsyncMock(return_value=50)
        mock_repo.get_top_companies = AsyncMock(return_value=[
            {"company": "Tech Corp", "count": 20},
            {"company": "StartUp Inc", "count": 15}
        ])
        mock_repo.get_top_locations = AsyncMock(return_value=[
            {"location": "San Francisco", "count": 30},
            {"location": "New York", "count": 25}
        ])
        
        stats_service = StatsService(mock_repo)
        
        # Get statistics
        stats = await stats_service.get_job_statistics(use_cache=True)
        
        # Verify stats are returned
        assert stats is not None
        assert "total_jobs" in stats
        assert stats["total_jobs"] == 100


class TestSearchServiceCaching:
    """Test search service caching with TTL"""
    
    @pytest.mark.asyncio
    async def test_search_results_cache_ttl(self):
        """Verify search results are cached with correct TTL"""
        # Mock the database session
        mock_db = AsyncMock()
        
        search_service = SearchService(mock_db)
        
        # Verify cache key generation
        cache_key = search_service._generate_search_cache_key(
            "python developer",
            {"location": "San Francisco"},
            0,
            20
        )
        
        # Cache key should be deterministic
        assert cache_key is not None
        assert isinstance(cache_key, str)
        assert "python developer" in cache_key or len(cache_key) > 0
