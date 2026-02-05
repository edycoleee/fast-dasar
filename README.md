# 🚀 FastAPI Clean Architecture - JWT & RBAC

Aplikasi FastAPI dengan **Clean Architecture** yang mengimplementasikan JWT Authentication dan Role-Based Access Control (RBAC).

## ✨ Fitur

### Authentication & Authorization
- ✅ **JWT Authentication** - Token-based authentication dengan expiry
- ✅ **Password Hashing** - Bcrypt untuk keamanan password
- ✅ **Role-Based Access Control (RBAC)** - Admin & User roles
- ✅ **Protected Endpoints** - Endpoint yang memerlukan authentication

### Role Permissions
- **Admin**: Full CRUD + Manage user roles
- **User**: Create, Read, Update (No Delete)

### Architecture
- ✅ **Clean Architecture** - Separation of concerns
- ✅ **Modular Design** - Easy to maintain and scale
- ✅ **Type Safety** - Pydantic schemas untuk validation
- ✅ **Docker Ready** - Containerization support
- ✅ **Auto Documentation** - Swagger & ReDoc

## 🛠️ Teknologi

- **FastAPI** 0.109.0 - Modern web framework
- **SQLAlchemy** 2.0.25 - ORM untuk database
- **Pydantic** 2.5.3 - Data validation
- **Pydantic Settings** 2.12.0 - Configuration management
- **python-jose** 3.3.0 - JWT token generation & validation
- **passlib** 1.7.4 - Password hashing
- **bcrypt** - Hashing algorithm
- **SQLite** - Database (production-ready untuk PostgreSQL)

## 📁 Struktur Folder

```
fast-dasar/
├── app/                          # Main application
│   ├── api/                      # API endpoints
│   │   └── v1/
│   │       ├── endpoints/        # Route handlers
│   │       │   ├── auth.py       # Login, logout, dashboard
│   │       │   ├── users.py      # User CRUD
│   │       │   └── admin.py      # Admin operations
│   │       └── api.py            # Router aggregation
│   │
│   ├── core/                     # Core functionality
│   │   ├── config.py             # Settings & configuration
│   │   ├── security.py           # JWT & password hashing
│   │   ├── deps.py               # Dependencies (DB, auth)
│   │   └── authorization.py      # RBAC utilities
│   │
│   ├── db/                       # Database
│   │   ├── base.py               # SQLAlchemy setup
│   │   └── session.py            # Session management
│   │
│   ├── models/                   # SQLAlchemy models
│   │   └── user.py               # User model
│   │
│   ├── schemas/                  # Pydantic schemas
│   │   ├── user.py               # User schemas
│   │   └── auth.py               # Auth schemas
│   │
│   ├── services/                 # Business logic
│   │   ├── user_service.py       # User operations
│   │   └── auth_service.py       # Authentication
│   │
│   └── middleware/               # Middleware
│       └── jwt_middleware.py     # JWT validation
│
├── main.py                       # Application entry point
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose
└── test_clean_architecture.py   # API tests
```

## 📦 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd fast-dasar
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment
```bash
cp .env.example .env
# Edit .env sesuai kebutuhan
```

## 🚀 Menjalankan Aplikasi

### Development Mode
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Aplikasi akan berjalan di: **http://localhost:8000**

## 📚 API Documentation

Setelah aplikasi berjalan, akses dokumentasi interaktif:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### Authentication
```
POST   /api/v1/auth/login      # Login (get JWT token)
POST   /api/v1/auth/logout     # Logout
GET    /api/v1/auth/dashboard  # Protected dashboard
```

#### Users (Requires Auth)
```
GET    /api/v1/users/          # Get all users
GET    /api/v1/users/{id}      # Get user by ID
POST   /api/v1/users/          # Create user
PUT    /api/v1/users/{id}      # Update user
DELETE /api/v1/users/{id}      # Delete user (Admin only)
```

#### Admin (Admin Only)
```
PATCH  /api/v1/admin/{id}/role # Update user role
```

## 🧪 Testing

### Manual Testing
```bash
# Pastikan server berjalan
python test_clean_architecture.py
```

### Menggunakan curl

1. **Create admin user** (first time):
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Admin User",
    "email": "admin@test.com",
    "password": "admin123",
    "role": "admin"
  }'
```

2. **Login untuk mendapatkan token**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin123"
  }'
```

3. **Akses protected endpoint**:
```bash
curl http://localhost:8000/api/v1/auth/dashboard \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

## 🐳 Docker

### Build dan Run dengan Docker
```bash
# Build image
docker build -t fastapi-clean .

# Run container
docker run -p 8000:8000 fastapi-clean
```

### Menggunakan Docker Compose
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

## 🔐 Environment Variables

File `.env.example` sudah disediakan. Copy dan sesuaikan:

```env
# Database
DATABASE_URL=sqlite:///./app/siswa.db

# JWT Settings  
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# App Settings
PROJECT_NAME=FastAPI JWT RBAC
VERSION=1.0.0
API_V1_PREFIX=/api/v1
```

## 🏗️ Clean Architecture Layers

1. **API Layer** (`app/api/`) - HTTP requests & responses
2. **Services Layer** (`app/services/`) - Business logic
3. **Models Layer** (`app/models/`) - Database models
4. **Schemas Layer** (`app/schemas/`) - Validation
5. **Core Layer** (`app/core/`) - Configuration & utilities
6. **Database Layer** (`app/db/`) - Database connection

Lihat [CLEAN_ARCHITECTURE.md](CLEAN_ARCHITECTURE.md) untuk penjelasan lengkap.

## 📝 Dokumentasi Tambahan

- [CLEAN_ARCHITECTURE.md](CLEAN_ARCHITECTURE.md) - Penjelasan arsitektur lengkap
- [AUTH_QUICKREF.md](AUTH_QUICKREF.md) - Quick reference JWT auth
- [AUTHORIZATION_GUIDE.md](AUTHORIZATION_GUIDE.md) - RBAC implementation guide

## 🎯 Quick Start

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run
uvicorn main:app --reload

# 3. Access docs
# Open http://localhost:8000/docs

# 4. Create admin (via Swagger UI or curl)
# 5. Login and get token
# 6. Use token untuk akses protected endpoints
```

## 👨‍💻 Development

Lihat dokumentasi lengkap di [CLEAN_ARCHITECTURE.md](CLEAN_ARCHITECTURE.md) untuk:
- Menambah endpoint baru
- Menambah model baru
- Menambah middleware
- Best practices
- Testing guidelines

---

Made with ❤️ using FastAPI & Clean Architecture
