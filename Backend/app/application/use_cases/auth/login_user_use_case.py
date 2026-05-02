"""
Login User Use Case

Handles user authentication and token generation.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta

from app.repositories.user_repo import UserRepository
from app.utils.security import verify_password, create_access_token, create_refresh_token

logger = logging.getLogger(__name__)


@dataclass
class LoginResult:
    """Result of user login"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class LoginUserUseCase:
    """
    Use Case: Authenticate user and generate tokens.
    
    Responsibilities:
    1. Verify user credentials
    2. Check if user is active
    3. Generate access and refresh tokens
    4. Return tokens
    
    Used by: Login endpoint
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize use case.
        
        Args:
            user_repository: Repository for user persistence
        """
        self.user_repository = user_repository
    
    async def execute(self, email: str, password: str) -> LoginResult:
        """
        Execute the use case.
        
        Args:
            email: User email
            password: User password
        
        Returns:
            LoginResult with tokens
        
        Raises:
            ValueError: If credentials are invalid or user is inactive
        """
        logger.info(f"Login attempt for user: {email}")
        
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: User not found - {email}")
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: Invalid password - {email}")
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed: User account inactive - {email}")
            raise ValueError("User account is inactive")
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=7)
        )
        
        logger.info(f"User logged in successfully: {user.id}")
        
        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600
        )
