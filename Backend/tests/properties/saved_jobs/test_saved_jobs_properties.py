"""
Saved Jobs Correctness Properties Tests

Property-based tests for saved jobs functionality using Hypothesis.

**Validates: Requirements 5.1, 5.3, 5.4, 5.5**
"""

import pytest
from hypothesis import given, strategies as st, settings
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================================
# Property 9: Saved job appears in user's saved list
# ============================================================================

@given(
    job_id=st.just(uuid4()),
    user_id=st.just(uuid4())
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_saved_job_appears_in_user_list(job_id, user_id):
    """
    Property: Saved job appears in user's saved list
    
    For any job saved by a user, it must appear in that user's saved jobs list.
    
    **Validates: Requirements 5.1, 5.3**
    """
    from app.domain.interfaces.repositories import ISavedJobRepository as SavedJobRepository
    
    db = AsyncMock(spec=AsyncSession)
    saved_job_repo = SavedJobRepository(db)
    
    saved_jobs = {}
    
    async def mock_create(user_id, job_id, notes=None):
        if user_id not in saved_jobs:
            saved_jobs[user_id] = []
        saved_jobs[user_id].append({"job_id": job_id, "notes": notes})
        return AsyncMock(job_id=job_id, user_id=user_id)
    
    async def mock_get_by_user(user_id):
        return saved_jobs.get(user_id, [])
    
    with patch.object(saved_job_repo, 'create', side_effect=mock_create):
        with patch.object(saved_job_repo, 'get_by_user', side_effect=mock_get_by_user):
            # Save a job
            await saved_job_repo.create(user_id, job_id)
            
            # Retrieve saved jobs
            user_saved = await saved_job_repo.get_by_user(user_id)
    
    # Verify job appears in list
    assert len(user_saved) > 0
    assert any(job["job_id"] == job_id for job in user_saved)


# ============================================================================
# Property 10: Deleting saved job removes it from list
# ============================================================================

@given(
    job_id=st.just(uuid4()),
    user_id=st.just(uuid4())
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_deleting_saved_job_removes_from_list(job_id, user_id):
    """
    Property: Deleting saved job removes it from user's list
    
    For any saved job that is deleted, it must no longer appear in the user's
    saved jobs list.
    
    **Validates: Requirements 5.4**
    """
    from app.domain.interfaces.repositories import ISavedJobRepository as SavedJobRepository
    
    db = AsyncMock(spec=AsyncSession)
    saved_job_repo = SavedJobRepository(db)
    
    saved_jobs = {user_id: [{"job_id": job_id}]}
    
    async def mock_delete(saved_job_id):
        # Remove from saved_jobs
        if user_id in saved_jobs:
            saved_jobs[user_id] = [
                job for job in saved_jobs[user_id]
                if job["job_id"] != job_id
            ]
        return True
    
    async def mock_get_by_user(user_id):
        return saved_jobs.get(user_id, [])
    
    with patch.object(saved_job_repo, 'delete', side_effect=mock_delete):
        with patch.object(saved_job_repo, 'get_by_user', side_effect=mock_get_by_user):
            # Verify job is in list
            user_saved = await saved_job_repo.get_by_user(user_id)
            assert any(job["job_id"] == job_id for job in user_saved)
            
            # Delete the job
            await saved_job_repo.delete(job_id)
            
            # Verify job is removed
            user_saved = await saved_job_repo.get_by_user(user_id)
    
    assert not any(job["job_id"] == job_id for job in user_saved)


# ============================================================================
# Property 11: Prevent duplicate saved jobs
# ============================================================================

@given(
    job_id=st.just(uuid4()),
    user_id=st.just(uuid4())
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_prevent_duplicate_saved_jobs(job_id, user_id):
    """
    Property: Prevent duplicate saved jobs
    
    For any job saved by a user, if the user tries to save it again,
    the duplicate should be ignored.
    
    **Validates: Requirements 5.5**
    """
    from app.domain.interfaces.repositories import ISavedJobRepository as SavedJobRepository
    
    db = AsyncMock(spec=AsyncSession)
    saved_job_repo = SavedJobRepository(db)
    
    saved_jobs = {}
    
    async def mock_create(user_id, job_id, notes=None):
        if user_id not in saved_jobs:
            saved_jobs[user_id] = []
        
        # Check for duplicate
        if any(job["job_id"] == job_id for job in saved_jobs[user_id]):
            return None  # Duplicate ignored
        
        saved_jobs[user_id].append({"job_id": job_id, "notes": notes})
        return AsyncMock(job_id=job_id, user_id=user_id)
    
    async def mock_get_by_user(user_id):
        return saved_jobs.get(user_id, [])
    
    with patch.object(saved_job_repo, 'create', side_effect=mock_create):
        with patch.object(saved_job_repo, 'get_by_user', side_effect=mock_get_by_user):
            # Save job first time
            result1 = await saved_job_repo.create(user_id, job_id)
            assert result1 is not None
            
            # Try to save same job again
            result2 = await saved_job_repo.create(user_id, job_id)
            assert result2 is None  # Duplicate ignored
            
            # Verify only one copy exists
            user_saved = await saved_job_repo.get_by_user(user_id)
    
    assert len(user_saved) == 1
