from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.core.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.repositories.user_repo import UserRepository
from app.utils.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    user_repo = UserRepository(db)
    
    # Check if email is being changed and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = await user_repo.get_by_email(user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    updated_user = await user_repo.update(current_user.id, user_update)
    await db.commit()
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Invalidate user cache
    await user_repo.invalidate_user_cache(current_user.id)
    if user_update.email and user_update.email != current_user.email:
        await user_repo.invalidate_user_email_cache(current_user.email)
        await user_repo.invalidate_user_email_cache(user_update.email)
    
    logger.info(f"User profile updated: {current_user.id}, cache invalidated")
    
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete current user account."""
    user_repo = UserRepository(db)
    success = await user_repo.delete(current_user.id)
    await db.commit()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Invalidate user cache
    await user_repo.invalidate_user_cache(current_user.id)
    logger.info(f"User account deleted: {current_user.id}, cache invalidated")
