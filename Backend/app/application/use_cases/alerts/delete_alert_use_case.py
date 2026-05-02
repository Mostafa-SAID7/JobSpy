"""
Delete Alert Use Case

Handles deleting an alert with authorization.
"""

from uuid import UUID
from app.domain.interfaces.repositories import IAlertRepository as AlertRepository
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException


class DeleteAlertUseCase:
    """Use case for deleting an alert."""

    def __init__(self, alert_repository: AlertRepository):
        """
        Initialize the use case.

        Args:
            alert_repository: Repository for alert operations
        """
        self._alert_repository = alert_repository

    async def execute(self, alert_id: UUID, user_id: UUID) -> bool:
        """
        Delete an alert with authorization check.

        Args:
            alert_id: ID of the alert to delete
            user_id: ID of the user requesting the deletion

        Returns:
            bool: True if deletion was successful

        Raises:
            NotFoundException: If alert is not found
            AuthorizationException: If user is not authorized to delete the alert
        """
        # Get the alert
        alert = await self._alert_repository.get_by_id(alert_id)
        
        if not alert:
            raise NotFoundException(f"Alert with ID {alert_id} not found")
        
        # Check authorization
        if alert.user_id != user_id:
            raise AuthorizationException("Not authorized to delete this alert")
        
        # Delete the alert
        success = await self._alert_repository.delete(alert_id)
        
        if not success:
            raise NotFoundException(f"Alert with ID {alert_id} not found")
        
        return success
