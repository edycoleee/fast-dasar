# 🔐 Authorization Quick Reference

## 🎯 Roles & Permissions

| Feature | Admin | User |
|---------|-------|------|
| Create siswa (any role) | ✅ | ❌ (forced to user) |
| Create siswa (role=user) | ✅ | ✅ |
| Read siswa | ✅ | ✅ |
| Update siswa | ✅ | ✅ |
| **Delete siswa** | ✅ | ❌ 403 |
| **View all users** | ✅ | ❌ 403 |
| **Change user roles** | ✅ | ❌ 403 |
| Access dashboard | ✅ | ✅ |

## 🚀 Quick Setup

```bash
# 1. Remove old database
rm -f siswa_orm.db

# 2. Start server
uvicorn main:app --reload

# 3. Create first admin
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Content-Type: application/json" \
  -d '{"nama":"Admin","email":"admin@example.com","password":"admin123","role":"admin"}'

# 4. Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq -r '.access_token')

# 5. Create user
curl -X POST http://localhost:8000/api/siswa/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nama":"User","email":"user@example.com","password":"user123","role":"user"}'

# 6. Login as user
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user123"}' | jq -r '.access_token')
```

## 📝 Common Operations

### Admin: Delete Siswa ✅
```bash
curl -X DELETE http://localhost:8000/api/siswa/3 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### User: Try Delete Siswa ❌ (403)
```bash
curl -X DELETE http://localhost:8000/api/siswa/3 \
  -H "Authorization: Bearer $USER_TOKEN"
# Response: {"detail": "Permission denied. Required role: admin. Your role: user"}
```

### Admin: View All Users ✅
```bash
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### User: Try View All Users ❌ (403)
```bash
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer $USER_TOKEN"
# Response: {"detail": "Permission denied..."}
```

### Admin: Change User Role ✅
```bash
# Promote to admin
curl -X PUT http://localhost:8000/api/users/2/role \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin"}'

# Demote to user
curl -X PUT http://localhost:8000/api/users/2/role \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"user"}'
```

### User: Try Change Role ❌ (403)
```bash
curl -X PUT http://localhost:8000/api/users/1/role \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin"}'
# Response: {"detail": "Permission denied..."}
```

## 🧪 Test

```bash
# Full test suite
python test_authorization.py
```

## 📂 Files

- `db_sqlalchemy.py` - Added `role` column
- `schemas.py` - Added role schemas
- `authorization.py` - NEW: Authorization utilities
- `main.py` - Added permission checks
- `test_authorization.py` - NEW: Test script
- `AUTHORIZATION_GUIDE.md` - Full documentation

## 🔑 Authorization Utilities

```python
from authorization import require_admin, require_role, get_current_user, Role

# In endpoint
@app.delete("/api/siswa/{id}")
async def delete_siswa(id: int, request: Request):
    require_admin(request)  # ⬅️ Only admin
    # ... delete logic

@app.get("/api/protected")
async def protected(request: Request):
    require_role(request, [Role.ADMIN, Role.USER])  # Admin or User
    # ... logic

@app.get("/api/me")
async def me(request: Request):
    user = get_current_user(request)  # Get current user
    return {"user": user}
```

## ⚠️ Important

1. **First user** can register without auth (becomes admin)
2. **User cannot create admin** - role forced to "user"
3. **Role in database** - not in JWT payload (instant effect on role change)
4. **Delete old database** - schema changed (added role column)

## 📊 API Endpoints

### Public (No Auth)
- `POST /api/auth/login`
- `GET /api/siswa/`
- `GET /api/siswa/{id}`

### Authenticated (Admin + User)
- `POST /api/siswa/` (user: role=user only)
- `PUT /api/siswa/{id}`
- `GET /api/dashboard`

### Admin Only
- `DELETE /api/siswa/{id}` 🔒
- `GET /api/users` 🔒
- `PUT /api/users/{id}/role` 🔒

## ✅ Success!

Authorization (RBAC) implemented with admin and user roles!
