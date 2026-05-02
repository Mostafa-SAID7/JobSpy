"""
Unit tests for repository layer
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from uuid import uuid4

from app.domain.entities.user import User
from app.domain.entities.job import Job
from app.domain.entities.saved_job import SavedJob
from app.domain.interfaces.repositories import IUserRepository as UserRepository
from app.domain.interfaces.repositories import IJobRepository as JobRepository
from app.domain.interfaces.repositories import ISavedJobRepository as SavedJobRepository
from app.presentation.api.v1.schemas.user import UserCreate, UserUpdate
from app.presentation.api.v1.schemas.job import JobCreate, JobUpdate
from app.presentation.api.v1.schemas.saved_job import SavedJobCreate, SavedJobUpdate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_job_create(suffix: str = "1", source: str = "linkedin") -> JobCreate:
    """Return a valid JobCreate with unique source_url."""
    return JobCreate(
        title=f"Developer {suffix}",
        company=f"Tech Corp {suffix}",
        location="Remote",
        description=f"Job description {suffix}",
        source_url=f"https://example.com/job/{suffix}",
        source=source,
    )


# ---------------------------------------------------------------------------
# User Repository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestUserRepository:
    """Test UserRepository methods"""

    async def test_create_user(self, db: AsyncSession):
        """Test creating a new user"""
        repo = UserRepository(db)

        user_in = UserCreate(
            email="create_test@example.com",
            full_name="Test User",
            password="password123",
        )
        user = await repo.create(user_in, hashed_password="hashed_password")

        assert user.email == "create_test@example.com"
        assert user.full_name == "Test User"
        assert user.id is not None

    async def test_get_user_by_email(self, db: AsyncSession, test_user: User):
        """Test retrieving user by email"""
        repo = UserRepository(db)

        user = await repo.get_by_email(test_user.email)

        assert user is not None
        assert user.email == test_user.email

    async def test_get_user_by_id(self, db: AsyncSession, test_user: User):
        """Test retrieving user by ID"""
        repo = UserRepository(db)

        user = await repo.get_by_id(test_user.id)

        assert user is not None
        assert user.id == test_user.id

    async def test_update_user(self, db: AsyncSession, test_user: User):
        """Test updating user full_name"""
        repo = UserRepository(db)

        user_update = UserUpdate(full_name="Updated Name")
        updated_user = await repo.update(test_user.id, user_update)

        assert updated_user.full_name == "Updated Name"

    async def test_delete_user(self, db: AsyncSession, test_user: User):
        """Test deleting user"""
        repo = UserRepository(db)
        user_id = test_user.id

        await repo.delete(user_id)

        deleted_user = await repo.get_by_id(user_id)
        assert deleted_user is None


# ---------------------------------------------------------------------------
# Job Repository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestJobRepository:
    """Test JobRepository methods"""

    async def test_create_job(self, db: AsyncSession):
        """Test creating a new job"""
        repo = JobRepository(db)

        job_in = JobCreate(
            title="Senior Developer",
            company="Tech Corp",
            location="Remote",
            description="Job description",
            source_url="https://example.com/job/create-test",
            source="linkedin",
        )
        job = await repo.create(job_in)

        assert job.title == "Senior Developer"
        assert job.company == "Tech Corp"
        assert job.id is not None

    async def test_search_jobs(self, db: AsyncSession):
        """Test searching jobs by keyword in description"""
        repo = JobRepository(db)

        job1_in = JobCreate(
            title="Python Engineer",
            company="Tech Corp",
            location="Remote",
            description="Python and Django development",
            source_url="https://example.com/job/search-1",
            source="linkedin",
        )
        await repo.create(job1_in)

        job2_in = JobCreate(
            title="Frontend Developer",
            company="Web Inc",
            location="Hybrid",
            description="React and TypeScript",
            source_url="https://example.com/job/search-2",
            source="indeed",
        )
        await repo.create(job2_in)

        # Search should match description
        results = await repo.search(query="Python")

        assert len(results) >= 1
        assert any(job.title == "Python Engineer" for job in results)

    async def test_get_job_by_id(self, db: AsyncSession):
        """Test retrieving job by ID"""
        repo = JobRepository(db)

        job_in = make_job_create(suffix="get-by-id")
        job = await repo.create(job_in)

        retrieved_job = await repo.get_by_id(job.id)

        assert retrieved_job is not None
        assert retrieved_job.id == job.id

    async def test_get_jobs_by_source(self, db: AsyncSession):
        """Test retrieving jobs filtered by source"""
        repo = JobRepository(db)

        await repo.create(JobCreate(
            title="Job LinkedIn",
            company="Company A",
            location="Remote",
            description="LinkedIn job",
            source_url="https://example.com/source-1",
            source="linkedin",
        ))

        await repo.create(JobCreate(
            title="Job Indeed",
            company="Company B",
            location="Remote",
            description="Indeed job",
            source_url="https://example.com/source-2",
            source="indeed",
        ))

        linkedin_jobs = await repo.get_by_source("linkedin")

        assert len(linkedin_jobs) >= 1
        assert all(job.source == "linkedin" for job in linkedin_jobs)


# ---------------------------------------------------------------------------
# SavedJob Repository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestSavedJobRepository:
    """Test SavedJobRepository methods"""

    async def _create_job(self, db: AsyncSession, suffix: str) -> Job:
        """Helper to create a unique job."""
        repo = JobRepository(db)
        return await repo.create(make_job_create(suffix=f"saved-{suffix}"))

    async def test_save_job(self, db: AsyncSession, test_user: User):
        """Test saving a job"""
        job = await self._create_job(db, "save")
        saved_repo = SavedJobRepository(db)

        saved_job_in = SavedJobCreate(job_id=job.id)
        saved_job = await saved_repo.create(test_user.id, saved_job_in)

        assert saved_job.user_id == test_user.id
        assert saved_job.job_id == job.id

    async def test_get_user_saved_jobs(self, db: AsyncSession, test_user: User):
        """Test retrieving user's saved jobs"""
        job1 = await self._create_job(db, "get-1")
        job2 = await self._create_job(db, "get-2")
        saved_repo = SavedJobRepository(db)

        await saved_repo.create(test_user.id, SavedJobCreate(job_id=job1.id))
        await saved_repo.create(test_user.id, SavedJobCreate(job_id=job2.id))

        saved_jobs = await saved_repo.get_by_user(test_user.id)

        assert len(saved_jobs) == 2

    async def test_unsave_job(self, db: AsyncSession, test_user: User):
        """Test removing a saved job"""
        job = await self._create_job(db, "unsave")
        saved_repo = SavedJobRepository(db)

        saved_job_in = SavedJobCreate(job_id=job.id)
        saved_job = await saved_repo.create(test_user.id, saved_job_in)

        await saved_repo.delete(saved_job.id)

        deleted = await saved_repo.get_by_id(saved_job.id)
        assert deleted is None

    async def test_check_job_saved(self, db: AsyncSession, test_user: User):
        """Test checking if a job is saved"""
        job = await self._create_job(db, "is-saved")
        saved_repo = SavedJobRepository(db)

        await saved_repo.create(test_user.id, SavedJobCreate(job_id=job.id))

        is_saved = await saved_repo.is_saved(test_user.id, job.id)

        assert is_saved is True
