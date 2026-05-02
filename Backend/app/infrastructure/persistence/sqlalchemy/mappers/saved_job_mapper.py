from app.domain.entities.saved_job import SavedJob
from app.infrastructure.persistence.sqlalchemy.models.saved_job_orm import SavedJobORM


class SavedJobMapper:
    """Mapper to convert between SavedJob domain entity and SavedJobORM model."""

    @staticmethod
    def to_domain(orm_saved_job: SavedJobORM) -> SavedJob:
        """Convert SQLAlchemy SavedJobORM to SavedJob domain entity."""
        if not orm_saved_job:
            return None
            
        return SavedJob(
            id=orm_saved_job.id,
            user_id=orm_saved_job.user_id,
            job_id=orm_saved_job.job_id,
            notes=orm_saved_job.notes,
            saved_at=orm_saved_job.saved_at,
            updated_at=orm_saved_job.updated_at
        )

    @staticmethod
    def to_orm(domain_saved_job: SavedJob) -> SavedJobORM:
        """Convert SavedJob domain entity to SQLAlchemy SavedJobORM."""
        if not domain_saved_job:
            return None
            
        return SavedJobORM(
            id=domain_saved_job.id,
            user_id=domain_saved_job.user_id,
            job_id=domain_saved_job.job_id,
            notes=domain_saved_job.notes,
            saved_at=domain_saved_job.saved_at,
            updated_at=domain_saved_job.updated_at
        )
