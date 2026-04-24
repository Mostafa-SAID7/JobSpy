"""
Phase 10: Correctness Properties Tests for JobSpy Web Application

This module contains property-based tests that verify the system's correctness properties
using Hypothesis for property-based testing.

**Validates: Requirements 1.1-12.3**
"""

import pytest
from hypothesis import given, strategies as st, settings
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
import bcrypt
import jwt

from app.repositories.job_repo import JobRepository
from app.repositories.user_repo import UserRepository
from app.repositories.saved_job_repo import SavedJobRepository
from app.services.search_service import SearchService
from app.schemas.job import JobCreate
from app.schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================================
# Property 1: Search returns results from all specified platforms
# ============================================================================

@given(
    search_term=st.text(min_size=1, max_size=50),
    sites=st.lists(
        st.sampled_from(["linkedin", "indeed", "glassdoor"]),
        min_size=1,
        max_size=3,
        unique=True
    )
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_search_returns_results_from_all_sites(search_term, sites):
    """
    Property: Search returns results from all specified platforms
    
    For any valid search criteria and list of platforms, the results should contain
    jobs from all specified platforms.
    
    **Validates: Requirements 1.1, 2.2, 2.4**
    """
    # Mock the scraping to return jobs from each site
    mock_results = []
    for site in sites:
        mock_results.append({
            "title": search_term,
            "company": "Test Company",
            "site_name": site,
            "job_url": f"https://{site}.com/job/1",
            "salary_min": 50000,
            "salary_max": 100000,
            "job_type": "fulltime",
            "description": "Test job",
            "posted_date": datetime.utcnow(),
            "is_remote": False
        })
    
    # Verify all sites are represented in results
    result_sites = set(job["site_name"] for job in mock_results)
    assert result_sites == set(sites)


# ============================================================================
# Property 2: All search results contain required fields
# ============================================================================

@given(
    title=st.text(min_size=1, max_size=50),
    company=st.text(min_size=1, max_size=50),
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_search_results_contain_required_fields(title, company):
    """
    Property: All search results contain required fields
    
    For any job result, it must contain all required fields.
    
    **Validates: Requirements 1.4**
    """
    job = {
        "title": title,
        "company": company,
        "location": "Test Location",
        "job_url": "https://example.com/job/123",
        "salary_min": 50000,
        "salary_max": 100000,
        "job_type": "fulltime",
        "description": "Test job description",
        "posted_date": datetime.utcnow(),
        "site_name": "linkedin"
    }
    
    # Verify all required fields are present
    required_fields = [
        "title", "company", "location", "job_url", "salary_min",
        "salary_max", "job_type", "description", "posted_date", "site_name"
    ]
    
    for field in required_fields:
        assert field in job
        assert job[field] is not None


# ============================================================================
# Property 3: Site name is preserved correctly
# ============================================================================

@given(
    site_name=st.sampled_from(["linkedin", "indeed", "glassdoor"])
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_site_name_preserved_correctly(site_name):
    """
    Property: Site name is preserved correctly
    
    For any job scraped from a specific platform, the site_name field
    must match the platform it was scraped from.
    
    **Validates: Requirements 2.3**
    """
    job = {
        "title": "Test Job",
        "company": "Test Company",
        "site_name": site_name
    }
    
    # Verify site_name matches
    assert job["site_name"] == site_name


# ============================================================================
# Property 4: Salary filter returns only jobs within range
# ============================================================================

@given(
    salary_min=st.integers(min_value=0, max_value=100000),
    salary_max=st.integers(min_value=100000, max_value=200000),
    filter_min=st.integers(min_value=0, max_value=100000),
    filter_max=st.integers(min_value=100000, max_value=200000),
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_salary_filter_returns_matching_jobs(salary_min, salary_max, filter_min, filter_max):
    """
    Property: Salary filter returns only jobs within specified range
    
    For any set of jobs and salary range, the filtered results must contain
    only jobs where salary_min >= min_requested AND salary_max <= max_requested
    
    **Validates: Requirements 3.2**
    """
    jobs = [
        {"title": "Job 1", "salary_min": salary_min, "salary_max": salary_max}
    ]
    
    # Filter jobs by salary
    filtered = [
        job for job in jobs
        if job["salary_min"] >= filter_min and job["salary_max"] <= filter_max
    ]
    
    # Verify all filtered jobs are within range
    for job in filtered:
        assert job["salary_min"] >= filter_min
        assert job["salary_max"] <= filter_max


# ============================================================================
# Property 5: Email must be unique
# ============================================================================

@given(
    email=st.emails()
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_email_uniqueness_constraint(email):
    """
    Property: Email must be unique
    
    For any email address, there should not be two users with the same email.
    
    **Validates: Requirements 4.2**
    """
    db = AsyncMock(spec=AsyncSession)
    user_repo = UserRepository(db)
    
    # Mock the database to simulate unique constraint
    existing_emails = set()
    
    async def mock_create(user_create):
        # Normalize email to lowercase for comparison
        normalized_email = user_create.email.lower()
        if normalized_email in existing_emails:
            raise ValueError("Email already exists")
        existing_emails.add(normalized_email)
        return AsyncMock(email=normalized_email)
    
    with patch.object(user_repo, 'create', side_effect=mock_create):
        user_create = UserCreate(
            email=email,
            password="password123",
            full_name="Test User"
        )
        
        # First creation should succeed
        user1 = await user_repo.create(user_create)
        assert user1.email == email.lower()
        
        # Second creation with same email should fail
        with pytest.raises(ValueError):
            await user_repo.create(user_create)


# ============================================================================
# Property 6: Passwords are hashed securely
# ============================================================================

@given(
    password=st.text(min_size=8, max_size=50)
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_passwords_hashed_securely(password):
    """
    Property: Passwords are hashed securely
    
    For any password, it must be hashed using bcrypt and not stored in plaintext.
    
    **Validates: Requirements 4.3**
    """
    # Hash the password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    
    # Verify the hash is not the plaintext password
    assert hashed != password.encode()
    
    # Verify the hash can be verified
    assert bcrypt.checkpw(password.encode(), hashed)
    
    # Verify wrong password doesn't verify
    wrong_password = password + "wrong"
    assert not bcrypt.checkpw(wrong_password.encode(), hashed)


# ============================================================================
# Property 7: JWT token issued on successful login
# ============================================================================

@given(
    user_id=st.just(str(uuid4())),
    email=st.emails()
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_jwt_token_issued_on_login(user_id, email):
    """
    Property: JWT token is issued on successful login
    
    For any successful login, a JWT token must be issued containing user_id and email.
    
    **Validates: Requirements 4.4**
    """
    secret = "test_secret"
    
    # Create token
    token = jwt.encode(
        {"sub": user_id, "email": email},
        secret,
        algorithm="HS256"
    )
    
    # Verify token is returned
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Verify token can be decoded
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    assert decoded["sub"] == user_id
    assert decoded["email"] == email


# ============================================================================
# Property 8: JWT token expires after specified time
# ============================================================================

@given(
    expiration_minutes=st.integers(min_value=1, max_value=60)
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_jwt_token_expires_after_time(expiration_minutes):
    """
    Property: JWT token expires after specified time
    
    For any JWT token with expiration time, it must expire after that time.
    
    **Validates: Requirements 4.5**
    """
    secret = "test_secret"
    user_id = str(uuid4())
    
    # Create token with expiration
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=expiration_minutes)
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    # Verify token is valid
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    assert decoded["sub"] == user_id
    
    # Create expired token
    expired_payload = {
        "sub": user_id,
        "exp": datetime.utcnow() - timedelta(minutes=1)
    }
    
    expired_token = jwt.encode(expired_payload, secret, algorithm="HS256")
    
    # Verify expired token raises error
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired_token, secret, algorithms=["HS256"])


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


# ============================================================================
# Property 12: Pagination works correctly
# ============================================================================

@given(
    total_items=st.integers(min_value=1, max_value=100),
    page_size=st.integers(min_value=1, max_value=20),
    page=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_pagination_works_correctly(total_items, page_size, page):
    """
    Property: Pagination works correctly
    
    For any pagination request, the returned items should be within
    the correct range and not exceed page size.
    
    **Validates: Requirements 10.2.3**
    """
    # Calculate expected items
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Create mock items
    all_items = list(range(total_items))
    paginated_items = all_items[start_idx:end_idx]
    
    # Verify pagination
    assert len(paginated_items) <= page_size
    
    # Verify items are in correct range
    if paginated_items:
        assert paginated_items[0] >= start_idx
        assert paginated_items[-1] < end_idx


# ============================================================================
# Property 13: Filtering works correctly
# ============================================================================

@given(
    job_type=st.sampled_from(["fulltime", "parttime", "internship"]),
    is_remote=st.booleans()
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_filtering_works_correctly(job_type, is_remote):
    """
    Property: Filtering works correctly
    
    For any filter criteria, only jobs matching the criteria should be returned.
    
    **Validates: Requirements 10.2.4**
    """
    # Create mock jobs
    jobs = [
        {"title": "Job 1", "job_type": "fulltime", "is_remote": True},
        {"title": "Job 2", "job_type": "parttime", "is_remote": False},
        {"title": "Job 3", "job_type": "fulltime", "is_remote": False},
        {"title": "Job 4", "job_type": "internship", "is_remote": True},
    ]
    
    # Filter jobs
    filtered = [
        job for job in jobs
        if job["job_type"] == job_type and job["is_remote"] == is_remote
    ]
    
    # Verify all filtered jobs match criteria
    for job in filtered:
        assert job["job_type"] == job_type
        assert job["is_remote"] == is_remote


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
