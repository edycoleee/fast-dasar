# 📚 FastAPI Middleware Guide

## Untuk Developer yang terbiasa dengan Node.js & Flask

---

## 🎯 Apa itu Middleware?

**Middleware** = Fungsi yang berjalan **sebelum dan sesudah** setiap request.

### Perbandingan dengan Framework Lain:

#### **Express.js (Node.js)**
```javascript
// Express middleware
app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`);
    next(); // Lanjut ke handler berikutnya
});
```

#### **Flask (Python)**
```python
# Flask before_request & after_request
@app.before_request
def before():
    print(f"{request.method} {request.url}")

@app.after_request
def after(response):
    response.headers['X-Custom'] = 'value'
    return response
```

#### **FastAPI (Python)**
```python
# FastAPI middleware
@app.middleware("http")
async def my_middleware(request: Request, call_next):
    print(f"{request.method} {request.url}")
    response = await call_next(request)  # next() di Express
    response.headers['X-Custom'] = 'value'
    return response
```

---

## 🔥 3 Cara Implementasi Middleware di FastAPI

### **1. Decorator `@app.middleware("http")` (Paling Simpel)**

**Mirip dengan:** `app.use()` di Express.js

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # BEFORE request processing
    print(f"Request: {request.method} {request.url}")
    
    # Process request (call next middleware/endpoint)
    response = await call_next(request)
    
    # AFTER request processing
    print(f"Response: {response.status_code}")
    
    return response
```

**Keuntungan:**
- ✅ Paling mudah untuk simple use cases
- ✅ Langsung bisa akses `request` dan `response`
- ✅ Mirip dengan Express.js, familiar!

**Kapan pakai:**
- Logging
- Add headers
- Timing requests
- Simple authentication checks

---

### **2. Class-based Middleware (BaseHTTPMiddleware)**

**Mirip dengan:** Custom middleware class di Express.js

```python
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, **options):
        super().__init__(app)
        self.options = options
    
    async def dispatch(self, request: Request, call_next):
        # Before
        request.state.custom_data = "value"
        
        # Process
        response = await call_next(request)
        
        # After
        response.headers["X-Custom"] = "value"
        
        return response

# Add to app
app.add_middleware(CustomMiddleware, option1="value1")
```

**Keuntungan:**
- ✅ Lebih terstruktur untuk complex logic
- ✅ Bisa terima parameters via `__init__`
- ✅ Reusable & testable

**Kapan pakai:**
- Rate limiting dengan config
- Authentication dengan multiple strategies
- Complex error handling
- Shared state management

---

### **3. Built-in Middleware (Production Ready)**

FastAPI/Starlette menyediakan middleware siap pakai:

#### **A. CORS Middleware**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE
    allow_headers=["*"],
)
```
**Mirip:** `cors` package di Express.js

---

#### **B. GZip Middleware**
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```
**Mirip:** `compression` package di Express.js

---

#### **C. Trusted Host Middleware**
```python
from fastapi.middleware.trustedhosts import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["example.com", "*.example.com"]
)
```

---

#### **D. HTTPSRedirect Middleware**
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 🎨 Use Cases Umum

### **1. Request Logging**

```python
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    
    logger.info(f"→ {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = (time.time() - start) * 1000
    logger.info(f"← Status: {response.status_code} - {duration:.2f}ms")
    
    response.headers["X-Process-Time"] = f"{duration:.2f}ms"
    return response
```

**Equivalent di Express.js:**
```javascript
app.use((req, res, next) => {
    const start = Date.now();
    console.log(`→ ${req.method} ${req.url}`);
    
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`← Status: ${res.statusCode} - ${duration}ms`);
    });
    
    next();
});
```

---

### **2. Authentication**

```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip public endpoints
    if request.url.path in ["/", "/login", "/docs"]:
        return await call_next(request)
    
    # Check token
    token = request.headers.get("Authorization")
    
    if not token or not token.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    # Validate token (simplified)
    # TODO: Validate with JWT or database
    
    # Store user in request state
    request.state.user = {"id": 1, "name": "User"}
    
    return await call_next(request)


# Di endpoint, access user:
@app.get("/protected")
async def protected(request: Request):
    user = request.state.user
    return {"message": f"Hello {user['name']}"}
```

**Equivalent di Express.js:**
```javascript
app.use((req, res, next) => {
    if (publicPaths.includes(req.path)) {
        return next();
    }
    
    const token = req.headers.authorization;
    
    if (!token) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    
    // Validate and attach user
    req.user = { id: 1, name: 'User' };
    next();
});
```

---

### **3. Error Handling**

```python
from starlette.middleware.base import BaseHTTPMiddleware

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={"error": "Bad Request", "detail": str(e)}
            )
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error"}
            )

app.add_middleware(ErrorHandlerMiddleware)
```

**Equivalent di Express.js:**
```javascript
app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).json({ error: 'Internal Server Error' });
});
```

---

### **4. Rate Limiting**

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls=100, period=60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = datetime.now()
        
        # Clean old requests
        cutoff = now - timedelta(seconds=self.period)
        self.clients[client_ip] = [
            ts for ts in self.clients[client_ip] if ts > cutoff
        ]
        
        # Check limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests"},
                headers={"Retry-After": str(self.period)}
            )
        
        # Record request
        self.clients[client_ip].append(now)
        
        return await call_next(request)

app.add_middleware(RateLimitMiddleware, calls=100, period=60)
```

**Equivalent di Express.js:**
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 100 // limit each IP to 100 requests per windowMs
});

app.use(limiter);
```

---

### **5. Add Custom Headers**

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    
    return response
```

**Equivalent di Express.js (dengan helmet):**
```javascript
const helmet = require('helmet');
app.use(helmet());
```

---

## ⚠️ Urutan Middleware (PENTING!)

Middleware dijalankan dalam urutan **STACK** (tumpukan):

```python
app.add_middleware(Middleware1)  # ← Terakhir keluar
app.add_middleware(Middleware2)
app.add_middleware(Middleware3)  # ← Pertama masuk
```

**Flow request/response:**

```
Request:
  → Middleware1 (before)
    → Middleware2 (before)
      → Middleware3 (before)
        → ENDPOINT
      ← Middleware3 (after)
    ← Middleware2 (after)
  ← Middleware1 (after)
```

**Urutan yang baik:**

```python
# 1. CORS - Paling luar, handle OPTIONS requests
app.add_middleware(CORSMiddleware, ...)

# 2. Security headers
app.middleware("http")(add_security_headers)

# 3. Error handling - Catch all errors
app.add_middleware(ErrorHandlerMiddleware)

# 4. Logging - Log requests & responses
app.middleware("http")(log_requests)

# 5. Rate limiting - Block excessive requests
app.add_middleware(RateLimitMiddleware)

# 6. Authentication - Validate users
app.middleware("http")(auth_middleware)

# 7. Request validation
app.middleware("http")(validate_request)
```

---

## 🔧 Request State (`request.state`)

Middleware bisa **share data** ke endpoints via `request.state`:

```python
# Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# Endpoint
@app.get("/test")
async def test(request: Request):
    # Access request_id yang di-set di middleware
    return {"request_id": request.state.request_id}
```

**Mirip dengan:**
- Express.js: `req.locals` atau `req.customProperty`
- Flask: `g.request_id` (flask.g object)

---

## 🚀 Testing Middleware

Jalankan aplikasi:
```bash
uvicorn main:app --reload
```

Test dengan curl:
```bash
# Test logging & headers
curl -i http://localhost:8000/api/siswa/

# Test auth middleware (jika diaktifkan)
curl -H "Authorization: Bearer secret-token" http://localhost:8000/api/siswa/

# Test rate limiting (jika diaktifkan)
for i in {1..105}; do curl http://localhost:8000/api/siswa/; done
```

Check logs di terminal untuk lihat middleware bekerja!

---

## 📝 Best Practices

### ✅ DO:
- Keep middleware focused (single responsibility)
- Use `request.state` untuk share data
- Log errors di middleware, jangan silent fail
- Add proper typing (`Request`, `Response`)
- Use built-in middleware (CORS, GZip) instead of custom

### ❌ DON'T:
- Jangan blocking operations di middleware (use async!)
- Jangan modify request body di middleware (complex & error-prone)
- Jangan lupa `return response` atau `return await call_next(request)`
- Jangan terlalu banyak middleware (performance overhead)

---

## 🎓 Perbedaan Utama dengan Express.js & Flask

| Aspect | Express.js | Flask | FastAPI |
|--------|-----------|-------|---------|
| **Syntax** | `app.use(fn)` | `@app.before_request` | `@app.middleware("http")` |
| **Async** | Callback-based | Sync | Async/await native |
| **Next** | `next()` | Implicit | `await call_next(request)` |
| **Error handling** | `next(err)` | Exception handlers | Try/except di middleware |
| **Order** | Top to bottom | Decorator order | **Bottom to top** (stack!) |
| **Built-in** | Via packages | Limited | Starlette middleware |

---

## 🔗 Resources

- [FastAPI Middleware Docs](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Starlette Middleware](https://www.starlette.io/middleware/)
- [ASGI Middleware Spec](https://asgi.readthedocs.io/)

---

## 💡 Next Steps

1. ✅ Coba jalankan `middleware_examples.py`
2. ✅ Aktifkan middleware di `main.py` (sudah di-setup)
3. ✅ Test dengan curl atau Postman
4. ✅ Buat custom middleware sendiri
5. ✅ Add authentication dengan JWT
6. ✅ Implement rate limiting untuk production

Happy coding! 🚀
