# Advanced Search Result Caching Implementation

## Overview

This document describes the implementation of advanced search result caching for the JobSpy application. The caching system improves performance by storing search results with all filter parameters, enabling fast retrieval for repeated searches with identical criteria.

## Architecture

### Cache Key Generation

The search caching system uses deterministic cache keys that include all search parameters:

```
search:advanced:{query}:{filter_hash}:{skip}:{limit}
```

**Components:**
- `search:advanced` - Prefix identifying advanced search cache
- `{query}` - The search query string
- `{filter_hash}` - MD5 hash of normalized filter parameters (first 8 characters)
- `{skip}` - Pagination offset
- `{limit}` - Results per page

**Example:**
```
search:advanced:Python Developer:a1b2c3d4:0:20
```

### Filter Normalization

Filters are normalized to ensure consistent cache keys:

1. **Sorting**: Filter keys are sorted alphabetically
2. **None Removal**: None values are excluded from the hash
3. **Hashing**: Normalized filters are converted to JSON and hashed with MD5
4. **Truncation**: Only first 8 characters of hash are used

This ensures that:
- Same filters always generate the same cache key
- Different filters generate different cache keys
- Cache keys remain reasonably short

### Supported Filters

The advanced search supports the following filter parameters:

```python
{
    "query": "Python Developer",           # Search query (required)
    "location": "San Francisco",           # Job location
    "job_type": "fulltime",                # Job type (fulltime, parttime, etc.)
    "experience_level": "senior",          # Experience level required
    "salary_min": 100000,                  # Minimum salary
    "salary_max": 150000,                  # Maximum salary
    "is_remote": True,                     # Remote work availability
    "skip": 0,                             # Pagination offset
    "limit": 20,                           # Results per page
}
```

## Implementation Details

### SearchService Methods

#### `_generate_search_cache_key()`

Generates a deterministic cache key for search results.

```python
cache_key = service._generate_search_cache_key(
    query="Python Developer",
    filters={"location": "NYC", "job_type": "fulltime"},
    skip=0,
    limit=20
)
# Returns: "search:advanced:Python Developer:a1b2c3d4:0:20"
```

#### `search_jobs()`

Performs search with automatic caching:

1. Generates cache key
2. Checks Redis for cached results
3. If cache hit, returns cached results
4. If cache miss:
   - Performs database search
   - Saves search history
   - Caches results with TTL
   - Returns results

```python
result = await service.search_jobs(
    user_id=1,
    query="Python Developer",
    filters={"location": "NYC"},
    skip=0,
    limit=20
)
```

#### `advanced_search()`

Handles complex search queries with multiple filters:

1. Extracts and validates search parameters
2. Builds filter dictionary
3. Generates cache key with all parameters
4. Checks cache
5. Calls `search_jobs()` if cache miss

```python
result = await service.advanced_search(
    user_id=1,
    search_params={
        "query": "Engineer",
        "location": "SF",
        "job_type": "fulltime",
        "salary_min": 150000,
        "salary_max": 250000,
        "is_remote": False,
        "skip": 0,
        "limit": 20,
    }
)
```

#### `invalidate_search_cache()`

Invalidates cache for a specific search query:

1. Deletes specific cache key
2. Deletes all pagination variations using pattern matching

```python
await service.invalidate_search_cache(
    query="Python Developer",
    filters={"location": "NYC"}
)
```

#### `invalidate_all_search_cache()`

Invalidates all search-related cache entries:

```python
await service.invalidate_all_search_cache()
```

Clears:
- `search:advanced:*` - Advanced search results
- `search:simple:*` - Simple search results
- `recommendations:*` - Job recommendations
- `trending_searches:*` - Trending searches

### API Endpoints

#### POST /api/v1/jobs/search/advanced

Advanced search endpoint with caching support.

**Query Parameters:**
- `query` (required): Search query string
- `location` (optional): Job location
- `job_type` (optional): Job type (fulltime, parttime, etc.)
- `experience_level` (optional): Experience level required
- `salary_min` (optional): Minimum salary
- `salary_max` (optional): Maximum salary
- `is_remote` (optional): Remote work availability
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 20, max: 100): Results per page

**Response:**
```json
{
    "query": "Python Developer",
    "filters": {
        "location": "San Francisco",
        "job_type": "fulltime"
    },
    "results": [...],
    "total_count": 150,
    "skip": 0,
    "limit": 20,
    "has_more": true,
    "cache_key": "search:advanced:Python Developer:a1b2c3d4:0:20"
}
```

## Cache Invalidation Strategy

### When Cache is Invalidated

Cache is automatically invalidated when:

1. **New Job Added**: All search caches cleared
   - Reason: New job might match existing searches
   - Scope: All search-related caches

2. **Job Updated**: All search caches cleared
   - Reason: Updated job might affect search results
   - Scope: All search-related caches

3. **Job Deleted**: All search caches cleared
   - Reason: Deleted job might have been in search results
   - Scope: All search-related caches

### Cache Invalidation Implementation

```python
# In jobs router endpoints
await job_repo.invalidate_all_jobs_cache()
await search_service.invalidate_all_search_cache()
```

## TTL Configuration

### Default TTL

- **Search Results**: 3600 seconds (1 hour)
- **Recommendations**: 1800 seconds (30 minutes)
- **Trending Searches**: 3600 seconds (1 hour)

### Configuration

TTL is configured in `Backend/app/core/config.py`:

```python
REDIS_CACHE_TTL: int = 3600  # 1 hour
```

## Performance Benefits

### Cache Hit Scenario

**Without Cache:**
- Database query: ~100-500ms
- Total response time: ~100-500ms

**With Cache:**
- Redis lookup: ~1-5ms
- Total response time: ~1-5ms

**Improvement:** 20-500x faster

### Example Metrics

For a typical search with 100 results:

| Operation | Time | Improvement |
|-----------|------|-------------|
| Database Query | 250ms | - |
| Redis Cache Hit | 2ms | 125x faster |
| Network Overhead | 10ms | - |
| Total (cached) | 12ms | 20x faster |

## Testing

### Test Coverage

The implementation includes 19 comprehensive tests:

1. **Cache Key Generation** (8 tests)
   - Simple queries
   - Complex filters
   - Pagination parameters
   - Deterministic behavior
   - Filter normalization

2. **Cache Invalidation** (2 tests)
   - Specific query invalidation
   - All cache invalidation

3. **Advanced Search** (3 tests)
   - Multiple filters
   - Cache hits
   - Filter building

4. **Cache Patterns** (2 tests)
   - Pattern matching
   - Bulk deletion

5. **TTL Configuration** (2 tests)
   - Settings validation
   - TTL usage

6. **Metadata** (2 tests)
   - Pagination metadata
   - has_more flag

### Running Tests

```bash
# Run all search caching tests
pytest Backend/tests/test_search_caching.py -v

# Run specific test class
pytest Backend/tests/test_search_caching.py::TestSearchCacheKeyGeneration -v

# Run with coverage
pytest Backend/tests/test_search_caching.py --cov=app.services.search_service
```

## Usage Examples

### Simple Search

```python
# Search for "Python Developer" in NYC
result = await search_service.search_jobs(
    user_id=1,
    query="Python Developer",
    filters={"location": "NYC"},
    skip=0,
    limit=20
)
```

### Advanced Search with Multiple Filters

```python
# Search for senior engineers in SF with salary range
result = await search_service.advanced_search(
    user_id=1,
    search_params={
        "query": "Software Engineer",
        "location": "San Francisco",
        "job_type": "fulltime",
        "experience_level": "senior",
        "salary_min": 150000,
        "salary_max": 250000,
        "is_remote": False,
        "skip": 0,
        "limit": 20,
    }
)
```

### API Usage

```bash
# Advanced search via API
curl -X POST "http://localhost:8000/api/v1/jobs/search/advanced?query=Python&location=NYC&job_type=fulltime&skip=0&limit=20" \
  -H "Authorization: Bearer {token}"
```

## Monitoring and Debugging

### Cache Statistics

Redis client provides cache statistics:

```python
stats = await redis_client.get_stats()
# Returns:
# {
#     "hits": 1250,
#     "misses": 150,
#     "sets": 200,
#     "deletes": 50,
#     "errors": 2,
#     "total_requests": 1400,
#     "hit_rate": "89.29%",
#     "timestamp": "2024-01-01T12:00:00"
# }
```

### Cache Key Debugging

The API response includes the cache key used:

```json
{
    "results": [...],
    "cache_key": "search:advanced:Python Developer:a1b2c3d4:0:20"
}
```

This helps debug cache behavior and verify correct key generation.

## Best Practices

1. **Use Consistent Filter Names**: Always use the same filter names to ensure cache hits
2. **Limit Results**: Use reasonable limit values (20-100) to avoid large cache entries
3. **Monitor Cache Hit Rate**: Track cache statistics to optimize TTL values
4. **Invalidate Strategically**: Only invalidate necessary caches to maintain performance
5. **Test Cache Behavior**: Verify cache hits and misses in development

## Future Improvements

1. **Partial Cache Invalidation**: Invalidate only affected searches instead of all
2. **Cache Warming**: Pre-populate cache with popular searches
3. **Adaptive TTL**: Adjust TTL based on search frequency
4. **Cache Compression**: Compress large search results before caching
5. **Distributed Caching**: Use Redis cluster for high-availability caching

## Troubleshooting

### Cache Not Working

1. **Check Redis Connection**:
   ```python
   await redis_client.redis.ping()
   ```

2. **Verify Cache Key**:
   - Check API response for `cache_key` field
   - Verify key format matches expected pattern

3. **Check TTL**:
   ```python
   ttl = await redis_client.get_ttl(cache_key)
   ```

### High Cache Miss Rate

1. **Verify Filter Consistency**: Ensure filters are normalized
2. **Check TTL**: May be too short for your use case
3. **Monitor Search Patterns**: Identify if searches are too varied

### Memory Issues

1. **Reduce TTL**: Shorter TTL means less memory usage
2. **Limit Cache Size**: Implement cache size limits
3. **Monitor Redis Memory**: Use `redis-cli INFO memory`

## References

- Redis Documentation: https://redis.io/documentation
- FastAPI Caching: https://fastapi.tiangolo.com/advanced/caching/
- Python Hashlib: https://docs.python.org/3/library/hashlib.html
