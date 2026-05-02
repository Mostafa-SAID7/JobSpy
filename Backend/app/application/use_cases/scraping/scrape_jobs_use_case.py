"""
Scrape Jobs Use Case

Orchestrates the scraping of jobs from various sources and 
delegates to the processing pipeline.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from app.domain.interfaces.scraper_interface import IJobScraper
from app.application.use_cases.scraping.process_scraped_jobs_use_case import ProcessScrapedJobsUseCase, ProcessingResult

logger = logging.getLogger(__name__)

@dataclass
class ScrapeJobsRequest:
    """Request for scraping jobs"""
    query: str
    location: Optional[str] = None
    site_names: Optional[List[str]] = None
    max_results: int = 50
    hours_old: Optional[int] = None
    job_type: Optional[str] = None
    is_remote: bool = False
    distance: Optional[int] = 50
    easy_apply: Optional[bool] = False
    country_indeed: str = 'USA'

class ScrapeJobsUseCase:
    """
    Use Case: Scrape and process jobs from external sources.
    
    Responsibilities:
    1. Call the scraper implementation
    2. Pass results to the processing pipeline
    3. Return consolidated statistics
    """
    
    def __init__(
        self,
        scraper: IJobScraper,
        process_use_case: ProcessScrapedJobsUseCase
    ):
        """
        Initialize with dependencies.
        
        Args:
            scraper: The scraper implementation (e.g. JobSpyLibraryScraper)
            process_use_case: Use case to handle normalization and persistence
        """
        self.scraper = scraper
        self.process_use_case = process_use_case
        
    async def execute(self, request: ScrapeJobsRequest) -> ProcessingResult:
        """
        Execute the scraping and processing pipeline.
        
        Args:
            request: Scrape request with filters and parameters
            
        Returns:
            ProcessingResult with statistics and jobs
        """
        logger.info(f"Starting scrape execution for query: {request.query}")
        
        # Call the scraper
        raw_jobs = await self.scraper.scrape_jobs(
            query=request.query,
            location=request.location,
            site_name=request.site_names,
            max_results=request.max_results,
            hours_old=request.hours_old,
            job_type=request.job_type,
            is_remote=request.is_remote,
            distance=request.distance,
            easy_apply=request.easy_apply,
            country_indeed=request.country_indeed
        )
        
        if not raw_jobs:
            logger.warning(f"No jobs found for query: {request.query}")
            return ProcessingResult(
                saved_count=0,
                duplicate_count=0,
                error_count=0,
                total_processed=0,
                processed_jobs=[]
            )
            
        # Process the raw jobs (map, clean, extract, save)
        result = await self.process_use_case.execute(
            jobs_data=raw_jobs,
            source=self.scraper.source_name
        )
        
        logger.info(f"Scrape execution complete. Saved {result.saved_count} jobs.")
        return result
