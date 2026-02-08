"""
Siswa CRUD Endpoints - Manajemen data siswa dengan SQLAlchemy ORM
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import SiswaCreate, SiswaUpdate, SiswaResponse
from app.database import (
    get_db,
    get_all_siswa,
    get_siswa_by_id,
    get_siswa_by_email,
    insert_siswa,
    update_siswa,
    delete_siswa
)


router = APIRouter(prefix="/siswa", tags=["Siswa"])


# ==================== CREATE ====================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SiswaResponse)
async def create_siswa(siswa: SiswaCreate, db: Session = Depends(get_db)):
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
        # Cek apakah email sudah ada
        existing_email = get_siswa_by_email(db, siswa.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {siswa.email} sudah digunakan"
            )
        
        # Insert siswa baru
        new_siswa = insert_siswa(db, siswa.nama, siswa.email)
        
        return new_siswa
    except HTTPException:
        raise
    except IntegrityError:
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
async def read_all_siswa(db: Session = Depends(get_db)):
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
        siswa_list = get_all_siswa(db)
        total = len(siswa_list)
        
        return {
            "success": True,
            "message": f"Berhasil mengambil {total} data siswa",
            "data": [
                {
                    "id": siswa.id,
                    "nama": siswa.nama,
                    "email": siswa.email
                }
                for siswa in siswa_list
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/{siswa_id}", response_model=SiswaResponse)
async def read_siswa(siswa_id: int, db: Session = Depends(get_db)):
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
        siswa = get_siswa_by_id(db, siswa_id)
        
        if siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        return {
            "id": siswa.id,
            "nama": siswa.nama,
            "email": siswa.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# ==================== UPDATE ====================

@router.put("/{siswa_id}", response_model=SiswaResponse)
async def update_siswa_data(siswa_id: int, siswa: SiswaUpdate, db: Session = Depends(get_db)):
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
        existing_siswa = get_siswa_by_id(db, siswa_id)
        if existing_siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        # Cek apakah email sudah digunakan siswa lain
        if existing_siswa.email != siswa.email:
            email_taken = get_siswa_by_email(db, siswa.email)
            if email_taken:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {siswa.email} sudah digunakan"
                )
        
        # Update siswa
        updated_siswa = update_siswa(db, siswa_id, siswa.nama, siswa.email)
        
        if not updated_siswa:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mengupdate siswa"
            )
        
        return {
            "id": updated_siswa.id,
            "nama": updated_siswa.nama,
            "email": updated_siswa.email
        }
    except HTTPException:
        raise
    except IntegrityError:
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
async def delete_siswa_data(siswa_id: int, db: Session = Depends(get_db)):
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
        existing_siswa = get_siswa_by_id(db, siswa_id)
        if existing_siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        # Delete siswa
        success = delete_siswa(db, siswa_id)
        
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
