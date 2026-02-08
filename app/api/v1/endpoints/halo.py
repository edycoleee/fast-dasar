from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/halo", tags=["Halo"])


class HaloRequest(BaseModel):
    nama: str
    handphone: str


class HaloResponse(BaseModel):
    message: str
    nama: str
    handphone: str


@router.get("/")
async def halo_get():
    """
    Endpoint GET sederhana yang mengembalikan pesan halo.
    
    Mirip dengan:
    - Flask: @app.route('/api/halo/', methods=['GET'])
    - Express: app.get('/api/halo/', ...)
    """
    return {
        "success": True,
        "message": "Get from Halo API",
        "data": []
    }


@router.post("/", response_model=HaloResponse)
async def halo_post(data: HaloRequest):
    """
    Endpoint POST yang menerima data nama dan handphone.
    
    Perbedaan dengan Flask/Express:
    - Tidak perlu manual parsing request.json atau req.body
    - Pydantic otomatis validasi tipe data
    - Auto-generate OpenAPI documentation
    
    Args:
        data: HaloRequest object dengan field nama dan handphone
    
    Returns:
        HaloResponse dengan message, nama, dan handphone
    """
    return {
        "message": f"Halo {data.nama}!",
        "nama": data.nama,
        "handphone": data.handphone
    }
