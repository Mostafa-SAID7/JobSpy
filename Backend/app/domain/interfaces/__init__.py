"""
Domain Interfaces - Contracts for infrastructure dependencies

These interfaces define contracts that infrastructure must implement.
This enables dependency inversion - domain doesn't depend on infrastructure.
"""

from .repositories import IJobRepository, IUserRepository, IAlertRepository
from .cache_repository import ICacheRepository
from .scraper_interface import IJobScraper

__all__ = [
    "IJobRepository",
    "IUserRepository",
    "IAlertRepository",
    "ICacheRepository",
    "IJobScraper",
]
