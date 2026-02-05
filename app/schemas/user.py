"""
User Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Literal


# ==================== BASE ====================

class UserBase(BaseModel):
    """Base user schema"""
    nama: str = Field(..., min_length=1, max_length=100, description="User name")
    email: EmailStr = Field(..., description="User email (must be unique)")


# ==================== REQUEST SCHEMAS ====================

class UserCreate(UserBase):
    """Schema for creating new user"""
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    role: Literal["admin", "user"] = Field(default="user", description="User role")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "nama": "John Doe",
                "email": "john@example.com",
                "password": "secret123",
                "role": "user"
            }]
        }
    )


class UserUpdate(UserBase):
    """Schema for updating user"""
    password: Optional[str] = Field(None, min_length=6, description="New password (optional)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "nama": "John Doe Updated",
                "email": "john.updated@example.com",
                "password": "newsecret123"
            }]
        }
    )


class UpdateRole(BaseModel):
    """Schema for updating user role (admin only)"""
    role: Literal["admin", "user"] = Field(..., description="New role")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"role": "admin"}]
        }
    )


# ==================== RESPONSE SCHEMAS ====================

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: str
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "nama": "John Doe",
                "email": "john@example.com",
                "role": "user"
            }]
        }
    )


class UserInDB(UserResponse):
    """User in database (includes password hash)"""
    password: str
