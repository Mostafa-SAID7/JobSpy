from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import logging
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.redis import redis_client

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_create: UserCreate, hashed_password: str) -> User:
        """Create a new user."""
        db_user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
        )
        self.session.add(db_user)
        try:
            await self.session.flush()
            return db_user
        except IntegrityError:
            await self.session.rollback()
            raise ValueError(f"User with email {user_create.email} already exists")

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID with caching."""
        # Try to get from cache
        cache_key = f"user:{user_id}"
        cached_user = await redis_client.get(cache_key)
        if cached_user:
            logger.debug(f"Cache hit for user {user_id}")
            return cached_user
        
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        # Cache the result with users TTL
        if user:
            await redis_client.set(cache_key, user, cache_type="users")
        
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email with caching."""
        # Try to get from cache
        cache_key = f"user:email:{email}"
        cached_user = await redis_client.get(cache_key)
        if cached_user:
            logger.debug(f"Cache hit for user email {email}")
            return cached_user
        
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        # Cache the result with users TTL
        if user:
            await redis_client.set(cache_key, user, cache_type="users")
        
        return user

    async def update(self, user_id: UUID, user_update: UserUpdate) -> User | None:
        """Update user and invalidate cache."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        self.session.add(user)
        await self.session.flush()
        
        # Invalidate user cache
        await self.invalidate_user_cache(user_id)
        
        return user

    async def delete(self, user_id: UUID) -> bool:
        """Delete user and invalidate cache."""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.flush()
        
        # Invalidate user cache
        await self.invalidate_user_cache(user_id)
        
        return True

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def count(self) -> int:
        """Count total users."""
        result = await self.session.execute(select(User))
        return len(result.scalars().all())

    async def invalidate_user_cache(self, user_id: UUID) -> bool:
        """
        Invalidate cache for a specific user.
        
        Args:
            user_id: User ID
        
        Returns:
            True if invalidated successfully
        """
        try:
            cache_key = f"user:{user_id}"
            await redis_client.delete(cache_key)
            logger.info(f"Cache invalidated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating user cache: {str(e)}")
            return False

    async def invalidate_user_email_cache(self, email: str) -> bool:
        """
        Invalidate cache for a user by email.
        
        Args:
            email: User email
        
        Returns:
            True if invalidated successfully
        """
        try:
            cache_key = f"user:email:{email}"
            await redis_client.delete(cache_key)
            logger.info(f"Cache invalidated for user email {email}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating user email cache: {str(e)}")
            return False

    async def invalidate_all_user_cache(self) -> bool:
        """
        Invalidate all user-related cache entries.
        
        Returns:
            True if invalidated successfully
        """
        try:
            patterns = [
                "user:*",
                "user:email:*",
            ]
            
            for pattern in patterns:
                await redis_client.delete_pattern(pattern)
            
            logger.info("All user cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating all user cache: {str(e)}")
            return False
