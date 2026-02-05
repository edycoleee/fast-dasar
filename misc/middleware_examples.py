"""
FastAPI Middleware Examples
Perbandingan dengan Node.js dan Flask
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import time
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== METHOD 1: @app.middleware (Paling Mirip Express.js) ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware untuk logging setiap request
    
    Mirip dengan Express.js:
    app.use((req, res, next) => {
        console.log(`${req.method} ${req.url}`);
        next();
    });
    
    Mirip dengan Flask:
    @app.before_request
    def log_request():
        print(f"{request.method} {request.url}")
    """
    start_time = time.time()
    
    # BEFORE REQUEST (sebelum request diproses)
    logger.info(f"🔵 REQUEST: {request.method} {request.url}")
    
    # Panggil endpoint berikutnya (seperti next() di Express)
    response = await call_next(request)
    
    # AFTER REQUEST (setelah request diproses)
    process_time = time.time() - start_time
    logger.info(f"🟢 RESPONSE: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    # Tambah custom header ke response
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Middleware untuk menambah security headers
    
    Mirip dengan helmet di Node.js:
    app.use(helmet());
    """
    response = await call_next(request)
    
    # Tambah security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response


@app.middleware("http")
async def check_api_key(request: Request, call_next):
    """
    Middleware untuk validasi API key
    
    Mirip dengan Express.js:
    app.use((req, res, next) => {
        if (!req.headers['x-api-key']) {
            return res.status(401).json({ error: 'No API key' });
        }
        next();
    });
    """
    # Skip validation untuk endpoint tertentu
    if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "API Key required"}
        )
    
    # Validasi API key (contoh sederhana)
    if api_key != "secret-key-123":
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "Invalid API Key"}
        )
    
    response = await call_next(request)
    return response


# ==================== METHOD 2: BaseHTTPMiddleware (Lebih Terstruktur) ====================

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

class CustomHeaderMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware class
    Mirip dengan custom middleware class di Express.js
    """
    async def dispatch(self, request: StarletteRequest, call_next):
        # Before request
        request.state.request_id = f"req_{int(time.time() * 1000)}"
        
        # Process request
        response = await call_next(request)
        
        # After request
        response.headers["X-Request-ID"] = request.state.request_id
        
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware
    
    Mirip dengan Express.js:
    app.use((err, req, res, next) => {
        console.error(err);
        res.status(500).json({ error: 'Something went wrong' });
    });
    """
    async def dispatch(self, request: StarletteRequest, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"❌ ERROR: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": str(e),
                    "path": str(request.url)
                }
            )


# Tambahkan middleware ke app
# app.add_middleware(CustomHeaderMiddleware)
# app.add_middleware(ErrorHandlerMiddleware)


# ==================== METHOD 3: CORS Middleware (Built-in) ====================

from fastapi.middleware.cors import CORSMiddleware

# CORS middleware (paling sering digunakan)
# Mirip dengan cors package di Express.js: app.use(cors())
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, dll
    allow_headers=["*"],  # Semua headers
)


# ==================== METHOD 4: Trusted Host Middleware ====================

from fastapi.middleware.trustedhosts import TrustedHostMiddleware

# Hanya izinkan request dari host tertentu
# app.add_middleware(
#     TrustedHostMiddleware, 
#     allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
# )


# ==================== METHOD 5: GZip Middleware ====================

from fastapi.middleware.gzip import GZipMiddleware

# Compress response dengan GZip
# Mirip dengan compression di Express.js: app.use(compression())
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ==================== ENDPOINTS UNTUK TESTING ====================

@app.get("/")
async def root():
    return {"message": "Hello! Check headers to see middleware in action"}


@app.get("/api/test")
async def test_endpoint(request: Request):
    """Test endpoint untuk lihat middleware bekerja"""
    return {
        "message": "Middleware test",
        "request_id": getattr(request.state, "request_id", None),
        "headers": dict(request.headers)
    }


@app.get("/api/error")
async def error_endpoint():
    """Endpoint untuk test error middleware"""
    raise Exception("This is a test error")


# ==================== URUTAN MIDDLEWARE (PENTING!) ====================
"""
Middleware dijalankan dalam urutan TUMPUKAN (stack):

Request flow (dari atas ke bawah):
  → Middleware 1 (before)
    → Middleware 2 (before)
      → Middleware 3 (before)
        → ENDPOINT HANDLER
      ← Middleware 3 (after)
    ← Middleware 2 (after)
  ← Middleware 1 (after)

Jadi middleware yang didefinisikan PERTAMA akan:
- Dijalankan PERTAMA saat request masuk
- Dijalankan TERAKHIR saat response keluar

Mirip dengan Express.js!
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
