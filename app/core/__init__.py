"""Core module exports"""

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    extract_bearer_token
)
from app.core.deps import get_db, get_current_user, get_current_active_user
from app.core.authorization import Role, require_admin, require_role, is_admin
from app.core.logging_config import setup_logging, get_logger
from app.core.exceptions import (
    AppException,
    AuthenticationException,
    InvalidCredentialsException,
    InvalidTokenException,
    InsufficientPermissionsException,
    ResourceNotFoundException,
    UserNotFoundException,
    ValidationException,
    DuplicateEmailException,
    BusinessLogicException,
    DatabaseException
)

__all__ = [
    "settings",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "extract_bearer_token",
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "Role",
    "require_admin",
    "require_role",
    "is_admin",
    "setup_logging",
    "get_logger",
    "AppException",
    "AuthenticationException",
    "InvalidCredentialsException",
    "InvalidTokenException",
    "InsufficientPermissionsException",
    "ResourceNotFoundException",
    "UserNotFoundException",
    "ValidationException",
    "DuplicateEmailException",
    "BusinessLogicException",
    "DatabaseException",
]
