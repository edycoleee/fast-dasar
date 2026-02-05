# 🔐 Authorization - Role-Based Access Control (RBAC)

## ✅ Implementation Summary

Implementasi RBAC dengan 2 role: **admin** dan **user**

### 🎯 Permissions

| Action | Admin | User |
|--------|-------|------|
| **CREATE siswa** | ✅ (any role) | ✅ (role=user only) |
| **READ siswa** | ✅ | ✅ |
| **UPDATE siswa** | ✅ | ✅ |
| **DELETE siswa** | ✅ | ❌ (403 Forbidden) |
| **VIEW all users** | ✅ | ❌ (403 Forbidden) |
| **CHANGE user roles** | ✅ | ❌ (403 Forbidden) |
| **ACCESS dashboard** | ✅ | ✅ |

## 📁 Files Modified/Created

### Modified Files:
1. **db_sqlalchemy.py** - Added `role` column
2. **schemas.py** - Added role to schemas + UpdateRoleRequest
3. **main.py** - Added authorization checks to endpoints

### New Files:
4. **authorization.py** - Authorization utilities (require_admin, require_role, etc)
5. **test_authorization.py** - Comprehensive test script

## 🏗️ Database Schema

```sql
CREATE TABLE siswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'  -- ⬅️ NEW
);
```

**Roles:**
- `admin` - Full access (CRUD + role management)
- `user` - Limited access (CRU only, no Delete)

## 🚀 Quick Start

### 1. Reset Database
```bash
# Remove old database (schema changed)
rm -f siswa_orm.db

# Start server
uvicorn main:app --reload
```

### 2. Create First Admin
```bash
# Register first admin (no auth needed for first user)
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Admin User",
    "email": "admin@example.com",
    "password": "admin123",
    "role": "admin"
  }'
```

### 3. Login as Admin
```bash
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.access_token')

echo "Admin Token: $ADMIN_TOKEN"
```

### 4. Create Regular User
```bash
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Regular User",
    "email": "user@example.com",
    "password": "user123",
    "role": "user"
  }'
```

### 5. Login as User
```bash
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user123"}' \
  | jq -r '.access_token')

echo "User Token: $USER_TOKEN"
```

## 🔑 Admin Features

### 1. Full CRUD Access

```bash
# CREATE (with any role)
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nama":"New User","email":"new@example.com","password":"pass123","role":"admin"}'

# READ
curl http://localhost:8000/api/siswa/

# UPDATE
curl -X PUT http://localhost:8000/api/siswa/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nama":"Updated","email":"updated@example.com"}'

# DELETE (only admin can do this)
curl -X DELETE http://localhost:8000/api/siswa/3 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 2. View All Users (Admin Only)

```bash
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Response:
```json
[
  {
    "id": 1,
    "nama": "Admin User",
    "email": "admin@example.com",
    "role": "admin"
  },
  {
    "id": 2,
    "nama": "Regular User",
    "email": "user@example.com",
    "role": "user"
  }
]
```

### 3. Change User Role (Admin Only)

```bash
# Promote user to admin
curl -X PUT http://localhost:8000/api/users/2/role \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin"}'

# Demote admin to user
curl -X PUT http://localhost:8000/api/users/2/role \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"user"}'
```

## 👤 User Features

### 1. Create Siswa (role=user only)

```bash
# User can create, but role will be forced to "user"
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nama":"New Siswa","email":"newsiswa@example.com","password":"pass123","role":"admin"}'
```

Response (role forced to "user"):
```json
{
  "id": 3,
  "nama": "New Siswa",
  "email": "newsiswa@example.com",
  "role": "user"  // ⬅️ Forced to user, even if requested admin
}
```

### 2. Read & Update Siswa

```bash
# READ (public)
curl http://localhost:8000/api/siswa/

# UPDATE
curl -X PUT http://localhost:8000/api/siswa/3 \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nama":"Updated Name","email":"newsiswa@example.com"}'
```

### 3. DELETE Siswa (FORBIDDEN for user)

```bash
curl -X DELETE http://localhost:8000/api/siswa/3 \
  -H "Authorization: Bearer $USER_TOKEN"
```

Response (403 Forbidden):
```json
{
  "detail": "Permission denied. Required role: admin. Your role: user"
}
```

### 4. View All Users (FORBIDDEN for user)

```bash
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer $USER_TOKEN"
```

Response (403 Forbidden):
```json
{
  "detail": "Permission denied. Required role: admin. Your role: user"
}
```

### 5. Change Role (FORBIDDEN for user)

```bash
curl -X PUT http://localhost:8000/api/users/2/role \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin"}'
```

Response (403 Forbidden):
```json
{
  "detail": "Permission denied. Required role: admin. Your role: user"
}
```

## 🛡️ Authorization Flow

```
┌─────────────────────────────────────────────────────────┐
│              AUTHORIZATION CHECK FLOW                    │
└─────────────────────────────────────────────────────────┘

1️⃣ Request dengan JWT Token
   ┌────────────────────────────────────────────┐
   │ DELETE /api/siswa/3                        │
   │ Authorization: Bearer <jwt_token>          │
   └────────────────────────────────────────────┘
                    ↓

2️⃣ JWT Middleware
   ┌────────────────────────────────────────────┐
   │ - Extract & validate token                │
   │ - Get user from database                  │
   │ - Set request.state.user = {              │
   │     id: 1,                                │
   │     email: "user@example.com",           │
   │     role: "user"  ⬅️ Include role        │
   │   }                                       │
   └────────────────────────────────────────────┘
                    ↓

3️⃣ Endpoint Handler
   ┌────────────────────────────────────────────┐
   │ @app.delete("/api/siswa/{siswa_id}")      │
   │ async def delete_siswa(..., request):     │
   │                                           │
   │   # Check permission                     │
   │   require_admin(request)  ⬅️ Check role  │
   │   ...                                    │
   └────────────────────────────────────────────┘
                    ↓

4️⃣ Authorization Check (authorization.py)
   ┌────────────────────────────────────────────┐
   │ def require_admin(request):               │
   │   user = get_current_user(request)       │
   │   # user["role"] = "user"                │
   │                                           │
   │   if user["role"] != "admin":            │
   │     ❌ raise 403 Forbidden               │
   └────────────────────────────────────────────┘
                    ↓

5️⃣ Response
   ┌────────────────────────────────────────────┐
   │ Status: 403 Forbidden                     │
   │ {                                         │
   │   "detail": "Permission denied.           │
   │              Required role: admin.        │
   │              Your role: user"             │
   │ }                                         │
   └────────────────────────────────────────────┘
```

## 🔧 Authorization Utilities

### authorization.py Functions

```python
from authorization import require_admin, require_role, get_current_user, Role

# 1. Get current user
user = get_current_user(request)
# Returns: {"id": 1, "nama": "...", "email": "...", "role": "user"}

# 2. Require admin role
require_admin(request)
# Raises 403 if not admin

# 3. Require specific role(s)
require_role(request, [Role.ADMIN])  # Admin only
require_role(request, [Role.ADMIN, Role.USER])  # Admin or User

# 4. Check if admin
if is_admin(request):
    # Do admin stuff
    pass

# 5. Check owner or admin
if is_owner_or_admin(request, resource_user_id):
    # Allow access
    pass
```

### Usage in Endpoints

```python
@app.delete("/api/siswa/{siswa_id}")
async def delete_siswa(siswa_id: int, request: Request, db: Session = Depends(get_db)):
    # Check permission
    require_admin(request)  # ⬅️ Only admin can delete
    
    # ... delete logic
```

## 🧪 Testing

### Run Full Test Suite
```bash
python test_authorization.py
```

### Manual Testing

```bash
# 1. Create admin
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Content-Type: application/json" \
  -d '{"nama":"Admin","email":"admin@example.com","password":"admin123","role":"admin"}'

# 2. Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq -r '.access_token')

# 3. Create user
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nama":"User","email":"user@example.com","password":"user123","role":"user"}'

# 4. Login as user
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user123"}' | jq -r '.access_token')

# 5. Test admin delete (should work)
curl -X DELETE http://localhost:8000/api/siswa/3 \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 6. Test user delete (should fail 403)
curl -X DELETE http://localhost:8000/api/siswa/2 \
  -H "Authorization: Bearer $USER_TOKEN"
```

## 📊 API Endpoints

### Public Endpoints (No Auth)
- `POST /api/auth/login` - Login
- `GET /api/siswa/` - Read all siswa
- `GET /api/siswa/{id}` - Read one siswa

### Authenticated Endpoints (Admin + User)
- `POST /api/siswa/` - Create siswa (user: role=user, admin: any role)
- `PUT /api/siswa/{id}` - Update siswa
- `GET /api/dashboard` - Access dashboard

### Admin Only Endpoints
- `DELETE /api/siswa/{id}` - Delete siswa
- `GET /api/users` - View all users
- `PUT /api/users/{id}/role` - Change user role

## ⚠️ Important Notes

### 1. First User Registration
Pertama kali aplikasi dijalankan, user pertama bisa register tanpa auth. Sebaiknya:
- Buat admin pertama via seeder/migration
- Atau disable public registration setelah admin pertama dibuat

### 2. Role Enforcement
User biasa **tidak bisa** set `role=admin` saat create siswa. Role akan di-force ke `user`:

```python
# In create_siswa endpoint
if current_user.get("role") != Role.ADMIN:
    siswa.role = "user"  # Force to user
```

### 3. Database Migration
Jika upgrade dari versi sebelumnya, database lama tidak punya column `role`. Solusi:
```bash
# Option 1: Delete database (development)
rm -f siswa_orm.db

# Option 2: Migrate (production)
# Add migration script to add role column with default 'user'
```

### 4. Role in JWT Token
Role disimpan di `request.state.user` (bukan di JWT token payload). JWT hanya simpan `email`:

```python
# JWT payload
{"sub": "user@example.com", "exp": 1234567890}

# request.state.user (from database)
{"id": 1, "email": "user@example.com", "role": "user"}
```

Keuntungan: Role change langsung aktif tanpa perlu re-login.

## 🎯 Best Practices

### 1. Always Check Permission
```python
# ❌ BAD: No permission check
@app.delete("/api/siswa/{id}")
async def delete_siswa(id: int):
    # Anyone can delete!
    ...

# ✅ GOOD: Check permission
@app.delete("/api/siswa/{id}")
async def delete_siswa(id: int, request: Request):
    require_admin(request)  # Only admin
    ...
```

### 2. Use Type-Safe Role Constants
```python
from authorization import Role

# ✅ GOOD: Type-safe
require_role(request, [Role.ADMIN])

# ❌ BAD: String typo risk
require_role(request, ["adnim"])  # Typo!
```

### 3. Explicit Permission Checks
```python
# ✅ GOOD: Clear and explicit
@app.delete("/api/siswa/{id}")
async def delete_siswa(id: int, request: Request):
    require_admin(request)
    ...

# ❌ BAD: Hidden in middleware (harder to debug)
# Middleware auto-checks all endpoints
```

### 4. Consistent Error Messages
```python
# ✅ GOOD: Helpful error message
HTTPException(
    status_code=403,
    detail=f"Permission denied. Required role: admin. Your role: {user_role}"
)

# ❌ BAD: Vague error
HTTPException(status_code=403, detail="Forbidden")
```

## 🔜 Next Steps

1. **Role Hierarchy** - Admin > Moderator > User
2. **Permissions** - Fine-grained permissions (create_user, delete_user, etc)
3. **Resource-Based Access** - User can only edit their own data
4. **Audit Log** - Track who did what
5. **Rate Limiting** - Different limits for admin vs user
6. **API Keys** - For service-to-service auth

## 📚 References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [RBAC Concepts](https://en.wikipedia.org/wiki/Role-based_access_control)
- [OAuth 2.0 Scopes](https://oauth.net/2/scope/)
