"""
TTL Cache Invalidation Tests
Tests cache invalidation works correctly with TTL
"""

import pytest
from app.core.redis import redis_client


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
