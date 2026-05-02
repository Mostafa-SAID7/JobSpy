"""
Delete Saved Job Use Case

Handles deleting a saved job.
"""

import logging
from uuid import UUID

from app.domain.interfaces.repositories import ISavedJobRepository as SavedJobRepository

logger = logging.getLogger(__name__)


class DeleteSavedJobUseCase:
    """
    Use Case: Delete a saved job.
    
    Responsibilities:
    1. Check if saved job exists
    2. Verify user ownership
    3. Delete saved job
    
    Used by: Delete saved job endpoint
    """
    
    def __init__(self, saved_job_repository: SavedJobRepository):
        """
        Initialize use case.
        
        Args:
            saved_job_repository: Repository for saved jobs
        """
        self.saved_job_repository = saved_job_repository
    
    async def execute(self, saved_job_id: UUID, user_id: int) -> bool:
        """
        Execute the use case.
        
        Args:
            saved_job_id: Saved job ID
            user_id: User ID
        
        Returns:
            True if deleted successfully
        
        Raises:
            ValueError: If saved job not found or user not authorized
        """
        logger.info(f"Deleting saved job {saved_job_id} for user {user_id}")
        
        # Get saved job
        saved_job = await self.saved_job_repository.get_by_id(saved_job_id)
        if not saved_job:
            logger.warning(f"Saved job not found: {saved_job_id}")
            raise ValueError("Saved job not found")
        
        # Verify ownership
        if saved_job.user_id != user_id:
            logger.warning(f"User {user_id} not authorized to delete saved job {saved_job_id}")
            raise ValueError("Not authorized to delete this saved job")
        
        # Delete saved job
        try:
            success = await self.saved_job_repository.delete(saved_job_id)
            if success:
                logger.info(f"Saved job deleted successfully: {saved_job_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting saved job: {str(e)}")
            raise ValueError(f"Failed to delete saved job: {str(e)}")
