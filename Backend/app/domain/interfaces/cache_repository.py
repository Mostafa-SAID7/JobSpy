"""
Cache Repository Interface

Contract for caching that infrastructure must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ICacheRepository(ABC):
    """
    Interface for cache repository.
    
    Separates caching concerns from business logic.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
        
        Returns:
            Number of keys deleted
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if exists
        """
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """
        Clear all cache.
        
        Returns:
            True if successful
        """
        pass
