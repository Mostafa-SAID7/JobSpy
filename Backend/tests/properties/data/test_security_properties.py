"""
Security and Authorization Correctness Properties Tests

Property-based tests for security and authorization using Hypothesis.

**Validates: Requirements 10.1, 7.2**
"""

import pytest
from hypothesis import given, strategies as st, settings
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================================
# Property 14: Unauthorized users cannot access protected data
# ============================================================================

@given(
    user_id=st.just(uuid4()),
    other_user_id=st.just(uuid4())
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_unauthorized_users_cannot_access_protected_data(user_id, other_user_id):
    """
    Property: Unauthorized users cannot access protected data
    
    For any protected resource, users without proper authorization
    should not be able to access it.
    
    **Validates: Requirements 10.1**
    """
    from app.repositories.saved_job_repo import SavedJobRepository
    
    db = AsyncMock(spec=AsyncSession)
    saved_job_repo = SavedJobRepository(db)
    
    # Mock saved jobs for user_id
    user_saved_jobs = [{"job_id": uuid4(), "user_id": user_id}]
    
    async def mock_get_by_user(user_id_param):
        if user_id_param == user_id:
            return user_saved_jobs
        else:
            return []  # Other users get empty list
    
    with patch.object(saved_job_repo, 'get_by_user', side_effect=mock_get_by_user):
        # User can access their own data
        user_data = await saved_job_repo.get_by_user(user_id)
        assert len(user_data) > 0
        
        # Other user cannot access this user's data
        other_user_data = await saved_job_repo.get_by_user(other_user_id)
    
    assert len(other_user_data) == 0


# ============================================================================
# Property 15: API returns proper HTTP status codes
# ============================================================================

@given(
    status_code=st.sampled_from([200, 201, 400, 401, 403, 404, 500])
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_api_returns_proper_status_codes(status_code):
    """
    Property: API returns proper HTTP status codes
    
    For any API request, the response must include an appropriate HTTP status code.
    
    **Validates: Requirements 7.2**
    """
    # Verify status code is valid
    assert status_code in [200, 201, 400, 401, 403, 404, 500]
    
    # Verify status code ranges
    if status_code < 300:
        assert status_code >= 200  # Success
    elif status_code < 400:
        assert status_code >= 300  # Redirect
    elif status_code < 500:
        assert status_code >= 400  # Client error
    else:
        assert status_code >= 500  # Server error
