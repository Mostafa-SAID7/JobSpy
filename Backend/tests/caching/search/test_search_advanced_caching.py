"""
Tests for Advanced Search Caching
Tests advanced search with caching
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.search_service import SearchService
from app.core.redis import redis_client


class TestAdvancedSearchCaching:
    """Test advanced search with caching."""
    
    @pytest.mark.asyncio
    async def test_advanced_search_with_multiple_filters(self):
        """Test advanced search with multiple filter criteria."""
        db = AsyncMock()
        service = SearchService(db)
        
        # Mock the job repository methods
        service.job_repo.search = AsyncMock(return_value=[])
        service.job_repo.count_search = AsyncMock(return_value=0)
        service.search_history_repo.create = AsyncMock()
        
        search_params = {
            "query": "Python Developer",
            "location": "San Francisco",
            "job_type": "fulltime",
            "salary_min": 100000,
            "salary_max": 150000,
            "is_remote": True,
            "skip": 0,
            "limit": 20,
        }
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=None):
            with patch.object(redis_client, 'set', new_callable=AsyncMock):
                result = await service.advanced_search(1, search_params)
        
        assert "query" in result
        assert "filters" in result
        assert "results" in result
    
    @pytest.mark.asyncio
    async def test_advanced_search_cache_hit(self):
        """Test that cached results are returned on cache hit."""
        db = AsyncMock()
        service = SearchService(db)
        
        search_params = {
            "query": "Python",
            "location": "NYC",
            "skip": 0,
            "limit": 20,
        }
        
        cached_result = {
            "query": "Python",
            "filters": {"location": "NYC"},
            "results": [{"id": "job1"}],
            "total_count": 1,
        }
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=cached_result):
            result = await service.advanced_search(1, search_params)
        
        assert result == cached_result
    
    @pytest.mark.asyncio
    async def test_advanced_search_builds_correct_filters(self):
        """Test that advanced search builds correct filter dictionary."""
        db = AsyncMock()
        service = SearchService(db)
        
        service.job_repo.search = AsyncMock(return_value=[])
        service.job_repo.count_search = AsyncMock(return_value=0)
        service.search_history_repo.create = AsyncMock()
        
        search_params = {
            "query": "Engineer",
            "location": "SF",
            "job_type": "fulltime",
            "experience_level": "senior",
            "salary_min": 150000,
            "salary_max": 250000,
            "is_remote": False,
            "skip": 0,
            "limit": 20,
        }
        
        with patch.object(redis_client, 'get', new_callable=AsyncMock, return_value=None):
            with patch.object(redis_client, 'set', new_callable=AsyncMock):
                result = await service.advanced_search(1, search_params)
        
        # Verify filters were built correctly
        assert result["filters"]["location"] == "SF"
        assert result["filters"]["job_type"] == "fulltime"
        assert result["filters"]["salary_min"] == 150000
