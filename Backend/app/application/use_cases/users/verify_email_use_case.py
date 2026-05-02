"""
Verify Email Use Case

Handles email verification with token.
"""

from datetime import datetime
from app.domain.interfaces.repositories import IUserRepository as UserRepository
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException


class VerifyEmailUseCase:
    """Use case for verifying user email."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the use case.

        Args:
            user_repository: Repository for user operations
        """
        self._user_repository = user_repository

    async def execute(self, token: str) -> dict:
        """
        Verify email with token.

        Args:
            token: Email verification token

        Returns:
            dict: Success message

        Raises:
            NotFoundException: If token is invalid
            AuthorizationException: If token is expired
        """
        # Find user by verification token
        user = await self._user_repository.get_by_verification_token(token)
        
        if not user:
            raise NotFoundException("Invalid verification token")
        
        # Check if token is expired
        if user.email_verification_token_expires < datetime.utcnow():
            raise AuthorizationException("Verification token has expired")
        
        # Mark email as verified
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_token_expires = None
        
        return {"message": "Email verified successfully"}
