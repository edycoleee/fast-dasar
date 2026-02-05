"""
Pydantic Schemas untuk Request/Response
Terpisah dari SQLAlchemy models untuk separation of concerns
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, Literal


class SiswaBase(BaseModel):
    """Base schema dengan field yang sama untuk Create dan Update"""
    nama: str = Field(..., min_length=1, max_length=100, description="Nama siswa")
    email: EmailStr = Field(..., description="Email siswa (harus unique)")


class SiswaCreate(SiswaBase):
    """
    Schema untuk membuat siswa baru (POST request)
    Inherit dari SiswaBase
    """
    password: str = Field(..., min_length=6, description="Password siswa (min 6 karakter)")
    role: Literal["admin", "user"] = Field(default="user", description="Role: admin atau user")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nama": "Edy Cole",
                    "email": "edycoleee@gmail.com",
                    "password": "secret123",
                    "role": "user"
                }
            ]
        }
    )


class SiswaUpdate(SiswaBase):
    """
    Schema untuk update siswa (PUT request)
    Inherit dari SiswaBase
    """
    password: Optional[str] = Field(None, min_length=6, description="Password siswa (optional, min 6 karakter)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nama": "Edy Cole Updated",
                    "email": "edy.updated@gmail.com",
                    "password": "newsecret123"
                }
            ]
        }
    )


class SiswaResponse(SiswaBase):
    """
    Schema untuk response siswa
    Include id dan role dari database
    
    model_config with from_attributes=True memungkinkan Pydantic
    membaca data dari SQLAlchemy model (bukan hanya dict)
    """
    id: int
    role: str
    
    model_config = ConfigDict(
        from_attributes=True,  # Dulu namanya orm_mode = True di Pydantic v1
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nama": "Edy Cole",
                    "email": "edycoleee@gmail.com",
                    "role": "user"
                }
            ]
        }
    )


# ==================== AUTH SCHEMAS ====================

class LoginRequest(BaseModel):
    """Schema untuk login request dengan email dan password"""
    email: EmailStr = Field(..., description="Email untuk login")
    password: str = Field(..., min_length=1, description="Password untuk login")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "edycoleee@gmail.com",
                    "password": "secret123"
                }
            ]
        }
    )


class LoginResponse(BaseModel):
    """Schema untuk login response dengan JWT token"""
    message: str
    access_token: str
    token_type: str = "bearer"
    user: dict
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "Login successful",
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "nama": "Edy Cole",
                        "email": "edycoleee@gmail.com",
                        "role": "user"
                    }
                }
            ]
        }
    )


# ==================== AUTHORIZATION SCHEMAS ====================

class UpdateRoleRequest(BaseModel):
    """Schema untuk update role user (hanya admin)"""
    role: Literal["admin", "user"] = Field(..., description="Role baru: admin atau user")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "role": "admin"
                }
            ]
        }
    )
            ]
        }
    )
