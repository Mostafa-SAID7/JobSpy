"""
Create Alert Use Case

Handles the creation of new job alerts for users.
"""

from uuid import UUID
from app.presentation.api.v1.schemas.alert import AlertCreate, AlertResponse
from app.domain.interfaces.repositories import IAlertRepository as AlertRepository


class CreateAlertUseCase:
    """Use case for creating a new alert."""

    def __init__(self, alert_repository: AlertRepository):
        """
        Initialize the use case.

        Args:
            alert_repository: Repository for alert operations
        """
        self._alert_repository = alert_repository

    async def execute(self, user_id: UUID, alert_create: AlertCreate) -> AlertResponse:
        """
        Create a new alert for the user.

        Args:
            user_id: ID of the user creating the alert
            alert_create: Alert creation data

        Returns:
            AlertResponse: The created alert

        Raises:
            ValueError: If alert data is invalid
        """
        # Create the alert
        alert = await self._alert_repository.create(user_id, alert_create)
        
        return AlertResponse.model_validate(alert)
