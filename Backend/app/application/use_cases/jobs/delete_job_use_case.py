"""
Delete Job Use Case

Handles deletion of job postings.
"""

import logging
from uuid import UUID

from app.domain.interfaces.repositories import IJobRepository
from app.domain.interfaces.cache_repository import ICacheRepository

logger = logging.getLogger(__name__)


class DeleteJobUseCase:
    """
    Use Case: Delete a job posting.
    
    Responsibilities:
    1. Verify job exists
    2. Delete from repository
    3. Invalidate cache
    
    Used by: Admin API, Job management
    """
    
    def __init__(
        self,
        job_repository: IJobRepository,
        cache_repository: ICacheRepository,
    ):
        """
        Initialize use case.
        
        Args:
            job_repository: Repository for job persistence
            cache_repository: Repository for caching
        """
        self.job_repository = job_repository
        self.cache_repository = cache_repository
    
    async def execute(self, job_id: UUID) -> bool:
        """
        Execute the use case.
        
        Args:
            job_id: Job ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting job: {job_id}")
        
        # Delete from repository
        deleted = await self.job_repository.delete(job_id)
        
        if not deleted:
            logger.warning(f"Job not found for deletion: {job_id}")
            return False
        
        # Invalidate cache
        cache_key = f"job:{job_id}"
        await self.cache_repository.delete(cache_key)
        
        # Also invalidate list caches
        await self.cache_repository.delete_pattern("jobs:*")
        
        logger.info(f"Job deleted successfully: {job_id}")
        
        return True
