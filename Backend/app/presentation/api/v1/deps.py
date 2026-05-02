"""
FastAPI Dependencies - JobSpy Backend

This module provides FastAPI dependency functions for common operations
like database session management, authentication, etc.

These are FastAPI-specific dependencies, separate from the DI container.
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.sqlalchemy.database import get_db
from app.presentation.api.v1.dependencies import container

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in get_db():
        yield session


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    FastAPI dependency for getting current user ID from token.
    
    Args:
        token: JWT token from Authorization header
    
    Returns:
        int: User ID
    
    Raises:
        HTTPException: If token is invalid
    """
    # TODO: Implement token validation
    # For now, this is a placeholder
    # In production, decode JWT and extract user_id
    
    # Example implementation:
    # try:
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    #     user_id: int = payload.get("sub")
    #     if user_id is None:
    #         raise HTTPException(status_code=401, detail="Invalid token")
    #     return user_id
    # except JWTError:
    #     raise HTTPException(status_code=401, detail="Invalid token")
    
    # Placeholder - return dummy user_id
    return 1


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database_session),
):
    """
    FastAPI dependency for getting current user object.
    
    Args:
        user_id: User ID from token
        db: Database session
    
    Returns:
        User: Current user object
    
    Raises:
        HTTPException: If user not found
    """
    # TODO: Implement user retrieval
    # For now, this is a placeholder
    
    # Example implementation:
    # from app.domain.interfaces.repositories import IUserRepository as UserRepository
    # user_repo = UserRepository(db)
    # user = await user_repo.get_by_id(user_id)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    # return user
    
    # Placeholder
    return {"id": user_id, "email": "user@example.com"}


def get_optional_user_id(token: str = Depends(oauth2_scheme)) -> int | None:
    """
    FastAPI dependency for getting optional user ID.
    
    Returns None if no token provided instead of raising exception.
    Useful for endpoints that work for both authenticated and anonymous users.
    
    Args:
        token: JWT token from Authorization header (optional)
    
    Returns:
        int | None: User ID or None
    """
    if not token:
        return None
    
    try:
        return get_current_user_id(token)
    except HTTPException:
        return None
