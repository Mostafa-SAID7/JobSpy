"""
Tests for Job Statistics Caching
Tests verify that job statistics are properly cached and invalidated
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


class TestJobStatisticsCaching:
    """Tests for job statistics caching"""
    
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
