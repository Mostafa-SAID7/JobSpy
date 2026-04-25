"""
Tests for Search Cache Metadata
Tests metadata included in cached search results
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.search_service import SearchService
from app.core.redis import redis_client


class TestSearchCacheMetadata:
    """Test metadata included in cached search results."""
    
    @pytest.mark.asyncio
    async def test_search_result_includes_pagination_metadata(self):
        """Test that search results include pagination metadata."""
        db = AsyncMock()
        service = SearchService(db)
        
        service.job_repo.search = AsyncMock(return_value=[])
        service.job_repo.count_search = AsyncMock(return_value=100)
        service.search_history_repo.create = AsyncMock()
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=None):
            with patch.object(redis_client, 'set', new_callable=AsyncMock):
                result = await service.search_jobs(1, "Python", skip=0, limit=20)
        
        assert "skip" in result
        assert "limit" in result
        assert "total_count" in result
        assert "has_more" in result
        assert result["skip"] == 0
        assert result["limit"] == 20
    
    @pytest.mark.asyncio
    async def test_search_result_has_more_flag(self):
        """Test that has_more flag is correctly set."""
        db = AsyncMock()
        service = SearchService(db)
        
        service.job_repo.search = AsyncMock(return_value=[])
        service.job_repo.count_search = AsyncMock(return_value=100)
        service.search_history_repo.create = AsyncMock()
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=None):
            with patch.object(redis_client, 'set', new_callable=AsyncMock):
                # First page
                result1 = await service.search_jobs(1, "Python", skip=0, limit=20)
                assert result1["has_more"] is True
                
                # Last page
                result2 = await service.search_jobs(1, "Python", skip=80, limit=20)
                assert result2["has_more"] is False
