"""
Application Layer - Use Cases and Orchestration

This layer contains:
- Use Cases: Application-specific business rules
- DTOs: Data Transfer Objects for crossing boundaries
- Mappers: Convert between domain entities and DTOs
- Application Services: Orchestration logic

Rules:
- Depends on domain layer (entities, value objects, interfaces)
- NO dependencies on infrastructure or presentation layers
- Orchestrates domain services and entities
- Handles application-specific workflows
"""
