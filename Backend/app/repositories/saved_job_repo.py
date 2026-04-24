from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from app.models.saved_job import SavedJob
from app.models.job import Job
from app.schemas.saved_job import SavedJobCreate, SavedJobUpdate


class SavedJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, saved_job_create: SavedJobCreate) -> SavedJob:
        """Create a new saved job."""
        db_saved_job = SavedJob(
            user_id=user_id,
            job_id=saved_job_create.job_id,
            notes=saved_job_create.notes,
        )
        self.session.add(db_saved_job)
        try:
            await self.session.flush()
            return db_saved_job
        except IntegrityError:
            await self.session.rollback()
            raise ValueError(f"Job {saved_job_create.job_id} is already saved by user {user_id}")

    async def get_by_id(self, saved_job_id: UUID) -> SavedJob | None:
        """Get saved job by ID."""
        result = await self.session.execute(
            select(SavedJob).where(SavedJob.id == saved_job_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_job(self, user_id: UUID, job_id: UUID) -> SavedJob | None:
        """Get saved job by user and job ID."""
        result = await self.session.execute(
            select(SavedJob).where(
                (SavedJob.user_id == user_id) & (SavedJob.job_id == job_id)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, saved_job_id: UUID, saved_job_update: SavedJobUpdate) -> SavedJob | None:
        """Update saved job."""
        saved_job = await self.get_by_id(saved_job_id)
        if not saved_job:
            return None

        update_data = saved_job_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(saved_job, field, value)

        self.session.add(saved_job)
        await self.session.flush()
        return saved_job

    async def delete(self, saved_job_id: UUID) -> bool:
        """Delete saved job."""
        saved_job = await self.get_by_id(saved_job_id)
        if not saved_job:
            return False

        await self.session.delete(saved_job)
        await self.session.flush()
        return True

    async def delete_by_user_and_job(self, user_id: UUID, job_id: UUID) -> bool:
        """Delete saved job by user and job ID."""
        saved_job = await self.get_by_user_and_job(user_id, job_id)
        if not saved_job:
            return False

        await self.session.delete(saved_job)
        await self.session.flush()
        return True

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[SavedJob]:
        """Get all saved jobs for a user."""
        result = await self.session.execute(
            select(SavedJob)
            .where(SavedJob.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(SavedJob.saved_at.desc())
        )
        return result.scalars().all()

    async def count_by_user(self, user_id: UUID) -> int:
        """Count saved jobs for a user."""
        result = await self.session.execute(
            select(SavedJob).where(SavedJob.user_id == user_id)
        )
        return len(result.scalars().all())

    async def is_saved(self, user_id: UUID, job_id: UUID) -> bool:
        """Check if a job is saved by a user."""
        saved_job = await self.get_by_user_and_job(user_id, job_id)
        return saved_job is not None
