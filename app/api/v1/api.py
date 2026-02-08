from fastapi import APIRouter
from app.api.v1.endpoints import halo, siswa

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(halo.router)
api_router.include_router(siswa.router)
