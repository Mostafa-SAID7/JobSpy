"""
Get Alert Use Case

Handles retrieving a specific alert by ID with authorization.
"""

from uuid import UUID
from app.schemas.alert import AlertResponse
from app.repositories.alert_repo import AlertRepository
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException


class GetAlertUseCase:
    """Use case for retrieving an alert by ID."""

    def __init__(self, alert_repository: AlertRepository):
        """
        Initialize the use case.

        Args:
            alert_repository: Repository for alert operations
        """
        self._alert_repository = alert_repository

    async def execute(self, alert_id: UUID, user_id: UUID) -> AlertResponse:
        """
        Get an alert by ID with authorization check.

        Args:
            alert_id: ID of the alert to retrieve
            user_id: ID of the user requesting the alert

        Returns:
            AlertResponse: The requested alert

        Raises:
            NotFoundException: If alert is not found
            AuthorizationException: If user is not authorized to access the alert
        """
        # Get the alert
        alert = await self._alert_repository.get_by_id(alert_id)
        
        if not alert:
            raise NotFoundException(f"Alert with ID {alert_id} not found")
        
        # Check authorization
        if alert.user_id != user_id:
            raise AuthorizationException("Not authorized to access this alert")
        
        return AlertResponse.model_validate(alert)
