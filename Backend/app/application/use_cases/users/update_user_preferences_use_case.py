"""
Update User Preferences Use Case

Handles updating user preferences.
"""

from uuid import UUID
from pydantic import BaseModel
from app.domain.interfaces.repositories import IUserRepository as UserRepository
from app.shared.exceptions.application_exceptions import NotFoundException


class UserPreferences(BaseModel):
    """User preferences schema"""
    theme: str = "light"
    notifications_enabled: bool = True
    email_alerts: bool = True
    job_recommendations: bool = True
    saved_jobs_limit: int = 1000


class UpdateUserPreferencesUseCase:
    """Use case for updating user preferences."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the use case.

        Args:
            user_repository: Repository for user operations
        """
        self._user_repository = user_repository

    async def execute(
        self, 
        user_id: UUID, 
        preferences: UserPreferences
    ) -> UserPreferences:
        """
        Update user preferences.

        Args:
            user_id: ID of the user
            preferences: New preferences to set

        Returns:
            UserPreferences: The updated preferences

        Raises:
            NotFoundException: If user is not found
        """
        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        # Update preferences
        user.preferences = preferences.model_dump()
        
        # Invalidate user cache
        await self._user_repository.invalidate_user_cache(user_id)
        
        return preferences
