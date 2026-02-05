"""Schemas module"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
    UpdateRole
)
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    Token,
    TokenData
)
from app.schemas.response import (
    StandardResponse,
    ErrorResponse,
    success_response,
    error_response
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "UpdateRole",
    "LoginRequest",
    "LoginResponse",
    "Token",
    "TokenData",
    "StandardResponse",
    "ErrorResponse",
    "success_response",
    "error_response",
]
