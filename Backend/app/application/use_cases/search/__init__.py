"""
Search Use Cases

Use cases for job search functionality.
"""

from .search_jobs_use_case import SearchJobsUseCase, SearchResult
from .advanced_search_use_case import AdvancedSearchUseCase, AdvancedSearchRequest

__all__ = [
    "SearchJobsUseCase",
    "SearchResult",
    "AdvancedSearchUseCase",
    "AdvancedSearchRequest",
]
