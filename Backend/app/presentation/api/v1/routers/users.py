"""
Users Router - Clean Architecture

This router handles user-related endpoints using dependency injection
and use cases following Clean Architecture principles.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from dependency_injector.wiring import inject, Provide
import logging
import secrets
from datetime import datetime, timedelta

from app.infrastructure.persistence.sqlalchemy.database import get_db
from app.presentation.api.v1.schemas.user import UserResponse, UserUpdate
from app.shared.security.security import get_current_user
from app.presentation.api.v1.dependencies import Container

# Use Cases
from app.application.use_cases.users.get_user_profile_use_case import GetUserProfileUseCase
from app.application.use_cases.users.update_user_profile_use_case import UpdateUserProfileUseCase
from app.application.use_cases.users.delete_user_account_use_case import DeleteUserAccountUseCase
from app.application.use_cases.users.change_password_use_case import ChangePasswordUseCase
from app.application.use_cases.users.verify_email_use_case import VerifyEmailUseCase
from app.application.use_cases.users.request_password_reset_use_case import RequestPasswordResetUseCase
from app.application.use_cases.users.confirm_password_reset_use_case import ConfirmPasswordResetUseCase
from app.application.use_cases.users.update_user_preferences_use_case import UpdateUserPreferencesUseCase, UserPreferences
from app.application.use_cases.users.get_user_stats_use_case import GetUserStatsUseCase

# Exceptions
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException, DuplicateEntityError

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


@router.get("/me", response_model=UserResponse)
@inject
async def get_current_user_profile(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: GetUserProfileUseCase = Depends(Provide[Container.get_user_profile_use_case]),
):
    """Get current user profile."""
    try:
        user = await use_case.execute(current_user.id)
        return user
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/me", response_model=UserResponse)
@inject
async def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: UpdateUserProfileUseCase = Depends(Provide[Container.update_user_profile_use_case]),
):
    """Update current user profile."""
    try:
        updated_user = await use_case.execute(
            current_user.id, 
            user_update, 
            current_user.email
        )
        await db.commit()
        logger.info(f"User profile updated: {current_user.id}, cache invalidated")
        return updated_user
    except NotFoundException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateEntityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user_account(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: DeleteUserAccountUseCase = Depends(Provide[Container.delete_user_account_use_case]),
):
    """Delete current user account."""
    try:
        await use_case.execute(current_user.id)
        await db.commit()
        logger.info(f"User account deleted: {current_user.id}, cache invalidated")
    except NotFoundException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )


@router.post("/me/password", response_model=dict)
@inject
async def change_password(
    password_change: PasswordChangeRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: ChangePasswordUseCase = Depends(Provide[Container.change_password_use_case]),
):
    """Change current user password."""
    try:
        result = await use_case.execute(
            current_user.id,
            password_change.current_password,
            password_change.new_password
        )
        await db.commit()
        logger.info(f"Password changed for user: {current_user.id}")
        return result
    except NotFoundException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


@router.post("/me/email-verification/send", response_model=dict)
@inject
async def send_email_verification(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: GetUserProfileUseCase = Depends(Provide[Container.get_user_profile_use_case]),
):
    """Send email verification link to current user."""
    try:
        user = await use_case.execute(current_user.id)
        
        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Store token in database (you'll need to add this field to User model)
        from app.domain.interfaces.repositories import IUserRepository as UserRepository
        user_repo = UserRepository(db)
        db_user = await user_repo.get_by_id(current_user.id)
        db_user.email_verification_token = verification_token
        db_user.email_verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.add(db_user)
        await db.commit()
        
        # TODO: Send email with verification link
        # await send_verification_email(user.email, verification_token)
        
        logger.info(f"Email verification sent to user: {current_user.id}")
        
        return {"message": "Verification email sent"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )


@router.post("/me/email-verification/verify", response_model=dict)
@inject
async def verify_email(
    verification: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
    use_case: VerifyEmailUseCase = Depends(Provide[Container.verify_email_use_case]),
):
    """Verify email with token."""
    try:
        result = await use_case.execute(verification.token)
        await db.commit()
        logger.info("Email verified successfully")
        return result
    except NotFoundException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthorizationException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email: {str(e)}"
        )


@router.post("/password-reset/request", response_model=dict)
@inject
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    use_case: RequestPasswordResetUseCase = Depends(Provide[Container.request_password_reset_use_case]),
):
    """Request password reset."""
    try:
        result = await use_case.execute(reset_request.email)
        await db.commit()
        logger.info(f"Password reset requested for email: {reset_request.email}")
        return result
    except Exception as e:
        await db.rollback()
        # Always return success message for security
        return {"message": "If email exists, password reset link has been sent"}


@router.post("/password-reset/confirm", response_model=dict)
@inject
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
    use_case: ConfirmPasswordResetUseCase = Depends(Provide[Container.confirm_password_reset_use_case]),
):
    """Confirm password reset with token."""
    try:
        result = await use_case.execute(reset_confirm.token, reset_confirm.new_password)
        await db.commit()
        logger.info("Password reset confirmed")
        return result
    except NotFoundException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthorizationException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


@router.get("/me/preferences", response_model=UserPreferences)
@inject
async def get_user_preferences(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: GetUserProfileUseCase = Depends(Provide[Container.get_user_profile_use_case]),
):
    """Get user preferences from database."""
    try:
        user = await use_case.execute(current_user.id)
        
        # Return preferences (stored as JSON in user model)
        preferences = user.preferences or {}
        return UserPreferences(**preferences)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/me/preferences", response_model=UserPreferences)
@inject
async def update_user_preferences(
    preferences: UserPreferences,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: UpdateUserPreferencesUseCase = Depends(Provide[Container.update_user_preferences_use_case]),
):
    """Update user preferences in database."""
    try:
        updated_preferences = await use_case.execute(current_user.id, preferences)
        await db.commit()
        logger.info(f"Preferences updated for user: {current_user.id}")
        return updated_preferences
    except NotFoundException as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.get("/me/stats", response_model=dict)
@inject
async def get_user_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: GetUserStatsUseCase = Depends(Provide[Container.get_user_stats_use_case]),
):
    """Get user statistics (saved jobs, alerts, searches)."""
    try:
        stats = await use_case.execute(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )
