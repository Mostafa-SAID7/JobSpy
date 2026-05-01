"""
Infrastructure Layer - External Concerns

This layer contains:
- Persistence: Database, ORM models, repositories
- Caching: Redis, cache implementations
- External Services: Email, SMS, APIs
- Scrapers: Job board scrapers

Rules:
- Implements interfaces defined in domain layer
- Depends on domain layer (entities, interfaces)
- NO business logic here
- Converts between infrastructure and domain representations
"""
