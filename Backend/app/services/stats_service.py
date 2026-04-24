"""
Statistics Service with Redis Caching
Handles computation and caching of various statistics
"""

import logging
from datetime import datetime
from typing import Optional

from app.repositories.stats_repo import StatsRepository
from app.core.redis import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache key prefixes
STATS_CACHE_PREFIX = "stats"
STATS_TTL = 3600  # 1 hour for most statistics
STATS_LONG_TTL = 86400  # 24 hours for less frequently changing stats


class StatsService:
    """Service for computing and caching statistics"""
    
    def __init__(self, stats_repo: StatsRepository):
        self.stats_repo = stats_repo
    
    def _get_cache_key(self, stat_type: str, *args) -> str:
        """Generate cache key for statistics"""
        if args:
            args_str = ":".join(str(arg) for arg in args)
            return f"{STATS_CACHE_PREFIX}:{stat_type}:{args_str}"
        return f"{STATS_CACHE_PREFIX}:{stat_type}"
    
    async def get_job_statistics(self, use_cache: bool = True) -> dict:
        """
        Get comprehensive job statistics
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with job statistics
        """
        cache_key = self._get_cache_key("jobs:all")
        
        # Try cache first
        if use_cache:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for job statistics")
                return cached
        
        # Compute statistics
        stats = {
            "total_jobs": await self.stats_repo.get_total_jobs(),
            "jobs_by_source": await self.stats_repo.get_jobs_by_source(),
            "jobs_by_type": await self.stats_repo.get_jobs_by_type(),
            "remote_jobs": await self.stats_repo.get_remote_jobs_count(),
            "salary_stats": await self.stats_repo.get_salary_statistics(),
            "jobs_posted_today": await self.stats_repo.get_jobs_posted_today(),
            "jobs_posted_this_week": await self.stats_repo.get_jobs_posted_this_week(),
            "top_companies": await self.stats_repo.get_jobs_by_company(limit=10),
            "top_locations": await self.stats_repo.get_jobs_by_location(limit=10),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Cache the results with statistics TTL
        await redis_client.set(cache_key, stats, cache_type="statistics")
        logger.info("Job statistics computed and cached")
        
        return stats
    
    async def get_user_statistics(self, use_cache: bool = True) -> dict:
        """
        Get user statistics
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with user statistics
        """
        cache_key = self._get_cache_key("users:all")
        
        # Try cache first
        if use_cache:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for user statistics")
                return cached
        
        # Compute statistics
        stats = {
            "total_users": await self.stats_repo.get_total_users(),
            "active_users_30d": await self.stats_repo.get_active_users(days=30),
            "active_users_7d": await self.stats_repo.get_active_users(days=7),
            "active_users_1d": await self.stats_repo.get_active_users(days=1),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Cache the results with statistics TTL
        await redis_client.set(cache_key, stats, cache_type="statistics")
        logger.info("User statistics computed and cached")
        
        return stats
    
    async def get_search_statistics(self, use_cache: bool = True) -> dict:
        """
        Get search statistics
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with search statistics
        """
        cache_key = self._get_cache_key("searches:all")
        
        # Try cache first
        if use_cache:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for search statistics")
                return cached
        
        # Compute statistics
        search_stats = await self.stats_repo.get_search_statistics()
        trending = await self.stats_repo.get_trending_searches(limit=10, days=7)
        
        stats = {
            **search_stats,
            "trending_searches": trending,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Cache the results with statistics TTL
        await redis_client.set(cache_key, stats, cache_type="statistics")
        logger.info("Search statistics computed and cached")
        
        return stats
    
    async def get_saved_jobs_statistics(self, use_cache: bool = True) -> dict:
        """
        Get saved jobs statistics
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with saved jobs statistics
        """
        cache_key = self._get_cache_key("saved_jobs:all")
        
        # Try cache first
        if use_cache:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for saved jobs statistics")
                return cached
        
        # Compute statistics
        stats = {
            "total_saved_jobs": await self.stats_repo.get_total_saved_jobs(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Cache the results with statistics TTL
        await redis_client.set(cache_key, stats, cache_type="statistics")
        logger.info("Saved jobs statistics computed and cached")
        
        return stats
    
    async def get_dashboard_statistics(self, use_cache: bool = True) -> dict:
        """
        Get comprehensive dashboard statistics
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with all statistics for dashboard
        """
        cache_key = self._get_cache_key("dashboard:all")
        
        # Try cache first
        if use_cache:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for dashboard statistics")
                return cached
        
        # Compute all statistics
        job_stats = await self.get_job_statistics(use_cache=False)
        user_stats = await self.get_user_statistics(use_cache=False)
        search_stats = await self.get_search_statistics(use_cache=False)
        saved_jobs_stats = await self.get_saved_jobs_statistics(use_cache=False)
        
        stats = {
            "jobs": job_stats,
            "users": user_stats,
            "searches": search_stats,
            "saved_jobs": saved_jobs_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Cache the results with statistics TTL
        await redis_client.set(cache_key, stats, cache_type="statistics")
        logger.info("Dashboard statistics computed and cached")
        
        return stats
    
    async def invalidate_job_statistics(self) -> bool:
        """Invalidate job statistics cache"""
        try:
            patterns = [
                self._get_cache_key("jobs:all"),
                self._get_cache_key("dashboard:all"),
            ]
            for pattern in patterns:
                await redis_client.delete(pattern)
            logger.info("Job statistics cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating job statistics cache: {str(e)}")
            return False
    
    async def invalidate_user_statistics(self) -> bool:
        """Invalidate user statistics cache"""
        try:
            patterns = [
                self._get_cache_key("users:all"),
                self._get_cache_key("dashboard:all"),
            ]
            for pattern in patterns:
                await redis_client.delete(pattern)
            logger.info("User statistics cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating user statistics cache: {str(e)}")
            return False
    
    async def invalidate_search_statistics(self) -> bool:
        """Invalidate search statistics cache"""
        try:
            patterns = [
                self._get_cache_key("searches:all"),
                self._get_cache_key("dashboard:all"),
            ]
            for pattern in patterns:
                await redis_client.delete(pattern)
            logger.info("Search statistics cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating search statistics cache: {str(e)}")
            return False
    
    async def invalidate_saved_jobs_statistics(self) -> bool:
        """Invalidate saved jobs statistics cache"""
        try:
            patterns = [
                self._get_cache_key("saved_jobs:all"),
                self._get_cache_key("dashboard:all"),
            ]
            for pattern in patterns:
                await redis_client.delete(pattern)
            logger.info("Saved jobs statistics cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating saved jobs statistics cache: {str(e)}")
            return False
    
    async def invalidate_all_statistics(self) -> bool:
        """Invalidate all statistics cache"""
        try:
            await redis_client.delete_pattern(f"{STATS_CACHE_PREFIX}:*")
            logger.info("All statistics cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating all statistics cache: {str(e)}")
            return False
