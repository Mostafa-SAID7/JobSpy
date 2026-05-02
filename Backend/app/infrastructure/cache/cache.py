"""
Cache Management Utilities
Provides decorators and utilities for caching with advanced strategies
"""

import functools
import json
import hashlib
import logging
from typing import Any, Callable, Optional, Dict, List
from app.infrastructure.cache.redis import redis_client
from app.config.settings import settings

logger = logging.getLogger(__name__)


# Cache key patterns for different data types
CACHE_KEYS = {
    "search_results": "search:{query_hash}",
    "job_details": "job:{job_id}",
    "job_stats": "job_stats:{job_id}",
    "active_alerts": "active_alerts",
    "user_alerts": "user_alerts:{user_id}",
    "user_saved_jobs": "user_saved_jobs:{user_id}",
    "trending_searches": "trending_searches:{limit}",
    "recommendations": "recommendations:{user_id}:{limit}",
    "search_suggestions": "search_suggestions:{query}",
}

# TTL configurations for different cache types
CACHE_TTLS = {
    "search_results": 3600,  # 1 hour
    "job_details": 604800,  # 7 days
    "job_stats": 86400,  # 24 hours
    "active_alerts": 3600,  # 1 hour
    "user_alerts": 1800,  # 30 minutes
    "user_saved_jobs": 86400,  # 24 hours
    "trending_searches": 3600,  # 1 hour
    "recommendations": 1800,  # 30 minutes
    "search_suggestions": 3600,  # 1 hour
}


def generate_cache_key(pattern: str, **kwargs) -> str:
    """
    Generate a cache key from pattern and parameters.
    
    Args:
        pattern: Cache key pattern
        **kwargs: Parameters to substitute in pattern
    
    Returns:
        Generated cache key
    """
    return pattern.format(**kwargs)


def generate_query_hash(query: str, filters: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a hash for search query and filters.
    
    Args:
        query: Search query
        filters: Filter criteria
    
    Returns:
        Hash string
    """
    combined = f"{query}:{json.dumps(filters or {}, sort_keys=True)}"
    return hashlib.md5(combined.encode()).hexdigest()


def cache_key(*args, prefix: str = "", **kwargs) -> str:
    """
    Generate a cache key from function arguments.
    
    Args:
        prefix: Cache key prefix
        args: Positional arguments
        kwargs: Keyword arguments
    
    Returns:
        Generated cache key
    """
    key_parts = [prefix] if prefix else []
    
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def cached(prefix: str = "", ttl: Optional[int] = None):
    """
    Decorator for caching function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            key = cache_key(*args, prefix=prefix or func.__name__, **kwargs)
            
            # Try to get from cache
            cached_result = await redis_client.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {key}")
                return cached_result
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_ttl = ttl or settings.REDIS_CACHE_TTL
            await redis_client.set(key, result, ttl=cache_ttl)
            
            return result
        
        return wrapper
    
    return decorator


def cache_with_invalidation(
    prefix: str = "",
    ttl: Optional[int] = None,
    invalidate_patterns: Optional[List[str]] = None,
):
    """
    Decorator for caching with invalidation support.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        invalidate_patterns: Patterns to invalidate on function call
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Call function
            result = await func(*args, **kwargs)
            
            # Invalidate related caches
            if invalidate_patterns:
                for pattern in invalidate_patterns:
                    await invalidate_cache(pattern)
            
            return result
        
        return wrapper
    
    return decorator


async def invalidate_cache(pattern: str) -> bool:
    """
    Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Cache key pattern (supports wildcards)
    
    Returns:
        True if successful
    """
    try:
        deleted = await redis_client.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} cache entries matching pattern: {pattern}")
        return True
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {str(e)}")
        return False


async def invalidate_user_cache(user_id: int) -> bool:
    """
    Invalidate all cache entries for a user.
    
    Args:
        user_id: User ID
    
    Returns:
        True if successful
    """
    patterns = [
        f"user_alerts:{user_id}*",
        f"user_saved_jobs:{user_id}*",
        f"recommendations:{user_id}*",
    ]
    
    for pattern in patterns:
        await invalidate_cache(pattern)
    
    return True


async def invalidate_job_cache(job_id: str) -> bool:
    """
    Invalidate all cache entries for a job.
    
    Args:
        job_id: Job ID
    
    Returns:
        True if successful
    """
    patterns = [
        f"job:{job_id}*",
        f"job_stats:{job_id}*",
        "search:*",  # Invalidate all search results
    ]
    
    for pattern in patterns:
        await invalidate_cache(pattern)
    
    return True


async def invalidate_search_cache() -> bool:
    """
    Invalidate all search-related cache entries.
    
    Returns:
        True if successful
    """
    patterns = [
        "search:*",
        "trending_searches:*",
        "search_suggestions:*",
    ]
    
    for pattern in patterns:
        await invalidate_cache(pattern)
    
    return True


async def clear_all_cache() -> bool:
    """
    Clear all cache.
    
    Returns:
        True if successful
    """
    return await redis_client.clear()


async def warm_cache(cache_type: str, data: Dict[str, Any]) -> bool:
    """
    Warm cache with precomputed data.
    
    Args:
        cache_type: Type of cache to warm
        data: Data to cache
    
    Returns:
        True if successful
    """
    try:
        for key, value in data.items():
            ttl = CACHE_TTLS.get(cache_type, settings.REDIS_CACHE_TTL)
            await redis_client.set(key, value, ttl=ttl)
        
        logger.info(f"Warmed {len(data)} cache entries for {cache_type}")
        return True
    except Exception as e:
        logger.error(f"Error warming cache for {cache_type}: {str(e)}")
        return False


async def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache stats
    """
    return await redis_client.get_stats()
