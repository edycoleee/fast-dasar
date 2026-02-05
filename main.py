"""
FastAPI Application dengan SQLAlchemy ORM
Week 2a: CRUD siswa dengan SQLAlchemy
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from db_sqlalchemy import Siswa, get_db, init_db
from schemas import SiswaCreate, SiswaUpdate, SiswaResponse

# Inisialisasi FastAPI app
app = FastAPI(
    title="Siswa CRUD API - SQLAlchemy",
    description="API CRUD untuk manajemen data siswa dengan SQLAlchemy ORM",
    version="2.1.0"
)


# ==================== STARTUP & SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Inisialisasi database saat aplikasi start"""
    init_db()
    print("🚀 FastAPI app started with SQLAlchemy ORM")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup saat aplikasi shutdown"""
    print("👋 FastAPI app shutting down")


# ==================== CRUD ENDPOINTS ====================

@app.post("/api/siswa/", response_model=SiswaResponse, status_code=status.HTTP_201_CREATED)
async def create_siswa(siswa: SiswaCreate, db: Session = Depends(get_db)):
    """
    CREATE - Tambah siswa baru
    
    SQLAlchemy ORM:
    1. Buat instance dari model Siswa
    2. Add ke session
    3. Commit untuk save ke database
    4. Refresh untuk mendapatkan data yang ter-generate (id)
    
    Equivalent SQL:
    INSERT INTO siswa (nama, email) VALUES (?, ?)
    """
    try:
        # 1. Buat instance SQLAlchemy model
        db_siswa = Siswa(
            nama=siswa.nama,
            email=siswa.email
        )
        
        # 2. Add ke database session
        db.add(db_siswa)
        
        # 3. Commit transaction
        db.commit()
        
        # 4. Refresh untuk mendapatkan data dari DB (seperti id yang auto-generated)
        db.refresh(db_siswa)
        
        return db_siswa
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {siswa.email} sudah digunakan"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.get("/api/siswa/", response_model=List[SiswaResponse])
async def read_all_siswa(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    READ ALL - Ambil semua data siswa dengan pagination
    
    Query Parameters:
    - skip: Berapa data yang di-skip (default 0)
    - limit: Maximum berapa data yang diambil (default 100)
    
    SQLAlchemy ORM:
    db.query(Siswa).offset(skip).limit(limit).all()
    
    Equivalent SQL:
    SELECT * FROM siswa LIMIT ? OFFSET ?
    """
    siswa_list = db.query(Siswa).offset(skip).limit(limit).all()
    return siswa_list


@app.get("/api/siswa/{siswa_id}", response_model=SiswaResponse)
async def read_siswa(siswa_id: int, db: Session = Depends(get_db)):
    """
    READ ONE - Ambil data siswa berdasarkan ID
    
    SQLAlchemy ORM:
    db.query(Siswa).filter(Siswa.id == siswa_id).first()
    
    Equivalent SQL:
    SELECT * FROM siswa WHERE id = ? LIMIT 1
    """
    siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
    
    if siswa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
        )
    
    return siswa


@app.put("/api/siswa/{siswa_id}", response_model=SiswaResponse)
async def update_siswa(
    siswa_id: int,
    siswa_update: SiswaUpdate,
    db: Session = Depends(get_db)
):
    """
    UPDATE - Update data siswa
    
    SQLAlchemy ORM:
    1. Query siswa by ID
    2. Update attribute
    3. Commit changes
    
    Equivalent SQL:
    UPDATE siswa SET nama = ?, email = ? WHERE id = ?
    """
    try:
        # 1. Cari siswa
        siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
        
        if siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        # 2. Update attributes
        siswa.nama = siswa_update.nama
        siswa.email = siswa_update.email
        
        # 3. Commit changes
        db.commit()
        
        # 4. Refresh untuk mendapatkan data terbaru
        db.refresh(siswa)
        
        return siswa
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {siswa_update.email} sudah digunakan"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.delete("/api/siswa/{siswa_id}")
async def delete_siswa(siswa_id: int, db: Session = Depends(get_db)):
    """
    DELETE - Hapus siswa
    
    SQLAlchemy ORM:
    1. Query siswa by ID
    2. Delete object
    3. Commit changes
    
    Equivalent SQL:
    DELETE FROM siswa WHERE id = ?
    """
    try:
        # 1. Cari siswa
        siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
        
        if siswa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
            )
        
        # 2. Delete object
        db.delete(siswa)
        
        # 3. Commit changes
        db.commit()
        
        return {
            "success": True,
            "message": f"Siswa dengan ID {siswa_id} berhasil dihapus",
            "data": None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# ==================== INFO ENDPOINTS ====================

@app.get("/")
async def root(db: Session = Depends(get_db)):
    """Root endpoint dengan informasi API"""
    total_siswa = db.query(Siswa).count()
    
    return {
        "message": "Siswa CRUD API with SQLAlchemy is running!",
        "version": "2.1.0",
        "orm": "SQLAlchemy",
        "total_siswa": total_siswa,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "create": "POST /api/siswa/",
            "read_all": "GET /api/siswa/?skip=0&limit=100",
            "read_one": "GET /api/siswa/{id}",
            "update": "PUT /api/siswa/{id}",
            "delete": "DELETE /api/siswa/{id}"
        }
    }


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        total_siswa = db.query(Siswa).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "orm": "SQLAlchemy",
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


# ==================== ADVANCED QUERIES ====================

@app.get("/api/siswa/search/", response_model=List[SiswaResponse])
async def search_siswa(
    q: str,
    db: Session = Depends(get_db)
):
    """
    SEARCH - Cari siswa berdasarkan nama atau email
    
    Query Parameter:
    - q: Search query
    
    SQLAlchemy ORM dengan filter OR:
    db.query(Siswa).filter(or_(
        Siswa.nama.contains(q),
        Siswa.email.contains(q)
    ))
    
    Equivalent SQL:
    SELECT * FROM siswa WHERE nama LIKE '%?%' OR email LIKE '%?%'
    """
    from sqlalchemy import or_
    
    siswa_list = db.query(Siswa).filter(
        or_(
            Siswa.nama.contains(q),
            Siswa.email.contains(q)
        )
    ).all()
    
    return siswa_list
