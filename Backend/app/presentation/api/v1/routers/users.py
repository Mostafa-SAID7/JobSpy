"""
Users Router - Clean Architecture - Manual DI Getters
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
import logging
import secrets
from datetime import datetime, timedelta

from app.infrastructure.persistence.sqlalchemy.database import get_db
from app.presentation.api.v1.schemas.user import UserResponse, UserUpdate
from app.shared.security.security import get_current_user
from app.container import container

from app.application.use_cases.users.get_user_profile_use_case import GetUserProfileUseCase
from app.application.use_cases.users.update_user_profile_use_case import UpdateUserProfileUseCase
from app.application.use_cases.users.delete_user_account_use_case import DeleteUserAccountUseCase
from app.application.use_cases.users.change_password_use_case import ChangePasswordUseCase
from app.application.use_cases.users.verify_email_use_case import VerifyEmailUseCase
from app.application.use_cases.users.request_password_reset_use_case import RequestPasswordResetUseCase
from app.application.use_cases.users.confirm_password_reset_use_case import ConfirmPasswordResetUseCase
from app.application.use_cases.users.update_user_preferences_use_case import UpdateUserPreferencesUseCase, UserPreferences
from app.application.use_cases.users.get_user_stats_use_case import GetUserStatsUseCase
from app.shared.exceptions.application_exceptions import NotFoundException, AuthorizationException, DuplicateEntityError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


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


def get_user_profile_uc(): return container.application.get_user_profile_use_case()
def get_update_profile_uc(): return container.application.update_user_profile_use_case()
def get_delete_account_uc(): return container.application.delete_user_account_use_case()
def get_change_password_uc(): return container.application.change_password_use_case()
def get_verify_email_uc(): return container.application.verify_email_use_case()
def get_request_reset_uc(): return container.application.request_password_reset_use_case()
def get_confirm_reset_uc(): return container.application.confirm_password_reset_use_case()
def get_update_preferences_uc(): return container.application.update_user_preferences_use_case()
def get_user_stats_uc(): return container.application.get_user_stats_use_case()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user=Depends(get_current_user),
    use_case: GetUserProfileUseCase = Depends(get_user_profile_uc),
):
    try:
        return await use_case.execute(current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user=Depends(get_current_user),
    use_case: UpdateUserProfileUseCase = Depends(get_update_profile_uc),
):
    try:
        return await use_case.execute(current_user.id, user_update, current_user.email)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateEntityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update profile: {str(e)}")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user=Depends(get_current_user),
    use_case: DeleteUserAccountUseCase = Depends(get_delete_account_uc),
):
    try:
        await use_case.execute(current_user.id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete account: {str(e)}")


@router.post("/me/password", response_model=dict)
async def change_password(
    password_change: PasswordChangeRequest,
    current_user=Depends(get_current_user),
    use_case: ChangePasswordUseCase = Depends(get_change_password_uc),
):
    try:
        return await use_case.execute(current_user.id, password_change.current_password, password_change.new_password)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to change password: {str(e)}")


@router.post("/me/email-verification/verify", response_model=dict)
async def verify_email(
    verification: EmailVerificationRequest,
    use_case: VerifyEmailUseCase = Depends(get_verify_email_uc),
):
    try:
        return await use_case.execute(verification.token)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to verify email: {str(e)}")


@router.post("/password-reset/request", response_model=dict)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    use_case: RequestPasswordResetUseCase = Depends(get_request_reset_uc),
):
    try:
        return await use_case.execute(reset_request.email)
    except Exception:
        return {"message": "If email exists, password reset link has been sent"}


@router.post("/password-reset/confirm", response_model=dict)
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    use_case: ConfirmPasswordResetUseCase = Depends(get_confirm_reset_uc),
):
    try:
        return await use_case.execute(reset_confirm.token, reset_confirm.new_password)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to reset password: {str(e)}")


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user=Depends(get_current_user),
    use_case: GetUserProfileUseCase = Depends(get_user_profile_uc),
):
    try:
        user = await use_case.execute(current_user.id)
        preferences = user.preferences or {}
        return UserPreferences(**preferences)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user=Depends(get_current_user),
    use_case: UpdateUserPreferencesUseCase = Depends(get_update_preferences_uc),
):
    try:
        return await use_case.execute(current_user.id, preferences)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update preferences: {str(e)}")


@router.get("/me/stats", response_model=dict)
async def get_user_stats(
    current_user=Depends(get_current_user),
    use_case: GetUserStatsUseCase = Depends(get_user_stats_uc),
):
    try:
        return await use_case.execute(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get user stats: {str(e)}")
