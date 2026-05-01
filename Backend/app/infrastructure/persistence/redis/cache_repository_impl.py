"""
Redis Cache Repository Implementation

Implements ICacheRepository interface using Redis.
"""

import logging
from typing import Any, Optional

from app.domain.interfaces.cache_repository import ICacheRepository
from app.core.redis import redis_client

logger = logging.getLogger(__name__)


class CacheRepositoryImpl(ICacheRepository):
    """
    Redis implementation of ICacheRepository.
    
    This is the concrete implementation that the domain layer
    depends on through the interface.
    """
    
    def __init__(self, redis_client_instance=None):
        """
        Initialize cache repository.
        
        Args:
            redis_client_instance: Redis client (uses global if not provided)
        """
        self.redis = redis_client_instance or redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        
        Returns:
            True if successful
        """
        try:
            return await self.redis.set(key, value, ttl=ttl)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if successful
        """
        try:
            return await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
        
        Returns:
            Number of keys deleted
        """
        try:
            return await self.redis.delete_pattern(pattern)
        except Exception as e:
            logger.error(f"Error deleting pattern {pattern}: {str(e)}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if exists
        """
        try:
            return await self.redis.exists(key)
        except Exception as e:
            logger.error(f"Error checking key existence {key}: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """
        Clear all cache.
        
        Returns:
            True if successful
        """
        try:
            return await self.redis.clear()
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
