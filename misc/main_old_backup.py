"""
FastAPI Application dengan SQLAlchemy ORM dan JWT Authentication
Week 2b: JWT Authentication Implementation
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

from misc.db_sqlalchemy import Siswa, get_db, init_db
from misc.schemas import SiswaCreate, SiswaUpdate, SiswaResponse, LoginRequest, LoginResponse, UpdateRoleRequest

# Import authentication utilities
from misc.auth_utils import hash_password, verify_password, create_access_token, decode_access_token, extract_bearer_token

# Import authorization utilities
from misc.authorization import require_admin, require_role, get_current_user, Role

# Import middleware
from misc.middleware import (
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
async def create_siswa(siswa: SiswaCreate, request: Request, db: Session = Depends(get_db)):
    """
    CREATE - Tambah siswa baru dengan password yang di-hash
    
    Permission:
    - Admin: bisa set role (admin/user)
    - User: hanya bisa buat user baru dengan role=user
    
    SQLAlchemy ORM:
    1. Buat instance dari model Siswa
    2. Hash password dengan bcrypt
    3. Set role (default: user)
    4. Add ke session
    5. Commit untuk save ke database
    6. Refresh untuk mendapatkan data yang ter-generate (id)
    
    Equivalent SQL:
    INSERT INTO siswa (nama, email, password, role) VALUES (?, ?, ?, ?)
    """
    try:
        # Check permission untuk set role
        current_user = get_current_user(request)
        
        # Jika bukan admin, force role = user
        if current_user.get("role") != Role.ADMIN:
            siswa.role = "user"
        
        # 1. Hash password sebelum disimpan
        hashed_password = hash_password(siswa.password)
        
        # 2. Buat instance SQLAlchemy model
        db_siswa = Siswa(
            nama=siswa.nama,
            email=siswa.email,
            password=hashed_password,
            role=siswa.role
        )
        
        # 3. Add ke database session
        db.add(db_siswa)
        
        # 4. Commit transaction
        db.commit()
        
        # 5. Refresh untuk mendapatkan data dari DB (seperti id yang auto-generated)
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
    UPDATE - Update data siswa (termasuk password jika ada)
    
    SQLAlchemy ORM:
    1. Query siswa by ID
    2. Update attribute
    3. Hash password baru jika ada
    4. Commit changes
    
    Equivalent SQL:
    UPDATE siswa SET nama = ?, email = ?, password = ? WHERE id = ?
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
        
        # 3. Update password jika ada (hash dulu)
        if siswa_update.password:
            siswa.password = hash_password(siswa_update.password)
        
        # 4. Commit changes
        db.commit()
        
        # 5. Refresh untuk mendapatkan data terbaru
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
async def delete_siswa(siswa_id: int, request: Request, db: Session = Depends(get_db)):
    """
    DELETE - Hapus siswa (HANYA ADMIN)
    
    Permission:
    - Admin: bisa delete semua siswa
    - User: TIDAK BISA delete (403 Forbidden)
    
    SQLAlchemy ORM:
    1. Check permission (admin only)
    2. Query siswa by ID
    3. Delete object
    4. Commit changes
    
    Equivalent SQL:
    DELETE FROM siswa WHERE id = ?
    """
    # Check admin permission
    require_admin(request)
    
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
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    LOGIN - Endpoint untuk login dengan email dan password
    
    Flow:
    1. Cari siswa berdasarkan email
    2. Verifikasi password dengan hash
    3. Generate JWT token
    4. Return token dan user info
    
    Cara test:
    ```bash
    # 1. Register siswa dulu
    curl -X POST http://localhost:8000/api/siswa/ \
      -H "Content-Type: application/json" \
      -d '{"nama":"Edy Cole","email":"edycoleee@gmail.com","password":"secret123"}'
    
    # 2. Login
    curl -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"edycoleee@gmail.com","password":"secret123"}'
    ```
    """
    # 1. Cari siswa berdasarkan email
    siswa = db.query(Siswa).filter(Siswa.email == credentials.email).first()
    
    if not siswa:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Verifikasi password
    if not verify_password(credentials.password, siswa.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate JWT token
    access_token = create_access_token(data={"sub": siswa.email})
    
    # 4. Return response
    return LoginResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user={
            "id": siswa.id,
            "nama": siswa.nama,
            "email": siswa.email,
            "role": siswa.role
        }
    )


@app.get("/api/dashboard", tags=["Authentication"])
async def dashboard(request: Request):
    """
    DASHBOARD - Protected endpoint dengan JWT authentication
    
    Harus include header:
    Authorization: Bearer <jwt_token>
    
    Cara test:
    ```bash
    # 1. Login dulu untuk dapat token
    TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"edycoleee@gmail.com","password":"secret123"}' \
      | jq -r '.access_token')
    
    # 2. Access dashboard dengan token
    curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard
    ```
    
    Endpoint ini menggunakan JWT middleware untuk authentication.
    User info sudah di-set di request.state oleh middleware.
    """
    # Data user dari middleware (di-set di request.state)
    user_data = getattr(request.state, "user", None)
    
    return {
        "message": "Welcome to the dashboard!",
        "description": "This is a protected endpoint - you need JWT token to access",
        "user": user_data,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/auth/logout", tags=["Authentication"])
async def logout():
    """
    LOGOUT - Endpoint untuk logout
    
    Note: Dengan JWT, logout biasanya dilakukan di client-side dengan menghapus token.
    Server tidak perlu menyimpan state karena JWT stateless.
    
    Untuk invalidasi token di server, bisa:
    1. Simpan blacklist token di Redis
    2. Set expiry time yang pendek
    3. Gunakan refresh token mechanism
    
    Cara test:
    ```bash
    curl -X POST http://localhost:8000/api/auth/logout
    ```
    """
    return {
        "message": "Logout successful",
        "instruction": "Please delete the JWT token from client storage"
    }


# ==================== AUTHORIZATION ENDPOINTS ====================
# Admin endpoints untuk manage user roles

@app.put("/api/users/{user_id}/role", response_model=SiswaResponse, tags=["Authorization"])
async def update_user_role(
    user_id: int,
    role_update: UpdateRoleRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    UPDATE USER ROLE - Ubah role user (HANYA ADMIN)
    
    Permission:
    - Admin: bisa ubah role siapa saja (admin/user)
    - User: TIDAK BISA (403 Forbidden)
    
    Cara test:
    ```bash
    # Login sebagai admin
    TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"admin@example.com","password":"admin123"}' \
      | jq -r '.access_token')
    
    # Update role user jadi admin
    curl -X PUT http://localhost:8000/api/users/2/role \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"role":"admin"}'
    ```
    """
    # Check admin permission
    require_admin(request)
    
    try:
        # Find user
        user = db.query(Siswa).filter(Siswa.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User dengan ID {user_id} tidak ditemukan"
            )
        
        # Update role
        user.role = role_update.role
        
        # Commit changes
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.get("/api/users", response_model=List[SiswaResponse], tags=["Authorization"])
async def get_all_users(request: Request, db: Session = Depends(get_db)):
    """
    GET ALL USERS - Lihat semua user dengan role (HANYA ADMIN)
    
    Permission:
    - Admin: bisa lihat semua user
    - User: TIDAK BISA (403 Forbidden)
    """
    # Check admin permission
    require_admin(request)
    
    users = db.query(Siswa).all()
    return users


# ==================== JWT AUTHENTICATION MIDDLEWARE ====================
# Middleware untuk check JWT token pada endpoint tertentu

@app.middleware("http")
async def jwt_auth_middleware(request: Request, call_next):
    """
    JWT Authentication Middleware
    
    Cara kerja:
    1. Check jika endpoint perlu authentication
    2. Extract Bearer token dari Authorization header
    3. Decode dan validasi JWT token
    4. Query user dari database berdasarkan email di token
    5. Jika valid, simpan user info di request.state
    6. Jika tidak, return 401 Unauthorized
    
    Protected endpoints:
    - /api/dashboard
    - /api/siswa/* (POST, PUT, DELETE)
    
    Mirip dengan Express.js:
    ```javascript
    app.use(async (req, res, next) => {
        if (protectedPaths.includes(req.path)) {
            const token = req.headers.authorization?.replace('Bearer ', '');
            const payload = jwt.verify(token, SECRET_KEY);
            req.user = await User.findOne({email: payload.sub});
        }
        next();
    });
    ```
    """
    # Daftar endpoint yang perlu authentication
    protected_paths = [
        "/api/dashboard",
    ]
    
    # Check juga berdasarkan method dan path pattern
    path = request.url.path
    method = request.method
    
    # Tambahkan endpoint siswa yang perlu auth (kecuali GET)
    requires_auth = (
        path in protected_paths or
        (path.startswith("/api/siswa/") and method in ["POST", "PUT", "DELETE"])
    )
    
    if requires_auth:
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        token = extract_bearer_token(auth_header)
        
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Missing or invalid Authorization header",
                    "hint": "Use: Authorization: Bearer <jwt_token>"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decode JWT token
        payload = decode_access_token(token)
        
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Invalid or expired token",
                    "hint": "Please login again to get a new token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract email dari token
        email = payload.get("sub")
        
        if not email:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Invalid token payload",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Query user dari database
        from misc.db_sqlalchemy import SessionLocal
        db = SessionLocal()
        try:
            siswa = db.query(Siswa).filter(Siswa.email == email).first()
            
            if not siswa:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "User not found",
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Token valid! Simpan user info di request.state
            request.state.user = {
                "id": siswa.id,
                "nama": siswa.nama,
                "email": siswa.email,
                "role": siswa.role,
                "authenticated_at": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    # Lanjutkan ke endpoint handler
    response = await call_next(request)
    return response
