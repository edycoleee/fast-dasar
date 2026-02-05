# JWT Authentication Implementation Guide

## 📚 Overview

Implementasi JWT (JSON Web Token) authentication untuk FastAPI dengan fitur:
- ✅ Password hashing dengan bcrypt
- ✅ JWT token generation dan validation
- ✅ Protected endpoints dengan middleware
- ✅ Login dengan email & password
- ✅ Logout endpoint

## 🔑 Key Components

### 1. Database Model (`db_sqlalchemy.py`)

```python
class Siswa(Base):
    id = Column(Integer, primary_key=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # 👈 Password hash
```

### 2. Schemas (`schemas.py`)

```python
class SiswaCreate(BaseModel):
    nama: str
    email: EmailStr
    password: str  # 👈 Plain password dari user

class LoginRequest(BaseModel):
    email: EmailStr  # 👈 Login dengan email, bukan username
    password: str

class LoginResponse(BaseModel):
    message: str
    access_token: str  # 👈 JWT token
    token_type: str = "bearer"
    user: dict
```

### 3. Authentication Utilities (`auth_utils.py`)

#### Password Hashing
```python
# Hash password sebelum disimpan
hashed = hash_password("secret123")
# $2b$12$KIXn0q4z...

# Verifikasi password saat login
is_valid = verify_password("secret123", hashed)
# True
```

#### JWT Token
```python
# Generate token
token = create_access_token({"sub": "user@example.com"})
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Decode token
payload = decode_access_token(token)
# {"sub": "user@example.com", "exp": 1234567890}
```

## 🚀 API Endpoints

### 1. Register Siswa
```bash
POST /api/siswa/
Content-Type: application/json

{
  "nama": "Edy Cole",
  "email": "edycoleee@gmail.com",
  "password": "secret123"
}

# Response (201 Created)
{
  "id": 1,
  "nama": "Edy Cole",
  "email": "edycoleee@gmail.com"
  # Note: password TIDAK muncul di response (security)
}
```

### 2. Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "edycoleee@gmail.com",
  "password": "secret123"
}

# Response (200 OK)
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nama": "Edy Cole",
    "email": "edycoleee@gmail.com"
  }
}
```

### 3. Access Protected Endpoint (Dashboard)
```bash
GET /api/dashboard
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Response (200 OK)
{
  "message": "Welcome to the dashboard!",
  "description": "This is a protected endpoint - you need JWT token to access",
  "user": {
    "id": 1,
    "nama": "Edy Cole",
    "email": "edycoleee@gmail.com",
    "authenticated_at": "2026-02-05T10:30:00"
  },
  "timestamp": "2026-02-05T10:30:00"
}

# Tanpa token (401 Unauthorized)
{
  "detail": "Missing or invalid Authorization header",
  "hint": "Use: Authorization: Bearer <jwt_token>"
}
```

### 4. Logout
```bash
POST /api/auth/logout

# Response (200 OK)
{
  "message": "Logout successful",
  "instruction": "Please delete the JWT token from client storage"
}
```

## 🔐 Security Features

### 1. Password Hashing
- Password TIDAK disimpan dalam plain text
- Menggunakan bcrypt dengan automatic salt
- Hash password: `$2b$12$KIXn0q4z...` (60 characters)

```python
# Saat register
plain_password = "secret123"
hashed_password = hash_password(plain_password)
# Simpan hashed_password ke database

# Saat login
is_valid = verify_password(user_input, stored_hash)
if is_valid:
    # Generate JWT token
```

### 2. JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "edycoleee@gmail.com",  // User identifier
    "exp": 1234567890               // Expiration timestamp
  },
  "signature": "..."
}
```

### 3. Protected Endpoints
Endpoints yang memerlukan JWT:
- `GET /api/dashboard`
- `POST /api/siswa/` (create)
- `PUT /api/siswa/{id}` (update)
- `DELETE /api/siswa/{id}` (delete)

Endpoints public (tidak perlu JWT):
- `POST /api/auth/login`
- `GET /api/siswa/` (read all)
- `GET /api/siswa/{id}` (read one)

## 🔄 Authentication Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. POST /api/siswa/ {nama, email, password}
       ├────────────────────────────────────────────►
       │                                              │
       │                                         ┌────▼────┐
       │                                         │  Server │
       │                                         └────┬────┘
       │                                              │
       │                                         Hash password
       │                                         Save to DB
       │                                              │
       │ 2. POST /api/auth/login {email, password}   │
       ├────────────────────────────────────────────►│
       │                                              │
       │                                         Verify password
       │                                         Generate JWT token
       │                                              │
       │ ◄────────────────────────────────────────────┤
       │    {access_token, user}                      │
       │                                              │
       │ 3. GET /api/dashboard                        │
       │    Authorization: Bearer <token>             │
       ├────────────────────────────────────────────►│
       │                                              │
       │                                         Decode JWT
       │                                         Validate token
       │                                         Get user from DB
       │                                              │
       │ ◄────────────────────────────────────────────┤
       │    {user_data, message}                      │
       │                                              │
       │ 4. POST /api/auth/logout                     │
       ├────────────────────────────────────────────►│
       │                                              │
       │ ◄────────────────────────────────────────────┤
       │    {message: "delete token from client"}    │
       │                                              │
       │ Delete token from localStorage/sessionStorage│
       │                                              │
```

## 🛠️ Implementation Details

### 1. CRUD dengan Password

#### Create Siswa
```python
@app.post("/api/siswa/")
async def create_siswa(siswa: SiswaCreate, db: Session = Depends(get_db)):
    # Hash password
    hashed_password = hash_password(siswa.password)
    
    # Save to database
    db_siswa = Siswa(
        nama=siswa.nama,
        email=siswa.email,
        password=hashed_password  # 👈 Save hash, bukan plain
    )
    
    db.add(db_siswa)
    db.commit()
    return db_siswa
```

#### Update Siswa (dengan optional password)
```python
@app.put("/api/siswa/{siswa_id}")
async def update_siswa(siswa_id: int, siswa_update: SiswaUpdate):
    siswa.nama = siswa_update.nama
    siswa.email = siswa_update.email
    
    # Update password hanya jika ada
    if siswa_update.password:
        siswa.password = hash_password(siswa_update.password)
    
    db.commit()
    return siswa
```

### 2. Login dengan JWT

```python
@app.post("/api/auth/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find user by email
    siswa = db.query(Siswa).filter(Siswa.email == credentials.email).first()
    
    if not siswa:
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    # 2. Verify password
    if not verify_password(credentials.password, siswa.password):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    # 3. Generate JWT token
    access_token = create_access_token(data={"sub": siswa.email})
    
    # 4. Return response
    return LoginResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user={"id": siswa.id, "nama": siswa.nama, "email": siswa.email}
    )
```

### 3. JWT Middleware

```python
@app.middleware("http")
async def jwt_auth_middleware(request: Request, call_next):
    # List protected endpoints
    protected_paths = ["/api/dashboard"]
    
    if request.url.path in protected_paths:
        # Extract token from header
        auth_header = request.headers.get("Authorization")
        token = extract_bearer_token(auth_header)
        
        if not token:
            return JSONResponse(status_code=401, content={"detail": "No token"})
        
        # Decode and validate token
        payload = decode_access_token(token)
        
        if not payload:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        
        # Get user from database
        email = payload.get("sub")
        siswa = db.query(Siswa).filter(Siswa.email == email).first()
        
        if not siswa:
            return JSONResponse(status_code=401, content={"detail": "User not found"})
        
        # Save user to request.state
        request.state.user = {
            "id": siswa.id,
            "nama": siswa.nama,
            "email": siswa.email
        }
    
    # Continue to endpoint
    response = await call_next(request)
    return response
```

## 🧪 Testing

### 1. Run Server
```bash
uvicorn main:app --reload
```

### 2. Run Tests
```bash
python test_jwt.py
```

### 3. Manual Testing with curl

#### Register
```bash
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Content-Type: application/json" \
  -d '{"nama":"Edy Cole","email":"edycoleee@gmail.com","password":"secret123"}'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"edycoleee@gmail.com","password":"secret123"}'
```

#### Save token
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"edycoleee@gmail.com","password":"secret123"}' \
  | jq -r '.access_token')
```

#### Access protected endpoint
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard
```

## ⚠️ Important Notes

### 1. Token Expiration
- Default: 30 minutes
- Setelah expire, user harus login ulang
- Bisa customize di `auth_utils.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Ubah sesuai kebutuhan
```

### 2. Secret Key
- Secret key untuk signing JWT
- **WAJIB** diganti di production!
- Generate dengan:
```bash
openssl rand -hex 32
```

### 3. Logout
- JWT adalah stateless (server tidak menyimpan session)
- Logout dilakukan di client-side dengan menghapus token
- Untuk blacklist token di server, perlu Redis/database

### 4. Password Requirements
- Minimum 6 karakter (bisa diubah di schemas)
- Sebaiknya tambahkan validation:
  - Minimal 1 huruf besar
  - Minimal 1 angka
  - Minimal 1 special character

### 5. Security Best Practices
- ✅ Password di-hash dengan bcrypt
- ✅ JWT token untuk authentication
- ✅ HTTPS untuk production (wajib!)
- ✅ CORS configuration
- ⚠️ Rate limiting untuk login endpoint
- ⚠️ Account lockout after failed attempts
- ⚠️ Password reset mechanism

## 📊 Database Changes

Old schema:
```sql
CREATE TABLE siswa (
    id INTEGER PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);
```

New schema:
```sql
CREATE TABLE siswa (
    id INTEGER PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL  -- Added
);
```

**Note:** Database lama harus di-drop atau migrate!

## 🎯 Next Steps

1. **Refresh Token**: Implement refresh token mechanism
2. **Password Reset**: Add forgot password feature
3. **Email Verification**: Send verification email
4. **OAuth**: Add Google/Facebook login
5. **Role-Based Access**: Add user roles (admin, user)
6. **Token Blacklist**: Implement token revocation with Redis
7. **Rate Limiting**: Add rate limiting for login endpoint
8. **Audit Log**: Track login attempts and activities

## 📖 References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/)
- [Passlib Documentation](https://passlib.readthedocs.io/)
- [Python-JOSE](https://python-jose.readthedocs.io/)
