"""
Create Job Use Case

Handles creation of new job postings.
"""

import logging
from typing import Dict, Any

from app.domain.entities.job import Job
from app.domain.interfaces.repositories import IJobRepository
from app.domain.services.skill_extraction_service import SkillExtractionService
from app.application.mappers.job_mapper import JobMapper

logger = logging.getLogger(__name__)


class CreateJobUseCase:
    """
    Use Case: Create a new job posting.
    
    Responsibilities:
    1. Validate job data
    2. Check for duplicates
    3. Extract skills
    4. Save to repository
    
    Used by: Admin API, Manual job posting
    """
    
    def __init__(
        self,
        job_repository: IJobRepository,
        skill_service: SkillExtractionService,
        job_mapper: JobMapper,
    ):
        """
        Initialize use case.
        
        Args:
            job_repository: Repository for job persistence
            skill_service: Service for extracting skills
            job_mapper: Mapper for converting data to entities
        """
        self.job_repository = job_repository
        self.skill_service = skill_service
        self.job_mapper = job_mapper
    
    async def execute(self, job_data: Dict[str, Any], source: str) -> Job:
        """
        Execute the use case.
        
        Args:
            job_data: Job data dictionary
            source: Job source
        
        Returns:
            Created job entity
        
        Raises:
            ValueError: If job already exists or validation fails
        """
        logger.info(f"Creating job: {job_data.get('title')} from {source}")
        
        # Parse to domain entity
        job = self.job_mapper.from_dict(job_data, source)
        
        # Check for duplicates
        existing_job = await self.job_repository.get_by_source_url(job.source_url)
        if existing_job:
            raise ValueError(f"Job already exists with URL: {job.source_url}")
        
        # Extract skills
        skills = self.skill_service.extract_skills(
            job.description,
            job.requirements
        )
        job.skills = skills
        
        # Save
        saved_job = await self.job_repository.save(job)
        
        logger.info(f"Job created successfully: {saved_job.id}")
        
        return saved_job
