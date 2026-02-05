"""
Pydantic Schemas untuk Request/Response
Terpisah dari SQLAlchemy models untuk separation of concerns
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class SiswaBase(BaseModel):
    """Base schema dengan field yang sama untuk Create dan Update"""
    nama: str = Field(..., min_length=1, max_length=100, description="Nama siswa")
    email: EmailStr = Field(..., description="Email siswa (harus unique)")


class SiswaCreate(SiswaBase):
    """
    Schema untuk membuat siswa baru (POST request)
    Inherit dari SiswaBase
    """
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nama": "Edy Cole",
                    "email": "edycoleee@gmail.com"
                }
            ]
        }
    )


class SiswaUpdate(SiswaBase):
    """
    Schema untuk update siswa (PUT request)
    Inherit dari SiswaBase
    """
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nama": "Edy Cole Updated",
                    "email": "edy.updated@gmail.com"
                }
            ]
        }
    )


class SiswaResponse(SiswaBase):
    """
    Schema untuk response siswa
    Include id dari database
    
    model_config with from_attributes=True memungkinkan Pydantic
    membaca data dari SQLAlchemy model (bukan hanya dict)
    """
    id: int
    
    model_config = ConfigDict(
        from_attributes=True,  # Dulu namanya orm_mode = True di Pydantic v1
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nama": "Edy Cole",
                    "email": "edycoleee@gmail.com"
                }
            ]
        }
    )


# ==================== AUTH SCHEMAS ====================

class LoginRequest(BaseModel):
    """Schema untuk login request"""
    username: str = Field(..., min_length=1, description="Username untuk login")
    password: str = Field(..., min_length=1, description="Password untuk login")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "admin",
                    "password": "admin"
                }
            ]
        }
    )


class LoginResponse(BaseModel):
    """Schema untuk login response"""
    message: str
    token: str
    username: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "Login successful",
                    "token": "123456",
                    "username": "admin"
                }
            ]
        }
    )
