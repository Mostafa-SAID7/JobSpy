"""
Custom Exceptions

Organized by layer for clarity.
"""

from .domain_exceptions import (
    DomainException,
    EntityNotFoundError,
    ValidationError,
    BusinessRuleViolationError,
)

from .application_exceptions import (
    ApplicationException,
    UseCaseError,
    DuplicateEntityError,
)

from .infrastructure_exceptions import (
    InfrastructureException,
    DatabaseError,
    CacheError,
    ExternalServiceError,
)

__all__ = [
    # Domain
    "DomainException",
    "EntityNotFoundError",
    "ValidationError",
    "BusinessRuleViolationError",
    # Application
    "ApplicationException",
    "UseCaseError",
    "DuplicateEntityError",
    # Infrastructure
    "InfrastructureException",
    "DatabaseError",
    "CacheError",
    "ExternalServiceError",
]
