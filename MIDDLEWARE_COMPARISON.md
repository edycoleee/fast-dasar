# 🔄 Middleware Comparison: Node.js vs Flask vs FastAPI

## Side-by-side examples untuk developer yang pindah dari Node.js/Flask ke FastAPI

---

## 1. Basic Logging Middleware

### Express.js (Node.js)
```javascript
// middleware.js
const logger = (req, res, next) => {
    console.log(`${req.method} ${req.url}`);
    next();
};

// app.js
app.use(logger);
```

### Flask
```python
# app.py
@app.before_request
def log_request():
    print(f"{request.method} {request.url}")

@app.after_request
def log_response(response):
    print(f"Status: {response.status_code}")
    return response
```

### FastAPI ⭐
```python
# middleware.py
@app.middleware("http")
async def log_middleware(request: Request, call_next):
    print(f"{request.method} {request.url}")
    response = await call_next(request)
    print(f"Status: {response.status_code}")
    return response
```

---

## 2. Add Custom Headers

### Express.js
```javascript
app.use((req, res, next) => {
    res.setHeader('X-Custom-Header', 'value');
    res.setHeader('X-Request-ID', generateId());
    next();
});
```

### Flask
```python
@app.after_request
def add_headers(response):
    response.headers['X-Custom-Header'] = 'value'
    response.headers['X-Request-ID'] = generate_id()
    return response
```

### FastAPI ⭐
```python
@app.middleware("http")
async def add_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Custom-Header'] = 'value'
    response.headers['X-Request-ID'] = generate_id()
    return response
```

---

## 3. Timing/Performance Measurement

### Express.js
```javascript
const morgan = require('morgan');
app.use(morgan('dev'));

// Or custom:
app.use((req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`${req.method} ${req.url} - ${duration}ms`);
    });
    
    next();
});
```

### Flask
```python
import time

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_time(response):
    duration = (time.time() - g.start_time) * 1000
    print(f"Duration: {duration:.2f}ms")
    return response
```

### FastAPI ⭐
```python
import time

@app.middleware("http")
async def timing(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    response.headers["X-Process-Time"] = f"{duration:.2f}ms"
    return response
```

---

## 4. CORS (Cross-Origin Resource Sharing)

### Express.js
```javascript
const cors = require('cors');

app.use(cors({
    origin: 'http://localhost:3000',
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));
```

### Flask
```python
from flask_cors import CORS

CORS(app, 
     origins=['http://localhost:3000'],
     supports_credentials=True,
     methods=['GET', 'POST', 'PUT', 'DELETE'])
```

### FastAPI ⭐
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
```

---

## 5. Authentication Middleware

### Express.js
```javascript
const authenticate = (req, res, next) => {
    const token = req.headers.authorization;
    
    if (!token) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    
    try {
        const user = verifyToken(token);
        req.user = user;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Invalid token' });
    }
};

// Apply to specific routes
app.use('/api/protected', authenticate);

// Or globally with exclusions
app.use((req, res, next) => {
    if (publicPaths.includes(req.path)) {
        return next();
    }
    authenticate(req, res, next);
});
```

### Flask
```python
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return {'error': 'Unauthorized'}, 401
        
        try:
            user = verify_token(token)
            g.user = user
            return f(*args, **kwargs)
        except:
            return {'error': 'Invalid token'}, 401
    
    return decorated

# Use as decorator
@app.route('/protected')
@require_auth
def protected():
    return {'user': g.user}

# Or globally
@app.before_request
def check_auth():
    if request.path in public_paths:
        return
    
    token = request.headers.get('Authorization')
    if not token:
        abort(401)
    
    g.user = verify_token(token)
```

### FastAPI ⭐
```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Public endpoints
    if request.url.path in ['/login', '/docs', '/']:
        return await call_next(request)
    
    token = request.headers.get('Authorization')
    
    if not token:
        return JSONResponse(
            status_code=401,
            content={'error': 'Unauthorized'}
        )
    
    try:
        user = verify_token(token)
        request.state.user = user  # Store for use in endpoints
        return await call_next(request)
    except:
        return JSONResponse(
            status_code=401,
            content={'error': 'Invalid token'}
        )

# Access in endpoint
@app.get('/protected')
async def protected(request: Request):
    user = request.state.user
    return {'user': user}
```

---

## 6. Error Handling

### Express.js
```javascript
// Error handling middleware (must be last)
app.use((err, req, res, next) => {
    console.error(err.stack);
    
    res.status(err.status || 500).json({
        error: err.message || 'Internal Server Error',
        path: req.path
    });
});
```

### Flask
```python
@app.errorhandler(Exception)
def handle_error(error):
    print(f"Error: {error}")
    
    return {
        'error': str(error),
        'path': request.path
    }, 500

# Or with before/after
@app.after_request
def handle_errors(response):
    if response.status_code >= 400:
        print(f"Error response: {response.status_code}")
    return response
```

### FastAPI ⭐
```python
from starlette.middleware.base import BaseHTTPMiddleware

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            print(f"Error: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    'error': str(exc),
                    'path': request.url.path
                }
            )

app.add_middleware(ErrorHandlerMiddleware)
```

---

## 7. Rate Limiting

### Express.js
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 100, // max requests per windowMs
    message: 'Too many requests'
});

app.use('/api/', limiter);
```

### Flask
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@app.route('/api/endpoint')
@limiter.limit("10 per minute")
def endpoint():
    return {'data': 'value'}
```

### FastAPI ⭐
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
        
        # Clean old entries
        cutoff = now - timedelta(seconds=self.period)
        self.clients[client_ip] = [
            ts for ts in self.clients[client_ip] if ts > cutoff
        ]
        
        # Check limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={'error': 'Too many requests'}
            )
        
        self.clients[client_ip].append(now)
        return await call_next(request)

app.add_middleware(RateLimitMiddleware, calls=100, period=60)
```

---

## 8. Request/Response Compression

### Express.js
```javascript
const compression = require('compression');

app.use(compression({
    threshold: 1024  // Only compress if > 1KB
}));
```

### Flask
```python
from flask_compress import Compress

Compress(app)
```

### FastAPI ⭐
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## 9. Security Headers

### Express.js
```javascript
const helmet = require('helmet');

app.use(helmet());

// Or manual:
app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    next();
});
```

### Flask
```python
from flask_talisman import Talisman

Talisman(app)

# Or manual:
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### FastAPI ⭐
```python
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## 10. Request Body Size Limit

### Express.js
```javascript
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb', extended: true }));
```

### Flask
```python
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# Or in middleware
@app.before_request
def check_content_length():
    if request.content_length and request.content_length > 10_000_000:
        abort(413, 'Request too large')
```

### FastAPI ⭐
```python
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get('content-length')
    
    if content_length and int(content_length) > 10_000_000:
        return JSONResponse(
            status_code=413,
            content={'error': 'Request too large'}
        )
    
    return await call_next(request)
```

---

## 📊 Key Differences Summary

| Feature | Express.js | Flask | FastAPI |
|---------|-----------|-------|---------|
| **Syntax** | `app.use(fn)` | `@before_request` | `@app.middleware()` |
| **Next** | `next()` | Implicit | `await call_next()` |
| **Async** | Callbacks | No | Native async/await |
| **Order** | Top→Down | Decorator order | **STACK** (reverse) |
| **Request state** | `req.customProp` | `g.value` | `request.state.value` |
| **Built-in** | Minimal | Extensions | Starlette middlewares |

---

## 🎯 Migration Tips

### Coming from Express.js?
- ✅ `app.use()` → `@app.middleware("http")`
- ✅ `next()` → `await call_next(request)`
- ✅ `req.user` → `request.state.user`
- ✅ Callbacks → async/await
- ⚠️ Middleware order is reversed (stack-based)!

### Coming from Flask?
- ✅ `@before_request` + `@after_request` → Single middleware function
- ✅ `g.value` → `request.state.value`
- ✅ Sync → async (add `async`/`await`)
- ✅ Extensions → Built-in Starlette middlewares
- ⚠️ Must return response explicitly

---

## 🚀 Quick Start Template

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# 1. CORS (from Express cors)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# 2. Logging (from Express morgan)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    print(f"→ {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = (time.time() - start) * 1000
    print(f"← {response.status_code} - {duration:.2f}ms")
    
    return response

# 3. Security headers (from Express helmet)
@app.middleware("http")
async def security(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

That's it! You're now using middleware like a pro! 🎉
