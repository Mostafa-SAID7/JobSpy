"""
Unsave Job Use Case

Handles unsaving a job by job ID.
"""

import logging
from uuid import UUID

from app.domain.interfaces.repositories import ISavedJobRepository as SavedJobRepository

logger = logging.getLogger(__name__)


class UnsaveJobUseCase:
    """
    Use Case: Unsave a job by job ID.
    
    Responsibilities:
    1. Delete saved job by user and job ID
    2. Return success status
    
    Used by: Unsave job endpoint
    """
    
    def __init__(self, saved_job_repository: SavedJobRepository):
        """
        Initialize use case.
        
        Args:
            saved_job_repository: Repository for saved jobs
        """
        self.saved_job_repository = saved_job_repository
    
    async def execute(self, user_id: int, job_id: UUID) -> bool:
        """
        Execute the use case.
        
        Args:
            user_id: User ID
            job_id: Job ID
        
        Returns:
            True if unsaved successfully
        
        Raises:
            ValueError: If saved job not found
        """
        logger.info(f"Unsaving job {job_id} for user {user_id}")
        
        # Delete saved job
        try:
            success = await self.saved_job_repository.delete_by_user_and_job(user_id, job_id)
            if not success:
                logger.warning(f"Saved job not found: user={user_id}, job={job_id}")
                raise ValueError("Saved job not found")
            
            logger.info(f"Job unsaved successfully: {job_id}")
            return success
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error unsaving job: {str(e)}")
            raise ValueError(f"Failed to unsave job: {str(e)}")
