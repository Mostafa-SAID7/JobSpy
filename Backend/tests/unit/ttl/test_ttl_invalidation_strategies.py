"""
TTL Cache Invalidation Strategies Tests
Tests different cache invalidation strategies
"""

import pytest
from app.infrastructure.cache.redis import redis_client


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
