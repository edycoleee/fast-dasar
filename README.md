# Belajar FastAPI - Panduan Tahapan

## 🎯 Untuk Anda yang Sudah Familiar dengan Flask & Node.js

FastAPI adalah framework modern Python yang menggabungkan kecepatan Node.js dengan kemudahan Flask, plus type safety dan auto-documentation!

---

## 📚 Tahapan Belajar FastAPI

### **CRUD SQL dengan FastAPI, SQLite, & Pytest**

Pada tahap ini kita akan belajar membuat **CRUD API** yang proper dengan database SQLite, routing yang terstruktur, dan comprehensive testing.

---

## 🏗️ Arsitektur Project (Clean Architecture)

```
fast-dasar/
├── main.py                      # Entry point aplikasi (95 lines)
├── requirements.txt             # Dependencies
├── pytest.ini                   # Pytest configuration
│
├── 📚 Documentation
│   ├── ARCHITECTURE.md          # Architecture guide
│   ├── QUICK_START.md           # Developer quick start
│   ├── MIGRATION_REPORT.md      # Migration details
│   ├── COMPLETION_SUMMARY.md    # Project completion
│   └── DOCUMENTATION_INDEX.md   # Navigation guide
│
├── 📦 app/                      # Main application package
│   ├── __init__.py
│   ├── database.py              # Database operations (198 lines)
│   ├── models.py                # Pydantic models (79 lines)
│   └── api/v1/                  # API v1 implementation
│       ├── __init__.py
│       ├── api.py               # Router aggregator (13 lines)
│       └── endpoints/
│           ├── __init__.py
│           ├── halo.py          # Greeting endpoints (~80 lines)
│           └── siswa.py         # CRUD endpoints (~240 lines)
│
├── 🧪 tests/                    # Test package
│   ├── conftest.py              # Pytest setup
│   ├── test_main.py             # 14 integration tests
│   └── __init__.py
│
└── siswa.db                     # SQLite database (auto-created)
```

**Penjelasan:**
- `main.py` - Entry point aplikasi dengan lifespan setup
- `app/database.py` - Raw SQL queries untuk database operations
- `app/models.py` - Pydantic models untuk validasi request/response
- `app/api/v1/endpoints/` - Modular endpoint routers (halo, siswa)
- `app/api/v1/api.py` - Router aggregator dengan prefix `/api/v1`
- `tests/` - Comprehensive test cases (14 tests, semua passing)

---

## 🔀 Routing - Mengorganisir Endpoint API

### Konsep Routing di FastAPI

Routing adalah cara untuk **memetakan URL path ke handler function**. Ini similar dengan Flask routes dan Express routes.

```python
# FastAPI routing
@app.get("/api/siswa/")           # GET endpoint
async def get_all_siswa():
    pass

@app.post("/api/siswa/")          # POST endpoint
async def create_siswa(siswa: SiswaCreate):
    pass

@app.put("/api/siswa/{id}")       # PUT endpoint dengan path parameter
async def update_siswa(id: int, siswa: SiswaUpdate):
    pass

@app.delete("/api/siswa/{id}")    # DELETE endpoint
async def delete_siswa(id: int):
    pass
```

### HTTP Methods dan Semantik REST

| Method | Fungsi | Status Code Success | Contoh |
|--------|--------|-------------------|---------|
| **GET** | Baca data | 200 OK | `GET /api/siswa/` → list semua |
| **POST** | Tambah data baru | 201 Created | `POST /api/siswa/` → create baru |
| **PUT** | Update data lengkap | 200 OK | `PUT /api/siswa/1` → update ID 1 |
| **PATCH** | Update partial | 200 OK | `PATCH /api/siswa/1` → update fields tertentu |
| **DELETE** | Hapus data | 200 OK | `DELETE /api/siswa/1` → hapus ID 1 |

### Path Parameters vs Query Parameters

```python
# Path parameter - untuk mengidentifikasi resource
@app.get("/api/siswa/{siswa_id}")  # {siswa_id} adalah path parameter
async def get_siswa(siswa_id: int):
    # siswa_id diambil dari URL path
    pass

# Query parameter - untuk filter/sort/pagination
@app.get("/api/siswa/")
async def get_all_siswa(skip: int = 0, limit: int = 10):
    # ?skip=0&limit=10 adalah query parameters
    pass
```

**Perbedaan:**
- **Path parameter** (`:id`) - Required, identifikasi resource
- **Query parameter** (`?key=value`) - Optional, filter/sort/pagination

---

## 💾 Database - SQLite & Raw SQL

### Mengapa SQLite?

| Database | Use Case | Pros | Cons |
|----------|----------|------|------|
| **SQLite** | Development, Testing, Small apps | Simple, No setup, File-based | Limited concurrency |
| **PostgreSQL** | Production, Large apps | Powerful, Reliable | Need setup |
| **MongoDB** | NoSQL, Flexible schema | Flexible | Not relational |

Untuk pembelajaran, **SQLite perfect** karena:
- ✅ Tidak perlu install server terpisah
- ✅ Database adalah file: `siswa.db`
- ✅ Cukup kuat untuk production kecil/medium
- ✅ SQLite datang built-in di Python!

### Raw SQL vs ORM

**Raw SQL (yang kita gunakan):**
```python
query = "INSERT INTO siswa (nama, email) VALUES (?, ?)"
cursor.execute(query, (nama, email))
```

**ORM (SQLAlchemy):**
```python
siswa = Siswa(nama=nama, email=email)
db.add(siswa)
db.commit()
```

**Kapan pakai apa?**
- **Raw SQL**: Learning, simple queries, full control
- **ORM**: Complex relations, automatic migrations, less code

### Database Schema

```sql
-- Tabel siswa dengan constraints
CREATE TABLE siswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,                    -- Tidak boleh kosong
    email TEXT NOT NULL UNIQUE,            -- Unik, tidak boleh duplicate
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contoh data
INSERT INTO siswa (nama, email) VALUES ('Edy', 'edy@example.com');
INSERT INTO siswa (nama, email) VALUES ('Budi', 'budi@example.com');
```

### Database Operations di Code

**File: database.py**

```python
import sqlite3
from typing import List, Optional, Dict

DB_NAME = "siswa.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Return rows as dict
    return conn

def init_db():
    """Initialize database dengan schema"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_all_siswa() -> List[Dict]:
    """Read all siswa"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM siswa")
    siswa_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return siswa_list

def get_siswa_by_id(siswa_id: int) -> Optional[Dict]:
    """Read siswa by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM siswa WHERE id = ?", (siswa_id,))
    siswa = cursor.fetchone()
    conn.close()
    return dict(siswa) if siswa else None

def insert_siswa(nama: str, email: str) -> Dict:
    """Create new siswa"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO siswa (nama, email) VALUES (?, ?)",
        (nama, email)
    )
    conn.commit()
    
    # Get inserted data
    siswa_id = cursor.lastrowid
    siswa = get_siswa_by_id(siswa_id)
    conn.close()
    return siswa

def update_siswa(siswa_id: int, nama: str, email: str) -> bool:
    """Update siswa"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE siswa SET nama = ?, email = ? WHERE id = ?",
        (nama, email, siswa_id)
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def delete_siswa(siswa_id: int) -> bool:
    """Delete siswa"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM siswa WHERE id = ?", (siswa_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def count_siswa() -> int:
    """Count total siswa"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM siswa")
    total = cursor.fetchone()["total"]
    conn.close()
    return total
```

**SQL Cheat Sheet:**

```sql
-- CREATE (INSERT)
INSERT INTO siswa (nama, email) VALUES ('Edy', 'edy@example.com');

-- READ
SELECT * FROM siswa;                      -- Semua
SELECT * FROM siswa WHERE id = 1;         -- By ID
SELECT nama, email FROM siswa;            -- Specific columns
SELECT * FROM siswa WHERE nama LIKE '%d%'; -- Search

-- UPDATE
UPDATE siswa SET nama = 'Edyson' WHERE id = 1;
UPDATE siswa SET nama = 'Edyson', email = 'edyson@example.com' WHERE id = 1;

-- DELETE
DELETE FROM siswa WHERE id = 1;

-- Aggregate
SELECT COUNT(*) as total FROM siswa;
SELECT MAX(id) FROM siswa;
SELECT * FROM siswa ORDER BY nama ASC LIMIT 10;
```

---

## 📋 Pydantic Models - Schema Validation

**File: models.py**

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Request Models (untuk input validation)
class SiswaCreate(BaseModel):
    """Schema untuk CREATE siswa"""
    nama: str  # Required
    email: EmailStr  # Validates email format
    
    class Config:
        schema_extra = {
            "example": {
                "nama": "Edy Santoso",
                "email": "edy@example.com"
            }
        }

class SiswaUpdate(BaseModel):
    """Schema untuk UPDATE siswa"""
    nama: str
    email: EmailStr

# Response Models (untuk output)
class SiswaResponse(BaseModel):
    """Schema untuk response siswa"""
    id: int
    nama: str
    email: str
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True  # Compatible dengan ORM
```

**Pydantic melakukan:**
- ✅ Validasi tipe data
- ✅ Validasi email format
- ✅ Convert tipe jika bisa
- ✅ Return error 422 jika invalid
- ✅ Auto-generate schema di docs

---

## 📡 API Specs - REST Endpoint Documentation

### Endpoint Specifications

#### 1. GET /api/siswa/ - Get All Siswa

```
GET /api/siswa/

Response (200 OK):
{
    "success": true,
    "message": "Berhasil mengambil 2 data siswa",
    "data": [
        {
            "id": 1,
            "nama": "Edy",
            "email": "edy@example.com",
            "created_at": "2026-02-08T10:00:00"
        },
        {
            "id": 2,
            "nama": "Budi",
            "email": "budi@example.com",
            "created_at": "2026-02-08T10:05:00"
        }
    ]
}
```

#### 2. GET /api/siswa/{id} - Get Siswa by ID

```
GET /api/siswa/1

Path Parameters:
- id (integer, required): ID siswa

Response (200 OK):
{
    "success": true,
    "message": "Siswa ditemukan",
    "data": {
        "id": 1,
        "nama": "Edy",
        "email": "edy@example.com",
        "created_at": "2026-02-08T10:00:00"
    }
}

Response (404 Not Found):
{
    "detail": "Siswa dengan ID 999 tidak ditemukan"
}
```

#### 3. POST /api/siswa/ - Create New Siswa

```
POST /api/siswa/
Content-Type: application/json

Request Body:
{
    "nama": "Edy Santoso",
    "email": "edy@example.com"
}

Response (201 Created):
{
    "success": true,
    "message": "Siswa berhasil ditambahkan",
    "data": {
        "id": 1,
        "nama": "Edy Santoso",
        "email": "edy@example.com",
        "created_at": "2026-02-08T10:00:00"
    }
}

Response (400 Bad Request) - Email sudah ada:
{
    "detail": "Email edy@example.com sudah digunakan"
}

Response (422 Unprocessable Entity) - Validation error:
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "invalid email format",
            "type": "value_error.email"
        }
    ]
}
```

#### 4. PUT /api/siswa/{id} - Update Siswa

```
PUT /api/siswa/1
Content-Type: application/json

Path Parameters:
- id (integer, required): ID siswa

Request Body:
{
    "nama": "Edy Santoso Updated",
    "email": "edy_baru@example.com"
}

Response (200 OK):
{
    "success": true,
    "message": "Siswa berhasil diupdate",
    "data": {
        "id": 1,
        "nama": "Edy Santoso Updated",
        "email": "edy_baru@example.com",
        "created_at": "2026-02-08T10:00:00"
    }
}

Response (404 Not Found):
{
    "detail": "Siswa dengan ID 999 tidak ditemukan"
}
```

#### 5. DELETE /api/siswa/{id} - Delete Siswa

```
DELETE /api/siswa/1

Path Parameters:
- id (integer, required): ID siswa

Response (200 OK):
{
    "success": true,
    "message": "Siswa dengan ID 1 berhasil dihapus",
    "data": null
}

Response (404 Not Found):
{
    "detail": "Siswa dengan ID 999 tidak ditemukan"
}
```

---

## 🧪 Pytest - Testing API dengan Comprehensive Test Cases

### Test Strategy

**Pyramid Testing:**
```
        🔴 E2E Tests (Integration)
       🟡🟡 API Tests
      🟢🟢🟢 Unit Tests
```

Kita fokus pada **API Tests** (integration) karena testing FastAPI.

### Test Fixtures - Setup dan Teardown

**File: tests/conftest.py**

```python
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import app

@pytest.fixture
def client():
    """Fixture untuk TestClient - digunakan di setiap test"""
    return TestClient(app)

@pytest.fixture
def sample_siswa_data():
    """Fixture untuk sample data"""
    return {
        "nama": "Sample Siswa",
        "email": "sample@example.com"
    }
```

### Test Struktur - Arrange, Act, Assert (AAA)

```python
def test_create_siswa_success(client):
    # ARRANGE - Setup data
    payload = {
        "nama": "Budi Santoso",
        "email": "budi_unique_123@example.com"
    }
    
    # ACT - Execute action
    response = client.post("/api/siswa/", json=payload)
    
    # ASSERT - Verify result
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["nama"] == "Budi Santoso"
```

### Test Categories

**1. Success Path Tests**
```python
def test_get_all_siswa(client):
    """Test GET /api/siswa/ - success case"""
    response = client.get("/api/siswa/")
    assert response.status_code == 200
    assert response.json()["success"] is True
```

**2. Error Path Tests**
```python
def test_get_siswa_not_found(client):
    """Test GET /api/siswa/{id} - not found"""
    response = client.get("/api/siswa/99999")
    assert response.status_code == 404
```

**3. Validation Tests**
```python
def test_create_siswa_invalid_email(client):
    """Test POST /api/siswa/ - invalid email validation"""
    payload = {"nama": "Test", "email": "invalid-email"}
    response = client.post("/api/siswa/", json=payload)
    assert response.status_code == 422
```

**4. Business Logic Tests**
```python
def test_create_siswa_duplicate_email(client):
    """Test POST /api/siswa/ - duplicate email constraint"""
    email = "unique@example.com"
    
    # Create first
    response1 = client.post("/api/siswa/", json={"nama": "First", "email": email})
    assert response1.status_code == 201
    
    # Try to create with same email
    response2 = client.post("/api/siswa/", json={"nama": "Second", "email": email})
    assert response2.status_code == 400
```

**5. Integration Tests**
```python
def test_crud_workflow(client):
    """Test full CRUD workflow: CREATE -> READ -> UPDATE -> DELETE"""
    
    # CREATE
    create_response = client.post("/api/siswa/", json={"nama": "Test", "email": "test@example.com"})
    siswa_id = create_response.json()["data"]["id"]
    
    # READ
    read_response = client.get(f"/api/siswa/{siswa_id}")
    assert read_response.status_code == 200
    
    # UPDATE
    update_response = client.put(f"/api/siswa/{siswa_id}", json={"nama": "Updated", "email": "updated@example.com"})
    assert update_response.status_code == 200
    
    # DELETE
    delete_response = client.delete(f"/api/siswa/{siswa_id}")
    assert delete_response.status_code == 200
    
    # Verify deleted
    verify_response = client.get(f"/api/siswa/{siswa_id}")
    assert verify_response.status_code == 404
```

### Menjalankan Tests

```bash
# Run all tests
pytest

# Run dengan verbose
pytest -v

# Run specific test file
pytest tests/test_main.py

# Run specific test function
pytest tests/test_main.py::test_create_siswa_success

# Run dengan coverage report
pytest --cov=. --cov-report=html
# Buka: htmlcov/index.html

# Run dengan show print statements
pytest -s

# Run dan stop di first failure
pytest -x

# Run dengan markers
pytest -m "slow"
```

### Test Output

```
tests/test_main.py::test_root PASSED                                     [  8%]
tests/test_main.py::test_health_check PASSED                             [ 16%]
tests/test_main.py::test_get_all_siswa PASSED                            [ 25%]
...
============================== 12 passed in 0.92s ==============================
```

---

## � Lifespan Events vs Middleware - Apa Bedanya?

### Apa itu Lifespan?

**Lifespan** adalah mechanism untuk menjalankan code pada **startup** dan **shutdown** application lifecycle.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== STARTUP (sebelum yield) =====
    print("App mulai...")
    init_db()
    
    yield  # ← App berjalan di sini
    
    # ===== SHUTDOWN (sesudah yield) =====
    print("App berhenti...")
    cleanup()
```

**Contoh timeline:**

```
1. Server dimulai
   ↓
2. Lifespan startup code dijalankan
   ├─ init_db() ✓
   ├─ Load config ✓
   ├─ Connect to external service ✓
   ↓
3. APP BERJALAN (menerima requests)
   ├─ GET /api/siswa/
   ├─ POST /api/siswa/
   ├─ ...requests lainnya...
   ↓
4. Server di-shutdown (Ctrl+C)
   ↓
5. Lifespan shutdown code dijalankan
   ├─ Close database ✓
   ├─ Save cache ✓
   ├─ Cleanup resources ✓
   ↓
6. Server selesai
```

### Apa itu Middleware?

**Middleware** adalah function yang **intercept setiap request/response**. Middleware berjalan **SELAMA aplikasi running**, bukan di startup/shutdown.

```python
from fastapi.middleware.cors import CORSMiddleware

# Ini adalah middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)
```

**Timeline Middleware:**

```
Request masuk
   ↓
Middleware 1 (Before)
   ↓
Middleware 2 (Before)
   ↓
Route handler (endpoint)
   ↓
Middleware 2 (After)
   ↓
Middleware 1 (After)
   ↓
Response kembali
```

### Perbedaan Lifespan vs Middleware

| Aspek | Lifespan | Middleware |
|-------|----------|-----------|
| **Dijalankan** | Saat startup & shutdown | Setiap request/response |
| **Tujuan** | Initialize & cleanup | Modify request/response |
| **Contoh** | Init database, load config | CORS, logging, auth |
| **Frekuensi** | 2x (startup + shutdown) | Ribuan kali per hari |
| **Code sebelum** | Startup | Before request |
| **Code sesudah** | Shutdown | After response |

### Analogi Real World

**Lifespan** = Restaurant Opening & Closing
```
Opening (Startup):
- Turn on lights
- Unlock doors
- Prep kitchen
- Count register

[Restaurant OPEN - serving customers]

Closing (Shutdown):
- Count register
- Clean kitchen
- Lock doors
- Turn off lights
```

**Middleware** = Staff handling customers
```
Customer comes in:
- Greeter welcomes (Before)
- [Process order]
- Staff cleans table (After)
```

---

## 📝 Use Cases - Kapan Pakai Apa?

### Gunakan Lifespan untuk:

✅ **Database connections**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db = Database("sqlite:///app.db")
    app.db = db
    yield
    # Shutdown
    await db.close()
```

✅ **Load configuration files**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config("config.yml")
    app.config = config
    yield
    save_config(config)
```

✅ **Connect to external services**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect once
    redis_client = redis.Redis()
    app.redis = redis_client
    yield
    # Disconnect once
    redis_client.close()
```

✅ **Background tasks startup**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background workers
    worker = BackgroundWorker()
    worker.start()
    yield
    # Stop workers gracefully
    worker.stop()
```

### Gunakan Middleware untuk:

✅ **CORS (Cross-Origin Resource Sharing)**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"]
)
```

✅ **Request logging**
```python
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response: {response.status_code}")
    return response
```

✅ **Authentication headers check**
```python
@app.middleware("http")
async def check_auth(request, call_next):
    if "Authorization" not in request.headers:
        return JSONResponse(status_code=401, content={"detail": "No auth"})
    return await call_next(request)
```

✅ **Request timing**
```python
@app.middleware("http")
async def add_process_time(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## 🔧 Praktik di Code Kita

### Lifespan yang Kita Gunakan:

**[main.py](main.py#L24-L48)**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== STARTUP =====
    init_db()  # Initialize SQLite database
    print("🚀 FastAPI app started")
    
    yield  # App running here
    
    # ===== SHUTDOWN =====
    print("👋 FastAPI app shutting down")

app = FastAPI(lifespan=lifespan)
```

**Apa yang terjadi:**

1. **Startup:** Database di-initialize sekali saat server start
2. **Running:** App melayani requests
3. **Shutdown:** Cleanup resources saat server stop

**Mengapa perlu?**

- ✅ Database hanya di-initialize **sekali** (efficient)
- ✅ Automatic cleanup saat server berhenti
- ✅ Tidak perlu manual connection management setiap request
- ✅ Graceful shutdown

---

## 📚 Complete Example - Lifespan + Middleware

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import logging

# Setup logging
logger = logging.getLogger(__name__)

# ===== LIFESPAN =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("Application starting up...")
    
    # Initialize database
    app.db = init_database()
    
    # Load configuration
    app.config = load_config()
    
    # Connect to Redis
    app.cache = redis.Redis()
    
    logger.info("✅ Application ready!")
    
    yield  # App running
    
    # SHUTDOWN
    logger.info("Application shutting down...")
    
    # Close database
    app.db.close()
    
    # Disconnect Redis
    app.cache.disconnect()
    
    logger.info("✅ Application stopped!")

# ===== MIDDLEWARE =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... lifespan code ...
    yield
    # ... cleanup code ...

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# Add custom middleware
@app.middleware("http")
async def log_and_time(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"📨 {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"✅ {response.status_code} - {process_time:.3f}s")
    
    return response

# ===== ENDPOINTS =====
@app.get("/api/siswa/")
async def get_siswa(request: Request):
    # Use database from lifespan
    siswa = request.app.db.query("SELECT * FROM siswa")
    
    # Use cache from lifespan
    cached = request.app.cache.get("siswa_list")
    
    return {"data": siswa}
```

**Timeline saat ada request:**

```
Server Start
│
├─ Lifespan Startup
│  ├─ init_database()
│  ├─ load_config()
│  └─ redis.connect()
│
└─ App Running
   
   Request GET /api/siswa/
   │
   ├─ Middleware: log_and_time (before)
   ├─ Middleware: CORSMiddleware (before)
   │
   ├─ Route handler: get_siswa()
   │
   ├─ Middleware: CORSMiddleware (after)
   └─ Middleware: log_and_time (after)
   
   Response sent
```

---

## ✅ Kesimpulan

**Lifespan BUKAN Middleware!**

- **Lifespan** = App lifecycle (startup + shutdown)
- **Middleware** = Request/response interceptor

Di code kita:
- ✅ Lifespan untuk **initialize database** saat startup
- 🔄 Middleware untuk **CORS, logging, auth** di setiap request

Keduanya penting untuk membuat API yang production-ready! 🚀

---

## 📚 Best Practices

### 1. API Response Format (Consistent)

**Success:**
```json
{
    "success": true,
    "message": "Deskripsi singkat",
    "data": {...}
}
```

**Error:**
```json
{
    "success": false,
    "detail": "Deskripsi error"
}
```

### 2. HTTP Status Codes

```python
200 OK              # Success GET, PUT, DELETE
201 CREATED         # Success POST
400 BAD REQUEST     # Client error (duplicate, invalid)
404 NOT FOUND       # Resource tidak ditemukan
422 UNPROCESSABLE   # Validation error
500 SERVER ERROR    # Server error
```

### 3. Database Best Practices

```python
# ❌ JANGAN: SQL Injection risk
query = f"SELECT * FROM siswa WHERE id = {siswa_id}"

# ✅ BENAR: Parameterized query
query = "SELECT * FROM siswa WHERE id = ?"
cursor.execute(query, (siswa_id,))
```

### 4. Error Handling

```python
@app.post("/api/siswa/")
async def create_siswa(siswa: SiswaCreate):
    try:
        result = insert_siswa(siswa.nama, siswa.email)
        return {"success": True, "data": result}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail=f"Email {siswa.email} sudah digunakan"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
```

### 5. Testing Best Practices

```python
# ❌ JANGAN: Hardcode data yang bisa conflict
email = "test@example.com"

# ✅ BENAR: Generate unique data
import uuid
email = f"test_{uuid.uuid4().hex[:8]}@example.com"
```

---

## 🔗 Perbedaan dengan Flask & Express

### Routing & Structure

| Aspek | FastAPI | Flask | Express |
|-------|---------|-------|---------|
| **Routing** | `@app.get()` | `@app.route()` | `app.get()` |
| **Path Param** | `{id}` | `<id>` | `:id` |
| **Type Hint** | ✅ Native | ❌ Manual | ❌ Manual |
| **Validation** | ✅ Pydantic | ❌ Manual | ❌ Manual |
| **Documentation** | ✅ Auto Swagger | ❌ Manual | ❌ Manual |
| **Async/Await** | ✅ Native | ⚠️ Manual | ✅ Native |
| **Testing** | `TestClient` | `@app.test_client()` | `supertest` |

### Code Comparison

**FastAPI:**
```python
@app.get("/api/siswa/{id}")
async def get_siswa(id: int) -> SiswaResponse:
    siswa = get_siswa_by_id(id)
    return siswa
```

**Flask:**
```python
@app.route("/api/siswa/<int:id>")
def get_siswa(id):
    siswa = get_siswa_by_id(id)
    return jsonify(siswa)
```

**Express:**
```javascript
app.get("/api/siswa/:id", (req, res) => {
    const siswa = getSiswaById(req.params.id);
    res.json(siswa);
});
```

---

## 📖 Rundown Pembelajaran

### Week 1: Fundamentals ✅
- ✅ Setup FastAPI & uvicorn
- ✅ Basic endpoints (GET, POST)
- ✅ Pydantic models & validation
- ✅ Pytest basics

### Week 2: Database (Current) 🔄
- 🔄 SQLite & raw SQL
- 🔄 Database operations (CRUD)
- 🔄 Lifespan events
- 🔄 Comprehensive testing

### Week 3: Advanced (Next) 📅
- 📅 Error handling & logging
- 📅 Dependency injection
- 📅 Middleware
- 📅 Authentication (JWT)

### Week 4: Production 📅
- 📅 Docker & deployment
- 📅 Database migrations
- 📅 API versioning
- 📅 Rate limiting

---

## 📚 Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **SQLite**: https://www.sqlite.org/
- **Pytest**: https://docs.pytest.org/
- **REST API Specs**: https://restfulapi.net/

---

## 🎯 Next Steps

1. ✅ Pahami CRUD operations dan database schema
2. ✅ Tulis comprehensive test cases
3. ✅ Practice dengan membuat API baru
4. ✅ Refactor ke APIRouter (Week 3)
5. ✅ Add authentication & authorization (Week 4)

Selamat belajar! 🚀


```bash
# 1. Buat virtual environment (best practice)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan server
uvicorn main:app --reload

# Server berjalan di: http://127.0.0.1:8000
```

### Menjalankan test:
```bash
# Jalankan semua test
pytest

# Dengan verbose output
pytest -v

# Jalankan file test tertentu
pytest tests/test_main.py

# Jalankan test dengan coverage
pip install pytest-cov
pytest --cov=. --cov-report=html
```