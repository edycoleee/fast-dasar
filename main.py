from fastapi import FastAPI
from pydantic import BaseModel

# Inisialisasi FastAPI app
app = FastAPI(
    title="Halo API",
    description="API sederhana untuk belajar FastAPI",
    version="1.0.0"
)

# Model untuk request POST (mirip dengan schema validation di Flask/Express)
class HaloRequest(BaseModel):
    nama: str
    handphone: str

# Model untuk response (opsional, tapi best practice)
class HaloResponse(BaseModel):
    message: str
    nama: str
    handphone: str


# Endpoint 1: GET /api/halo/
@app.get("/api/halo/")
async def halo_get():
    """
    Endpoint GET sederhana yang mengembalikan pesan halo.
    
    Mirip dengan:
    - Flask: @app.route('/api/halo/', methods=['GET'])
    - Express: app.get('/api/halo/', ...)
    """
    return {"message": "Halo! Welcome to FastAPI"}


# Endpoint 2: POST /api/halo/
@app.post("/api/halo/", response_model=HaloResponse)
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


# Root endpoint (bonus)
@app.get("/")
async def root():
    """Root endpoint untuk testing"""
    return {
        "message": "FastAPI is running!",
        "docs": "/docs",
        "redoc": "/redoc"
    }
