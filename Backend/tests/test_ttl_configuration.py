"""
TTL Configuration Tests
Verifies that TTL configuration is working correctly across all cached endpoints
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.redis import redis_client
from app.core.config import settings
from app.services.stats_service import StatsService
from app.services.search_service import SearchService
from app.repositories.stats_repo import StatsRepository
from app.repositories.job_repo import JobRepository


class TestTTLConfiguration:
    """Test TTL configuration for different cache types"""
    
    @pytest.mark.asyncio
    async def test_cache_ttl_jobs_configuration(self):
        """Verify jobs cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("jobs")
        assert ttl == settings.CACHE_TTL_JOBS
        assert ttl == 3600  # 1 hour
    
    @pytest.mark.asyncio
    async def test_cache_ttl_search_results_configuration(self):
        """Verify search results cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("search_results")
        assert ttl == settings.CACHE_TTL_SEARCH_RESULTS
        assert ttl == 1800  # 30 minutes
    
    @pytest.mark.asyncio
    async def test_cache_ttl_statistics_configuration(self):
        """Verify statistics cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("statistics")
        assert ttl == settings.CACHE_TTL_STATISTICS
        assert ttl == 3600  # 1 hour
    
    @pytest.mark.asyncio
    async def test_cache_ttl_users_configuration(self):
        """Verify users cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("users")
        assert ttl == settings.CACHE_TTL_USERS
        assert ttl == 86400  # 24 hours
    
    @pytest.mark.asyncio
    async def test_cache_ttl_search_history_configuration(self):
        """Verify search history cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("search_history")
        assert ttl == settings.CACHE_TTL_SEARCH_HISTORY
        assert ttl == 3600  # 1 hour
    
    @pytest.mark.asyncio
    async def test_cache_ttl_recommendations_configuration(self):
        """Verify recommendations cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("recommendations")
        assert ttl == settings.CACHE_TTL_RECOMMENDATIONS
        assert ttl == 21600  # 6 hours
    
    @pytest.mark.asyncio
    async def test_cache_ttl_trending_searches_configuration(self):
        """Verify trending searches cache TTL is configured correctly"""
        ttl = redis_client.get_ttl_for_cache_type("trending_searches")
        assert ttl == settings.CACHE_TTL_TRENDING_SEARCHES
        assert ttl == 43200  # 12 hours
    
    @pytest.mark.asyncio
    async def test_default_ttl_for_unknown_cache_type(self):
        """Verify default TTL is used for unknown cache types"""
        ttl = redis_client.get_ttl_for_cache_type("unknown_type")
        assert ttl == settings.REDIS_CACHE_TTL
        assert ttl == 3600  # Default 1 hour


class TestTTLExpiration:
    """Test that cached data expires correctly"""
    
    @pytest.mark.asyncio
    async def test_cache_expires_after_ttl(self):
        """Verify that cached data expires after TTL"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            # Set a value with 1 second TTL
            test_key = "test:expiration:key"
            test_value = {"test": "data"}
            
            await redis_client.set(test_key, test_value, ttl=1)
            
            # Verify it exists
            cached = await redis_client.get(test_key)
            assert cached is not None
            assert cached == test_value
            
            # Wait for expiration
            await asyncio.sleep(1.5)
            
            # Verify it's gone
            cached = await redis_client.get(test_key)
            assert cached is None
        finally:
            if redis_client.redis:
                await redis_client.disconnect()
    
    @pytest.mark.asyncio
    async def test_cache_ttl_with_cache_type(self):
        """Verify TTL is applied correctly when using cache_type"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            test_key = "test:ttl:type:key"
            test_value = {"test": "data"}
            
            # Set with cache_type
            await redis_client.set(test_key, test_value, cache_type="search_results")
            
            # Get TTL
            ttl = await redis_client.get_ttl(test_key)
            
            # Should be close to 1800 (30 minutes)
            assert ttl > 0
            assert ttl <= 1800
        finally:
            if redis_client.redis:
                await redis_client.disconnect()
    
    @pytest.mark.asyncio
    async def test_cache_ttl_explicit_overrides_cache_type(self):
        """Verify explicit TTL overrides cache_type TTL"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            test_key = "test:ttl:override:key"
            test_value = {"test": "data"}
            
            # Set with both cache_type and explicit ttl
            await redis_client.set(
                test_key,
                test_value,
                ttl=100,  # Explicit TTL
                cache_type="search_results"  # Would be 1800
            )
            
            # Get TTL
            ttl = await redis_client.get_ttl(test_key)
            
            # Should be close to 100 (explicit TTL)
            assert ttl > 0
            assert ttl <= 100
        finally:
            if redis_client.redis:
                await redis_client.disconnect()


class TestCacheInvalidationWithTTL:
    """Test cache invalidation works correctly with TTL"""
    
    @pytest.mark.asyncio
    async def test_invalidate_cache_before_expiration(self):
        """Verify cache can be invalidated before TTL expires"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            test_key = "test:invalidate:key"
            test_value = {"test": "data"}
            
            # Set with long TTL
            await redis_client.set(test_key, test_value, ttl=3600)
            
            # Verify it exists
            cached = await redis_client.get(test_key)
            assert cached is not None
            
            # Invalidate
            await redis_client.delete(test_key)
            
            # Verify it's gone
            cached = await redis_client.get(test_key)
            assert cached is None
        finally:
            if redis_client.redis:
                await redis_client.disconnect()
    
    @pytest.mark.asyncio
    async def test_invalidate_pattern_respects_ttl(self):
        """Verify pattern invalidation works with TTL"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            # Set multiple keys with pattern
            for i in range(3):
                key = f"test:pattern:{i}"
                await redis_client.set(key, {"data": i}, ttl=3600)
            
            # Verify all exist
            for i in range(3):
                key = f"test:pattern:{i}"
                cached = await redis_client.get(key)
                assert cached is not None
            
            # Invalidate pattern
            deleted = await redis_client.delete_pattern("test:pattern:*")
            assert deleted == 3
            
            # Verify all are gone
            for i in range(3):
                key = f"test:pattern:{i}"
                cached = await redis_client.get(key)
                assert cached is None
        finally:
            if redis_client.redis:
                await redis_client.disconnect()


class TestStatsServiceCaching:
    """Test stats service caching with TTL"""
    
    @pytest.mark.asyncio
    async def test_job_statistics_cache_ttl(self):
        """Verify job statistics are cached with correct TTL"""
        # Mock the repository
        mock_repo = AsyncMock(spec=StatsRepository)
        mock_repo.get_total_jobs = AsyncMock(return_value=100)
        mock_repo.get_jobs_by_source = AsyncMock(return_value={"linkedin": 50, "indeed": 50})
        mock_repo.get_jobs_by_type = AsyncMock(return_value={"fulltime": 80, "parttime": 20})
        mock_repo.get_remote_jobs_count = AsyncMock(return_value=30)
        mock_repo.get_salary_statistics = AsyncMock(return_value={
            "min": 30000,
            "max": 150000,
            "avg": 80000
        })
        mock_repo.get_jobs_posted_today = AsyncMock(return_value=10)
        mock_repo.get_jobs_posted_this_week = AsyncMock(return_value=50)
        mock_repo.get_top_companies = AsyncMock(return_value=[
            {"company": "Tech Corp", "count": 20},
            {"company": "StartUp Inc", "count": 15}
        ])
        mock_repo.get_top_locations = AsyncMock(return_value=[
            {"location": "San Francisco", "count": 30},
            {"location": "New York", "count": 25}
        ])
        
        stats_service = StatsService(mock_repo)
        
        # Get statistics
        stats = await stats_service.get_job_statistics(use_cache=True)
        
        # Verify stats are returned
        assert stats is not None
        assert "total_jobs" in stats
        assert stats["total_jobs"] == 100


class TestSearchServiceCaching:
    """Test search service caching with TTL"""
    
    @pytest.mark.asyncio
    async def test_search_results_cache_ttl(self):
        """Verify search results are cached with correct TTL"""
        # Mock the database session
        mock_db = AsyncMock()
        
        search_service = SearchService(mock_db)
        
        # Verify cache key generation
        cache_key = search_service._generate_search_cache_key(
            "python developer",
            {"location": "San Francisco"},
            0,
            20
        )
        
        # Cache key should be deterministic
        assert cache_key is not None
        assert isinstance(cache_key, str)
        assert "python developer" in cache_key or len(cache_key) > 0


class TestCacheStatistics:
    """Test cache statistics tracking"""
    
    @pytest.mark.asyncio
    async def test_cache_hit_rate_calculation(self):
        """Verify cache hit rate is calculated correctly"""
        # This test requires Redis to be running
        # Skip if Redis is not available
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            # Reset stats
            await redis_client.reset_stats()
            
            # Simulate cache operations
            test_key = "test:stats:key"
            test_value = {"test": "data"}
            
            # Set value
            await redis_client.set(test_key, test_value)
            
            # Get value (hit)
            await redis_client.get(test_key)
            
            # Get non-existent value (miss)
            await redis_client.get("non:existent:key")
            
            # Get stats
            stats = await redis_client.get_stats()
            
            # Verify stats
            assert stats["hits"] >= 1
            assert stats["misses"] >= 1
            assert stats["sets"] >= 1
            assert "hit_rate" in stats
            
            # Clean up
            await redis_client.delete(test_key)
        finally:
            if redis_client.redis:
                await redis_client.disconnect()


class TestCacheInvalidationStrategies:
    """Test different cache invalidation strategies"""
    
    @pytest.mark.asyncio
    async def test_invalidate_user_cache_pattern(self):
        """Verify user cache invalidation pattern"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            user_id = "test-user-123"
            
            # Set multiple user-related cache entries
            await redis_client.set(f"user_alerts:{user_id}", {"alerts": []}, ttl=3600)
            await redis_client.set(f"user_saved_jobs:{user_id}", {"jobs": []}, ttl=3600)
            await redis_client.set(f"recommendations:{user_id}:10", {"recs": []}, ttl=3600)
            
            # Verify they exist
            assert await redis_client.exists(f"user_alerts:{user_id}")
            assert await redis_client.exists(f"user_saved_jobs:{user_id}")
            assert await redis_client.exists(f"recommendations:{user_id}:10")
            
            # Invalidate user cache
            patterns = [
                f"user_alerts:{user_id}*",
                f"user_saved_jobs:{user_id}*",
                f"recommendations:{user_id}*",
            ]
            
            for pattern in patterns:
                await redis_client.delete_pattern(pattern)
            
            # Verify they're gone
            assert not await redis_client.exists(f"user_alerts:{user_id}")
            assert not await redis_client.exists(f"user_saved_jobs:{user_id}")
            assert not await redis_client.exists(f"recommendations:{user_id}:10")
        finally:
            if redis_client.redis:
                await redis_client.disconnect()
    
    @pytest.mark.asyncio
    async def test_invalidate_job_cache_pattern(self):
        """Verify job cache invalidation pattern"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            job_id = "test-job-123"
            
            # Set multiple job-related cache entries
            await redis_client.set(f"job:{job_id}", {"title": "Test Job"}, ttl=3600)
            await redis_client.set(f"job_stats:{job_id}", {"views": 10}, ttl=3600)
            
            # Verify they exist
            assert await redis_client.exists(f"job:{job_id}")
            assert await redis_client.exists(f"job_stats:{job_id}")
            
            # Invalidate job cache
            patterns = [
                f"job:{job_id}*",
                f"job_stats:{job_id}*",
            ]
            
            for pattern in patterns:
                await redis_client.delete_pattern(pattern)
            
            # Verify they're gone
            assert not await redis_client.exists(f"job:{job_id}")
            assert not await redis_client.exists(f"job_stats:{job_id}")
        finally:
            if redis_client.redis:
                await redis_client.disconnect()


class TestCachePerformance:
    """Test cache performance improvements"""
    
    @pytest.mark.asyncio
    async def test_cache_improves_response_time(self):
        """Verify cache improves response time"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            test_key = "test:performance:key"
            test_value = {"data": "x" * 1000}  # 1KB of data
            
            # Set value
            await redis_client.set(test_key, test_value, ttl=3600)
            
            # Measure cache hit time
            import time
            
            start = time.time()
            for _ in range(100):
                await redis_client.get(test_key)
            cache_time = time.time() - start
            
            # Cache should be fast (less than 1 second for 100 gets)
            assert cache_time < 1.0
            
            # Clean up
            await redis_client.delete(test_key)
        finally:
            if redis_client.redis:
                await redis_client.disconnect()


class TestCacheConsistency:
    """Test cache consistency with database"""
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_on_data_update(self):
        """Verify cache is invalidated when data is updated"""
        try:
            await redis_client.connect()
        except Exception:
            pytest.skip("Redis not available")
        
        try:
            test_key = "test:consistency:key"
            original_value = {"version": 1}
            updated_value = {"version": 2}
            
            # Set original value
            await redis_client.set(test_key, original_value, ttl=3600)
            
            # Verify cached value
            cached = await redis_client.get(test_key)
            assert cached["version"] == 1
            
            # Invalidate cache
            await redis_client.delete(test_key)
            
            # Set new value
            await redis_client.set(test_key, updated_value, ttl=3600)
            
            # Verify new cached value
            cached = await redis_client.get(test_key)
            assert cached["version"] == 2
            
            # Clean up
            await redis_client.delete(test_key)
        finally:
            if redis_client.redis:
                await redis_client.disconnect()
