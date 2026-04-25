from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
import logging
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.repositories.user_repo import UserRepository
from app.utils.security import get_current_user, hash_password, verify_password
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


# Request/Response schemas
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class EmailVerificationRequest(BaseModel):
    token: str


class UserPreferences(BaseModel):
    theme: str = "light"
    notifications_enabled: bool = True
    email_alerts: bool = True
    job_recommendations: bool = True
    saved_jobs_limit: int = 1000


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



@router.post("/me/password", response_model=dict)
async def change_password(
    password_change: PasswordChangeRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change current user password."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_change.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Update password
    user.hashed_password = hash_password(password_change.new_password)
    db.add(user)
    await db.commit()
    
    # Invalidate user cache
    await user_repo.invalidate_user_cache(current_user.id)
    logger.info(f"Password changed for user: {current_user.id}")
    
    return {"message": "Password changed successfully"}


@router.post("/me/email-verification/send", response_model=dict)
async def send_email_verification(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send email verification link to current user."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Store token in database (you'll need to add this field to User model)
    user.email_verification_token = verification_token
    user.email_verification_token_expires = datetime.utcnow() + timedelta(hours=24)
    db.add(user)
    await db.commit()
    
    # TODO: Send email with verification link
    # await send_verification_email(user.email, verification_token)
    
    logger.info(f"Email verification sent to user: {current_user.id}")
    
    return {"message": "Verification email sent"}


@router.post("/me/email-verification/verify", response_model=dict)
async def verify_email(
    verification: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify email with token."""
    user_repo = UserRepository(db)
    
    # Find user by verification token
    result = await db.execute(
        select(User).where(User.email_verification_token == verification.token)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Check if token is expired
    if user.email_verification_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    # Mark email as verified
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires = None
    db.add(user)
    await db.commit()
    
    logger.info(f"Email verified for user: {user.id}")
    
    return {"message": "Email verified successfully"}


@router.post("/password-reset/request", response_model=dict)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(reset_request.email)
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, password reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Store token in database
    user.password_reset_token = reset_token
    user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.add(user)
    await db.commit()
    
    # TODO: Send email with reset link
    # await send_password_reset_email(user.email, reset_token)
    
    logger.info(f"Password reset requested for user: {user.id}")
    
    return {"message": "If email exists, password reset link has been sent"}


@router.post("/password-reset/confirm", response_model=dict)
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset with token."""
    # Find user by reset token
    result = await db.execute(
        select(User).where(User.password_reset_token == reset_confirm.token)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Check if token is expired
    if user.password_reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update password
    user.hashed_password = hash_password(reset_confirm.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    db.add(user)
    await db.commit()
    
    logger.info(f"Password reset confirmed for user: {user.id}")
    
    return {"message": "Password reset successfully"}


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user preferences from database."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return preferences (stored as JSON in user model)
    preferences = user.preferences or {}
    return UserPreferences(**preferences)


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences in database."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update preferences
    user.preferences = preferences.model_dump()
    db.add(user)
    await db.commit()
    
    # Invalidate user cache
    await user_repo.invalidate_user_cache(current_user.id)
    logger.info(f"Preferences updated for user: {current_user.id}")
    
    return preferences


@router.get("/me/stats", response_model=dict)
async def get_user_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user statistics (saved jobs, alerts, searches)."""
    from app.repositories.saved_job_repo import SavedJobRepository
    from app.repositories.alert_repo import AlertRepository
    from app.repositories.search_history_repo import SearchHistoryRepository
    
    saved_job_repo = SavedJobRepository(db)
    alert_repo = AlertRepository(db)
    search_history_repo = SearchHistoryRepository(db)
    
    # Get counts
    saved_jobs_count = await saved_job_repo.count_by_user(current_user.id)
    alerts_count = await alert_repo.count_by_user(current_user.id)
    searches_count = await search_history_repo.count_by_user(current_user.id)
    
    return {
        "saved_jobs": saved_jobs_count,
        "active_alerts": alerts_count,
        "total_searches": searches_count
    }
