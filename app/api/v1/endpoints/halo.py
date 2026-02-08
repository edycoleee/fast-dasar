"""
Halo Endpoints - Simple greeting API
"""

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/halo", tags=["Halo"])


# ==================== Models ====================

class HaloRequest(BaseModel):
    """Request model untuk POST /halo/"""
    nama: str
    handphone: str


class HaloResponse(BaseModel):
    """Response model untuk POST /halo/"""
    message: str
    nama: str
    handphone: str


# ==================== Endpoints ====================

@router.get("/")
async def halo_get():
    """
    GET /api/v1/halo/ - Simple greeting
    
    Returns:
    - 200: Greeting message
    
    Example:
        GET /api/v1/halo/
        
        Response:
        {
            "success": true,
            "message": "Get from Halo API",
            "data": []
        }
    """
    return {
        "success": True,
        "message": "Get from Halo API",
        "data": []
    }


@router.post("/", response_model=HaloResponse)
async def halo_post(data: HaloRequest):
    """
    POST /api/v1/halo/ - Greeting dengan nama dan handphone
    
    Request body:
    - nama: string (required)
    - handphone: string (required)
    
    Returns:
    - 200: Personalized greeting
    
    Example:
        POST /api/v1/halo/
        Content-Type: application/json
        
        {
            "nama": "Edy Santoso",
            "handphone": "08123456789"
        }
        
        Response:
        {
            "message": "Halo Edy Santoso!",
            "nama": "Edy Santoso",
            "handphone": "08123456789"
        }
    """
    return {
        "message": f"Halo {data.nama}!",
        "nama": data.nama,
        "handphone": data.handphone
    }
