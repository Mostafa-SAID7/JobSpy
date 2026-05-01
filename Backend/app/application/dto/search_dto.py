"""
Search Data Transfer Objects

DTOs for search requests and responses.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from .job_dto import JobDTO
from app.domain.entities.job import Job


@dataclass
class SearchRequestDTO:
    """
    DTO for search request.
    
    Used to transfer search parameters from API to use case.
    """
    
    query: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_remote: Optional[bool] = None
    source: Optional[str] = None
    skills: Optional[List[str]] = None
    skip: int = 0
    limit: int = 20


@dataclass
class SearchResponseDTO:
    """
    DTO for search response.
    
    Used to transfer search results from use case to API.
    """
    
    query: str
    filters: Dict[str, Any]
    results: List[JobDTO]
    total_count: int
    skip: int
    limit: int
    has_more: bool
    page: int
    
    @classmethod
    def from_jobs(
        cls,
        query: str,
        filters: Dict[str, Any],
        jobs: List[Job],
        total_count: int,
        skip: int,
        limit: int,
    ) -> "SearchResponseDTO":
        """
        Create DTO from search results.
        
        Args:
            query: Search query
            filters: Applied filters
            jobs: List of job entities
            total_count: Total number of results
            skip: Number of results skipped
            limit: Maximum results per page
        
        Returns:
            SearchResponseDTO instance
        """
        job_dtos = [JobDTO.from_entity(job) for job in jobs]
        page = (skip // limit) + 1 if limit > 0 else 1
        has_more = (skip + limit) < total_count
        
        return cls(
            query=query,
            filters=filters,
            results=job_dtos,
            total_count=total_count,
            skip=skip,
            limit=limit,
            has_more=has_more,
            page=page,
        )
