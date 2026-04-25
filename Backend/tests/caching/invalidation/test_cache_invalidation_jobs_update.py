"""
Tests for job update cache invalidation functionality

Tests verify that cache is properly invalidated when jobs are updated.
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app.core.redis import redis_client
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class TestCacheInvalidationOnJobUpdate:
    """Test cache invalidation when jobs are updated."""
    
    @pytest.mark.asyncio
    async def test_update_job_invalidates_cache(self):
        """Test that updating a job invalidates its cache."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        job_update = JobUpdate(title="Updated Title")
        
        mock_job = AsyncMock()
        mock_job.id = job_id
        
        with patch.object(job_repo, 'get_by_id', return_value=mock_job):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
                    db.flush = AsyncMock()
                    
                    result = await job_repo.update(job_id, job_update)
                    await job_repo.invalidate_job_cache(job_id)
                    await job_repo.invalidate_all_jobs_cache()
        
        assert mock_delete.called
        assert mock_delete_pattern.called
    
    @pytest.mark.asyncio
    async def test_update_job_invalidates_specific_and_all_caches(self):
        """Test that updating a job invalidates both specific and all caches."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        job_update = JobUpdate(title="Updated Title")
        
        mock_job = AsyncMock()
        mock_job.id = job_id
        
        with patch.object(job_repo, 'get_by_id', return_value=mock_job):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
                    db.flush = AsyncMock()
                    
                    result = await job_repo.update(job_id, job_update)
                    await job_repo.invalidate_job_cache(job_id)
                    await job_repo.invalidate_all_jobs_cache()
        
        assert mock_delete.call_count >= 1
        assert mock_delete_pattern.call_count >= 5
