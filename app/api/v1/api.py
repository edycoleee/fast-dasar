"""
API v1 Router - Agregasi semua endpoints versi 1
"""

from fastapi import APIRouter

from app.api.v1.endpoints.halo import router as halo_router
from app.api.v1.endpoints.siswa import router as siswa_router


# Buat router agregator dengan prefix /api/v1
api_router = APIRouter(prefix="/api/v1")

# Include semua sub-routers
api_router.include_router(halo_router)
api_router.include_router(siswa_router)
