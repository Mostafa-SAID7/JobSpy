from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import logging
from app.models.search_history import SearchHistory
from app.schemas.search_history import SearchHistoryCreate
from app.core.redis import redis_client

logger = logging.getLogger(__name__)


class SearchHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, search_create: SearchHistoryCreate) -> SearchHistory:
        """Create a new search history record."""
        db_search = SearchHistory(
            user_id=user_id,
            job_id=search_create.job_id,
            query=search_create.query,
            filters=search_create.filters,
            results_count=search_create.results_count,
            search_type=search_create.search_type,
        )
        self.session.add(db_search)
        await self.session.flush()
        
        # Invalidate search history cache for this user
        await self.invalidate_user_search_history_cache(user_id)
        
        return db_search

    async def get_by_id(self, search_id: UUID) -> SearchHistory | None:
        """Get search history by ID with caching."""
        # Try to get from cache
        cache_key = f"search_history:{search_id}"
        cached_search = await redis_client.get(cache_key)
        if cached_search:
            logger.debug(f"Cache hit for search history {search_id}")
            return cached_search
        
        result = await self.session.execute(
            select(SearchHistory).where(SearchHistory.id == search_id)
        )
        search = result.scalar_one_or_none()
        
        # Cache the result with search_history TTL
        if search:
            await redis_client.set(cache_key, search, cache_type="search_history")
        
        return search

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[SearchHistory]:
        """Get search history for a user with caching."""
        # Generate cache key
        cache_key = f"search_history:user:{user_id}:{skip}:{limit}"
        
        # Try to get from cache
        cached_searches = await redis_client.get(cache_key)
        if cached_searches:
            logger.debug(f"Cache hit for search history by user {user_id}")
            return cached_searches
        
        result = await self.session.execute(
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(SearchHistory.created_at.desc())
        )
        searches = result.scalars().all()
        
        # Cache the result with search_history TTL
        if searches:
            await redis_client.set(cache_key, searches, cache_type="search_history")
        
        return searches

    async def get_by_user_and_query(self, user_id: UUID, query: str, skip: int = 0, limit: int = 100) -> list[SearchHistory]:
        """Get search history for a user by query with caching."""
        # Generate cache key
        cache_key = f"search_history:user:{user_id}:query:{query}:{skip}:{limit}"
        
        # Try to get from cache
        cached_searches = await redis_client.get(cache_key)
        if cached_searches:
            logger.debug(f"Cache hit for search history by user {user_id} and query {query}")
            return cached_searches
        
        result = await self.session.execute(
            select(SearchHistory)
            .where(
                (SearchHistory.user_id == user_id) &
                (SearchHistory.query.ilike(f"%{query}%"))
            )
            .offset(skip)
            .limit(limit)
            .order_by(SearchHistory.created_at.desc())
        )
        searches = result.scalars().all()
        
        # Cache the result with search_history TTL
        if searches:
            await redis_client.set(cache_key, searches, cache_type="search_history")
        
        return searches

    async def delete(self, search_id: UUID) -> bool:
        """Delete search history and invalidate cache."""
        search = await self.get_by_id(search_id)
        if not search:
            return False

        await self.session.delete(search)
        await self.session.flush()
        
        # Invalidate search history cache
        await self.invalidate_search_history_cache(search_id)
        await self.invalidate_user_search_history_cache(search.user_id)
        
        return True

    async def delete_by_user(self, user_id: UUID) -> int:
        """Delete all search history for a user and invalidate cache."""
        result = await self.session.execute(
            select(SearchHistory).where(SearchHistory.user_id == user_id)
        )
        searches = result.scalars().all()
        count = len(searches)

        for search in searches:
            await self.session.delete(search)

        await self.session.flush()
        
        # Invalidate all search history cache for this user
        await self.invalidate_user_search_history_cache(user_id)
        
        return count

    async def count_by_user(self, user_id: UUID) -> int:
        """Count search history for a user."""
        result = await self.session.execute(
            select(SearchHistory).where(SearchHistory.user_id == user_id)
        )
        return len(result.scalars().all())

    async def get_popular_queries(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most popular search queries."""
        result = await self.session.execute(
            select(SearchHistory.query)
            .group_by(SearchHistory.query)
            .order_by(select(SearchHistory).where(SearchHistory.query == SearchHistory.query).count().desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def invalidate_search_history_cache(self, search_id: UUID) -> bool:
        """
        Invalidate cache for a specific search history entry.
        
        Args:
            search_id: Search history ID
        
        Returns:
            True if invalidated successfully
        """
        try:
            cache_key = f"search_history:{search_id}"
            await redis_client.delete(cache_key)
            logger.info(f"Cache invalidated for search history {search_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating search history cache: {str(e)}")
            return False

    async def invalidate_user_search_history_cache(self, user_id: UUID) -> bool:
        """
        Invalidate all search history cache for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            True if invalidated successfully
        """
        try:
            pattern = f"search_history:user:{user_id}:*"
            await redis_client.delete_pattern(pattern)
            logger.info(f"Cache invalidated for search history by user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating user search history cache: {str(e)}")
            return False

    async def invalidate_all_search_history_cache(self) -> bool:
        """
        Invalidate all search history cache entries.
        
        Returns:
            True if invalidated successfully
        """
        try:
            patterns = [
                "search_history:*",
                "search_history:user:*",
            ]
            
            for pattern in patterns:
                await redis_client.delete_pattern(pattern)
            
            logger.info("All search history cache invalidated")
            return True
        except Exception as e:
            logger.error(f"Error invalidating all search history cache: {str(e)}")
            return False
