"""
FastAPI Application dengan CRUD SQLite
Week 1b: CRUD siswa dengan SQLite menggunakan raw SQL
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from contextlib import asynccontextmanager
import sqlite3

from models import SiswaCreate, SiswaUpdate, SiswaResponse
from database import (
    init_db,
    get_all_siswa,
    get_siswa_by_id,
    insert_siswa,
    update_siswa,
    delete_siswa,
    count_siswa
)


# ==================== Lifespan Event Handler (Modern Approach) ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager untuk startup dan shutdown events.
    
    Ini adalah cara modern (recommended oleh FastAPI) untuk menangani
    startup dan shutdown events, menggantikan @app.on_event() yang deprecated.
    
    Sintaks:
    - Code sebelum yield: jalankan saat startup
    - Code sesudah yield: jalankan saat shutdown
    """
    # Startup event
    init_db()
    print("🚀 FastAPI app started with SQLite database")
    
    yield  # Aplikasi berjalan di sini
    
    # Shutdown event
    print("👋 FastAPI app shutting down")


# Inisialisasi FastAPI app dengan lifespan
app = FastAPI(
    title="Siswa CRUD API",
    description="API CRUD untuk manajemen data siswa dengan SQLite",
    version="2.0.0",
    lifespan=lifespan
)


# ==================== CRUD ENDPOINTS ====================

@app.post("/api/siswa/", status_code=status.HTTP_201_CREATED)
async def create_siswa(siswa: SiswaCreate):
    """
    CREATE - Tambah siswa baru
    
    Body:
    - nama: string (required, min 1 char)
    - email: string (required, valid email, unique)
    
    Returns:
    - 201: Siswa berhasil dibuat
    - 400: Email sudah digunakan
    """
    try:
        siswa_id = insert_siswa(siswa.nama, siswa.email)
        new_siswa = get_siswa_by_id(siswa_id)
        
        return {
            "success": True,
            "message": "Siswa berhasil ditambahkan",
            "data": new_siswa
        }
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


@app.get("/api/siswa/")
async def read_all_siswa():
    """
    READ ALL - Ambil semua data siswa
    
    Returns:
    - 200: List siswa (bisa kosong)
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


@app.get("/api/siswa/{siswa_id}")
async def read_siswa(siswa_id: int):
    """
    READ ONE - Ambil data siswa berdasarkan ID
    
    Path Parameter:
    - siswa_id: integer (ID siswa)
    
    Returns:
    - 200: Data siswa ditemukan
    - 404: Siswa tidak ditemukan
    """
    try:
        siswa = get_siswa_by_id(siswa_id)
        
        if siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        return {
            "success": True,
            "message": "Siswa ditemukan",
            "data": siswa
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.put("/api/siswa/{siswa_id}")
async def update_siswa_data(siswa_id: int, siswa: SiswaUpdate):
    """
    UPDATE - Update data siswa
    
    Path Parameter:
    - siswa_id: integer (ID siswa)
    
    Body:
    - nama: string (required)
    - email: string (required, valid email, unique)
    
    Returns:
    - 200: Siswa berhasil diupdate
    - 404: Siswa tidak ditemukan
    - 400: Email sudah digunakan siswa lain
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
        
        return {
            "success": True,
            "message": "Siswa berhasil diupdate",
            "data": updated_siswa
        }
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


@app.delete("/api/siswa/{siswa_id}")
async def delete_siswa_data(siswa_id: int):
    """
    DELETE - Hapus siswa
    
    Path Parameter:
    - siswa_id: integer (ID siswa)
    
    Returns:
    - 200: Siswa berhasil dihapus
    - 404: Siswa tidak ditemukan
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


# ==================== INFO ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint dengan informasi API"""
    total_siswa = count_siswa()
    
    return {
        "message": "Siswa CRUD API is running!",
        "version": "2.0.0",
        "total_siswa": total_siswa,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "create": "POST /api/siswa/",
            "read_all": "GET /api/siswa/",
            "read_one": "GET /api/siswa/{id}",
            "update": "PUT /api/siswa/{id}",
            "delete": "DELETE /api/siswa/{id}"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        total_siswa = count_siswa()
        return {
            "status": "healthy",
            "database": "connected",
            "total_siswa": total_siswa
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )
