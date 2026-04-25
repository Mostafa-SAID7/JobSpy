"""
Authentication JWT Token Tests

Tests for JWT token creation, validation, and expiration.

**Validates: Requirements 4.4, 4.5**
"""

import pytest
from datetime import timedelta
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestJWTTokens:
    """Test JWT token creation and validation."""
    
    def test_access_token_creation(self):
        """
        Property: JWT access token is created with correct payload
        
        For any user ID, the access token should contain the user ID
        and have an expiration time.
        
        **Validates: Requirements 4.4**
        """
        user_id = "test-user-123"
        token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(hours=1)
        )
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Token should be decodable
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert "exp" in payload
    
    def test_refresh_token_creation(self):
        """
        Property: JWT refresh token is created with correct payload
        
        For any user ID, the refresh token should contain the user ID,
        have type='refresh', and have a longer expiration time.
        """
        user_id = "test-user-123"
        token = create_refresh_token(
            data={"sub": user_id},
            expires_delta=timedelta(days=7)
        )
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Token should be decodable
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_expired_token_rejection(self):
        """
        Property: Expired tokens are rejected
        
        For any token with expiration in the past, decoding should raise
        an exception.
        
        **Validates: Requirements 4.5**
        """
        user_id = "test-user-123"
        # Create token that expires immediately
        token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Decoding expired token should raise exception
        with pytest.raises(Exception):
            decode_token(token)
    
    def test_invalid_token_rejection(self):
        """
        Property: Invalid tokens are rejected
        
        For any malformed or tampered token, decoding should raise an exception.
        """
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):
            decode_token(invalid_token)
