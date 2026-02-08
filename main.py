"""
FastAPI Application dengan CRUD SQLite
Week 1b: CRUD siswa dengan SQLite menggunakan raw SQL

Architecture:
- main.py: Entry point, setup lifespan dan include router
- app/api/v1/: API versioning folder
  - endpoints/: Individual endpoint routers
    - siswa.py: CRUD endpoints untuk siswa
    - halo.py: Simple greeting endpoints
  - api.py: Router aggregator
- database.py: Database operations
- models.py: Pydantic models
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import status
from contextlib import asynccontextmanager

from app.database import init_db, count_siswa
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
    print("🚀 FastAPI app started with SQLite database")
    
    yield  # App running
    
    # ===== SHUTDOWN =====
    print("👋 FastAPI app shutting down")


# ==================== FastAPI Setup ====================

app = FastAPI(
    title="Siswa CRUD API",
    description="API CRUD untuk manajemen data siswa dengan SQLite - v1.0",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include router dari app/api/v1/
app.include_router(api_router)


# ==================== Root & Health Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint dengan informasi API"""
    total_siswa = count_siswa()
    
    return {
        "message": "Siswa CRUD API is running!",
        "version": "1.0.0",
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
async def health_check():
    """Health check endpoint untuk monitoring"""
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

