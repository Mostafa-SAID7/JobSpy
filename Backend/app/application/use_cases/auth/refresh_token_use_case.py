"""
Refresh Token Use Case

Handles token refresh operations.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta

from app.shared.security.security import decode_token, create_access_token

logger = logging.getLogger(__name__)


@dataclass
class RefreshTokenResult:
    """Result of token refresh"""
    access_token: str
    token_type: str
    expires_in: int


class RefreshTokenUseCase:
    """
    Use Case: Refresh access token using refresh token.
    
    Responsibilities:
    1. Decode and validate refresh token
    2. Extract user ID
    3. Generate new access token
    4. Return new token
    
    Used by: Token refresh endpoint
    """
    
    def __init__(self):
        """Initialize use case."""
        pass
    
    async def execute(self, refresh_token: str) -> RefreshTokenResult:
        """
        Execute the use case.
        
        Args:
            refresh_token: Refresh token string
        
        Returns:
            RefreshTokenResult with new access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        logger.info("Token refresh attempt")
        
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            
            if not user_id:
                logger.warning("Token refresh failed: Invalid token payload")
                raise ValueError("Invalid refresh token")
            
            # Create new access token
            access_token = create_access_token(
                data={"sub": user_id},
                expires_delta=timedelta(hours=1)
            )
            
            logger.info(f"Token refreshed successfully for user: {user_id}")
            
            return RefreshTokenResult(
                access_token=access_token,
                token_type="bearer",
                expires_in=3600
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise ValueError("Invalid refresh token")
