from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from datetime import datetime
import json
import logging
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from app.core.redis import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job_create: JobCreate) -> Job:
        """Create a new job."""
        db_job = Job(**job_create.model_dump())
        self.session.add(db_job)
        try:
            await self.session.flush()
            return db_job
        except IntegrityError:
            await self.session.rollback()
            raise ValueError(f"Job with source_url {job_create.source_url} already exists")

    async def get_by_id(self, job_id: UUID) -> Job | None:
        """Get job by ID with caching."""
        # Try to get from cache
        cache_key = f"job:{job_id}"
        cached_job = await redis_client.get(cache_key)
        if cached_job:
            logger.debug(f"Cache hit for job {job_id}")
            return cached_job
        
        result = await self.session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        # Cache the result with jobs TTL
        if job:
            await redis_client.set(cache_key, job, cache_type="jobs")
        
        return job

    async def get_by_source_url(self, source_url: str) -> Job | None:
        """Get job by source URL."""
        result = await self.session.execute(
            select(Job).where(Job.source_url == source_url)
        )
        return result.scalar_one_or_none()

    async def get_by_source_job_id(self, source: str, source_job_id: str) -> Job | None:
        """Get job by source and source job ID."""
        result = await self.session.execute(
            select(Job).where(
                (Job.source == source) & (Job.source_job_id == source_job_id)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, job_id: UUID, job_update: JobUpdate) -> Job | None:
        """Update job."""
        job = await self.get_by_id(job_id)
        if not job:
            return None

        update_data = job_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        job.updated_at = datetime.utcnow()
        self.session.add(job)
        await self.session.flush()
        return job

    async def delete(self, job_id: UUID) -> bool:
        """Delete job."""
        job = await self.get_by_id(job_id)
        if not job:
            return False

        await self.session.delete(job)
        await self.session.flush()
        return True

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Job]:
        """Get all jobs with pagination and caching."""
        # Generate cache key
        cache_key = f"jobs:all:{skip}:{limit}"
        
        # Try to get from cache
        cached_jobs = await redis_client.get(cache_key)
        if cached_jobs:
            logger.debug(f"Cache hit for jobs list {skip}:{limit}")
            return cached_jobs
        
        result = await self.session.execute(
            select(Job).offset(skip).limit(limit).order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()
        
        # Cache the result with jobs TTL
        if jobs:
            await redis_client.set(cache_key, jobs, cache_type="jobs")
        
        return jobs

    async def get_by_source(self, source: str, skip: int = 0, limit: int = 100) -> list[Job]:
        """Get jobs by source with caching."""
        # Generate cache key
        cache_key = f"jobs:source:{source}:{skip}:{limit}"
        
        # Try to get from cache
        cached_jobs = await redis_client.get(cache_key)
        if cached_jobs:
            logger.debug(f"Cache hit for jobs by source {source}")
            return cached_jobs
        
        result = await self.session.execute(
            select(Job)
            .where(Job.source == source)
            .offset(skip)
            .limit(limit)
            .order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()
        
        # Cache the result with jobs TTL
        if jobs:
            await redis_client.set(cache_key, jobs, cache_type="jobs")
        
        return jobs

    async def get_by_company(self, company: str, skip: int = 0, limit: int = 100) -> list[Job]:
        """Get jobs by company with caching."""
        # Generate cache key
        cache_key = f"jobs:company:{company}:{skip}:{limit}"
        
        # Try to get from cache
        cached_jobs = await redis_client.get(cache_key)
        if cached_jobs:
            logger.debug(f"Cache hit for jobs by company {company}")
            return cached_jobs
        
        result = await self.session.execute(
            select(Job)
            .where(Job.company.ilike(f"%{company}%"))
            .offset(skip)
            .limit(limit)
            .order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()
        
        # Cache the result with jobs TTL
        if jobs:
            await redis_client.set(cache_key, jobs, cache_type="jobs")
        
        return jobs

    async def search(self, query: str, skip: int = 0, limit: int = 100) -> list[Job]:
        """Search jobs by title or description with caching."""
        # Generate cache key
        cache_key = f"jobs:search:{query}:{skip}:{limit}"
        
        # Try to get from cache
        cached_jobs = await redis_client.get(cache_key)
        if cached_jobs:
            logger.debug(f"Cache hit for search query {query}")
            return cached_jobs
        
        result = await self.session.execute(
            select(Job)
            .where(
                (Job.title.ilike(f"%{query}%")) |
                (Job.description.ilike(f"%{query}%"))
            )
            .offset(skip)
            .limit(limit)
            .order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()
        
        # Cache the result with jobs TTL
        if jobs:
            await redis_client.set(cache_key, jobs, cache_type="jobs")
        
        return jobs

    async def count(self) -> int:
        """Count total jobs."""
        result = await self.session.execute(select(Job))
        return len(result.scalars().all())

    async def count_by_source(self, source: str) -> int:
        """Count jobs by source."""
        result = await self.session.execute(
            select(Job).where(Job.source == source)
        )
        return len(result.scalars().all())

    async def increment_view_count(self, job_id: UUID) -> Job | None:
        """Increment view count for a job."""
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.view_count += 1
        self.session.add(job)
        await self.session.flush()
        return job

    async def increment_apply_count(self, job_id: UUID) -> Job | None:
        """Increment apply count for a job."""
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.apply_count += 1
        self.session.add(job)
        await self.session.flush()
        return job

    async def invalidate_job_cache(self, job_id: UUID) -> bool:
        """
        Invalidate cache for a specific job.
        
        Args:
            job_id: Job ID
        
        Returns:
            True if invalidated successfully
        """
        try:
            cache_key = f"job:{job_id}"
            await redis_client.delete(cache_key)
            logger.info(f"Cache invalidated for job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating job cache: {str(e)}")
            return False

    async def invalidate_all_jobs_cache(self) -> bool:
        """
        Invalidate all jobs-related cache entries.
        
        Returns:
            True if invalidated successfully
        """
        try:
            patterns = [
                "jobs:all:*",
                "jobs:source:*",
                "jobs:company:*",
                "jobs:search:*",
                "job:*",
            ]
            
            for pattern in patterns:
                await redis_client.delete_pattern(pattern)
            
            logger.info("All jobs cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating all jobs cache: {str(e)}")
            return False


    async def search_with_filters(
        self, 
        query: str = "", 
        source: str = None,
        job_type: str = None,
        location: str = None,
        salary_min: int = None,
        salary_max: int = None,
        is_remote: bool = None,
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[list[Job], int]:
        """Search jobs with server-side filtering (no N+1 queries)."""
        # Build query
        q = select(Job)
        
        # Apply filters
        if query:
            q = q.where(
                (Job.title.ilike(f"%{query}%")) |
                (Job.description.ilike(f"%{query}%"))
            )
        
        if source:
            q = q.where(Job.source == source)
        
        if job_type:
            q = q.where(Job.job_type == job_type)
        
        if location:
            q = q.where(Job.location.ilike(f"%{location}%"))
        
        if salary_min is not None:
            q = q.where(Job.salary_min >= salary_min)
        
        if salary_max is not None:
            q = q.where(Job.salary_max <= salary_max)
        
        if is_remote is not None:
            q = q.where(Job.is_remote == (2 if is_remote else 0))
        
        # Get total count
        count_result = await self.session.execute(
            select(Job).from_statement(q.statement)
        )
        total = len(count_result.scalars().all())
        
        # Apply pagination and ordering
        q = q.offset(skip).limit(limit).order_by(Job.created_at.desc())
        
        result = await self.session.execute(q)
        jobs = result.scalars().all()
        
        return jobs, total
