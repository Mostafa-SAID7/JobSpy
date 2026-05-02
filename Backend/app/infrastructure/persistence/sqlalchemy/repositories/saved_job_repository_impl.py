from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_

from app.domain.entities.saved_job import SavedJob
from app.domain.entities.job import Job
from app.domain.interfaces.repositories import ISavedJobRepository
from app.infrastructure.persistence.sqlalchemy.models.saved_job_orm import SavedJobORM
from app.infrastructure.persistence.sqlalchemy.models.job_orm import JobORM
from app.infrastructure.persistence.sqlalchemy.mappers.saved_job_mapper import SavedJobMapper
from app.infrastructure.persistence.sqlalchemy.mappers.job_mapper import JobMapper


class SavedJobRepositoryImpl(ISavedJobRepository):
    """
    SQLAlchemy implementation of ISavedJobRepository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, saved_job: SavedJob) -> SavedJob:
        """Create a new saved job."""
        orm_saved_job = SavedJobMapper.to_orm(saved_job)
        self.session.add(orm_saved_job)
        await self.session.flush()
        return SavedJobMapper.to_domain(orm_saved_job)

    async def get_by_id(self, saved_job_id: UUID) -> Optional[SavedJob]:
        """Get saved job by ID."""
        result = await self.session.execute(
            select(SavedJobORM).where(SavedJobORM.id == saved_job_id)
        )
        orm_saved_job = result.scalar_one_or_none()
        return SavedJobMapper.to_domain(orm_saved_job) if orm_saved_job else None

    async def get_by_user_and_job(self, user_id: UUID, job_id: UUID) -> Optional[SavedJob]:
        """Get saved job by user and job ID."""
        result = await self.session.execute(
            select(SavedJobORM).where(
                and_(SavedJobORM.user_id == user_id, SavedJobORM.job_id == job_id)
            )
        )
        orm_saved_job = result.scalar_one_or_none()
        return SavedJobMapper.to_domain(orm_saved_job) if orm_saved_job else None

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[SavedJob]:
        """Get all saved jobs for a user."""
        result = await self.session.execute(
            select(SavedJobORM)
            .where(SavedJobORM.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(SavedJobORM.saved_at.desc())
        )
        orm_saved_jobs = result.scalars().all()
        return [SavedJobMapper.to_domain(s) for s in orm_saved_jobs]

    async def get_by_user_with_jobs(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Tuple[SavedJob, Job]]:
        """Get all saved jobs with job details."""
        result = await self.session.execute(
            select(SavedJobORM, JobORM)
            .join(JobORM, SavedJobORM.job_id == JobORM.id)
            .where(SavedJobORM.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(SavedJobORM.saved_at.desc())
        )
        rows = result.all()
        return [
            (SavedJobMapper.to_domain(row[0]), JobMapper.to_domain(row[1]))
            for row in rows
        ]

    async def delete(self, saved_job_id: UUID) -> bool:
        """Delete saved job."""
        result = await self.session.execute(
            select(SavedJobORM).where(SavedJobORM.id == saved_job_id)
        )
        orm_saved_job = result.scalar_one_or_none()
        if not orm_saved_job:
            return False
        
        await self.session.delete(orm_saved_job)
        await self.session.flush()
        return True

    async def delete_by_user_and_job(self, user_id: UUID, job_id: UUID) -> bool:
        """Delete saved job by user and job ID."""
        saved_job = await self.get_by_user_and_job(user_id, job_id)
        if not saved_job:
            return False
        
        await self.delete(saved_job.id)
        return True

    async def count_by_user(self, user_id: UUID) -> int:
        """Count saved jobs for a user."""
        result = await self.session.execute(
            select(func.count(SavedJobORM.id)).where(SavedJobORM.user_id == user_id)
        )
        return result.scalar() or 0

    async def is_saved(self, user_id: UUID, job_id: UUID) -> bool:
        """Check if a job is saved by a user."""
        saved_job = await self.get_by_user_and_job(user_id, job_id)
        return saved_job is not None
