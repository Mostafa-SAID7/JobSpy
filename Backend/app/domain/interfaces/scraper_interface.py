"""
Job Scraper Interface

Contract for job scrapers that infrastructure must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ScraperConfig:
    """Configuration for job scrapers"""
    
    timeout: int = 30
    retries: int = 3
    delay: int = 1
    max_results: int = 100
    user_agent: Optional[str] = None
    
    # python-jobspy specific parameters
    site_name: Optional[List[str]] = None
    location: Optional[str] = None
    distance: Optional[int] = 50
    job_type: Optional[str] = None
    is_remote: Optional[bool] = False
    easy_apply: Optional[bool] = None
    hours_old: Optional[int] = None
    country_indeed: Optional[str] = 'USA'
    enforce_annual_salary: Optional[bool] = False
    proxies: Optional[List[str]] = None
    linkedin_fetch_description: Optional[bool] = False


class IJobScraper(ABC):
    """
    Interface for job scrapers.
    
    Each job board (LinkedIn, Indeed, etc.) must implement this interface.
    This enables pluggable scrapers and easy testing.
    """
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """
        Name of the job source.
        
        Returns:
            Source name (e.g., "LinkedIn", "Indeed")
        """
        pass
    
    @abstractmethod
    async def scrape_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Scrape jobs from source.
        
        Args:
            query: Search query
            location: Job location
            **kwargs: Additional scraper-specific parameters
        
        Returns:
            List of raw job dictionaries
        
        Raises:
            ScraperException: If scraping fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if scraper is operational.
        
        Returns:
            True if operational, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed job information.
        
        Args:
            job_url: Job URL
        
        Returns:
            Job details dictionary or None if not found
        """
        pass
