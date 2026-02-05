"""
Authentication Schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="Password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "email": "john@example.com",
                "password": "secret123"
            }]
        }
    )


class LoginResponse(BaseModel):
    """Login response schema"""
    message: str
    access_token: str
    token_type: str = "bearer"
    user: dict
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "message": "Login successful",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "nama": "John Doe",
                    "email": "john@example.com",
                    "role": "user"
                }
            }]
        }
    )


class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None

