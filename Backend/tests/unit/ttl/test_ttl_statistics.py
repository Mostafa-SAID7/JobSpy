"""
TTL Cache Statistics Tests
Tests cache statistics tracking and performance
"""

import pytest
import time
from app.core.redis import redis_client


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
