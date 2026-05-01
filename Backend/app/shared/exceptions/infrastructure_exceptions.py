"""
Infrastructure Layer Exceptions

Exceptions that represent infrastructure failures.
"""


class InfrastructureException(Exception):
    """Base exception for infrastructure layer"""
    pass


class DatabaseError(InfrastructureException):
    """Raised when database operation fails"""
    
    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Database {operation} failed: {message}")


class CacheError(InfrastructureException):
    """Raised when cache operation fails"""
    
    def __init__(self, operation: str, key: str, message: str):
        self.operation = operation
        self.key = key
        super().__init__(f"Cache {operation} failed for key '{key}': {message}")


class ExternalServiceError(InfrastructureException):
    """Raised when external service call fails"""
    
    def __init__(self, service: str, message: str):
        self.service = service
        super().__init__(f"External service '{service}' failed: {message}")
