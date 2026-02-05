"""
Test Middleware in Action
Run this file to see middleware working
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import time

app = FastAPI(title="Middleware Demo")

# ==================== MIDDLEWARE 1: Timing ====================

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """Ukur berapa lama request diproses"""
    start = time.time()
    
    print(f"⏱️  START: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = (time.time() - start) * 1000
    print(f"✅ DONE: {request.method} {request.url.path} - {duration:.2f}ms")
    
    # Tambah header
    response.headers["X-Process-Time"] = f"{duration:.2f}ms"
    
    return response


# ==================== MIDDLEWARE 2: Request ID ====================

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Tambah unique ID ke setiap request"""
    request_id = f"req_{int(time.time() * 1000)}"
    
    # Store di request.state (bisa diakses di endpoint)
    request.state.id = request_id
    
    print(f"🆔 Request ID: {request_id}")
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# ==================== MIDDLEWARE 3: Custom Headers ====================

@app.middleware("http")
async def custom_headers_middleware(request: Request, call_next):
    """Tambah custom headers ke response"""
    response = await call_next(request)
    
    response.headers["X-Custom-Header"] = "FastAPI Middleware Demo"
    response.headers["X-Author"] = "Your Name"
    
    return response


# ==================== MIDDLEWARE 4: Rate Limiting (Simplified) ====================

from collections import defaultdict

request_counts = defaultdict(int)

@app.middleware("http")
async def simple_rate_limit(request: Request, call_next):
    """Simple rate limiting - max 5 requests per session"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Skip untuk docs
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    request_counts[client_ip] += 1
    
    print(f"📊 Request count for {client_ip}: {request_counts[client_ip]}")
    
    # Jika lebih dari 10, tolak
    if request_counts[client_ip] > 10:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too many requests",
                "message": f"You've made {request_counts[client_ip]} requests. Reload the server to reset.",
                "limit": 10
            }
        )
    
    response = await call_next(request)
    response.headers["X-Request-Count"] = str(request_counts[client_ip])
    
    return response


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """
    Homepage - tidak ada middleware khusus
    Tapi semua middleware tetap jalan!
    """
    return {
        "message": "Middleware Demo API",
        "tip": "Check response headers to see middleware in action!"
    }


@app.get("/info")
async def info(request: Request):
    """
    Endpoint dengan access ke request.state
    Bisa akses data yang di-set di middleware
    """
    return {
        "request_id": request.state.id,  # Dari request_id_middleware
        "client": request.client.host if request.client else "unknown",
        "method": request.method,
        "path": request.url.path
    }


@app.get("/slow")
async def slow_endpoint():
    """
    Endpoint yang lambat - buat test timing middleware
    """
    import asyncio
    await asyncio.sleep(2)  # Sleep 2 detik
    return {"message": "This was slow! Check X-Process-Time header"}


@app.get("/error")
async def error_endpoint():
    """
    Endpoint yang throw error
    """
    raise HTTPException(status_code=500, detail="Intentional error for testing")


@app.post("/data")
async def post_data(data: dict):
    """
    POST endpoint - test dengan body
    """
    return {
        "received": data,
        "message": "Data received successfully"
    }


# ==================== INSTRUKSI TESTING ====================

"""
🚀 Cara Test:

1. Jalankan server:
   uvicorn test_middleware:app --reload

2. Buka browser:
   http://localhost:8000/docs

3. Test dengan curl:

   # Test basic request
   curl -i http://localhost:8000/
   
   # Lihat headers (X-Process-Time, X-Request-ID, dll)
   curl -i http://localhost:8000/info
   
   # Test slow endpoint
   curl -i http://localhost:8000/slow
   
   # Test rate limiting (jalankan 15x)
   for i in {1..15}; do curl http://localhost:8000/info; echo; done
   
   # Test POST
   curl -X POST http://localhost:8000/data \
     -H "Content-Type: application/json" \
     -d '{"name": "test", "value": 123}'

4. Check terminal untuk lihat log dari middleware!

📝 Yang akan Anda lihat:

- Console logs dari setiap middleware
- Headers tambahan di response (X-Process-Time, X-Request-ID, dll)
- Rate limiting setelah 10 requests
- Timing untuk slow endpoint
"""

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Middleware Demo Server...")
    print("📖 Open http://localhost:8000/docs untuk API docs")
    print("💡 Check terminal untuk lihat middleware logs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
