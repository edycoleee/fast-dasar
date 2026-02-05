"""
Custom Exception Classes
Application-specific exceptions for better error handling
"""

from typing import Any, Optional


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


# Authentication & Authorization Exceptions

class AuthenticationException(AppException):
    """Base authentication exception"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class InvalidCredentialsException(AuthenticationException):
    """Invalid email or password"""
    def __init__(self):
        super().__init__("Invalid email or password")


class InvalidTokenException(AuthenticationException):
    """Invalid or expired JWT token"""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)


class InsufficientPermissionsException(AppException):
    """Insufficient permissions for the operation"""
    def __init__(self, required_role: str = "admin"):
        super().__init__(
            f"Insufficient permissions. Required role: {required_role}",
            status_code=403
        )


# Resource Exceptions

class ResourceNotFoundException(AppException):
    """Base resource not found exception"""
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            f"{resource} with identifier '{identifier}' not found",
            status_code=404
        )


class UserNotFoundException(ResourceNotFoundException):
    """User not found"""
    def __init__(self, user_id: int | None = None, email: str | None = None):
        identifier = f"ID {user_id}" if user_id else f"email {email}"
        super().__init__("User", identifier)


# Validation Exceptions

class ValidationException(AppException):
    """Data validation error"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=422, details=details)


class DuplicateResourceException(AppException):
    """Resource already exists"""
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            f"{resource} with {field} '{value}' already exists",
            status_code=400
        )


class DuplicateEmailException(DuplicateResourceException):
    """Email already registered"""
    def __init__(self, email: str):
        super().__init__("User", "email", email)


# Business Logic Exceptions

class BusinessLogicException(AppException):
    """Business logic validation failed"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class PasswordValidationException(BusinessLogicException):
    """Password does not meet requirements"""
    def __init__(self, message: str = "Password does not meet requirements"):
        super().__init__(message)


# Database Exceptions

class DatabaseException(AppException):
    """Database operation failed"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)
