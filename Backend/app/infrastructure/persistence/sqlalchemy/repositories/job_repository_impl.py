from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.domain.entities.job import Job
from app.domain.interfaces.repositories import IJobRepository
from app.infrastructure.persistence.sqlalchemy.models.job_orm import JobORM
from app.infrastructure.persistence.sqlalchemy.mappers.job_mapper import JobMapper


class JobRepositoryImpl(IJobRepository):
    """
    SQLAlchemy implementation of the Job repository.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, job: Job) -> Job:
        """Save a job entity to the database."""
        orm_job = JobMapper.to_orm(job)
        self._session.add(orm_job)
        try:
            await self._session.flush()
            # Update domain object with ID if it was newly created
            job.id = orm_job.id
            return job
        except IntegrityError as e:
            await self._session.rollback()
            raise ValueError(f"Could not save job: {str(e)}")

    async def get_by_id(self, job_id: UUID) -> Optional[Job]:
        """Fetch a job by its unique identifier."""
        result = await self._session.execute(
            select(JobORM).where(JobORM.id == job_id)
        )
        orm_job = result.scalar_one_or_none()
        return JobMapper.to_domain(orm_job)

    async def get_by_source_url(self, source_url: str) -> Optional[Job]:
        """Fetch a job by its source URL."""
        result = await self._session.execute(
            select(JobORM).where(JobORM.source_url == source_url)
        )
        orm_job = result.scalar_one_or_none()
        return JobMapper.to_domain(orm_job)

    async def exists_by_url(self, source_url: str) -> bool:
        """Check if a job with the given URL exists."""
        result = await self._session.execute(
            select(func.count()).select_from(JobORM).where(JobORM.source_url == source_url)
        )
        return result.scalar() > 0

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Job]:
        """Fetch all jobs with pagination."""
        result = await self._session.execute(
            select(JobORM)
            .offset(skip)
            .limit(limit)
            .order_by(JobORM.created_at.desc())
        )
        return [JobMapper.to_domain(orm_job) for orm_job in result.scalars().all()]

    async def find_by_source(self, source: str, skip: int = 0, limit: int = 100) -> List[Job]:
        """Fetch jobs from a specific source."""
        result = await self._session.execute(
            select(JobORM)
            .where(JobORM.source == source)
            .offset(skip)
            .limit(limit)
            .order_by(JobORM.created_at.desc())
        )
        return [JobMapper.to_domain(orm_job) for orm_job in result.scalars().all()]

    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Job]:
        """Search jobs by title or description."""
        result = await self._session.execute(
            select(JobORM)
            .where(
                (JobORM.title.ilike(f"%{query}%")) |
                (JobORM.description.ilike(f"%{query}%"))
            )
            .offset(skip)
            .limit(limit)
            .order_by(JobORM.created_at.desc())
        )
        return [JobMapper.to_domain(orm_job) for orm_job in result.scalars().all()]

    async def update(self, job: Job) -> Job:
        """Update an existing job entity."""
        # Check if exists
        result = await self._session.execute(
            select(JobORM).where(JobORM.id == job.id)
        )
        orm_job = result.scalar_one_or_none()
        if not orm_job:
            raise ValueError(f"Job with id {job.id} not found")
        
        # Map domain changes to ORM object
        # We don't want to create a NEW ORM object, but update the existing one attached to the session
        updated_orm = JobMapper.to_orm(job)
        
        # Manual update for now (we could use a better tool or SQLAlchemy's merge)
        for column in JobORM.__table__.columns:
            if column.name != "id":
                setattr(orm_job, column.name, getattr(updated_orm, column.name))
        
        await self._session.flush()
        return job

    async def delete(self, job_id: UUID) -> bool:
        """Delete a job by ID."""
        result = await self._session.execute(
            delete(JobORM).where(JobORM.id == job_id)
        )
        return result.rowcount > 0

    async def count(self) -> int:
        """Count total number of jobs."""
        result = await self._session.execute(
            select(func.count()).select_from(JobORM)
        )
        return result.scalar() or 0
