"""
List Alerts Use Case

Handles retrieving all alerts for a user with pagination.
"""

from uuid import UUID
from app.schemas.alert import AlertListResponse
from app.repositories.alert_repo import AlertRepository


class ListAlertsUseCase:
    """Use case for listing user alerts with pagination."""

    def __init__(self, alert_repository: AlertRepository):
        """
        Initialize the use case.

        Args:
            alert_repository: Repository for alert operations
        """
        self._alert_repository = alert_repository

    async def execute(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> AlertListResponse:
        """
        List all alerts for a user with pagination.

        Args:
            user_id: ID of the user
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            AlertListResponse: Paginated list of alerts
        """
        # Get alerts for the user
        alerts = await self._alert_repository.get_by_user(user_id, skip, limit)
        
        # Get total count
        total = await self._alert_repository.count_by_user(user_id)
        
        return AlertListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            items=alerts
        )
