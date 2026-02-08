from fastapi import FastAPI
from app.api.v1.api import api_router

# Inisialisasi FastAPI app
app = FastAPI(
    title="Halo API",
    description="API sederhana untuk belajar FastAPI",
    version="1.0.0"
)

# Include router dari app/api/v1/
app.include_router(api_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint untuk testing"""
    return {
        "message": "FastAPI is running!",
        "docs": "/docs",
        "redoc": "/redoc"
    }
