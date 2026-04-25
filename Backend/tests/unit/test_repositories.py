"""
Unit tests for repository layer
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models.user import User
from app.models.job import Job
from app.models.saved_job import SavedJob
from app.repositories.user_repo import UserRepository
from app.repositories.job_repo import JobRepository
from app.repositories.saved_job_repo import SavedJobRepository


@pytest.mark.asyncio
class TestUserRepository:
    """Test UserRepository methods"""

    async def test_create_user(self, db: AsyncSession):
        """Test creating a new user"""
        repo = UserRepository(db)
        
        user = await repo.create(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
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
        """Test updating user"""
        repo = UserRepository(db)
        
        updated_user = await repo.update(
            test_user.id,
            username="newusername"
        )
        
        assert updated_user.username == "newusername"

    async def test_delete_user(self, db: AsyncSession, test_user: User):
        """Test deleting user"""
        repo = UserRepository(db)
        user_id = test_user.id
        
        await repo.delete(user_id)
        
        deleted_user = await repo.get_by_id(user_id)
        assert deleted_user is None


@pytest.mark.asyncio
class TestJobRepository:
    """Test JobRepository methods"""

    async def test_create_job(self, db: AsyncSession):
        """Test creating a new job"""
        repo = JobRepository(db)
        
        job = await repo.create(
            title="Senior Developer",
            company="Tech Corp",
            location="Remote",
            description="Job description",
            url="https://example.com/job/1",
            source="linkedin"
        )
        
        assert job.title == "Senior Developer"
        assert job.company == "Tech Corp"
        assert job.id is not None

    async def test_search_jobs(self, db: AsyncSession):
        """Test searching jobs"""
        repo = JobRepository(db)
        
        # Create test jobs
        await repo.create(
            title="Python Developer",
            company="Tech Corp",
            location="Remote",
            description="Python job",
            url="https://example.com/1",
            source="linkedin"
        )
        
        await repo.create(
            title="JavaScript Developer",
            company="Web Inc",
            location="New York",
            description="JavaScript job",
            url="https://example.com/2",
            source="indeed"
        )
        
        # Search for Python jobs
        results = await repo.search(query="Python")
        
        assert len(results) >= 1
        assert any(job.title == "Python Developer" for job in results)

    async def test_get_job_by_id(self, db: AsyncSession):
        """Test retrieving job by ID"""
        repo = JobRepository(db)
        
        job = await repo.create(
            title="Developer",
            company="Tech Corp",
            location="Remote",
            description="Job description",
            url="https://example.com/job/1",
            source="linkedin"
        )
        
        retrieved_job = await repo.get_by_id(job.id)
        
        assert retrieved_job is not None
        assert retrieved_job.id == job.id

    async def test_get_jobs_by_source(self, db: AsyncSession):
        """Test retrieving jobs by source"""
        repo = JobRepository(db)
        
        await repo.create(
            title="Job 1",
            company="Company 1",
            location="Remote",
            description="Description",
            url="https://example.com/1",
            source="linkedin"
        )
        
        await repo.create(
            title="Job 2",
            company="Company 2",
            location="Remote",
            description="Description",
            url="https://example.com/2",
            source="indeed"
        )
        
        linkedin_jobs = await repo.get_by_source("linkedin")
        
        assert len(linkedin_jobs) >= 1
        assert all(job.source == "linkedin" for job in linkedin_jobs)


@pytest.mark.asyncio
class TestSavedJobRepository:
    """Test SavedJobRepository methods"""

    async def test_save_job(self, db: AsyncSession, test_user: User):
        """Test saving a job"""
        job_repo = JobRepository(db)
        saved_repo = SavedJobRepository(db)
        
        job = await job_repo.create(
            title="Developer",
            company="Tech Corp",
            location="Remote",
            description="Job description",
            url="https://example.com/job/1",
            source="linkedin"
        )
        
        saved_job = await saved_repo.create(
            user_id=test_user.id,
            job_id=job.id
        )
        
        assert saved_job.user_id == test_user.id
        assert saved_job.job_id == job.id

    async def test_get_user_saved_jobs(self, db: AsyncSession, test_user: User):
        """Test retrieving user's saved jobs"""
        job_repo = JobRepository(db)
        saved_repo = SavedJobRepository(db)
        
        job1 = await job_repo.create(
            title="Job 1",
            company="Company 1",
            location="Remote",
            description="Description",
            url="https://example.com/1",
            source="linkedin"
        )
        
        job2 = await job_repo.create(
            title="Job 2",
            company="Company 2",
            location="Remote",
            description="Description",
            url="https://example.com/2",
            source="indeed"
        )
        
        await saved_repo.create(user_id=test_user.id, job_id=job1.id)
        await saved_repo.create(user_id=test_user.id, job_id=job2.id)
        
        saved_jobs = await saved_repo.get_by_user(test_user.id)
        
        assert len(saved_jobs) == 2

    async def test_unsave_job(self, db: AsyncSession, test_user: User):
        """Test removing a saved job"""
        job_repo = JobRepository(db)
        saved_repo = SavedJobRepository(db)
        
        job = await job_repo.create(
            title="Developer",
            company="Tech Corp",
            location="Remote",
            description="Job description",
            url="https://example.com/job/1",
            source="linkedin"
        )
        
        saved_job = await saved_repo.create(
            user_id=test_user.id,
            job_id=job.id
        )
        
        await saved_repo.delete(saved_job.id)
        
        deleted = await saved_repo.get_by_id(saved_job.id)
        assert deleted is None

    async def test_check_job_saved(self, db: AsyncSession, test_user: User):
        """Test checking if job is saved"""
        job_repo = JobRepository(db)
        saved_repo = SavedJobRepository(db)
        
        job = await job_repo.create(
            title="Developer",
            company="Tech Corp",
            location="Remote",
            description="Job description",
            url="https://example.com/job/1",
            source="linkedin"
        )
        
        await saved_repo.create(user_id=test_user.id, job_id=job.id)
        
        is_saved = await saved_repo.is_saved(test_user.id, job.id)
        
        assert is_saved is True
