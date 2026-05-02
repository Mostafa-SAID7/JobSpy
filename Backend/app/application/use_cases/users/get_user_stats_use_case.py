"""
Get User Stats Use Case

Handles retrieving user statistics (saved jobs, alerts, searches).
"""

from uuid import UUID
from app.domain.interfaces.repositories import ISavedJobRepository as SavedJobRepository
from app.domain.interfaces.repositories import IAlertRepository as AlertRepository
from app.domain.interfaces.repositories import ISearchHistoryRepository as SearchHistoryRepository


class GetUserStatsUseCase:
    """Use case for retrieving user statistics."""

    def __init__(
        self,
        saved_job_repository: SavedJobRepository,
        alert_repository: AlertRepository,
        search_history_repository: SearchHistoryRepository,
    ):
        """
        Initialize the use case.

        Args:
            saved_job_repository: Repository for saved job operations
            alert_repository: Repository for alert operations
            search_history_repository: Repository for search history operations
        """
        self._saved_job_repository = saved_job_repository
        self._alert_repository = alert_repository
        self._search_history_repository = search_history_repository

    async def execute(self, user_id: UUID) -> dict:
        """
        Get user statistics.

        Args:
            user_id: ID of the user

        Returns:
            dict: User statistics including saved jobs, alerts, and searches
        """
        # Get counts
        saved_jobs_count = await self._saved_job_repository.count_by_user(user_id)
        alerts_count = await self._alert_repository.count_by_user(user_id)
        searches_count = await self._search_history_repository.count_by_user(user_id)
        
        return {
            "saved_jobs": saved_jobs_count,
            "active_alerts": alerts_count,
            "total_searches": searches_count
        }
