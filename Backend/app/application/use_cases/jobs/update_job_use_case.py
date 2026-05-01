"""
Update Job Use Case

Handles updating existing job postings.
"""

import logging
from uuid import UUID
from typing import Dict, Any, Optional

from app.domain.entities.job import Job
from app.domain.interfaces.repositories import IJobRepository
from app.domain.interfaces.cache_repository import ICacheRepository

logger = logging.getLogger(__name__)


class UpdateJobUseCase:
    """
    Use Case: Update an existing job posting.
    
    Responsibilities:
    1. Retrieve existing job
    2. Apply updates
    3. Validate changes
    4. Save to repository
    5. Invalidate cache
    
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
    
    async def execute(
        self,
        job_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[Job]:
        """
        Execute the use case.
        
        Args:
            job_id: Job ID to update
            updates: Dictionary of fields to update
        
        Returns:
            Updated job entity or None if not found
        
        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Updating job: {job_id}")
        
        # Retrieve existing job
        job = await self.job_repository.get_by_id(job_id)
        
        if not job:
            logger.warning(f"Job not found for update: {job_id}")
            return None
        
        # Apply updates using entity method
        job.update_details(
            title=updates.get("title"),
            description=updates.get("description"),
            requirements=updates.get("requirements"),
            benefits=updates.get("benefits"),
        )
        
        # Save updated job
        updated_job = await self.job_repository.update(job)
        
        # Invalidate cache
        cache_key = f"job:{job_id}"
        await self.cache_repository.delete(cache_key)
        
        logger.info(f"Job updated successfully: {job_id}")
        
        return updated_job
