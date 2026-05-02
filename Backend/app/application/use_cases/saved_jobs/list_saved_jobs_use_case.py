"""
List Saved Jobs Use Case

Handles listing saved jobs for a user.
"""

import logging
from dataclasses import dataclass
from typing import List

from app.models.saved_job import SavedJob
from app.repositories.saved_job_repo import SavedJobRepository

logger = logging.getLogger(__name__)


@dataclass
class ListSavedJobsResult:
    """Result of listing saved jobs"""
    saved_jobs: List[SavedJob]
    total_count: int
    page: int
    page_size: int


class ListSavedJobsUseCase:
    """
    Use Case: List saved jobs for a user.
    
    Responsibilities:
    1. Retrieve saved jobs for user
    2. Apply pagination
    3. Return with metadata
    
    Used by: List saved jobs endpoint
    """
    
    def __init__(self, saved_job_repository: SavedJobRepository):
        """
        Initialize use case.
        
        Args:
            saved_job_repository: Repository for saved jobs
        """
        self.saved_job_repository = saved_job_repository
    
    async def execute(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> ListSavedJobsResult:
        """
        Execute the use case.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            ListSavedJobsResult with saved jobs and metadata
        """
        logger.debug(f"Listing saved jobs for user {user_id}: skip={skip}, limit={limit}")
        
        # Get saved jobs
        saved_jobs = await self.saved_job_repository.get_by_user(user_id, skip, limit)
        total_count = await self.saved_job_repository.count_by_user(user_id)
        
        page = (skip // limit) + 1
        
        logger.info(f"Found {len(saved_jobs)} saved jobs for user {user_id}")
        
        return ListSavedJobsResult(
            saved_jobs=saved_jobs,
            total_count=total_count,
            page=page,
            page_size=limit,
        )
