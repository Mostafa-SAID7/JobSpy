"""
Update Saved Job Use Case

Handles updating saved job notes.
"""

import logging
from uuid import UUID

from app.schemas.saved_job import SavedJobUpdate
from app.models.saved_job import SavedJob
from app.repositories.saved_job_repo import SavedJobRepository

logger = logging.getLogger(__name__)


class UpdateSavedJobUseCase:
    """
    Use Case: Update saved job notes.
    
    Responsibilities:
    1. Check if saved job exists
    2. Verify user ownership
    3. Update saved job
    4. Return updated saved job
    
    Used by: Update saved job endpoint
    """
    
    def __init__(self, saved_job_repository: SavedJobRepository):
        """
        Initialize use case.
        
        Args:
            saved_job_repository: Repository for saved jobs
        """
        self.saved_job_repository = saved_job_repository
    
    async def execute(
        self,
        saved_job_id: UUID,
        user_id: int,
        saved_job_update: SavedJobUpdate,
    ) -> SavedJob:
        """
        Execute the use case.
        
        Args:
            saved_job_id: Saved job ID
            user_id: User ID
            saved_job_update: Update data
        
        Returns:
            Updated saved job
        
        Raises:
            ValueError: If saved job not found or user not authorized
        """
        logger.info(f"Updating saved job {saved_job_id} for user {user_id}")
        
        # Get saved job
        saved_job = await self.saved_job_repository.get_by_id(saved_job_id)
        if not saved_job:
            logger.warning(f"Saved job not found: {saved_job_id}")
            raise ValueError("Saved job not found")
        
        # Verify ownership
        if saved_job.user_id != user_id:
            logger.warning(f"User {user_id} not authorized to update saved job {saved_job_id}")
            raise ValueError("Not authorized to update this saved job")
        
        # Update saved job
        try:
            updated_saved_job = await self.saved_job_repository.update(saved_job_id, saved_job_update)
            logger.info(f"Saved job updated successfully: {saved_job_id}")
            return updated_saved_job
        except Exception as e:
            logger.error(f"Error updating saved job: {str(e)}")
            raise ValueError(f"Failed to update saved job: {str(e)}")
