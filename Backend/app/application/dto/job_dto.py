"""
Job Data Transfer Objects

DTOs for transferring job data between layers.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from app.domain.entities.job import Job


@dataclass
class JobDTO:
    """
    Data Transfer Object for Job.
    
    Used for API responses and inter-layer communication.
    Simpler than domain entity - only data, no business logic.
    """
    
    id: str
    title: str
    company: str
    location: str
    description: str
    job_type: str
    experience_level: str
    salary_range: Optional[str]
    requirements: List[str]
    skills: List[str]
    benefits: List[str]
    source: str
    source_url: str
    posted_date: datetime
    deadline: Optional[datetime]
    company_logo_url: Optional[str]
    company_website: Optional[str]
    view_count: int
    apply_count: int
    created_at: datetime
    
    @classmethod
    def from_entity(cls, job: Job) -> "JobDTO":
        """
        Create DTO from domain entity.
        
        Args:
            job: Job domain entity
        
        Returns:
            JobDTO instance
        """
        return cls(
            id=str(job.id),
            title=job.title,
            company=job.company,
            location=job.location.format(),
            description=job.description,
            job_type=job.job_type.value,
            experience_level=job.experience_level.value,
            salary_range=job.salary.format() if job.salary else None,
            requirements=job.requirements,
            skills=job.skills,
            benefits=job.benefits,
            source=job.source,
            source_url=job.source_url,
            posted_date=job.posted_date,
            deadline=job.deadline,
            company_logo_url=job.company_logo_url,
            company_website=job.company_website,
            view_count=job.view_count,
            apply_count=job.apply_count,
            created_at=job.created_at,
        )


@dataclass
class JobListDTO:
    """
    DTO for paginated job list.
    
    Used for list endpoints with pagination metadata.
    """
    
    jobs: List[JobDTO]
    total_count: int
    page: int
    page_size: int
    has_more: bool
    
    @classmethod
    def from_entities(
        cls,
        jobs: List[Job],
        total_count: int,
        page: int,
        page_size: int,
    ) -> "JobListDTO":
        """
        Create DTO from list of entities.
        
        Args:
            jobs: List of job entities
            total_count: Total number of jobs
            page: Current page number
            page_size: Number of jobs per page
        
        Returns:
            JobListDTO instance
        """
        job_dtos = [JobDTO.from_entity(job) for job in jobs]
        has_more = (page * page_size) < total_count
        
        return cls(
            jobs=job_dtos,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_more=has_more,
        )
