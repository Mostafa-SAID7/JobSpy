# TTL (Time-To-Live) Implementation for Cache

## Overview

This document describes the Time-To-Live (TTL) configuration implementation for the JobSpy caching system. TTL ensures that cached data automatically expires after a specified duration, preventing stale data from being served to users.

## TTL Configuration

### Default TTL Values

Different cache types have different TTL values based on data freshness requirements:

| Cache Type | TTL | Duration | Reason |
|-----------|-----|----------|--------|
| Jobs | 3600 | 1 hour | Job listings change frequently |
| Search Results | 1800 | 30 minutes | Search results need to be fresh |
| Statistics | 3600 | 1 hour | Statistics update hourly |
| Users | 86400 | 24 hours | User profiles change infrequently |
| Search History | 3600 | 1 hour | Search history is frequently accessed |
| Recommendations | 21600 | 6 hours | Recommendations can be stale longer |
| Trending Searches | 43200 | 12 hours | Trends change slowly |

### Configuration

TTL values are configured in `Backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # ── Cache TTL Configuration (in seconds) ──────────────────────────────
    CACHE_TTL_JOBS: int = 3600  # Jobs: 1 hour
    CACHE_TTL_SEARCH_RESULTS: int = 1800  # Search results: 30 minutes
    CACHE_TTL_STATISTICS: int = 3600  # Statistics: 1 hour
    CACHE_TTL_USERS: int = 86400  # Users: 24 hours
    CACHE_TTL_SEARCH_HISTORY: int = 3600  # Search history: 1 hour
    CACHE_TTL_RECOMMENDATIONS: int = 21600  # Recommendations: 6 hours
    CACHE_TTL_TRENDING_SEARCHES: int = 43200  # Trending searches: 12 hours
```

These values can be overridden via environment variables in `.env`:

```bash
CACHE_TTL_JOBS=3600
CACHE_TTL_SEARCH_RESULTS=1800
CACHE_TTL_STATISTICS=3600
CACHE_TTL_USERS=86400
CACHE_TTL_SEARCH_HISTORY=3600
CACHE_TTL_RECOMMENDATIONS=21600
CACHE_TTL_TRENDING_SEARCHES=43200
```

## Implementation Details

### Redis Client Enhancement

The `RedisClient` class in `Backend/app/core/redis.py` has been enhanced with:

1. **`get_ttl_for_cache_type(cache_type: str) -> int`**: Returns the TTL value for a specific cache type

```python
def get_ttl_for_cache_type(self, cache_type: str) -> int:
    """Get TTL for a specific cache type"""
    ttl_map = {
        "jobs": settings.CACHE_TTL_JOBS,
        "search_results": settings.CACHE_TTL_SEARCH_RESULTS,
        "statistics": settings.CACHE_TTL_STATISTICS,
        "users": settings.CACHE_TTL_USERS,
        "search_history": settings.CACHE_TTL_SEARCH_HISTORY,
        "recommendations": settings.CACHE_TTL_RECOMMENDATIONS,
        "trending_searches": settings.CACHE_TTL_TRENDING_SEARCHES,
    }
    return ttl_map.get(cache_type, settings.REDIS_CACHE_TTL)
```

2. **Enhanced `set()` method**: Now accepts `cache_type` parameter for automatic TTL selection

```python
async def set(
    self,
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    cache_type: Optional[str] = None,
) -> bool:
    """
    Set value in cache
    
    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds (overrides cache_type)
        cache_type: Type of cache for automatic TTL selection
    """
```

### Usage Patterns

#### Pattern 1: Using cache_type parameter (Recommended)

```python
# Cache jobs with automatic TTL
await redis_client.set(cache_key, jobs, cache_type="jobs")

# Cache search results with automatic TTL
await redis_client.set(cache_key, results, cache_type="search_results")

# Cache user data with automatic TTL
await redis_client.set(cache_key, user, cache_type="users")
```

#### Pattern 2: Using explicit TTL

```python
# Override TTL for specific use case
await redis_client.set(cache_key, data, ttl=600)  # 10 minutes
```

#### Pattern 3: Using default TTL

```python
# Use default TTL from settings
await redis_client.set(cache_key, data)
```

## Updated Components

### Repositories

All repositories have been updated to use cache_type parameter:

1. **JobRepository** (`Backend/app/repositories/job_repo.py`)
   - `get_by_id()`: Uses `cache_type="jobs"`
   - `get_all()`: Uses `cache_type="jobs"`
   - `get_by_source()`: Uses `cache_type="jobs"`
   - `get_by_company()`: Uses `cache_type="jobs"`
   - `search()`: Uses `cache_type="jobs"`

2. **UserRepository** (`Backend/app/repositories/user_repo.py`)
   - `get_by_id()`: Uses `cache_type="users"`
   - `get_by_email()`: Uses `cache_type="users"`

3. **SearchHistoryRepository** (`Backend/app/repositories/search_history_repo.py`)
   - `get_by_id()`: Uses `cache_type="search_history"`
   - `get_by_user()`: Uses `cache_type="search_history"`
   - `get_by_user_and_query()`: Uses `cache_type="search_history"`

### Services

Services have been updated to use cache_type parameter:

1. **SearchService** (`Backend/app/services/search_service.py`)
   - `search_jobs()`: Uses `cache_type="search_results"`

2. **StatsService** (`Backend/app/services/stats_service.py`)
   - `get_job_statistics()`: Uses `cache_type="statistics"`
   - `get_user_statistics()`: Uses `cache_type="statistics"`
   - `get_search_statistics()`: Uses `cache_type="statistics"`
   - `get_saved_jobs_statistics()`: Uses `cache_type="statistics"`
   - `get_dashboard_statistics()`: Uses `cache_type="statistics"`

## Automatic Cache Expiration

Redis automatically handles cache expiration:

1. **Expiration Mechanism**: Redis uses the `SETEX` command which sets both the value and TTL atomically
2. **Background Cleanup**: Redis automatically removes expired keys in the background
3. **TTL Verification**: Use `redis_client.get_ttl(key)` to check remaining TTL for a key

### Example: Checking TTL

```python
# Get remaining TTL for a key
ttl = await redis_client.get_ttl("job:123")
if ttl > 0:
    print(f"Key expires in {ttl} seconds")
elif ttl == -1:
    print("Key exists but has no expiration")
elif ttl == -2:
    print("Key does not exist")
```

## Monitoring and Logging

### Cache Statistics

The Redis client tracks cache operations:

```python
stats = await redis_client.get_stats()
# Returns:
# {
#     "hits": 150,
#     "misses": 50,
#     "sets": 200,
#     "deletes": 10,
#     "errors": 2,
#     "total_requests": 200,
#     "hit_rate": "75.00%",
#     "timestamp": "2024-01-01T12:00:00"
# }
```

### Logging

Cache operations are logged with TTL information:

```
DEBUG: Cache set for key job:123 with TTL 3600s
DEBUG: Cache hit for job 123
INFO: Cache invalidated for job 123
```

## Testing

Comprehensive tests are provided in `Backend/tests/test_ttl_configuration.py`:

1. **TTL Configuration Tests**: Verify all TTL values are configured correctly
2. **Cache Set Tests**: Verify cache_type parameter works correctly
3. **Repository Tests**: Verify repositories use correct TTL
4. **Expiration Tests**: Verify cache expires after TTL period
5. **Monitoring Tests**: Verify cache statistics and logging

### Running Tests

```bash
# Run all TTL tests
pytest Backend/tests/test_ttl_configuration.py -v

# Run specific test class
pytest Backend/tests/test_ttl_configuration.py::TestTTLConfiguration -v

# Run with coverage
pytest Backend/tests/test_ttl_configuration.py --cov=app.core.redis
```

## Performance Considerations

### Benefits

1. **Automatic Cleanup**: Expired data is automatically removed, freeing memory
2. **Fresh Data**: Users always get reasonably fresh data
3. **Reduced Database Load**: Frequently accessed data stays cached longer
4. **Configurable**: TTL values can be adjusted based on requirements

### Trade-offs

1. **Stale Data**: Users might see slightly outdated information
2. **Cache Misses**: More frequent cache misses for short TTL values
3. **Memory Usage**: Longer TTL values consume more memory

## Best Practices

1. **Use cache_type parameter**: Always use the cache_type parameter for automatic TTL selection
2. **Override when needed**: Use explicit TTL only when cache_type doesn't fit the use case
3. **Monitor cache stats**: Regularly check cache hit rates and adjust TTL if needed
4. **Test expiration**: Verify cache expiration behavior in tests
5. **Document TTL decisions**: Document why specific TTL values were chosen

## Future Enhancements

1. **Dynamic TTL**: Adjust TTL based on cache hit rates
2. **TTL Metrics**: Track TTL effectiveness and adjust automatically
3. **Cache Warming**: Pre-populate cache with frequently accessed data
4. **Conditional Expiration**: Expire cache based on data changes, not just time
5. **TTL Policies**: Define TTL policies per cache key pattern

## Troubleshooting

### Cache Not Expiring

1. Check Redis is running: `redis-cli ping`
2. Verify TTL is set: `redis-cli TTL key_name`
3. Check Redis memory: `redis-cli INFO memory`

### High Cache Miss Rate

1. Increase TTL values for frequently accessed data
2. Check cache invalidation logic
3. Monitor cache statistics

### Memory Issues

1. Reduce TTL values to expire data faster
2. Implement cache eviction policies
3. Monitor Redis memory usage

## References

- [Redis SETEX Command](https://redis.io/commands/setex/)
- [Redis TTL Command](https://redis.io/commands/ttl/)
- [Redis Expiration Documentation](https://redis.io/docs/manual/data-types/strings/#expiration)
