"""
Get User Profile Use Case

Handles retrieving the current user's profile.
"""

from uuid import UUID
from app.schemas.user import UserResponse
from app.repositories.user_repo import UserRepository
from app.shared.exceptions.application_exceptions import NotFoundException


class GetUserProfileUseCase:
    """Use case for retrieving user profile."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the use case.

        Args:
            user_repository: Repository for user operations
        """
        self._user_repository = user_repository

    async def execute(self, user_id: UUID) -> UserResponse:
        """
        Get user profile by ID.

        Args:
            user_id: ID of the user

        Returns:
            UserResponse: The user profile

        Raises:
            NotFoundException: If user is not found
        """
        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        return UserResponse.model_validate(user)
