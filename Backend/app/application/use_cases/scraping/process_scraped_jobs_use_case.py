"""
Process Scraped Jobs Use Case

Orchestrates the complete pipeline for processing scraped jobs.
This replaces the god class JobProcessingService.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any

from app.domain.entities.job import Job
from app.domain.interfaces.repositories import IJobRepository
from app.domain.interfaces.cache_repository import ICacheRepository
from app.domain.services.job_scoring_service import JobScoringService
from app.domain.services.skill_extraction_service import SkillExtractionService
from app.application.mappers.job_mapper import JobMapper

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """
    Result of processing scraped jobs.
    
    Attributes:
        saved_count: Number of jobs successfully saved
        duplicate_count: Number of duplicate jobs skipped
        error_count: Number of jobs that failed processing
        total_processed: Total number of jobs processed
        processed_jobs: List of successfully processed jobs
    """
    
    saved_count: int
    duplicate_count: int
    error_count: int
    total_processed: int
    processed_jobs: List[Job]


class ProcessScrapedJobsUseCase:
    """
    Use Case: Process scraped jobs from external sources.
    
    Responsibilities:
    1. Parse raw job data into domain entities
    2. Extract skills from descriptions
    3. Calculate job scores
    4. Check for duplicates
    5. Save to repository
    
    This is the SINGLE entry point for processing scraped jobs.
    Replaces the scattered logic in JobProcessingService.
    """
    
    def __init__(
        self,
        job_repository: IJobRepository,
        cache_repository: ICacheRepository,
        scoring_service: JobScoringService,
        skill_service: SkillExtractionService,
        job_mapper: JobMapper,
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            job_repository: Repository for job persistence
            cache_repository: Repository for caching
            scoring_service: Service for calculating job scores
            skill_service: Service for extracting skills
            job_mapper: Mapper for converting raw data to domain entities
        """
        self.job_repository = job_repository
        self.cache_repository = cache_repository
        self.scoring_service = scoring_service
        self.skill_service = skill_service
        self.job_mapper = job_mapper
    
    async def execute(
        self,
        jobs_data: List[Dict[str, Any]],
        source: str
    ) -> ProcessingResult:
        """
        Execute the use case.
        
        Pipeline:
        1. Raw Data → Domain Entity (via mapper)
        2. Extract Skills (domain service)
        3. Calculate Score (domain service)
        4. Check Duplicates (repository)
        5. Save (repository)
        
        Args:
            jobs_data: List of raw job dictionaries from scraper
            source: Job source (LinkedIn, Indeed, Wuzzuf, Bayt)
        
        Returns:
            ProcessingResult with statistics
        """
        saved_count = 0
        duplicate_count = 0
        error_count = 0
        processed_jobs: List[Job] = []
        
        logger.info(f"Processing {len(jobs_data)} jobs from {source}")
        
        for job_data in jobs_data:
            try:
                # Step 1: Parse raw data to domain entity
                job = self.job_mapper.from_dict(job_data, source)
                
                # Step 2: Extract skills
                skills = self.skill_service.extract_skills(
                    job.description,
                    job.requirements
                )
                # Update job with extracted skills
                job.skills = skills
                
                # Step 3: Calculate score (for ranking/recommendations)
                score = self.scoring_service.calculate_score(job)
                # Note: Score is calculated but not stored in entity
                # It can be stored in a separate analytics table if needed
                
                # Step 4: Check for duplicates
                if await self.job_repository.exists_by_url(job.source_url):
                    duplicate_count += 1
                    logger.debug(f"Duplicate job skipped: {job.source_url}")
                    continue
                
                # Step 5: Save to repository
                saved_job = await self.job_repository.save(job)
                processed_jobs.append(saved_job)
                saved_count += 1
                
                logger.debug(f"Job saved: {saved_job.title} at {saved_job.company}")
                
            except Exception as e:
                error_count += 1
                logger.error(
                    f"Error processing job from {source}: {str(e)}",
                    exc_info=True
                )
                continue
        
        result = ProcessingResult(
            saved_count=saved_count,
            duplicate_count=duplicate_count,
            error_count=error_count,
            total_processed=len(jobs_data),
            processed_jobs=processed_jobs
        )
        logger.info(
            f"Processing complete: {saved_count} saved, "
            f"{duplicate_count} duplicates, {error_count} errors"
        )
        
        # Clear cache after successful scraping to ensure new jobs are visible
        if saved_count > 0:
            logger.info(f"Clearing cache after saving {saved_count} jobs")
            await self.cache_repository.clear()
            
        return result
    
    async def execute_single(
        self,
        job_data: Dict[str, Any],
        source: str
    ) -> Job:
        """
        Process a single job.
        
        Useful for testing or processing individual jobs.
        
        Args:
            job_data: Raw job dictionary
            source: Job source
        
        Returns:
            Processed and saved job entity
        
        Raises:
            ValueError: If job already exists or validation fails
        """
        # Parse to domain entity
        job = self.job_mapper.from_dict(job_data, source)
        
        # Extract skills
        skills = self.skill_service.extract_skills(
            job.description,
            job.requirements
        )
        job.skills = skills
        
        # Check for duplicates
        if await self.job_repository.exists_by_url(job.source_url):
            raise ValueError(f"Job already exists: {job.source_url}")
        
        # Save
        saved_job = await self.job_repository.save(job)
        
        return saved_job
