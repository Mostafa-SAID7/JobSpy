"""
List Jobs Use Case

Retrieves paginated list of jobs with optional filtering.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

from app.domain.entities.job import Job
from app.domain.interfaces.repositories import IJobRepository
from app.domain.interfaces.cache_repository import ICacheRepository

logger = logging.getLogger(__name__)


@dataclass
class ListJobsResult:
    """Result of listing jobs"""
    jobs: List[Job]
    total_count: int
    page: int
    page_size: int
    has_more: bool


class ListJobsUseCase:
    """
    Use Case: List jobs with pagination and filtering.
    
    Responsibilities:
    1. Apply filters
    2. Retrieve paginated results
    3. Cache results
    4. Return with metadata
    
    Used by: Job listing page, API endpoints
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
        skip: int = 0,
        limit: int = 20,
        source: Optional[str] = None,
    ) -> ListJobsResult:
        """
        Execute the use case.
        
        Args:
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
            source: Optional source filter
        
        Returns:
            ListJobsResult with jobs and metadata
        """
        logger.debug(f"Listing jobs: skip={skip}, limit={limit}, source={source}")
        
        # Generate cache key
        cache_key = f"jobs:list:{source or 'all'}:{skip}:{limit}"
        
        # Try cache first
        cached_result = await self.cache_repository.get(cache_key)
        if cached_result:
            logger.debug("Cache hit for job list")
            return cached_result
        
        # Fetch from repository
        if source:
            jobs = await self.job_repository.find_by_source(source, skip, limit)
        else:
            jobs = await self.job_repository.find_all(skip, limit)
        
        # Get total count
        total_count = await self.job_repository.count()
        
        # Calculate pagination metadata
        page = (skip // limit) + 1
        has_more = (skip + limit) < total_count
        
        result = ListJobsResult(
            jobs=jobs,
            total_count=total_count,
            page=page,
            page_size=limit,
            has_more=has_more,
        )
        
        # Cache the result
        await self.cache_repository.set(
            cache_key,
            result,
            ttl=1800  # 30 minutes
        )
        
        return result
