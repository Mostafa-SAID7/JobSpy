"""
Advanced cache invalidation tests for job creation

Tests verify advanced cache invalidation scenarios including service integration,
logging, and complex invalidation patterns.
"""
import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.core.redis import redis_client
from app.repositories.job_repo import JobRepository
from app.services.search_service import SearchService
from app.services.stats_service import StatsService
from app.schemas.job import JobCreate
from sqlalchemy.ext.asyncio import AsyncSession


class TestCacheInvalidationJobsAdvanced:
    """Advanced cache invalidation tests for job creation."""
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_on_job_creation_with_search_service(self):
        """Test that job creation invalidates both job and search caches."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        search_service = SearchService(db)
        
        job_create = JobCreate(
            title="Python Developer",
            company="Tech Corp",
            location="San Francisco",
            source_url="https://example.com/job/123",
            source="linkedin",
            source_job_id="123",
            description="A great job",
            salary_min=100000,
            salary_max=150000,
            job_type="fulltime",
            is_remote=False,
            posted_date=datetime.utcnow(),
        )
        
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            job = await job_repo.create(job_create)
            job_result = await job_repo.invalidate_all_jobs_cache()
            search_result = await search_service.invalidate_all_search_cache()
        
        assert job_result is True
        assert search_result is True
        assert mock_delete_pattern.call_count >= 9
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_on_job_creation_with_stats_service(self):
        """Test that job creation invalidates job statistics cache."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        stats_repo = AsyncMock()
        stats_service = StatsService(stats_repo)
        
        job_create = JobCreate(
            title="Python Developer",
            company="Tech Corp",
            location="San Francisco",
            source_url="https://example.com/job/123",
            source="linkedin",
            source_job_id="123",
            description="A great job",
            salary_min=100000,
            salary_max=150000,
            job_type="fulltime",
            is_remote=False,
            posted_date=datetime.utcnow(),
        )
        
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock):
                job = await job_repo.create(job_create)
                result = await stats_service.invalidate_job_statistics()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_smart_cache_invalidation_by_source(self):
        """Test smart cache invalidation that only invalidates relevant entries."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_create = JobCreate(
            title="Python Developer",
            company="Tech Corp",
            location="San Francisco",
            source_url="https://example.com/job/123",
            source="linkedin",
            source_job_id="123",
            description="A great job",
            salary_min=100000,
            salary_max=150000,
            job_type="fulltime",
            is_remote=False,
            posted_date=datetime.utcnow(),
        )
        
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            job = await job_repo.create(job_create)
            pattern = f"jobs:source:{job_create.source}:*"
            await redis_client.delete_pattern(pattern)
        
        mock_delete_pattern.assert_called()
    
    @pytest.mark.asyncio
    async def test_multiple_job_creations_invalidate_cache_each_time(self):
        """Test that each job creation invalidates cache."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            for i in range(3):
                job_create = JobCreate(
                    title=f"Job {i}",
                    company="Tech Corp",
                    location="San Francisco",
                    source_url=f"https://example.com/job/{i}",
                    source="linkedin",
                    source_job_id=str(i),
                    description="A great job",
                    salary_min=100000,
                    salary_max=150000,
                    job_type="fulltime",
                    is_remote=False,
                    posted_date=datetime.utcnow(),
                )
                
                job = await job_repo.create(job_create)
                await job_repo.invalidate_all_jobs_cache()
        
        assert mock_delete_pattern.call_count >= 15
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_patterns_are_comprehensive(self):
        """Test that cache invalidation patterns cover all job-related caches."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        patterns = [
            "jobs:all:*",
            "jobs:source:*",
            "jobs:company:*",
            "jobs:search:*",
            "job:*",
        ]
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            await job_repo.invalidate_all_jobs_cache()
        
        called_patterns = [call[0][0] for call in mock_delete_pattern.call_args_list]
        for pattern in patterns:
            assert pattern in called_patterns
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_logging(self):
        """Test that cache invalidation is properly logged."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        
        with patch.object(redis_client, 'delete', new_callable=AsyncMock):
            with patch('app.repositories.job_repo.logger') as mock_logger:
                result = await job_repo.invalidate_job_cache(job_id)
        
        assert result is True
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_all_jobs_logging(self):
        """Test that all jobs cache invalidation is properly logged."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock):
            with patch('app.repositories.job_repo.logger') as mock_logger:
                result = await job_repo.invalidate_all_jobs_cache()
        
        assert result is True
        mock_logger.info.assert_called()
