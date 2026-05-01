"""
Get Job Details Use Case

Retrieves detailed information about a specific job.
"""

import logging
from uuid import UUID
from typing import Optional

from app.domain.entities.job import Job
from app.domain.interfaces.repositories import IJobRepository
from app.domain.interfaces.cache_repository import ICacheRepository

logger = logging.getLogger(__name__)


class GetJobDetailsUseCase:
    """
    Use Case: Get detailed job information.
    
    Responsibilities:
    1. Check cache first
    2. Retrieve from repository if not cached
    3. Increment view count
    4. Cache the result
    
    Used by: Job details page, API endpoints
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
        increment_views: bool = True
    ) -> Optional[Job]:
        """
        Execute the use case.
        
        Args:
            job_id: Job ID
            increment_views: Whether to increment view count
        
        Returns:
            Job entity or None if not found
        """
        logger.debug(f"Fetching job details: {job_id}")
        
        # Try cache first
        cache_key = f"job:{job_id}"
        cached_job = await self.cache_repository.get(cache_key)
        
        if cached_job:
            logger.debug(f"Cache hit for job: {job_id}")
            job = cached_job
        else:
            # Fetch from repository
            job = await self.job_repository.get_by_id(job_id)
            
            if not job:
                logger.warning(f"Job not found: {job_id}")
                return None
            
            # Cache for future requests
            await self.cache_repository.set(
                cache_key,
                job,
                ttl=3600  # 1 hour
            )
        
        # Increment view count if requested
        if increment_views and job:
            job.increment_views()
            await self.job_repository.update(job)
        
        return job
