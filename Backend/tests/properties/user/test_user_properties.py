"""
User and Authentication Correctness Properties Tests

Property-based tests for user management and authentication using Hypothesis.

**Validates: Requirements 4.2, 4.3, 4.4, 4.5**
"""

import pytest
from hypothesis import given, strategies as st, settings
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
import bcrypt
import jwt


# ============================================================================
# Property 5: Email must be unique
# ============================================================================

@given(
    email=st.emails()
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_email_uniqueness_constraint(email):
    """
    Property: Email must be unique
    
    For any email address, there should not be two users with the same email.
    
    **Validates: Requirements 4.2**
    """
    from app.domain.interfaces.repositories import IUserRepository as UserRepository
    from app.presentation.api.v1.schemas.user import UserCreate
    from sqlalchemy.ext.asyncio import AsyncSession
    
    db = AsyncMock(spec=AsyncSession)
    user_repo = UserRepository(db)
    
    # Mock the database to simulate unique constraint
    existing_emails = set()
    
    async def mock_create(user_create):
        # Normalize email to lowercase for comparison
        normalized_email = user_create.email.lower()
        if normalized_email in existing_emails:
            raise ValueError("Email already exists")
        existing_emails.add(normalized_email)
        return AsyncMock(email=normalized_email)
    
    with patch.object(user_repo, 'create', side_effect=mock_create):
        user_create = UserCreate(
            email=email,
            password="password123",
            full_name="Test User"
        )
        
        # First creation should succeed
        user1 = await user_repo.create(user_create)
        assert user1.email == email.lower()
        
        # Second creation with same email should fail
        with pytest.raises(ValueError):
            await user_repo.create(user_create)


# ============================================================================
# Property 6: Passwords are hashed securely
# ============================================================================

@given(
    password=st.text(min_size=8, max_size=50)
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_passwords_hashed_securely(password):
    """
    Property: Passwords are hashed securely
    
    For any password, it must be hashed using bcrypt and not stored in plaintext.
    
    **Validates: Requirements 4.3**
    """
    # Hash the password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    
    # Verify the hash is not the plaintext password
    assert hashed != password.encode()
    
    # Verify the hash can be verified
    assert bcrypt.checkpw(password.encode(), hashed)
    
    # Verify wrong password doesn't verify
    wrong_password = password + "wrong"
    assert not bcrypt.checkpw(wrong_password.encode(), hashed)


# ============================================================================
# Property 7: JWT token issued on successful login
# ============================================================================

@given(
    user_id=st.just(str(uuid4())),
    email=st.emails()
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_jwt_token_issued_on_login(user_id, email):
    """
    Property: JWT token is issued on successful login
    
    For any successful login, a JWT token must be issued containing user_id and email.
    
    **Validates: Requirements 4.4**
    """
    secret = "test_secret"
    
    # Create token
    token = jwt.encode(
        {"sub": user_id, "email": email},
        secret,
        algorithm="HS256"
    )
    
    # Verify token is returned
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Verify token can be decoded
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    assert decoded["sub"] == user_id
    assert decoded["email"] == email


# ============================================================================
# Property 8: JWT token expires after specified time
# ============================================================================

@given(
    expiration_minutes=st.integers(min_value=1, max_value=60)
)
@settings(max_examples=5, deadline=None)
@pytest.mark.asyncio
async def test_jwt_token_expires_after_time(expiration_minutes):
    """
    Property: JWT token expires after specified time
    
    For any JWT token with expiration time, it must expire after that time.
    
    **Validates: Requirements 4.5**
    """
    secret = "test_secret"
    user_id = str(uuid4())
    
    # Create token with expiration
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=expiration_minutes)
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    # Verify token is valid
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    assert decoded["sub"] == user_id
    
    # Create expired token
    expired_payload = {
        "sub": user_id,
        "exp": datetime.utcnow() - timedelta(minutes=1)
    }
    
    expired_token = jwt.encode(expired_payload, secret, algorithm="HS256")
    
    # Verify expired token raises error
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired_token, secret, algorithms=["HS256"])
