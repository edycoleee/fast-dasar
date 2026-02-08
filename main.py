"""
FastAPI Application dengan CRUD SQLAlchemy ORM
Week 1c: CRUD siswa dengan SQLite menggunakan SQLAlchemy ORM

Architecture:
- main.py: Entry point, setup lifespan dan include router
- app/api/v1/: API versioning folder
  - endpoints/: Individual endpoint routers
    - siswa.py: CRUD endpoints untuk siswa
    - halo.py: Simple greeting endpoints
  - api.py: Router aggregator
- database.py: SQLAlchemy configuration dan ORM models
- models.py: Pydantic request/response schemas
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import status, Depends
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.database import init_db, SessionLocal, get_db, SiswaORM
from app.api.v1.api import api_router


# ==================== Lifespan Event Handler ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager untuk startup dan shutdown events.
    
    Lifecycle:
    - Startup: Initialize database
    - Running: App melayani requests
    - Shutdown: Cleanup resources
    """
    # ===== STARTUP =====
    init_db()
    print("🚀 FastAPI app started with SQLAlchemy ORM")
    
    yield  # App running
    
    # ===== SHUTDOWN =====
    print("👋 FastAPI app shutting down")


# ==================== FastAPI Setup ====================

app = FastAPI(
    title="Siswa CRUD API",
    description="API CRUD untuk manajemen data siswa dengan SQLAlchemy - v2.0",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include router dari app/api/v1/
app.include_router(api_router)


# ==================== Root & Health Endpoints ====================

@app.get("/")
async def root(db: Session = Depends(get_db)):
    """Root endpoint dengan informasi API"""
    total_siswa = db.query(SiswaORM).count()
    
    return {
        "message": "Siswa CRUD API is running!",
        "version": "2.0.0",
        "database": "SQLAlchemy ORM",
        "total_siswa": total_siswa,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "siswa": "GET /api/v1/siswa/",
            "halo": "GET /api/v1/halo/"
        }
    }


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint untuk monitoring"""
    try:
        total_siswa = db.query(SiswaORM).count()
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

