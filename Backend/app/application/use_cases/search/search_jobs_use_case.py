"""
Search Jobs Use Case

Handles basic job search with caching.
"""

import logging
import hashlib
import json
from typing import List
from dataclasses import dataclass

from app.domain.entities.job import Job
from app.domain.interfaces.repositories import IJobRepository
from app.domain.interfaces.cache_repository import ICacheRepository
from app.domain.services.job_scoring_service import JobScoringService

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result of job search"""
    query: str
    jobs: List[Job]
    total_count: int
    skip: int
    limit: int
    has_more: bool


class SearchJobsUseCase:
    """
    Use Case: Search for jobs by query.
    
    Responsibilities:
    1. Generate cache key
    2. Check cache
    3. Search repository if not cached
    4. Score and rank results
    5. Cache results
    
    Used by: Search page, API endpoints
    
    This replaces SearchService.search_jobs()
    """
    
    def __init__(
        self,
        job_repository: IJobRepository,
        cache_repository: ICacheRepository,
        scoring_service: JobScoringService,
    ):
        """
        Initialize use case.
        
        Args:
            job_repository: Repository for job persistence
            cache_repository: Repository for caching
            scoring_service: Service for scoring jobs
        """
        self.job_repository = job_repository
        self.cache_repository = cache_repository
        self.scoring_service = scoring_service
    
    async def execute(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> SearchResult:
        """
        Execute the use case.
        
        Args:
            query: Search query
            skip: Number of results to skip
            limit: Maximum number of results
        
        Returns:
            SearchResult with jobs and metadata
        """
        logger.info(f"Searching jobs: query='{query}', skip={skip}, limit={limit}")
        
        # Generate cache key
        cache_key = self._generate_cache_key(query, skip, limit)
        
        # Try cache first
        cached_result = await self.cache_repository.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for search: {query}")
            return cached_result
        
        # Search repository
        jobs = await self.job_repository.search(query, skip, limit)
        
        # Score jobs for ranking (optional - can be done at display time)
        # scored_jobs = [(job, self.scoring_service.calculate_score(job)) for job in jobs]
        # jobs = [job for job, score in sorted(scored_jobs, key=lambda x: x[1], reverse=True)]
        
        # Get total count (for pagination)
        # Note: This is a simplified version. In production, you'd want a count_search method
        total_count = len(jobs)  # Approximate
        
        # Create result
        result = SearchResult(
            query=query,
            jobs=jobs,
            total_count=total_count,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total_count,
        )
        
        # Cache the result
        await self.cache_repository.set(
            cache_key,
            result,
            ttl=1800  # 30 minutes
        )
        
        logger.info(f"Search complete: {len(jobs)} jobs found")
        
        return result
    
    def _generate_cache_key(self, query: str, skip: int, limit: int) -> str:
        """
        Generate cache key for search.
        
        Args:
            query: Search query
            skip: Skip value
            limit: Limit value
        
        Returns:
            Cache key string
        """
        return f"search:simple:{query}:{skip}:{limit}"
