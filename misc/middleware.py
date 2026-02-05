"""
Middleware untuk Siswa CRUD API
Implementasi praktis untuk production
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 1. REQUEST LOGGING MIDDLEWARE ====================

async def request_logging_middleware(request: Request, call_next):
    """
    Log semua incoming requests
    Berguna untuk monitoring dan debugging
    """
    start_time = time.time()
    request_id = f"{int(time.time() * 1000)}"
    
    # Simpan request_id di request.state (bisa diakses di endpoint)
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"- Client: {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (time.time() - start_time) * 1000  # ms
    logger.info(
        f"[{request_id}] Status: {response.status_code} "
        f"- Process Time: {process_time:.2f}ms"
    )
    
    # Tambah headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    return response


# ==================== 2. ERROR HANDLING MIDDLEWARE ====================

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handler untuk catch semua unhandled exceptions
    Mirip dengan error middleware di Express.js
    """
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            # Log error
            logger.error(
                f"Unhandled error at {request.url.path}: {str(exc)}",
                exc_info=True
            )
            
            # Return error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Internal server error",
                    "detail": str(exc) if request.app.debug else None,
                    "path": request.url.path,
                    "timestamp": datetime.now().isoformat()
                }
            )


# ==================== 3. RATE LIMITING MIDDLEWARE ====================

from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    Batasi jumlah request per IP dalam periode waktu tertentu
    """
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Maksimal calls
        self.period = period  # Dalam detik
        self.clients = defaultdict(list)  # IP -> [timestamps]
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip untuk endpoint docs
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get current time
        now = datetime.now()
        
        # Clean old timestamps
        cutoff = now - timedelta(seconds=self.period)
        self.clients[client_ip] = [
            ts for ts in self.clients[client_ip] 
            if ts > cutoff
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error",
                    "message": f"Rate limit exceeded. Max {self.calls} requests per {self.period} seconds",
                    "retry_after": self.period
                },
                headers={"Retry-After": str(self.period)}
            )
        
        # Add timestamp
        self.clients[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(
            self.calls - len(self.clients[client_ip])
        )
        
        return response


# ==================== 4. REQUEST VALIDATION MIDDLEWARE ====================

async def request_validation_middleware(request: Request, call_next):
    """
    Validasi basic request (content-type, size, dll)
    """
    # Check content length (max 1MB)
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1_000_000:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                "status": "error",
                "message": "Request body too large. Max 1MB allowed"
            }
        )
    
    # Validate content-type untuk POST/PUT
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            # Skip jika memang tidak ada body
            if content_length and int(content_length) > 0:
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "status": "error",
                        "message": "Content-Type must be application/json"
                    }
                )
    
    return await call_next(request)


# ==================== 5. DATABASE SESSION MIDDLEWARE ====================

async def db_session_middleware(request: Request, call_next):
    """
    Ensure database session cleanup
    Mirip dengan session management di Express.js
    """
    try:
        response = await call_next(request)
        return response
    finally:
        # Cleanup jika perlu
        # db.close() or similar
        pass


# ==================== 6. CORS HELPER ====================

def setup_cors(app, origins: list = None):
    """
    Setup CORS middleware dengan konfigurasi
    
    Usage:
        setup_cors(app, origins=["http://localhost:3000"])
    """
    from fastapi.middleware.cors import CORSMiddleware
    
    if origins is None:
        origins = [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8080",
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ==================== 7. AUTHENTICATION MIDDLEWARE ====================

async def auth_middleware(request: Request, call_next):
    """
    Simple token authentication middleware
    
    Mirip dengan passport di Express.js atau @login_required di Flask
    """
    # Public endpoints (tidak perlu auth)
    public_paths = ["/", "/docs", "/redoc", "/openapi.json", "/api/health"]
    
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status": "error",
                "message": "Authentication required"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Validate token (contoh sederhana)
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status": "error",
                "message": "Invalid authentication scheme. Use Bearer token"
            }
        )
    
    token = auth_header.replace("Bearer ", "")
    
    # TODO: Validate token dengan JWT atau database
    # Untuk contoh, kita anggap token "secret-token" valid
    if token != "secret-token":
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "status": "error",
                "message": "Invalid or expired token"
            }
        )
    
    # Simpan user info di request.state
    request.state.user = {"id": 1, "username": "admin"}
    
    return await call_next(request)
