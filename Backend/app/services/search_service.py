"""
خدمة البحث - JobSpy
Search service for JobSpy
"""
import logging
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.job_repo import JobRepository
from app.repositories.search_history_repo import SearchHistoryRepository
from app.schemas.search_history import SearchHistoryCreate
from app.core.redis import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for handling search operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.search_history_repo = SearchHistoryRepository(db)
    
    def _generate_search_cache_key(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> str:
        """
        Generate a cache key for search results that includes all parameters.
        
        This method creates a deterministic cache key that includes:
        - Search query
        - All filter parameters (location, job_type, salary range, etc.)
        - Pagination parameters (skip, limit)
        
        Args:
            query: Search query string
            filters: Dictionary of filter parameters
            skip: Number of results to skip
            limit: Maximum number of results
        
        Returns:
            Cache key string
        """
        # Create a normalized filter dictionary for consistent key generation
        normalized_filters = {}
        if filters:
            for key in sorted(filters.keys()):
                value = filters[key]
                # Skip None values to avoid cache key variations
                if value is not None:
                    normalized_filters[key] = value
        
        # Create a deterministic string representation
        filter_str = json.dumps(normalized_filters, sort_keys=True, default=str)
        
        # Create hash of filters to keep cache key length reasonable
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
        
        # Generate cache key with all parameters
        cache_key = f"search:advanced:{query}:{filter_hash}:{skip}:{limit}"
        
        logger.debug(f"Generated cache key: {cache_key} for query: {query}, filters: {normalized_filters}")
        
        return cache_key
    
    def _generate_simple_search_cache_key(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> str:
        """
        Generate a cache key for simple search results.
        
        Args:
            query: Search query string
            skip: Number of results to skip
            limit: Maximum number of results
        
        Returns:
            Cache key string
        """
        cache_key = f"search:simple:{query}:{skip}:{limit}"
        return cache_key
    
    async def search_jobs(
        self,
        user_id: int,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Search for jobs and save search history.
        
        This method:
        1. Generates a cache key that includes all search parameters
        2. Checks if results are cached
        3. If cached, returns cached results
        4. If not cached, performs search and caches results
        5. Saves search history for user
        
        Args:
            user_id: User ID
            query: Search query
            filters: Additional filters (location, job_type, salary_min, salary_max, etc.)
            skip: Number of results to skip
            limit: Maximum number of results
        
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Generate cache key with all parameters
            cache_key = self._generate_search_cache_key(query, filters, skip, limit)
            
            # Try to get from cache
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for search: {query} with filters: {filters}")
                return cached_result
            
            # Search for jobs
            jobs = await self.job_repo.search(query, filters=filters, skip=skip, limit=limit)
            total_count = await self.job_repo.count_search(query, filters=filters)
            
            # Save search history
            search_history = SearchHistoryCreate(
                user_id=user_id,
                query=query,
                search_type="advanced" if filters else "simple",
                filters=filters or {},
                results_count=len(jobs),
            )
            
            await self.search_history_repo.create(search_history)
            await self.db.commit()
            
            result = {
                "query": query,
                "filters": filters or {},
                "results": jobs,
                "total_count": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total_count,
            }
            
            # Cache the result with search_results TTL
            await redis_client.set(cache_key, result, cache_type="search_results")
            
            logger.info(f"Search performed by user {user_id}: {query}, cached with key: {cache_key}")
            
            return result
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return {
                "query": query,
                "filters": filters or {},
                "results": [],
                "total_count": 0,
                "skip": skip,
                "limit": limit,
                "has_more": False,
                "error": str(e),
            }
    
    async def advanced_search(
        self,
        user_id: int,
        search_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform advanced search with multiple criteria.
        
        This method handles complex search queries with multiple filters:
        - Query string
        - Location filtering
        - Job type filtering
        - Experience level filtering
        - Salary range filtering
        - Remote work filtering
        - Pagination
        
        Cache key includes all parameters to ensure proper cache hits for
        identical search combinations.
        
        Args:
            user_id: User ID
            search_params: Advanced search parameters including:
                - query: Search query string
                - location: Job location
                - job_type: Type of job (fulltime, parttime, etc.)
                - experience_level: Required experience level
                - salary_min: Minimum salary
                - salary_max: Maximum salary
                - is_remote: Whether job is remote
                - skip: Pagination offset
                - limit: Results per page
        
        Returns:
            Dictionary with search results
        """
        try:
            # Extract search parameters
            query = search_params.get("query", "")
            location = search_params.get("location")
            job_type = search_params.get("job_type")
            experience_level = search_params.get("experience_level")
            salary_min = search_params.get("salary_min")
            salary_max = search_params.get("salary_max")
            is_remote = search_params.get("is_remote")
            skip = search_params.get("skip", 0)
            limit = search_params.get("limit", 20)
            
            # Build filters dictionary
            filters = {}
            if location:
                filters["location"] = location
            if job_type:
                filters["job_type"] = job_type
            if experience_level:
                filters["experience_level"] = experience_level
            if salary_min is not None:
                filters["salary_min"] = salary_min
            if salary_max is not None:
                filters["salary_max"] = salary_max
            if is_remote is not None:
                filters["is_remote"] = is_remote
            
            # Generate cache key with all filter combinations
            cache_key = self._generate_search_cache_key(query, filters, skip, limit)
            
            # Try to get from cache
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for advanced search: {query} with filters: {filters}")
                return cached_result
            
            # Perform search
            result = await self.search_jobs(user_id, query, filters, skip, limit)
            
            logger.info(f"Advanced search performed: query={query}, filters={filters}, cache_key={cache_key}")
            
            return result
        except Exception as e:
            logger.error(f"Error performing advanced search: {str(e)}")
            return {
                "results": [],
                "total_count": 0,
                "error": str(e),
            }
    
    async def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions based on previous searches.
        
        Args:
            query: Partial query
            limit: Maximum number of suggestions
        
        Returns:
            List of search suggestions
        """
        try:
            # Get suggestions from search history
            suggestions = await self.search_history_repo.get_suggestions(query, limit)
            return suggestions
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []
    
    async def get_trending_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending searches.
        
        Args:
            limit: Maximum number of trending searches
        
        Returns:
            List of trending searches with counts
        """
        try:
            # Try to get from cache
            cache_key = f"trending_searches:{limit}"
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info("Cache hit for trending searches")
                return cached_result
            
            trending = await self.search_history_repo.get_trending_searches(limit)
            
            # Cache the result
            await redis_client.set(cache_key, trending, ttl=3600)  # Cache for 1 hour
            
            return trending
        except Exception as e:
            logger.error(f"Error getting trending searches: {str(e)}")
            return []
    
    async def get_user_search_history(
        self,
        user_id: int,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get user's search history.
        
        Args:
            user_id: User ID
            limit: Maximum number of searches
        
        Returns:
            List of user's searches
        """
        try:
            history = await self.search_history_repo.get_by_user_id(user_id, limit)
            return history
        except Exception as e:
            logger.error(f"Error getting search history: {str(e)}")
            return []
    
    async def clear_user_search_history(self, user_id: int) -> bool:
        """
        Clear user's search history.
        
        Args:
            user_id: User ID
        
        Returns:
            True if cleared successfully
        """
        try:
            await self.search_history_repo.delete_by_user_id(user_id)
            await self.db.commit()
            logger.info(f"Search history cleared for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing search history: {str(e)}")
            return False
    
    async def get_job_recommendations(
        self,
        user_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get job recommendations based on user's search history.
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations
        
        Returns:
            List of recommended jobs
        """
        try:
            # Try to get from cache
            cache_key = f"recommendations:{user_id}:{limit}"
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for recommendations for user {user_id}")
                return cached_result
            
            # Get user's search history
            search_history = await self.search_history_repo.get_by_user_id(user_id, limit=5)
            
            if not search_history:
                # Return popular jobs if no search history
                recommendations = await self.job_repo.get_popular_jobs(limit)
            else:
                # Extract queries from search history
                queries = [sh.get("query") for sh in search_history if sh.get("query")]
                
                # Search for jobs matching these queries
                recommendations = []
                for query in queries:
                    jobs = await self.job_repo.search(query, limit=limit // len(queries))
                    recommendations.extend(jobs)
                
                # Remove duplicates and limit results
                seen_ids = set()
                unique_recommendations = []
                for job in recommendations:
                    if job.get("id") not in seen_ids:
                        unique_recommendations.append(job)
                        seen_ids.add(job.get("id"))
                        if len(unique_recommendations) >= limit:
                            break
                
                recommendations = unique_recommendations
            
            # Cache the result
            await redis_client.set(cache_key, recommendations, ttl=1800)  # Cache for 30 minutes
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting job recommendations: {str(e)}")
            return []
    
    async def filter_jobs(
        self,
        jobs: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Filter jobs based on criteria.
        
        Args:
            jobs: List of jobs to filter
            filters: Filter criteria
        
        Returns:
            Filtered list of jobs
        """
        filtered = jobs
        
        if "location" in filters and filters["location"]:
            location = filters["location"].lower()
            filtered = [j for j in filtered if location in (j.get("location") or "").lower()]
        
        if "job_type" in filters and filters["job_type"]:
            job_type = filters["job_type"].lower()
            filtered = [j for j in filtered if j.get("job_type") and job_type in j.get("job_type", "").lower()]
        
        if "experience_level" in filters and filters["experience_level"]:
            exp_level = filters["experience_level"].lower()
            filtered = [j for j in filtered if j.get("experience_level") and exp_level in j.get("experience_level", "").lower()]
        
        if "salary_min" in filters and filters["salary_min"]:
            min_salary = filters["salary_min"]
            filtered = [j for j in filtered if j.get("salary_max") and j.get("salary_max") >= min_salary]
        
        if "salary_max" in filters and filters["salary_max"]:
            max_salary = filters["salary_max"]
            filtered = [j for j in filtered if j.get("salary_min") and j.get("salary_min") <= max_salary]
        
        if "is_remote" in filters and filters["is_remote"] is not None:
            is_remote = filters["is_remote"]
            filtered = [j for j in filtered if j.get("is_remote") == is_remote]
        
        return filtered
    
    async def sort_jobs(
        self,
        jobs: List[Dict[str, Any]],
        sort_by: str = "posted_date",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Sort jobs based on criteria.
        
        Args:
            jobs: List of jobs to sort
            sort_by: Sort field (posted_date, salary, company, etc)
            order: Sort order (asc, desc)
        
        Returns:
            Sorted list of jobs
        """
        reverse = order.lower() == "desc"
        
        if sort_by == "posted_date":
            return sorted(jobs, key=lambda x: x.get("posted_date") or datetime.min, reverse=reverse)
        elif sort_by == "salary":
            return sorted(jobs, key=lambda x: x.get("salary_max") or 0, reverse=reverse)
        elif sort_by == "company":
            return sorted(jobs, key=lambda x: x.get("company") or "", reverse=reverse)
        elif sort_by == "title":
            return sorted(jobs, key=lambda x: x.get("title") or "", reverse=reverse)
        else:
            return jobs
    
    async def invalidate_search_cache(self, query: str, filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Invalidate search cache for a specific query.
        
        This method invalidates cache for a specific search query and filter combination.
        It also invalidates all pagination variations of the same search.
        
        Args:
            query: Search query
            filters: Filter criteria
        
        Returns:
            True if invalidated successfully
        """
        try:
            # Invalidate specific search cache key
            cache_key = self._generate_search_cache_key(query, filters, 0, 20)
            await redis_client.delete(cache_key)
            
            # Also invalidate all pagination variations
            # Generate pattern for all pagination variations
            normalized_filters = {}
            if filters:
                for key in sorted(filters.keys()):
                    value = filters[key]
                    if value is not None:
                        normalized_filters[key] = value
            
            filter_str = json.dumps(normalized_filters, sort_keys=True, default=str)
            filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
            
            # Delete all pagination variations
            pattern = f"search:advanced:{query}:{filter_hash}:*"
            await redis_client.delete_pattern(pattern)
            
            logger.info(f"Cache invalidated for search: {query} with filters: {filters}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating search cache: {str(e)}")
            return False
    
    async def invalidate_all_search_cache(self) -> bool:
        """
        Invalidate all search-related cache entries.
        
        This method clears all cached search results, recommendations, and trending searches.
        Use this when search-related data changes significantly.
        
        Returns:
            True if invalidated successfully
        """
        try:
            patterns = [
                "search:advanced:*",
                "search:simple:*",
                "recommendations:*",
                "trending_searches:*",
            ]
            
            for pattern in patterns:
                await redis_client.delete_pattern(pattern)
            
            logger.info("All search cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating all search cache: {str(e)}")
            return False
    
    async def invalidate_recommendations_cache(self, user_id: int) -> bool:
        """
        Invalidate recommendations cache for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            True if invalidated successfully
        """
        try:
            # Invalidate all recommendation caches for this user
            for limit in [5, 10, 20]:
                cache_key = f"recommendations:{user_id}:{limit}"
                await redis_client.delete(cache_key)
            logger.info(f"Recommendations cache invalidated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating recommendations cache: {str(e)}")
            return False
    
    async def invalidate_trending_cache(self) -> bool:
        """
        Invalidate trending searches cache.
        
        Returns:
            True if invalidated successfully
        """
        try:
            for limit in [5, 10, 20]:
                cache_key = f"trending_searches:{limit}"
                await redis_client.delete(cache_key)
            logger.info("Trending searches cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating trending cache: {str(e)}")
            return False
