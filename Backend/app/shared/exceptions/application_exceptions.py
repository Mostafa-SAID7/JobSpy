"""
Application Layer Exceptions

Exceptions that represent application/use case errors.
"""


class ApplicationException(Exception):
    """Base exception for application layer"""
    pass


class UseCaseError(ApplicationException):
    """Raised when a use case fails"""
    
    def __init__(self, use_case: str, message: str):
        self.use_case = use_case
        super().__init__(f"Use case '{use_case}' failed: {message}")


class DuplicateEntityError(ApplicationException):
    """Raised when trying to create a duplicate entity"""
    
    def __init__(self, entity_type: str, identifier: str):
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(f"{entity_type} already exists: {identifier}")
