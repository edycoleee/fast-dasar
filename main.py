"""
FastAPI Application dengan SQLAlchemy ORM
Week 2a: CRUD siswa dengan SQLAlchemy
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from db_sqlalchemy import Siswa, get_db, init_db
from schemas import SiswaCreate, SiswaUpdate, SiswaResponse, LoginRequest, LoginResponse

# Import middleware
from middleware import (
    request_logging_middleware,
    ErrorHandlingMiddleware,
    request_validation_middleware,
    # RateLimitMiddleware,  # Uncomment jika mau pake rate limiting
    # auth_middleware,  # Uncomment jika mau pake authentication
)

# Inisialisasi FastAPI app
app = FastAPI(
    title="Siswa CRUD API - SQLAlchemy",
    description="API CRUD untuk manajemen data siswa dengan SQLAlchemy ORM",
    version="2.1.0"
)

# ==================== MIDDLEWARE SETUP ====================
# Urutan penting! Middleware dijalankan dari atas ke bawah untuk request,
# dan dari bawah ke atas untuk response

# 1. CORS - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Error handling - Catch semua errors
app.add_middleware(ErrorHandlingMiddleware)

# 3. Request logging - Log semua requests
app.middleware("http")(request_logging_middleware)

# 4. Request validation - Validate request size & content-type
app.middleware("http")(request_validation_middleware)

# 5. Rate limiting (optional) - Batasi request per IP
# app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# 6. Authentication (optional) - Require token untuk semua endpoints
# app.middleware("http")(auth_middleware)


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


# ==================== AUTHENTICATION ENDPOINTS ====================
# Simulasi sederhana untuk belajar middleware sebelum JWT

@app.post("/api/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(credentials: LoginRequest):
    """
    LOGIN - Endpoint untuk login dengan username dan password
    
    Credential yang valid:
    - username: admin
    - password: admin
    
    Response:
    - token: "123456" (token sederhana untuk simulasi, nanti akan diganti JWT)
    
    Cara test:
    ```bash
    curl -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","password":"admin"}'
    ```
    """
    # Validasi credentials (hardcoded untuk pembelajaran)
    if credentials.username == "admin" and credentials.password == "admin":
        return LoginResponse(
            message="Login successful",
            token="123456",
            username=credentials.username
        )
    
    # Jika credentials salah
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/api/landing", tags=["Authentication"])
async def landing_page(request: Request):
    """
    LANDING PAGE - Endpoint yang di-protect dengan Bearer token
    
    Harus include header:
    Authorization: Bearer 123456
    
    Cara test:
    ```bash
    # Tanpa token (akan error 401)
    curl http://localhost:8000/api/landing
    
    # Dengan token (success)
    curl -H "Authorization: Bearer 123456" http://localhost:8000/api/landing
    ```
    
    Endpoint ini menggunakan middleware authentication.
    Lihat middleware di bawah yang check Authorization header.
    """
    # Data user dari middleware (di-set di request.state)
    user_data = getattr(request.state, "user", None)
    
    return {
        "message": "Welcome to the landing page!",
        "description": "This is a protected endpoint - you need Bearer token to access",
        "user": user_data,
        "info": "Token ini sederhana, nanti akan diganti dengan JWT yang lebih secure"
    }


# ==================== AUTHENTICATION MIDDLEWARE ====================
# Middleware untuk check Bearer token pada endpoint tertentu

@app.middleware("http")
async def simple_auth_middleware(request: Request, call_next):
    """
    Simple Authentication Middleware
    
    Cara kerja:
    1. Check jika endpoint perlu authentication (hanya /api/landing)
    2. Check Authorization header
    3. Validasi Bearer token = "123456"
    4. Jika valid, simpan user info di request.state
    5. Jika tidak, return 401 Unauthorized
    
    Ini adalah simulasi sederhana untuk belajar middleware.
    Nanti akan diganti dengan JWT authentication yang lebih secure.
    
    Mirip dengan Express.js:
    ```javascript
    app.use((req, res, next) => {
        if (req.path === '/api/landing') {
            const token = req.headers.authorization;
            if (token !== 'Bearer 123456') {
                return res.status(401).json({error: 'Unauthorized'});
            }
            req.user = {username: 'admin'};
        }
        next();
    });
    ```
    """
    # Daftar endpoint yang perlu authentication
    protected_paths = ["/api/landing"]
    
    # Check apakah endpoint perlu auth
    if request.url.path in protected_paths:
        # Ambil Authorization header
        auth_header = request.headers.get("Authorization")
        
        # Check format: "Bearer 123456"
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Missing or invalid Authorization header",
                    "hint": "Use: Authorization: Bearer 123456"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token
        token = auth_header.replace("Bearer ", "")
        
        # Validasi token (hardcoded untuk pembelajaran)
        if token != "123456":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Invalid token",
                    "hint": "Valid token is: 123456"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Token valid! Simpan user info di request.state
        # Ini bisa diakses di endpoint handler
        request.state.user = {
            "username": "admin",
            "role": "administrator",
            "authenticated_at": "2026-02-05"
        }
    
    # Lanjutkan ke endpoint handler
    response = await call_next(request)
    return response
