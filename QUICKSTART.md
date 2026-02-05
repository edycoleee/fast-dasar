# ⚡ Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies (1 min)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Application (30 sec)
```bash
uvicorn main:app --reload
```

Application running at: **http://localhost:8000**

### 3. Open API Docs (30 sec)
Visit: **http://localhost:8000/docs**

### 4. Create Admin User (1 min)
Di Swagger UI, gunakan endpoint `POST /api/v1/users/`:
```json
{
  "nama": "Admin User",
  "email": "admin@test.com",
  "password": "admin123",
  "role": "admin"
}
```

### 5. Login (1 min)
Gunakan endpoint `POST /api/v1/auth/login`:
```json
{
  "email": "admin@test.com",
  "password": "admin123"
}
```

Copy `access_token` dari response.

### 6. Test Protected Endpoint (1 min)
Click "Authorize" button di Swagger UI, paste token: `Bearer <your_token>`

Test endpoint `GET /api/v1/auth/dashboard`

## ✅ Done!

You now have:
- ✅ JWT Authentication working
- ✅ Admin user created
- ✅ Token-based access
- ✅ Protected endpoints

## 📚 Next Steps

1. Read [README.md](README.md) for full documentation
2. Explore [CLEAN_ARCHITECTURE.md](CLEAN_ARCHITECTURE.md)
3. Check [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) if migrating from old code
4. Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## 🧪 Quick Test Script

```bash
python test_clean_architecture.py
```

## 🐳 Docker (Alternative)

```bash
docker-compose up -d
```

---

**Happy Coding! 🎉**
