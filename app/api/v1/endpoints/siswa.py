"""
Siswa CRUD Endpoints - Manajemen data siswa
"""

from fastapi import APIRouter, HTTPException, status
import sqlite3

from app.models import SiswaCreate, SiswaUpdate, SiswaResponse
from app.database import (
    get_all_siswa,
    get_siswa_by_id,
    insert_siswa,
    update_siswa,
    delete_siswa,
    count_siswa
)


router = APIRouter(prefix="/siswa", tags=["Siswa"])


# ==================== CREATE ====================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SiswaResponse)
async def create_siswa(siswa: SiswaCreate):
    """
    POST /api/v1/siswa/ - Tambah siswa baru
    
    Request body:
    - nama: string (required)
    - email: string (required, valid email, unique)
    
    Returns:
    - 201 Created: Siswa berhasil dibuat
    - 400 Bad Request: Email sudah digunakan
    - 422 Unprocessable Entity: Validation error
    
    Example:
        POST /api/v1/siswa/
        Content-Type: application/json
        
        {
            "nama": "Edy Santoso",
            "email": "edy@example.com"
        }
    """
    try:
        siswa_id = insert_siswa(siswa.nama, siswa.email)
        new_siswa = get_siswa_by_id(siswa_id)
        
        return new_siswa
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {siswa.email} sudah digunakan"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# ==================== READ ====================

@router.get("/")
async def read_all_siswa():
    """
    GET /api/v1/siswa/ - Ambil semua data siswa
    
    Returns:
    - 200 OK: List siswa (bisa kosong)
    
    Example:
        GET /api/v1/siswa/
        
        Response:
        {
            "success": true,
            "message": "Berhasil mengambil 2 data siswa",
            "data": [
                {"id": 1, "nama": "Edy", "email": "edy@example.com"},
                {"id": 2, "nama": "Budi", "email": "budi@example.com"}
            ]
        }
    """
    try:
        siswa_list = get_all_siswa()
        total = len(siswa_list)
        
        return {
            "success": True,
            "message": f"Berhasil mengambil {total} data siswa",
            "data": siswa_list
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/{siswa_id}", response_model=SiswaResponse)
async def read_siswa(siswa_id: int):
    """
    GET /api/v1/siswa/{id} - Ambil data siswa berdasarkan ID
    
    Path parameters:
    - siswa_id: integer (ID siswa)
    
    Returns:
    - 200 OK: Data siswa ditemukan
    - 404 Not Found: Siswa tidak ditemukan
    
    Example:
        GET /api/v1/siswa/1
        
        Response:
        {
            "id": 1,
            "nama": "Edy",
            "email": "edy@example.com"
        }
    """
    try:
        siswa = get_siswa_by_id(siswa_id)
        
        if siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        return siswa
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# ==================== UPDATE ====================

@router.put("/{siswa_id}", response_model=SiswaResponse)
async def update_siswa_data(siswa_id: int, siswa: SiswaUpdate):
    """
    PUT /api/v1/siswa/{id} - Update data siswa
    
    Path parameters:
    - siswa_id: integer (ID siswa)
    
    Request body:
    - nama: string (required)
    - email: string (required, valid email, unique)
    
    Returns:
    - 200 OK: Siswa berhasil diupdate
    - 404 Not Found: Siswa tidak ditemukan
    - 400 Bad Request: Email sudah digunakan siswa lain
    - 422 Unprocessable Entity: Validation error
    
    Example:
        PUT /api/v1/siswa/1
        Content-Type: application/json
        
        {
            "nama": "Edy Santoso Updated",
            "email": "edy_new@example.com"
        }
    """
    try:
        # Cek apakah siswa exists
        existing_siswa = get_siswa_by_id(siswa_id)
        if existing_siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        # Update siswa
        success = update_siswa(siswa_id, siswa.nama, siswa.email)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mengupdate siswa"
            )
        
        # Get updated data
        updated_siswa = get_siswa_by_id(siswa_id)
        
        return updated_siswa
    except HTTPException:
        raise
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {siswa.email} sudah digunakan"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# ==================== DELETE ====================

@router.delete("/{siswa_id}")
async def delete_siswa_data(siswa_id: int):
    """
    DELETE /api/v1/siswa/{id} - Hapus siswa
    
    Path parameters:
    - siswa_id: integer (ID siswa)
    
    Returns:
    - 200 OK: Siswa berhasil dihapus
    - 404 Not Found: Siswa tidak ditemukan
    
    Example:
        DELETE /api/v1/siswa/1
        
        Response:
        {
            "success": true,
            "message": "Siswa dengan ID 1 berhasil dihapus",
            "data": null
        }
    """
    try:
        # Cek apakah siswa exists
        existing_siswa = get_siswa_by_id(siswa_id)
        if existing_siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        # Delete siswa
        success = delete_siswa(siswa_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal menghapus siswa"
            )
        
        return {
            "success": True,
            "message": f"Siswa dengan ID {siswa_id} berhasil dihapus",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
