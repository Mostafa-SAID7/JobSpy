"""
Tests for Search Cache Invalidation
Tests cache invalidation for search results
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.search_service import SearchService
from app.infrastructure.cache.redis import redis_client


class TestSearchCacheInvalidation:
    """Test cache invalidation for search results."""
    
    @pytest.mark.asyncio
    async def test_invalidate_search_cache_specific_query(self):
        """Test invalidating cache for specific search query."""
        db = AsyncMock()
        service = SearchService(db)
        
        query = "Python Developer"
        filters = {"location": "NYC"}
        
        with patch.object(redis_client, 'delete', new_callable=AsyncMock) as mock_delete:
            with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
                result = await service.invalidate_search_cache(query, filters)
        
        assert result is True
        mock_delete.assert_called_once()
        mock_delete_pattern.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_invalidate_all_search_cache(self):
        """Test invalidating all search-related cache."""
        db = AsyncMock()
        service = SearchService(db)
        
        with patch.object(redis_client, 'delete_pattern', new_callable=AsyncMock) as mock_delete_pattern:
            result = await service.invalidate_all_search_cache()
        
        assert result is True
        # Should delete multiple patterns
        assert mock_delete_pattern.call_count >= 4
