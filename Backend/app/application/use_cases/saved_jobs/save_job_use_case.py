"""
Save Job Use Case

Handles saving a job for a user.
"""

import logging
from uuid import UUID

from app.presentation.api.v1.schemas.saved_job import SavedJobCreate
from app.domain.entities.saved_job import SavedJob
from app.domain.interfaces.repositories import ISavedJobRepository, IJobRepository

logger = logging.getLogger(__name__)


class SaveJobUseCase:
    """
    Use Case: Save a job for a user.
    
    Responsibilities:
    1. Check if job exists
    2. Check if already saved
    3. Create saved job record
    4. Return saved job with details
    
    Used by: Save job endpoint
    """
    
    def __init__(
        self,
        saved_job_repository: ISavedJobRepository,
        job_repository: IJobRepository,
    ):
        """
        Initialize use case.
        
        Args:
            saved_job_repository: Repository for saved jobs
            job_repository: Repository for jobs
        """
        self.saved_job_repository = saved_job_repository
        self.job_repository = job_repository
    
    async def execute(
        self,
        user_id: int,
        saved_job_create: SavedJobCreate,
    ) -> SavedJob:
        """
        Execute the use case.
        
        Args:
            user_id: User ID
            saved_job_create: Saved job creation data
        
        Returns:
            Created saved job
        
        Raises:
            ValueError: If job not found or already saved
        """
        logger.info(f"Saving job {saved_job_create.job_id} for user {user_id}")
        
        # Check if job exists
        job = await self.job_repository.get_by_id(saved_job_create.job_id)
        if not job:
            logger.warning(f"Job not found: {saved_job_create.job_id}")
            raise ValueError("Job not found")
        
        # Check if already saved
        is_saved = await self.saved_job_repository.is_saved(user_id, saved_job_create.job_id)
        if is_saved:
            logger.warning(f"Job already saved: {saved_job_create.job_id} for user {user_id}")
            raise ValueError("Job is already saved")
        
        # Create saved job domain entity and persist
        try:
            domain_saved_job = SavedJob(
                user_id=user_id,
                job_id=saved_job_create.job_id,
                notes=getattr(saved_job_create, 'notes', None),
            )
            saved_job = await self.saved_job_repository.create(domain_saved_job)
            logger.info(f"Job saved successfully: {saved_job.id}")
            return saved_job
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            raise ValueError(f"Failed to save job: {str(e)}")
