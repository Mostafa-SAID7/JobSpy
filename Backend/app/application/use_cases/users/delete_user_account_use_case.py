"""
Delete User Account Use Case

Handles deleting a user account.
"""

from uuid import UUID
from app.domain.interfaces.repositories import IUserRepository as UserRepository
from app.shared.exceptions.application_exceptions import NotFoundException


class DeleteUserAccountUseCase:
    """Use case for deleting user account."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the use case.

        Args:
            user_repository: Repository for user operations
        """
        self._user_repository = user_repository

    async def execute(self, user_id: UUID) -> bool:
        """
        Delete user account.

        Args:
            user_id: ID of the user to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            NotFoundException: If user is not found
        """
        success = await self._user_repository.delete(user_id)
        
        if not success:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        # Invalidate user cache
        await self._user_repository.invalidate_user_cache(user_id)
        
        return success
