"""
Register User Use Case

Handles user registration with validation and password hashing.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from app.schemas.user import UserCreate
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.utils.security import hash_password

logger = logging.getLogger(__name__)


@dataclass
class RegisterUserResult:
    """Result of user registration"""
    user: User
    success: bool
    message: str


class RegisterUserUseCase:
    """
    Use Case: Register a new user.
    
    Responsibilities:
    1. Check if user already exists
    2. Hash password
    3. Create user in repository
    4. Return user data
    
    Used by: Registration endpoint
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize use case.
        
        Args:
            user_repository: Repository for user persistence
        """
        self.user_repository = user_repository
    
    async def execute(self, user_create: UserCreate) -> User:
        """
        Execute the use case.
        
        Args:
            user_create: User creation data
        
        Returns:
            Created user
        
        Raises:
            ValueError: If user already exists or validation fails
        """
        logger.info(f"Registering new user: {user_create.email}")
        
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_create.email)
        if existing_user:
            logger.warning(f"Registration failed: Email already registered - {user_create.email}")
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = hash_password(user_create.password)
        
        # Create user
        try:
            user = await self.user_repository.create(user_create, hashed_password)
            logger.info(f"User registered successfully: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise ValueError(f"Failed to register user: {str(e)}")
