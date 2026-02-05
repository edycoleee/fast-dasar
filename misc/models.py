"""
Pydantic Models untuk API Siswa
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any


class SiswaCreate(BaseModel):
    """Model untuk membuat siswa baru (POST request)"""
    nama: str = Field(..., min_length=1, max_length=100, description="Nama siswa")
    email: EmailStr = Field(..., description="Email siswa (harus unique)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nama": "Edy Cole",
                    "email": "edycoleee@gmail.com"
                }
            ]
        }
    }


class SiswaUpdate(BaseModel):
    """Model untuk update siswa (PUT request)"""
    nama: str = Field(..., min_length=1, max_length=100, description="Nama siswa")
    email: EmailStr = Field(..., description="Email siswa (harus unique)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nama": "Edy Cole Updated",
                    "email": "edy.updated@gmail.com"
                }
            ]
        }
    }


class SiswaResponse(BaseModel):
    """Model untuk response siswa"""
    id: int = Field(..., description="ID siswa")
    nama: str = Field(..., description="Nama siswa")
    email: str = Field(..., description="Email siswa")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "nama": "Edy Cole",
                    "email": "edycoleee@gmail.com"
                }
            ]
        }
    }


class ApiResponse(BaseModel):
    """Model untuk format response API yang konsisten"""
    success: bool = Field(..., description="Status operasi")
    message: str = Field(..., description="Pesan deskriptif")
    data: Optional[Any] = Field(default=None, description="Data response")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Operation successful",
                    "data": []
                }
            ]
        }
    }
