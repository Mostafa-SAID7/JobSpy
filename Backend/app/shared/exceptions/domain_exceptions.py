"""
Domain Layer Exceptions

Exceptions that represent domain rule violations.
"""


class DomainException(Exception):
    """Base exception for domain layer"""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found"""
    
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} not found: {entity_id}")


class ValidationError(DomainException):
    """Raised when entity validation fails"""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated"""
    
    def __init__(self, rule: str, message: str):
        self.rule = rule
        super().__init__(f"Business rule '{rule}' violated: {message}")
