"""
Update Alert Use Case

Handles updating an existing alert with authorization.
"""

from uuid import UUID
from app.schemas.alert import AlertUpdate, AlertResponse
from app.repositories.alert_repo import AlertRepository
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException


class UpdateAlertUseCase:
    """Use case for updating an alert."""

    def __init__(self, alert_repository: AlertRepository):
        """
        Initialize the use case.

        Args:
            alert_repository: Repository for alert operations
        """
        self._alert_repository = alert_repository

    async def execute(
        self, 
        alert_id: UUID, 
        user_id: UUID, 
        alert_update: AlertUpdate
    ) -> AlertResponse:
        """
        Update an alert with authorization check.

        Args:
            alert_id: ID of the alert to update
            user_id: ID of the user requesting the update
            alert_update: Alert update data

        Returns:
            AlertResponse: The updated alert

        Raises:
            NotFoundException: If alert is not found
            AuthorizationException: If user is not authorized to update the alert
        """
        # Get the alert
        alert = await self._alert_repository.get_by_id(alert_id)
        
        if not alert:
            raise NotFoundException(f"Alert with ID {alert_id} not found")
        
        # Check authorization
        if alert.user_id != user_id:
            raise AuthorizationException("Not authorized to update this alert")
        
        # Update the alert
        updated_alert = await self._alert_repository.update(alert_id, alert_update)
        
        if not updated_alert:
            raise NotFoundException(f"Alert with ID {alert_id} not found")
        
        return AlertResponse.model_validate(updated_alert)
