"""
Scraping Use Cases

Use cases related to job scraping and processing.
"""

from .process_scraped_jobs_use_case import ProcessScrapedJobsUseCase, ProcessingResult
from .scrape_jobs_use_case import ScrapeJobsUseCase, ScrapeJobsRequest

__all__ = [
    "ProcessScrapedJobsUseCase",
    "ProcessingResult",
    "ScrapeJobsUseCase",
    "ScrapeJobsRequest",
]
