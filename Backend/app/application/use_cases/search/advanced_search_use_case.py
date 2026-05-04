"""
Advanced Search Use Case

Handles complex job search with multiple filters.
"""

import logging
import hashlib
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from decimal import Decimal

from app.domain.entities.job import Job
from app.domain.interfaces.repositories import IJobRepository
from app.domain.interfaces.cache_repository import ICacheRepository
from app.domain.services.job_scoring_service import JobScoringService
from app.domain.value_objects.job_type import JobType
from app.domain.value_objects.experience_level import ExperienceLevel

logger = logging.getLogger(__name__)


@dataclass
class AdvancedSearchRequest:
    """Request for advanced search"""
    query: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_remote: Optional[bool] = None
    source: Optional[str] = None
    skills: Optional[List[str]] = None
    posted_date: Optional[int] = None  # Number of days (1, 7, 30, 90)
    skip: int = 0
    limit: int = 20


@dataclass
class AdvancedSearchResult:
    """Result of advanced search"""
    query: str
    filters: Dict[str, Any]
    jobs: List[Job]
    total_count: int
    skip: int
    limit: int
    has_more: bool


class AdvancedSearchUseCase:
    """
    Use Case: Advanced job search with multiple filters.
    
    Responsibilities:
    1. Parse and validate filters
    2. Generate cache key from all parameters
    3. Check cache
    4. Apply filters and search
    5. Score and rank results
    6. Cache results
    
    Used by: Advanced search page, API endpoints
    
    This replaces SearchService.advanced_search()
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
    
    async def execute(self, request: AdvancedSearchRequest) -> AdvancedSearchResult:
        """
        Execute the use case.
        
        Args:
            request: Advanced search request with filters
        
        Returns:
            AdvancedSearchResult with filtered jobs
        """
        logger.info(
            f"Advanced search: query='{request.query}', "
            f"location={request.location}, job_type={request.job_type}"
        )
        
        # Generate cache key from all parameters
        cache_key = self._generate_cache_key(request)
        
        # Try cache first
        cached_result = await self.cache_repository.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for advanced search: {request.query}")
            return cached_result
        
        # Search with basic query first
        jobs = await self.job_repository.search(
            request.query,
            request.skip,
            request.limit
        )
        
        # Apply filters in memory (ideally this would be in repository)
        filtered_jobs = self._apply_filters(jobs, request)
        
        # Score and rank
        scored_jobs = [
            (job, self.scoring_service.calculate_score(job))
            for job in filtered_jobs
        ]
        ranked_jobs = [
            job for job, score in sorted(scored_jobs, key=lambda x: x[1], reverse=True)
        ]
        
        # Build filters dict for response
        filters = self._build_filters_dict(request)
        
        # Create result
        result = AdvancedSearchResult(
            query=request.query,
            filters=filters,
            jobs=ranked_jobs,
            total_count=len(ranked_jobs),
            skip=request.skip,
            limit=request.limit,
            has_more=(request.skip + request.limit) < len(ranked_jobs),
        )
        
        # Cache the result
        await self.cache_repository.set(
            cache_key,
            result,
            ttl=1800  # 30 minutes
        )
        
        logger.info(f"Advanced search complete: {len(ranked_jobs)} jobs found")
        
        return result
    
    def _apply_filters(
        self,
        jobs: List[Job],
        request: AdvancedSearchRequest
    ) -> List[Job]:
        """
        Apply filters to job list.
        
        Args:
            jobs: List of jobs to filter
            request: Search request with filters
        
        Returns:
            Filtered list of jobs
        """
        filtered = jobs
        
        # Location filter
        if request.location:
            filtered = [
                job for job in filtered
                if job.location.matches_location(request.location)
            ]
        
        # Job type filter
        if request.job_type:
            job_type_enum = JobType.from_string(request.job_type)
            filtered = [
                job for job in filtered
                if job.job_type == job_type_enum
            ]
        
        # Experience level filter
        if request.experience_level:
            exp_level_enum = ExperienceLevel.from_string(request.experience_level)
            filtered = [
                job for job in filtered
                if job.experience_level == exp_level_enum
            ]
        
        # Salary filters
        if request.salary_min:
            salary_min = Decimal(str(request.salary_min))
            filtered = [
                job for job in filtered
                if job.salary and job.salary.max_amount and job.salary.max_amount >= salary_min
            ]
        
        if request.salary_max:
            salary_max = Decimal(str(request.salary_max))
            filtered = [
                job for job in filtered
                if job.salary and job.salary.min_amount and job.salary.min_amount <= salary_max
            ]
        
        # Remote filter
        if request.is_remote is not None:
            if request.is_remote:
                filtered = [job for job in filtered if job.is_remote() or job.is_hybrid()]
            else:
                filtered = [job for job in filtered if job.is_on_site()]
        
        # Source filter
        if request.source:
            filtered = [
                job for job in filtered
                if job.source.lower() == request.source.lower()
            ]
        
        # Skills filter
        if request.skills:
            filtered = [
                job for job in filtered
                if job.matches_skills(request.skills)
            ]
        
        # Posted date filter
        if request.posted_date:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=request.posted_date)
            filtered = [
                job for job in filtered
                if job.posted_date >= cutoff_date
            ]
        
        return filtered
    
    def _generate_cache_key(self, request: AdvancedSearchRequest) -> str:
        """
        Generate cache key from all search parameters.
        
        Args:
            request: Search request
        
        Returns:
            Cache key string
        """
        # Create normalized filter dictionary
        filters = self._build_filters_dict(request)
        
        # Create deterministic string
        filter_str = json.dumps(filters, sort_keys=True, default=str)
        
        # Hash for reasonable key length
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
        
        return f"search:advanced:{request.query}:{filter_hash}:{request.skip}:{request.limit}"
    
    def _build_filters_dict(self, request: AdvancedSearchRequest) -> Dict[str, Any]:
        """
        Build filters dictionary from request.
        
        Args:
            request: Search request
        
        Returns:
            Filters dictionary
        """
        filters = {}
        
        if request.location:
            filters["location"] = request.location
        if request.job_type:
            filters["job_type"] = request.job_type
        if request.experience_level:
            filters["experience_level"] = request.experience_level
        if request.salary_min is not None:
            filters["salary_min"] = request.salary_min
        if request.salary_max is not None:
            filters["salary_max"] = request.salary_max
        if request.is_remote is not None:
            filters["is_remote"] = request.is_remote
        if request.source:
            filters["source"] = request.source
        if request.skills:
            filters["skills"] = request.skills
        if request.posted_date is not None:
            filters["posted_date"] = request.posted_date
        
        return filters
