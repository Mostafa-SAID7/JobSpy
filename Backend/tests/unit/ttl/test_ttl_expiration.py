"""
TTL Expiration Tests
Tests that cached data expires correctly after TTL
"""

import pytest
import asyncio
from app.core.redis import redis_client


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
