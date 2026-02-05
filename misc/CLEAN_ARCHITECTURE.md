# Clean Architecture - FastAPI dengan JWT & RBAC

Proyek ini menggunakan **Clean Architecture** untuk memudahkan maintenance dan development, khususnya untuk deployment dengan Docker Compose.

## 📁 Struktur Folder

```
fast-dasar/
├── app/                          # Main application folder
│   ├── __init__.py
│   ├── api/                      # API layer (routes/endpoints)
│   │   ├── __init__.py
│   │   └── v1/                   # API version 1
│   │       ├── __init__.py
│   │       ├── api.py            # Main API router
│   │       └── endpoints/        # Individual endpoint files
│   │           ├── __init__.py
│   │           ├── auth.py       # Authentication endpoints
│   │           ├── users.py      # User CRUD endpoints
│   │           └── admin.py      # Admin-only endpoints
│   │
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration (settings)
│   │   ├── security.py           # Security utils (JWT, password)
│   │   ├── deps.py               # Dependencies (DB, auth)
│   │   └── authorization.py      # RBAC utilities
│   │
│   ├── db/                       # Database layer
│   │   ├── __init__.py
│   │   ├── base.py               # Database setup
│   │   └── session.py            # Session management
│   │
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py               # User model
│   │
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py               # User schemas
│   │   └── auth.py               # Auth schemas
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py       # User business logic
│   │   └── auth_service.py       # Auth business logic
│   │
│   └── middleware/               # Middleware
│       ├── __init__.py
│       └── jwt_middleware.py     # JWT middleware (optional)
│
├── main.py                       # FastAPI app entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
└── .dockerignore                 # Docker ignore file
```

## 🏗️ Penjelasan Arsitektur

### 1. **Core Layer** (`app/core/`)
Layer inti yang berisi konfigurasi dan utilities:
- **config.py**: Centralized configuration dengan Pydantic Settings
- **security.py**: Password hashing & JWT token management
- **deps.py**: FastAPI dependencies (database session, authentication)
- **authorization.py**: Role-based access control (RBAC)

### 2. **Database Layer** (`app/db/`)
Layer database yang mengelola koneksi:
- **base.py**: SQLAlchemy engine, SessionLocal, Base class
- **session.py**: Database session exports

### 3. **Models Layer** (`app/models/`)
SQLAlchemy ORM models:
- **user.py**: User/Siswa model dengan kolom id, nama, email, password, role

### 4. **Schemas Layer** (`app/schemas/`)
Pydantic schemas untuk validasi:
- **user.py**: UserCreate, UserUpdate, UserResponse, UpdateRole
- **auth.py**: LoginRequest, LoginResponse, Token

### 5. **Services Layer** (`app/services/`)
Business logic layer:
- **user_service.py**: CRUD operations untuk user
- **auth_service.py**: Authentication logic (login, token creation)

### 6. **API Layer** (`app/api/`)
Routes/endpoints:
- **v1/endpoints/auth.py**: Login, logout, dashboard
- **v1/endpoints/users.py**: User CRUD (GET, POST, PUT, DELETE)
- **v1/endpoints/admin.py**: Admin-only operations (update role)
- **v1/api.py**: Router aggregation

### 7. **Middleware Layer** (`app/middleware/`)
Middleware untuk request processing:
- **jwt_middleware.py**: JWT validation middleware (optional)

## 🚀 Cara Menjalankan

### Lokal (tanpa Docker)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Jalankan aplikasi:
```bash
uvicorn main:app --reload
```

4. Akses dokumentasi API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Dengan Docker Compose

1. Build dan jalankan:
```bash
docker-compose up --build
```

2. Aplikasi akan berjalan di: http://localhost:8000

3. Stop aplikasi:
```bash
docker-compose down
```

## 🔐 Autentikasi & Autorisasi

### Roles:
- **Admin**: Full CRUD + manage user roles
- **User**: Create, Read, Update (no Delete)

### Flow:
1. Login: `POST /api/v1/auth/login`
2. Dapatkan JWT token
3. Gunakan token di header: `Authorization: Bearer <token>`
4. Akses protected endpoints

## 📊 Database

Database SQLite akan dibuat otomatis di `app/siswa.db` saat aplikasi pertama kali dijalankan.

Untuk production, gunakan PostgreSQL dengan mengubah `DATABASE_URL` di `.env`.

## 🛠️ Development Tips

### Menambah Endpoint Baru:
1. Buat file di `app/api/v1/endpoints/`
2. Definisikan router dan endpoints
3. Tambahkan ke `app/api/v1/api.py`

### Menambah Model Baru:
1. Buat model di `app/models/`
2. Buat schemas di `app/schemas/`
3. Buat service di `app/services/`
4. Buat endpoints di `app/api/v1/endpoints/`

### Menambah Middleware:
1. Buat middleware di `app/middleware/`
2. Register di `main.py` dengan `app.add_middleware()`

## 🐳 Docker Best Practices

Clean architecture ini memudahkan Docker deployment:
- Semua code di folder `/app`
- Configuration via environment variables
- Volume mounting untuk development
- Multi-stage builds ready
- Production-ready structure

## 📝 Testing

```bash
# Install testing dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 🔧 Configuration

Semua konfigurasi di `app/core/config.py` menggunakan Pydantic Settings:
- Environment variables dari `.env`
- Type-safe configuration
- Easy to override per environment

## 📚 Dependencies

Lihat `requirements.txt` untuk semua dependencies.

## 🎯 Keuntungan Clean Architecture

1. **Separation of Concerns**: Setiap layer punya tanggung jawab jelas
2. **Maintainability**: Mudah mencari dan memperbaiki code
3. **Testability**: Mudah untuk testing karena modular
4. **Scalability**: Mudah menambah fitur baru
5. **Docker-Ready**: Structure cocok untuk containerization
6. **Team Collaboration**: Developer bisa kerja parallel di layer berbeda

---

Made with ❤️ using FastAPI & Clean Architecture
