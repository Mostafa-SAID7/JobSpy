"""
Change Password Use Case

Handles changing user password with current password verification.
"""

from uuid import UUID
from app.repositories.user_repo import UserRepository
from app.utils.security import verify_password, hash_password
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException


class ChangePasswordUseCase:
    """Use case for changing user password."""

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
        current_password: str, 
        new_password: str
    ) -> dict:
        """
        Change user password.

        Args:
            user_id: ID of the user
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            dict: Success message

        Raises:
            NotFoundException: If user is not found
            AuthorizationException: If current password is incorrect
        """
        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise AuthorizationException("Current password is incorrect")
        
        # Update password
        user.hashed_password = hash_password(new_password)
        
        # Invalidate user cache
        await self._user_repository.invalidate_user_cache(user_id)
        
        return {"message": "Password changed successfully"}
