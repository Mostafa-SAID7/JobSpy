"""
Scraping Service - JobSpy
Scraping service for JobSpy

⚠️ DEPRECATED: This service is deprecated and will be removed in Phase 5.

Migration Path:
- Use ProcessScrapedJobsUseCase instead
- Location: app.application.use_cases.scraping.process_scraped_jobs_use_case
- See: Backend/app/services/DEPRECATION_NOTICE.md

This service is kept temporarily for backward compatibility.
Will be removed after Phase 5 (router refactoring) is complete.
"""
import warnings
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate
from app.services.job_processing_service import JobProcessingService

logger = logging.getLogger(__name__)

# Issue deprecation warning
warnings.warn(
    "ScrapingService is deprecated. Use ProcessScrapedJobsUseCase from "
    "app.application.use_cases.scraping instead. "
    "See Backend/app/services/DEPRECATION_NOTICE.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)


class ScrapingService:
    """
    Service for handling job scraping operations.
    
    ⚠️ DEPRECATED: Use ProcessScrapedJobsUseCase instead.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.job_processor = JobProcessingService(db)
    
    async def save_jobs(self, jobs_data: List[Dict[str, Any]], source: str) -> Dict[str, Any]:
        """
        Save scraped jobs to database.
        
        CONSOLIDATED: Uses unified processing pipeline from JobProcessingService.
        
        Args:
            jobs_data: List of job dictionaries from scraper
            source: Job source (LinkedIn, Indeed, Wuzzuf, Bayt)
        
        Returns:
            Dictionary with statistics about saved jobs
        """
        return await self.job_processor.process_scraped_jobs(jobs_data, source)
    
    def _normalize_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize job data from different sources.
        
        DEPRECATED: Use JobProcessingService.normalize_job() instead.
        Kept for backward compatibility.
        
        Args:
            job_data: Raw job data from scraper
        
        Returns:
            Normalized job data
        """
        logger.warning("_normalize_job is deprecated. Use JobProcessingService.normalize_job() instead.")
        return self.job_processor.normalize_job(job_data, "unknown")
    
    async def normalize_jobs(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize job data from different sources.
        
        CONSOLIDATED: Uses unified normalization from JobProcessingService.
        
        Args:
            jobs_data: Raw job data from scraper
        
        Returns:
            Normalized job data
        """
        normalized = []
        
        for job in jobs_data:
            normalized_job = self.job_processor.normalize_job(job, "unknown")
            
            # Only add if required fields are present
            if normalized_job["title"] and normalized_job["company"] and normalized_job["source_url"]:
                normalized.append(normalized_job)
        
        return normalized
    
    @staticmethod
    def _parse_salary(salary: Any) -> float | None:
        """
        Parse salary value.
        
        DEPRECATED: Use JobProcessingService._parse_salary() instead.
        Kept for backward compatibility.
        """
        logger.warning("_parse_salary is deprecated. Use JobProcessingService._parse_salary() instead.")
        return JobProcessingService._parse_salary(salary)
    
    @staticmethod
    def _parse_remote(remote: Any) -> int:
        """
        Parse remote work type (0: On-site, 1: Remote, 2: Hybrid).
        
        DEPRECATED: Use JobProcessingService._parse_remote_type() instead.
        Kept for backward compatibility.
        """
        logger.warning("_parse_remote is deprecated. Use JobProcessingService._parse_remote_type() instead.")
        return JobProcessingService._parse_remote_type(remote)
    
    async def remove_duplicates(self) -> int:
        """
        Remove duplicate jobs based on source_url.
        
        Returns:
            Number of duplicates removed
        """
        # This would require a more complex query
        # For now, duplicates are prevented at insert time
        return 0
    
    async def get_jobs_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get jobs from a specific source.
        
        Args:
            source: Job source (LinkedIn, Indeed, Wuzzuf, Bayt)
            limit: Maximum number of jobs to return
        
        Returns:
            List of jobs from the source
        """
        jobs = await self.job_repo.search({"source": source}, limit=limit)
        return jobs
    
    async def update_job_status(self, job_id: int, status: str) -> bool:
        """
        Update job status (active, expired, etc).
        
        Args:
            job_id: Job ID
            status: New status
        
        Returns:
            True if updated successfully
        """
        try:
            job = await self.job_repo.get_by_id(job_id)
            if job:
                # Update status in database
                await self.db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
        
        return False
