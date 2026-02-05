# 🚀 Quick Reference: Login & Auth Middleware

## Credentials
```
Username: admin
Password: admin
Token: 123456
```

---

## 🔑 Endpoints

### 1. Login (Public)
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}

# Response:
{
  "message": "Login successful",
  "token": "123456",
  "username": "admin"
}
```

### 2. Landing (Protected)
```bash
GET /api/landing
Authorization: Bearer 123456

# Response:
{
  "message": "Welcome to the landing page!",
  "user": {
    "username": "admin",
    "role": "administrator",
    "authenticated_at": "2026-02-05"
  }
}
```

---

## 💻 Curl Commands

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Access Protected (SUCCESS)
curl -H "Authorization: Bearer 123456" \
  http://localhost:8000/api/landing

# Without token (FAIL - 401)
curl http://localhost:8000/api/landing

# Wrong token (FAIL - 401)
curl -H "Authorization: Bearer wrong" \
  http://localhost:8000/api/landing
```

---

## 🐍 Python Requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "admin", "password": "admin"}
)
token = response.json()["token"]

# Access protected endpoint
response = requests.get(
    "http://localhost:8000/api/landing",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```

---

## 🔄 Authentication Flow

```
┌────────┐
│ Client │
└───┬────┘
    │
    │ 1. POST /api/auth/login
    │    {username, password}
    │
    ▼
┌────────────┐
│   Login    │ ─── Check: admin/admin?
│  Endpoint  │
└─────┬──────┘
      │
      │ 2. Return {token: "123456"}
      │
      ▼
┌────────┐
│ Client │ ─── Store token
└───┬────┘
    │
    │ 3. GET /api/landing
    │    Header: Bearer 123456
    │
    ▼
┌─────────────┐
│ Middleware  │ ─── Check token valid?
│ (BEFORE     │
│  endpoint)  │
└─────┬───────┘
      │
      │ 4. Set request.state.user
      │
      ▼
┌─────────────┐
│  Landing    │ ─── Access request.state.user
│  Endpoint   │
└─────┬───────┘
      │
      │ 5. Return {message, user}
      │
      ▼
┌────────┐
│ Client │
└────────┘
```

---

## 🎯 Middleware Code Pattern

```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # 1. Check if protected
    if request.url.path in protected_paths:
        
        # 2. Get token
        auth = request.headers.get("Authorization")
        
        # 3. Validate format
        if not auth or not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, ...)
        
        # 4. Validate token
        token = auth.replace("Bearer ", "")
        if token != "123456":
            return JSONResponse(status_code=401, ...)
        
        # 5. Store user
        request.state.user = {...}
    
    # 6. Continue
    return await call_next(request)
```

---

## 📊 Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | ✅ OK | Login success, landing success |
| 401 | ❌ Unauthorized | Wrong password, invalid token, missing token |
| 404 | ❌ Not Found | Endpoint doesn't exist |

---

## 🧪 Testing Checklist

- [ ] Start server: `uvicorn main:app --reload`
- [ ] Login dengan credentials benar → Get token
- [ ] Login dengan password salah → 401 error
- [ ] Access landing tanpa token → 401 error
- [ ] Access landing dengan token salah → 401 error
- [ ] Access landing dengan token benar → Success
- [ ] Check `request.state.user` di response
- [ ] Run `python test_auth.py` untuk auto test

---

## 🔧 How to Modify

### Tambah Protected Endpoint
```python
# 1. Add to protected_paths in middleware
protected_paths = ["/api/landing", "/api/profile"]

# 2. Create endpoint
@app.get("/api/profile")
async def profile(request: Request):
    user = request.state.user
    return {"profile": user}
```

### Tambah User Baru
```python
@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    # Check multiple users
    if credentials.username == "admin" and credentials.password == "admin":
        return {"token": "123456", "username": "admin"}
    elif credentials.username == "user" and credentials.password == "user123":
        return {"token": "654321", "username": "user"}
    else:
        raise HTTPException(401, "Invalid credentials")
```

### Store Different User Data
```python
# In middleware
request.state.user = {
    "username": "admin",
    "role": "administrator",
    "email": "admin@example.com",
    "permissions": ["read", "write", "delete"]
}
```

---

## 📚 Files Created

1. **main.py** - Login endpoint, landing endpoint, auth middleware
2. **schemas.py** - LoginRequest, LoginResponse schemas
3. **LOGIN_TUTORIAL.md** - Full tutorial & explanation
4. **test_auth.py** - Automated testing script
5. **AUTH_QUICKREF.md** - This quick reference

---

## 🎓 Next: Upgrade to JWT

Current vs JWT:

| Feature | Current (Simple) | JWT (Next) |
|---------|-----------------|------------|
| Token | `"123456"` | `"eyJhbGc..."` |
| Security | Low (hardcoded) | High (encrypted) |
| Expiration | No | Yes (exp claim) |
| User info | In server state | In token payload |
| Validation | String compare | Signature verify |

---

## 🚀 Quick Start

```bash
# 1. Start server
uvicorn main:app --reload

# 2. Open browser
http://localhost:8000/docs

# 3. Test login
# 4. Copy token: 123456
# 5. Click "Authorize" button
# 6. Input: Bearer 123456
# 7. Test /api/landing endpoint
```

---

**Happy Learning! 🎉**
