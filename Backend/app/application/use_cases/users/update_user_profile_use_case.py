"""
Update User Profile Use Case

Handles updating user profile information.
"""

from uuid import UUID
from app.presentation.api.v1.schemas.user import UserUpdate, UserResponse
from app.domain.interfaces.repositories import IUserRepository as UserRepository
from app.shared.exceptions.application_exceptions import NotFoundException, DuplicateEntityError


class UpdateUserProfileUseCase:
    """Use case for updating user profile."""

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
        user_update: UserUpdate,
        current_email: str
    ) -> UserResponse:
        """
        Update user profile.

        Args:
            user_id: ID of the user to update
            user_update: User update data
            current_email: Current email of the user (for validation)

        Returns:
            UserResponse: The updated user profile

        Raises:
            NotFoundException: If user is not found
            DuplicateEntityError: If email is already in use
        """
        # Check if email is being changed and if it's already taken
        if user_update.email and user_update.email != current_email:
            existing_user = await self._user_repository.get_by_email(user_update.email)
            if existing_user:
                raise DuplicateEntityError("User", user_update.email)
        
        # Update the user
        updated_user = await self._user_repository.update(user_id, user_update)
        
        if not updated_user:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        # Invalidate user cache
        await self._user_repository.invalidate_user_cache(user_id)
        if user_update.email and user_update.email != current_email:
            await self._user_repository.invalidate_user_email_cache(current_email)
            await self._user_repository.invalidate_user_email_cache(user_update.email)
        
        return UserResponse.model_validate(updated_user)
