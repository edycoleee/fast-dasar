# 🔐 JWT Authentication - Quick Start

## ✅ Implementation Completed!

Semua requirement JWT authentication sudah diimplementasikan:

1. ✅ **Password field** - Ditambahkan ke model Siswa dengan hashing bcrypt
2. ✅ **CRUD dengan password** - Create & Update siswa dengan password
3. ✅ **Tabel auth** - Menggunakan tabel siswa untuk authentication
4. ✅ **Login email/password** - Login dengan email dan password (bukan username)
5. ✅ **Generate JWT** - JWT token generation dengan python-jose
6. ✅ **Dashboard dengan JWT** - Protected endpoint `/api/dashboard` dengan JWT middleware
7. ✅ **Logout** - Endpoint logout

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install --break-system-packages python-jose[cryptography] passlib[bcrypt]
```

### 2. Start Server
```bash
# Remove old database (karena ada perubahan schema)
rm -f siswa_orm.db

# Start server
uvicorn main:app --reload
```

Server akan running di: http://localhost:8000

### 3. Test dengan Script
```bash
# Option 1: Bash script (pakai curl dan jq)
bash test_jwt.sh

# Option 2: Python script (pakai requests)
python test_jwt.py
```

### 4. Test Manual

#### Register Siswa Baru
```bash
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Edy Cole",
    "email": "edycoleee@gmail.com",
    "password": "secret123"
  }'
```

Response:
```json
{
  "id": 1,
  "nama": "Edy Cole",
  "email": "edycoleee@gmail.com"
}
```
**Note:** Password TIDAK muncul di response (security)

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "edycoleee@gmail.com",
    "password": "secret123"
  }'
```

Response:
```json
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

#### Save Token
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"edycoleee@gmail.com","password":"secret123"}' \
  | jq -r '.access_token')
```

#### Access Protected Endpoint
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard
```

Response:
```json
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
```

#### Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout
```

## 📁 Files Modified/Created

### Modified Files:
- ✅ `db_sqlalchemy.py` - Added password column to Siswa model
- ✅ `schemas.py` - Updated schemas with password field
- ✅ `main.py` - Implemented JWT authentication
- ✅ `requirements.txt` - Added JWT dependencies

### New Files:
- ✅ `auth_utils.py` - Password hashing & JWT utilities
- ✅ `test_jwt.py` - Python test script
- ✅ `test_jwt.sh` - Bash test script
- ✅ `JWT_GUIDE.md` - Comprehensive documentation
- ✅ `JWT_QUICKSTART.md` - This file

## 🔑 Key Features

### 1. Password Security
- Password di-hash dengan **bcrypt** (bukan plain text)
- Hash: `$2b$12$KIXn0q4z...` (60 characters)
- Automatic salt generation
- Password tidak pernah muncul di response

### 2. JWT Token
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Expiration:** 30 minutes (configurable)
- **Payload:** `{"sub": "user@example.com", "exp": 1234567890}`
- **Format:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 3. Protected Endpoints
Endpoints yang **memerlukan JWT**:
- `GET /api/dashboard` ✅
- `POST /api/siswa/` ✅
- `PUT /api/siswa/{id}` ✅
- `DELETE /api/siswa/{id}` ✅

Endpoints **public** (tidak perlu JWT):
- `POST /api/auth/login` 🌐
- `GET /api/siswa/` 🌐
- `GET /api/siswa/{id}` 🌐

### 4. Middleware
- **JWT Middleware** - Auto-check JWT untuk protected endpoints
- Extract token dari `Authorization: Bearer <token>`
- Decode & validate token
- Query user dari database
- Save user info di `request.state.user`

## 🔄 Authentication Flow

```
1. Register
   POST /api/siswa/ {nama, email, password}
   → Password di-hash dengan bcrypt
   → Save to database
   
2. Login
   POST /api/auth/login {email, password}
   → Verify email
   → Verify password dengan hash
   → Generate JWT token
   → Return token + user info
   
3. Access Protected Endpoint
   GET /api/dashboard
   Headers: Authorization: Bearer <token>
   → Middleware extract token
   → Decode & validate token
   → Get user from database
   → Allow access
   
4. Logout
   POST /api/auth/logout
   → Client delete token from storage
   → Server tidak perlu track (stateless)
```

## 📊 API Documentation

Buka browser: http://localhost:8000/docs

Swagger UI akan menampilkan semua endpoints dengan:
- Request/Response schemas
- Try it out functionality
- Authentication support (klik Authorize 🔒)

## 🧪 Test Results

Expected output dari `test_jwt.sh`:
```
✅ Server is running
✅ Registration successful
✅ Login successful
✅ JWT token generated
✅ Wrong password rejected
✅ Access denied without token
✅ Dashboard accessed with token
✅ Total siswa: 1
✅ Logout endpoint called
```

## ⚠️ Important Notes

### 1. Database Schema Changed
**Old:**
```sql
CREATE TABLE siswa (
    id INTEGER PRIMARY KEY,
    nama VARCHAR(100),
    email VARCHAR(100) UNIQUE
);
```

**New:**
```sql
CREATE TABLE siswa (
    id INTEGER PRIMARY KEY,
    nama VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255)  -- Added
);
```

**Action:** Delete old database atau migrate
```bash
rm -f siswa_orm.db
```

### 2. Secret Key
- Default secret key untuk development
- **WAJIB diganti** di production!
- Generate new secret:
```bash
openssl rand -hex 32
```

Update di `auth_utils.py`:
```python
SECRET_KEY = "your-new-secret-key-here"
```

### 3. Token Expiration
- Default: 30 minutes
- Setelah expire, user harus login ulang
- Configure di `auth_utils.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### 4. HTTPS Required
- JWT token harus dikirim via HTTPS di production
- HTTP hanya untuk development
- Token bisa di-intercept di HTTP (security risk)

### 5. CORS
- Frontend dari domain lain perlu CORS enabled
- Sudah dikonfigurasi di `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 Next Steps

### Recommended Improvements:
1. **Refresh Token** - Implement refresh token untuk auto-renew
2. **Password Reset** - Forgot password dengan email verification
3. **Email Verification** - Verify email setelah register
4. **Role-Based Access** - Add user roles (admin, user, guest)
5. **Rate Limiting** - Limit login attempts (prevent brute force)
6. **Token Blacklist** - Revoke tokens dengan Redis
7. **OAuth** - Add Google/Facebook login
8. **Audit Log** - Track login attempts dan activities
9. **Password Requirements** - Enforce strong passwords
10. **Account Lockout** - Lock account after failed attempts

### Password Validation Example:
```python
import re

def validate_password(password: str) -> bool:
    """
    Password requirements:
    - Minimum 8 characters
    - At least 1 uppercase
    - At least 1 lowercase
    - At least 1 number
    - At least 1 special character
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

## 📚 Documentation

- 📘 **JWT_GUIDE.md** - Comprehensive documentation
- 📗 **JWT_QUICKSTART.md** - This quick start guide
- 📙 **Swagger UI** - http://localhost:8000/docs
- 📕 **ReDoc** - http://localhost:8000/redoc

## 🆘 Troubleshooting

### Error: "Missing or invalid Authorization header"
**Solution:** Include `Authorization: Bearer <token>` header
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard
```

### Error: "Invalid or expired token"
**Solution:** Token expired atau invalid, login ulang
```bash
# Get new token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"edycoleee@gmail.com","password":"secret123"}' \
  | jq -r '.access_token')
```

### Error: "Email atau password salah"
**Solution:** Check email & password
- Email harus yang sudah register
- Password case-sensitive
- Password harus minimal 6 karakter

### Error: "Email sudah digunakan"
**Solution:** Email sudah terdaftar, gunakan email lain atau login
```bash
# Login dengan email existing
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"edycoleee@gmail.com","password":"secret123"}'
```

### Database Error
**Solution:** Delete database dan restart server
```bash
rm -f siswa_orm.db
uvicorn main:app --reload
```

## 💡 Tips

1. **Save token** di environment variable untuk testing:
```bash
export JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -H "Authorization: Bearer $JWT_TOKEN" http://localhost:8000/api/dashboard
```

2. **Decode JWT** untuk debug (jwt.io):
```bash
echo $TOKEN | pbcopy  # Copy to clipboard
# Paste di https://jwt.io/
```

3. **Check token expiration**:
```bash
# Decode payload (base64)
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq '.'
```

4. **Auto-format JSON** dengan jq:
```bash
curl -s http://localhost:8000/api/siswa/ | jq '.'
```

## 🎉 Success!

JWT Authentication berhasil diimplementasikan dengan fitur:
- ✅ Secure password hashing (bcrypt)
- ✅ JWT token generation & validation
- ✅ Protected endpoints dengan middleware
- ✅ Login dengan email & password
- ✅ Logout endpoint
- ✅ Comprehensive documentation
- ✅ Test scripts (Python & Bash)

**Happy coding!** 🚀
