"""
Auth Router - JobSpy Backend (Clean Architecture)

Thin controllers that delegate all business logic to use cases.
Uses manual dependency injection getters (no @inject/Provide).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.infrastructure.persistence.sqlalchemy.database import get_db
from app.presentation.api.v1.schemas.user import UserCreate, UserResponse, UserLogin
from app.container import container

# Use Cases
from app.application.use_cases.auth.register_user_use_case import RegisterUserUseCase
from app.application.use_cases.auth.login_user_use_case import LoginUserUseCase
from app.application.use_cases.auth.refresh_token_use_case import RefreshTokenUseCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_register_user_use_case():
    return container.application.register_user_use_case()

def get_login_user_use_case():
    return container.application.login_user_use_case()

def get_refresh_token_use_case():
    return container.application.refresh_token_use_case()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    """
    Register a new user.

    Thin controller - delegates to RegisterUserUseCase.
    """
    try:
        user = await use_case.execute(user_create)
        logger.info(f"User registered: {user.id}")
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login")
async def login(
    login_data: UserLogin,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
):
    """
    Login user and return tokens.

    Thin controller - delegates to LoginUserUseCase.
    """
    try:
        result = await use_case.execute(login_data.email, login_data.password)

        return {
            "access_token": result.access_token,
            "refresh_token": result.refresh_token,
            "token_type": result.token_type,
            "expires_in": result.expires_in,
            "user": result.user
        }

    except ValueError as e:
        if "inactive" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh")
async def refresh(
    refresh_token: str,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
):
    """
    Refresh access token using refresh token.

    Thin controller - delegates to RefreshTokenUseCase.
    """
    try:
        result = await use_case.execute(refresh_token)

        return {
            "access_token": result.access_token,
            "token_type": result.token_type,
            "expires_in": result.expires_in
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout():
    """
    Logout user (client-side token removal).

    Note: This is a client-side operation. The client should remove the tokens.
    """
    return {"message": "Logged out successfully"}
