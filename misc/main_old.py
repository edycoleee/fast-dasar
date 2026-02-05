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
    return {
        "success": True, 
        "message": "Get from Halo API", 
        "data": []
    }


# Endpoint 3: GET /api/siswa/
@app.get("/api/siswa/")
async def siswa_get():
    """
    Endpoint GET yang mengembalikan data siswa.
    
    Untuk tahap belajar ini, data masih hardcoded.
    Nanti akan diganti dengan database (Week 1b - SQLite).
    """
    return {
        "success": True, 
        "message": "Get from siswa API", 
        "data": [
            {
                "no": 1, 
                "nama": "Edy", 
                "email": "edycoleee@gmail.com"
            }
        ]
    }


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
