"""
Redis Cache Client with Connection Pool and Advanced Features
"""

import json
import logging
from typing import Any, Optional, List, Dict
from datetime import datetime

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client wrapper with connection pool and caching utilities
    """
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.pool: Optional[ConnectionPool] = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }
    
    async def connect(self) -> None:
        """
        Connect to Redis with connection pool
        """
        try:
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                encoding="utf8",
                decode_responses=True,
                max_connections=20,
            )
            self.redis = redis.Redis(connection_pool=self.pool)
            await self.redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.stats["errors"] += 1
    
    async def disconnect(self) -> None:
        """
        Disconnect from Redis
        """
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                self.stats["hits"] += 1
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                self.stats["misses"] += 1
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            self.stats["errors"] += 1
            return None
    
    def get_ttl_for_cache_type(self, cache_type: str) -> int:
        """
        Get TTL for a specific cache type
        
        Args:
            cache_type: Type of cache (jobs, search_results, statistics, users, search_history, recommendations, trending_searches)
            
        Returns:
            TTL in seconds
        """
        ttl_map = {
            "jobs": settings.CACHE_TTL_JOBS,
            "search_results": settings.CACHE_TTL_SEARCH_RESULTS,
            "statistics": settings.CACHE_TTL_STATISTICS,
            "users": settings.CACHE_TTL_USERS,
            "search_history": settings.CACHE_TTL_SEARCH_HISTORY,
            "recommendations": settings.CACHE_TTL_RECOMMENDATIONS,
            "trending_searches": settings.CACHE_TTL_TRENDING_SEARCHES,
        }
        return ttl_map.get(cache_type, settings.REDIS_CACHE_TTL)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        cache_type: Optional[str] = None,
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (overrides cache_type)
            cache_type: Type of cache for automatic TTL selection
            
        Returns:
            True if successful
        """
        if not self.redis:
            return False
        
        # Determine TTL: explicit ttl > cache_type > default
        if ttl is None:
            if cache_type:
                ttl = self.get_ttl_for_cache_type(cache_type)
            else:
                ttl = settings.REDIS_CACHE_TTL
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis.setex(key, ttl, value)
            self.stats["sets"] += 1
            logger.debug(f"Cache set for key {key} with TTL {ttl}s")
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            self.stats["errors"] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            self.stats["deletes"] += 1
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
            self.stats["errors"] += 1
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Key pattern (supports wildcards)
            
        Returns:
            Number of keys deleted
        """
        if not self.redis:
            return 0
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                self.stats["deletes"] += deleted
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error deleting pattern {pattern}: {str(e)}")
            self.stats["errors"] += 1
            return 0
    
    async def clear(self) -> bool:
        """
        Clear all cache
        
        Returns:
            True if successful
        """
        if not self.redis:
            return False
        
        try:
            await self.redis.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            self.stats["errors"] += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        if not self.redis:
            return False
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking key existence {key}: {str(e)}")
            self.stats["errors"] += 1
            return False
    
    async def get_ttl(self, key: str) -> int:
        """
        Get TTL for a key
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        if not self.redis:
            return -2
        
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for {key}: {str(e)}")
            self.stats["errors"] += 1
            return -2
    
    async def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Set TTL for a key
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        if not self.redis:
            return False
        
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Error setting TTL for {key}: {str(e)}")
            self.stats["errors"] += 1
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter
        
        Args:
            key: Cache key
            amount: Amount to increment
            
        Returns:
            New value
        """
        if not self.redis:
            return 0
        
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing {key}: {str(e)}")
            self.stats["errors"] += 1
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100)
            if total_requests > 0
            else 0
        )
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
            "errors": self.stats["errors"],
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.2f}%",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def reset_stats(self) -> None:
        """
        Reset cache statistics
        """
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }


# Create global Redis client instance
redis_client = RedisClient()
