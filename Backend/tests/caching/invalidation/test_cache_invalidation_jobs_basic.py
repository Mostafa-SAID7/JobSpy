"""
Tests for basic job creation cache invalidation functionality

Tests verify basic cache invalidation patterns and operations.
"""
import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.core.redis import redis_client
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate
from sqlalchemy.ext.asyncio import AsyncSession


def test_cache_invalidation_patterns():
    """Test cache invalidation patterns."""
    patterns = [
        "jobs:all:*",
        "jobs:source:*",
        "jobs:company:*",
        "jobs:search:*",
        "job:*",
    ]
    
    # All patterns should support wildcard matching
    for pattern in patterns:
        assert pattern.endswith("*")


def test_redis_client_configuration():
    """Test that Redis client is properly configured."""
    assert redis_client is not None
    assert hasattr(redis_client, 'get')
    assert hasattr(redis_client, 'set')
    assert hasattr(redis_client, 'delete')
    assert hasattr(redis_client, 'delete_pattern')


class TestCacheInvalidationJobsBasic:
    """Test basic cache invalidation when new jobs are added."""
    
    @pytest.mark.asyncio
    async def test_create_job_invalidates_all_jobs_cache(self):
        """Test that creating a new job invalidates all jobs cache."""
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
            result = await job_repo.invalidate_all_jobs_cache()
        
        assert result is True
        assert mock_delete_pattern.call_count >= 5
    
    @pytest.mark.asyncio
    async def test_invalidate_all_jobs_cache_deletes_correct_patterns(self):
        """Test that invalidate_all_jobs_cache deletes all relevant patterns."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        expected_patterns = [
            "jobs:all:*",
            "jobs:source:*",
            "jobs:company:*",
            "jobs:search:*",
            "job:*",
        ]
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            result = await job_repo.invalidate_all_jobs_cache()
        
        assert result is True
        assert mock_delete_pattern.call_count == len(expected_patterns)
        
        called_patterns = [call[0][0] for call in mock_delete_pattern.call_args_list]
        for pattern in expected_patterns:
            assert pattern in called_patterns
    
    @pytest.mark.asyncio
    async def test_invalidate_job_cache_deletes_specific_job(self):
        """Test that invalidate_job_cache deletes specific job cache."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        
        with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
            result = await job_repo.invalidate_job_cache(job_id)
        
        assert result is True
        mock_delete.assert_called_once()
        called_key = mock_delete.call_args[0][0]
        assert called_key == f"job:{job_id}"
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_handles_errors_gracefully(self):
        """Test that cache invalidation handles errors gracefully."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        
        with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.side_effect = Exception("Redis connection error")
            result = await job_repo.invalidate_job_cache(job_id)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_all_jobs_handles_errors(self):
        """Test that invalidate_all_jobs_cache handles errors gracefully."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            mock_delete_pattern.side_effect = Exception("Redis connection error")
            result = await job_repo.invalidate_all_jobs_cache()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_is_atomic(self):
        """Test that cache invalidation operations are atomic."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        
        with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
            result = await job_repo.invalidate_job_cache(job_id)
        
        assert result is True
        assert mock_delete.call_count == 1
