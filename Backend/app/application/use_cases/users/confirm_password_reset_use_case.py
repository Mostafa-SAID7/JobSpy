"""
Confirm Password Reset Use Case

Handles password reset confirmation with token.
"""

from datetime import datetime
from app.repositories.user_repo import UserRepository
from app.utils.security import hash_password
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException


class ConfirmPasswordResetUseCase:
    """Use case for confirming password reset."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the use case.

        Args:
            user_repository: Repository for user operations
        """
        self._user_repository = user_repository

    async def execute(self, token: str, new_password: str) -> dict:
        """
        Confirm password reset with token.

        Args:
            token: Password reset token
            new_password: New password to set

        Returns:
            dict: Success message

        Raises:
            NotFoundException: If token is invalid
            AuthorizationException: If token is expired
        """
        # Find user by reset token
        user = await self._user_repository.get_by_reset_token(token)
        
        if not user:
            raise NotFoundException("Invalid reset token")
        
        # Check if token is expired
        if user.password_reset_token_expires < datetime.utcnow():
            raise AuthorizationException("Reset token has expired")
        
        # Update password
        user.hashed_password = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_token_expires = None
        
        return {"message": "Password reset successfully"}
