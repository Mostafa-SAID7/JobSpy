"""
Request Password Reset Use Case

Handles password reset request generation.
"""

import secrets
from datetime import datetime, timedelta
from app.repositories.user_repo import UserRepository


class RequestPasswordResetUseCase:
    """Use case for requesting password reset."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the use case.

        Args:
            user_repository: Repository for user operations
        """
        self._user_repository = user_repository

    async def execute(self, email: str) -> dict:
        """
        Request password reset.

        Args:
            email: Email address of the user

        Returns:
            dict: Success message (always returns success for security)
        """
        user = await self._user_repository.get_by_email(email)
        
        if not user:
            # Don't reveal if email exists
            return {"message": "If email exists, password reset link has been sent"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store token in database
        user.password_reset_token = reset_token
        user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        
        # TODO: Send email with reset link
        # await send_password_reset_email(user.email, reset_token)
        
        return {"message": "If email exists, password reset link has been sent"}
