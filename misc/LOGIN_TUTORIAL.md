# 🔐 Tutorial: Login & Authentication Middleware

## Untuk Belajar Middleware Sebelum JWT

---

## 📚 Apa yang Kita Buat?

Sistem authentication sederhana dengan:
1. **Endpoint Login** (`POST /api/auth/login`) - Login dengan username/password
2. **Endpoint Landing** (`GET /api/landing`) - Protected endpoint dengan Bearer token
3. **Auth Middleware** - Middleware yang check token sebelum akses endpoint

Ini adalah **simulasi sederhana** untuk memahami cara kerja middleware authentication sebelum implement JWT yang lebih complex.

---

## 🎯 Flow Authentication

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. POST /api/auth/login
       │    { username: "admin", password: "admin" }
       ▼
┌─────────────────┐
│ Login Endpoint  │ ← Check credentials
└──────┬──────────┘
       │
       │ 2. Return token
       │    { token: "123456", ... }
       ▼
┌─────────────┐
│   Client    │ ← Save token
└──────┬──────┘
       │
       │ 3. GET /api/landing
       │    Header: Authorization: Bearer 123456
       ▼
┌─────────────────────┐
│  Auth Middleware    │ ← Check token di header
│  (runs BEFORE       │
│   endpoint handler) │
└──────┬──────────────┘
       │
       │ 4. Token valid? ✓
       │    Set request.state.user
       ▼
┌─────────────────┐
│ Landing Endpoint│ ← Access request.state.user
└──────┬──────────┘
       │
       │ 5. Return response
       │    { message: "Welcome!", user: {...} }
       ▼
┌─────────────┐
│   Client    │
└─────────────┘
```

---

## 🚀 Cara Testing

### 1. Jalankan Server

```bash
cd /Users/edycole/dev/fast-dasar
uvicorn main:app --reload
```

Server akan jalan di: http://localhost:8000

---

### 2. Test Login Endpoint

#### ✅ Login Success (Credentials Benar)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "123456",
  "username": "admin"
}
```

#### ❌ Login Failed (Credentials Salah)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'
```

**Response:**
```json
{
  "detail": "Invalid username or password"
}
```

---

### 3. Test Landing Endpoint (Protected)

#### ❌ Tanpa Token (DITOLAK)

```bash
curl http://localhost:8000/api/landing
```

**Response:**
```json
{
  "detail": "Missing or invalid Authorization header",
  "hint": "Use: Authorization: Bearer 123456"
}
```

#### ❌ Dengan Token Salah (DITOLAK)

```bash
curl -H "Authorization: Bearer wrong-token" \
  http://localhost:8000/api/landing
```

**Response:**
```json
{
  "detail": "Invalid token",
  "hint": "Valid token is: 123456"
}
```

#### ✅ Dengan Token Benar (SUCCESS)

```bash
curl -H "Authorization: Bearer 123456" \
  http://localhost:8000/api/landing
```

**Response:**
```json
{
  "message": "Welcome to the landing page!",
  "description": "This is a protected endpoint - you need Bearer token to access",
  "user": {
    "username": "admin",
    "role": "administrator",
    "authenticated_at": "2026-02-05"
  },
  "info": "Token ini sederhana, nanti akan diganti dengan JWT yang lebih secure"
}
```

---

### 4. Test di Browser (Swagger UI)

Buka: http://localhost:8000/docs

**Step 1: Login**
1. Expand `POST /api/auth/login`
2. Click "Try it out"
3. Input:
   ```json
   {
     "username": "admin",
     "password": "admin"
   }
   ```
4. Click "Execute"
5. Copy token dari response: `123456`

**Step 2: Access Landing**
1. Click tombol "Authorize" di pojok kanan atas
2. Input: `Bearer 123456` (HARUS ada kata "Bearer ")
3. Click "Authorize"
4. Expand `GET /api/landing`
5. Click "Try it out"
6. Click "Execute"
7. Akan success! ✅

---

## 🔬 Cara Kerja Middleware

### Code Middleware di main.py:

```python
@app.middleware("http")
async def simple_auth_middleware(request: Request, call_next):
    # 1. Check apakah endpoint perlu auth
    protected_paths = ["/api/landing"]
    
    if request.url.path in protected_paths:
        # 2. Ambil Authorization header
        auth_header = request.headers.get("Authorization")
        
        # 3. Check format: "Bearer 123456"
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"}
            )
        
        # 4. Extract token
        token = auth_header.replace("Bearer ", "")
        
        # 5. Validasi token
        if token != "123456":
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        # 6. Token valid! Simpan user info
        request.state.user = {
            "username": "admin",
            "role": "administrator"
        }
    
    # 7. Lanjutkan ke endpoint handler
    response = await call_next(request)
    return response
```

### Penjelasan Step-by-Step:

1. **Check path** - Apakah endpoint ini perlu authentication?
2. **Get header** - Ambil `Authorization` header dari request
3. **Validate format** - Harus format `Bearer <token>`
4. **Extract token** - Ambil token dari header
5. **Validate token** - Check apakah token = "123456"
6. **Store user** - Simpan user info di `request.state`
7. **Continue** - Lanjut ke endpoint handler dengan `call_next()`

---

## 🎓 Perbandingan dengan Express.js & Flask

### Express.js
```javascript
// Middleware
app.use('/api/landing', (req, res, next) => {
    const token = req.headers.authorization;
    
    if (token !== 'Bearer 123456') {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    
    req.user = { username: 'admin' };
    next();
});

// Endpoint
app.get('/api/landing', (req, res) => {
    res.json({ 
        message: 'Welcome!',
        user: req.user  // ← Dari middleware
    });
});
```

### Flask
```python
# Middleware
@app.before_request
def check_auth():
    if request.path == '/api/landing':
        token = request.headers.get('Authorization')
        
        if token != 'Bearer 123456':
            abort(401, 'Unauthorized')
        
        g.user = {'username': 'admin'}

# Endpoint
@app.route('/api/landing')
def landing():
    return {
        'message': 'Welcome!',
        'user': g.user  # ← Dari middleware
    }
```

### FastAPI ⭐
```python
# Middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == '/api/landing':
        token = request.headers.get('Authorization')
        
        if token != 'Bearer 123456':
            return JSONResponse(status_code=401, content={'error': 'Unauthorized'})
        
        request.state.user = {'username': 'admin'}
    
    return await call_next(request)

# Endpoint
@app.get('/api/landing')
async def landing(request: Request):
    return {
        'message': 'Welcome!',
        'user': request.state.user  # ← Dari middleware
    }
```

---

## 💡 Konsep Penting

### 1. `request.state` - Share Data Antar Middleware & Endpoint

```python
# Di middleware
request.state.user = {"username": "admin"}

# Di endpoint
@app.get("/protected")
async def protected(request: Request):
    user = request.state.user  # ← Akses data dari middleware
    return {"user": user}
```

**Mirip dengan:**
- Express.js: `req.user` atau `req.locals`
- Flask: `g.user` (Flask's global object)

---

### 2. Protected Paths - Pilih Endpoint Mana yang Perlu Auth

```python
# Method 1: List of paths
protected_paths = ["/api/landing", "/api/profile", "/api/admin"]

if request.url.path in protected_paths:
    # Check auth


# Method 2: Pattern matching
if request.url.path.startswith("/api/admin"):
    # Check auth


# Method 3: Exclude public paths
public_paths = ["/", "/api/auth/login", "/docs"]

if request.url.path not in public_paths:
    # Check auth
```

---

### 3. Authorization Header Format

**Standard format:**
```
Authorization: Bearer <token>
```

**Contoh:**
```
Authorization: Bearer 123456
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Extract token:**
```python
auth_header = "Bearer 123456"
token = auth_header.replace("Bearer ", "")  # → "123456"

# Atau dengan split:
token = auth_header.split(" ")[1]  # → "123456"
```

---

## 🔄 Evolution ke JWT

Sistem ini adalah **stepping stone** ke JWT authentication:

### Current (Simple Token)
```
Token: "123456"
- Hardcoded
- Tidak expire
- Tidak ada info user di token
- Mudah ditebak
```

### Next Step (JWT)
```
Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
- Encoded dengan secret key
- Ada expiration time
- Carry user info (payload)
- Secure & standard
```

**Yang berubah nanti:**

1. **Login endpoint:**
   ```python
   # Sekarang
   return {"token": "123456"}
   
   # Dengan JWT
   token = create_jwt_token(user_id=1, username="admin")
   return {"token": token}
   ```

2. **Middleware validation:**
   ```python
   # Sekarang
   if token != "123456":
       raise Unauthorized
   
   # Dengan JWT
   try:
       payload = decode_jwt_token(token)
       request.state.user = payload
   except JWTError:
       raise Unauthorized
   ```

**Yang TIDAK berubah:**
- Struktur middleware (tetap `@app.middleware("http")`)
- Authorization header format (`Bearer <token>`)
- `request.state` untuk share data
- Protected paths logic

---

## 📝 Exercise untuk Belajar

1. **Tambah protected endpoint:**
   ```python
   @app.get("/api/profile")
   async def profile(request: Request):
       user = request.state.user
       return {"profile": user}
   ```
   Jangan lupa tambahkan `/api/profile` ke `protected_paths`!

2. **Tambah user role check:**
   ```python
   # Di middleware
   request.state.user = {
       "username": "admin",
       "role": "admin"  # atau "user"
   }
   
   # Di endpoint
   @app.get("/api/admin")
   async def admin_only(request: Request):
       if request.state.user["role"] != "admin":
           raise HTTPException(403, "Admin only")
       return {"message": "Admin area"}
   ```

3. **Multiple users:**
   ```python
   USERS = {
       "admin": {"password": "admin", "role": "admin"},
       "user": {"password": "user123", "role": "user"}
   }
   
   @app.post("/api/auth/login")
   async def login(credentials: LoginRequest):
       user = USERS.get(credentials.username)
       if user and user["password"] == credentials.password:
           return {"token": "123456", "role": user["role"]}
       raise HTTPException(401, "Invalid credentials")
   ```

---

## 🎯 Next Steps

1. ✅ Test semua endpoint dengan curl
2. ✅ Test di Swagger UI (http://localhost:8000/docs)
3. ✅ Tambah custom protected endpoint
4. ✅ Experiment dengan different tokens
5. 📚 Nanti: Upgrade ke JWT authentication

---

## 📖 Resources

- [FastAPI Security Tutorial](https://fastapi.tiangolo.com/tutorial/security/)
- [HTTP Bearer Authentication](https://tools.ietf.org/html/rfc6750)
- [JWT.io](https://jwt.io) - Untuk nanti belajar JWT

Happy Learning! 🚀
