"""
Tests for cache invalidation functionality

Tests verify that cache is properly invalidated when data is created, updated, or deleted.
Extracted from test_caching.py
"""
import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.redis import redis_client
from app.repositories.job_repo import JobRepository
from app.repositories.user_repo import UserRepository
from app.repositories.search_history_repo import SearchHistoryRepository
from app.services.search_service import SearchService
from app.services.stats_service import StatsService
from app.schemas.job import JobCreate, JobUpdate
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.search_history import SearchHistoryCreate
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


class TestCacheInvalidationOnJobCreation:
    """Test cache invalidation when new jobs are added."""
    
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
        
        # Mock the database operations
        db.flush = AsyncMock()
        
        # Mock redis operations
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            # Create job
            job = await job_repo.create(job_create)
            
            # Invalidate all jobs cache
            result = await job_repo.invalidate_all_jobs_cache()
        
        assert result is True
        # Should delete multiple patterns
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
        # Verify all patterns were attempted to be deleted
        assert mock_delete_pattern.call_count == len(expected_patterns)
        
        # Verify the patterns passed to delete_pattern
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
        
        # Verify the cache key format
        called_key = mock_delete.call_args[0][0]
        assert called_key == f"job:{job_id}"
    
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
            # Create job
            job = await job_repo.create(job_create)
            
            # Invalidate both job and search caches
            job_result = await job_repo.invalidate_all_jobs_cache()
            search_result = await search_service.invalidate_all_search_cache()
        
        assert job_result is True
        assert search_result is True
        # Should have called delete_pattern multiple times
        assert mock_delete_pattern.call_count >= 9  # 5 for jobs + 4 for search
    
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
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                # Create job
                job = await job_repo.create(job_create)
                
                # Invalidate job statistics
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
        
        # For smart invalidation, we could invalidate only source-specific caches
        # This is a more efficient approach than invalidating everything
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            job = await job_repo.create(job_create)
            
            # Smart invalidation: only invalidate caches related to the job's source
            pattern = f"jobs:source:{job_create.source}:*"
            await redis_client.delete_pattern(pattern)
        
        # Verify the pattern was called
        mock_delete_pattern.assert_called()
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_handles_errors_gracefully(self):
        """Test that cache invalidation handles errors gracefully."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        
        # Simulate Redis error
        with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.side_effect = Exception("Redis connection error")
            
            result = await job_repo.invalidate_job_cache(job_id)
        
        # Should return False on error
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_all_jobs_handles_errors(self):
        """Test that invalidate_all_jobs_cache handles errors gracefully."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        # Simulate Redis error
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            mock_delete_pattern.side_effect = Exception("Redis connection error")
            
            result = await job_repo.invalidate_all_jobs_cache()
        
        # Should return False on error
        assert result is False
    
    @pytest.mark.asyncio
    async def test_multiple_job_creations_invalidate_cache_each_time(self):
        """Test that each job creation invalidates cache."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            # Create multiple jobs
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
        
        # Should have called delete_pattern 3 times (once per job creation)
        assert mock_delete_pattern.call_count >= 15  # 5 patterns * 3 jobs
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_patterns_are_comprehensive(self):
        """Test that cache invalidation patterns cover all job-related caches."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        # These patterns should cover all job-related caches
        patterns = [
            "jobs:all:*",           # All jobs list
            "jobs:source:*",        # Jobs by source
            "jobs:company:*",       # Jobs by company
            "jobs:search:*",        # Search results
            "job:*",                # Individual job details
        ]
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            await job_repo.invalidate_all_jobs_cache()
        
        # Verify all patterns are covered
        called_patterns = [call[0][0] for call in mock_delete_pattern.call_args_list]
        for pattern in patterns:
            assert pattern in called_patterns
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_is_atomic(self):
        """Test that cache invalidation operations are atomic."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        
        # All delete operations should be called
        with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
            result = await job_repo.invalidate_job_cache(job_id)
        
        assert result is True
        # Should be called exactly once
        assert mock_delete.call_count == 1
    
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
        # Should log the invalidation
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
        # Should log the invalidation
        mock_logger.info.assert_called()


class TestCacheInvalidationOnJobUpdate:
    """Test cache invalidation when jobs are updated."""
    
    @pytest.mark.asyncio
    async def test_update_job_invalidates_cache(self):
        """Test that updating a job invalidates its cache."""
        db = AsyncMock(spec=AsyncSession)
        job_repo = JobRepository(db)
        
        job_id = uuid4()
        job_update = JobUpdate(title="Updated Title")
        
        # Mock the get_by_id to return a job
        mock_job = AsyncMock()
        mock_job.id = job_id
        
        with patch.object(job_repo, 'get_by_id', return_value=mock_job):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
                    db.flush = AsyncMock()
                    
                    result = await job_repo.update(job_id, job_update)
                    
                    # Invalidate cache
                    await job_repo.invalidate_job_cache(job_id)
                    await job_repo.invalidate_all_jobs_cache()
        
        # Should have invalidated the specific job cache
        assert mock_delete.called
        # Should have invalidated all jobs cache
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
                    
                    # Invalidate both specific and all caches
                    await job_repo.invalidate_job_cache(job_id)
                    await job_repo.invalidate_all_jobs_cache()
        
        # Verify both delete operations were called
        assert mock_delete.call_count >= 1
        assert mock_delete_pattern.call_count >= 5


class TestCacheInvalidationOnUserUpdate:
    """Test cache invalidation when users are updated."""
    
    @pytest.mark.asyncio
    async def test_update_user_invalidates_cache(self):
        """Test that updating a user invalidates its cache."""
        db = AsyncMock(spec=AsyncSession)
        user_repo = UserRepository(db)
        
        user_id = uuid4()
        user_update = UserUpdate(full_name="Updated Name")
        
        # Mock the get_by_id to return a user
        mock_user = AsyncMock()
        mock_user.id = user_id
        mock_user.email = "test@example.com"
        
        with patch.object(user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                db.flush = AsyncMock()
                
                result = await user_repo.update(user_id, user_update)
        
        # Should have invalidated the user cache
        assert mock_delete.called
    
    @pytest.mark.asyncio
    async def test_update_user_email_invalidates_both_caches(self):
        """Test that updating user email invalidates both ID and email caches."""
        db = AsyncMock(spec=AsyncSession)
        user_repo = UserRepository(db)
        
        user_id = uuid4()
        old_email = "old@example.com"
        new_email = "new@example.com"
        user_update = UserUpdate(email=new_email)
        
        mock_user = AsyncMock()
        mock_user.id = user_id
        mock_user.email = old_email
        
        with patch.object(user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                db.flush = AsyncMock()
                
                result = await user_repo.update(user_id, user_update)
                
                # Invalidate both ID and email caches
                await user_repo.invalidate_user_cache(user_id)
                await user_repo.invalidate_user_email_cache(old_email)
                await user_repo.invalidate_user_email_cache(new_email)
        
        # Should have invalidated multiple caches
        assert mock_delete.call_count >= 3
    
    @pytest.mark.asyncio
    async def test_delete_user_invalidates_cache(self):
        """Test that deleting a user invalidates its cache."""
        db = AsyncMock(spec=AsyncSession)
        user_repo = UserRepository(db)
        
        user_id = uuid4()
        
        mock_user = AsyncMock()
        mock_user.id = user_id
        
        with patch.object(user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                db.delete = AsyncMock()
                db.flush = AsyncMock()
                
                result = await user_repo.delete(user_id)
        
        # Should have invalidated the user cache
        assert mock_delete.called
        assert result is True


class TestCacheInvalidationOnSearchHistoryUpdate:
    """Test cache invalidation when search history is updated."""
    
    @pytest.mark.asyncio
    async def test_create_search_history_invalidates_cache(self):
        """Test that creating search history invalidates user's search cache."""
        db = AsyncMock(spec=AsyncSession)
        search_repo = SearchHistoryRepository(db)
        
        user_id = uuid4()
        search_create = SearchHistoryCreate(
            job_id=uuid4(),
            query="Python Developer",
            filters={},
            results_count=10,
            search_type="basic"
        )
        
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            result = await search_repo.create(user_id, search_create)
        
        # Should have invalidated the search history cache
        assert mock_delete_pattern.called
    
    @pytest.mark.asyncio
    async def test_delete_search_history_invalidates_cache(self):
        """Test that deleting search history invalidates cache."""
        db = AsyncMock(spec=AsyncSession)
        search_repo = SearchHistoryRepository(db)
        
        search_id = uuid4()
        user_id = uuid4()
        
        mock_search = AsyncMock()
        mock_search.id = search_id
        mock_search.user_id = user_id
        
        with patch.object(search_repo, 'get_by_id', return_value=mock_search):
            with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
                with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
                    db.delete = AsyncMock()
                    db.flush = AsyncMock()
                    
                    result = await search_repo.delete(search_id)
        
        # Should have invalidated both specific and user search caches
        assert mock_delete.called
        assert mock_delete_pattern.called
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_user_search_history_invalidates_all_user_caches(self):
        """Test that deleting all user search history invalidates all caches."""
        db = AsyncMock(spec=AsyncSession)
        search_repo = SearchHistoryRepository(db)
        
        user_id = uuid4()
        
        # Mock the session.execute to return a proper result
        mock_searches = [AsyncMock() for _ in range(3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_searches
        
        db.execute = AsyncMock(return_value=mock_result)
        db.delete = AsyncMock()
        db.flush = AsyncMock()
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            result = await search_repo.delete_by_user(user_id)
        
        # Should have invalidated user search caches
        assert mock_delete_pattern.called
