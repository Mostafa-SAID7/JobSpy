"""
Domain Layer - Core Business Logic

This layer contains:
- Entities: Core business objects with identity
- Value Objects: Immutable objects defined by their attributes
- Domain Services: Business logic that doesn't belong to entities
- Interfaces: Contracts for infrastructure dependencies
- Specifications: Business rules and validation logic

Rules:
- NO dependencies on outer layers (application, infrastructure, presentation)
- Pure Python - no frameworks, no ORM, no external libraries
- All business logic lives here
"""
