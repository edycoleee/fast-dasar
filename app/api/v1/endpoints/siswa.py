from fastapi import APIRouter

router = APIRouter(prefix="/siswa", tags=["Siswa"])


@router.get("/")
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
