# Week 1b: CRUD Operations dengan SQLite

## 📚 Pelajaran: CRUD dengan Raw SQL

### 🎯 Tujuan Pembelajaran
Memahami cara membuat CRUD (Create, Read, Update, Delete) operations menggunakan SQLite dengan raw SQL queries (bukan ORM).

---

## 1. Persiapan Database

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS siswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);
```

**Field Explanation:**
- `id`: Primary key, auto-increment
- `nama`: Nama siswa (required)
- `email`: Email siswa (required, unique constraint)

### Database Helper (`database.py`)

```python
import sqlite3

DB_PATH = "siswa.db"

def get_db_connection():
    """Membuat koneksi dengan row_factory untuk dict-like access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

**Row Factory Benefits:**
- Hasil query bisa diakses seperti dictionary
- Lebih mudah convert ke JSON
- Compatible dengan Pydantic models

---

## 2. CRUD Operations dengan Raw SQL

### CREATE - Insert Data

```python
def insert_siswa(nama: str, email: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO siswa (nama, email) VALUES (?, ?)",
        (nama, email)
    )
    
    siswa_id = cursor.lastrowid  # Get ID yang baru dibuat
    conn.commit()
    conn.close()
    
    return siswa_id
```

**Endpoint:**
```python
@app.post("/api/siswa/", status_code=201)
async def create_siswa(siswa: SiswaCreate):
    try:
        siswa_id = insert_siswa(siswa.nama, siswa.email)
        new_siswa = get_siswa_by_id(siswa_id)
        
        return {
            "success": True,
            "message": "Siswa berhasil ditambahkan",
            "data": new_siswa
        }
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail=f"Email {siswa.email} sudah digunakan"
        )
```

**Test:**
```bash
curl -X POST http://127.0.0.1:8000/api/siswa/ \
  -H "Content-Type: application/json" \
  -d '{"nama": "Edy Cole", "email": "edycoleee@gmail.com"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Siswa berhasil ditambahkan",
  "data": {
    "id": 1,
    "nama": "Edy Cole",
    "email": "edycoleee@gmail.com"
  }
}
```

---

### READ ALL - Get All Data

```python
def get_all_siswa() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nama, email FROM siswa ORDER BY id")
    rows = cursor.fetchall()
    
    conn.close()
    
    # Convert Row objects to dictionaries
    return [dict(row) for row in rows]
```

**Endpoint:**
```python
@app.get("/api/siswa/")
async def read_all_siswa():
    siswa_list = get_all_siswa()
    total = len(siswa_list)
    
    return {
        "success": True,
        "message": f"Berhasil mengambil {total} data siswa",
        "data": siswa_list
    }
```

**Test:**
```bash
curl http://127.0.0.1:8000/api/siswa/
```

**Response:**
```json
{
  "success": true,
  "message": "Berhasil mengambil 2 data siswa",
  "data": [
    {
      "id": 1,
      "nama": "Edy Cole",
      "email": "edycoleee@gmail.com"
    },
    {
      "id": 2,
      "nama": "John Doe",
      "email": "john@example.com"
    }
  ]
}
```

---

### READ ONE - Get by ID

```python
def get_siswa_by_id(siswa_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nama, email FROM siswa WHERE id = ?",
        (siswa_id,)
    )
    row = cursor.fetchone()
    
    conn.close()
    
    return dict(row) if row else None
```

**Endpoint:**
```python
@app.get("/api/siswa/{siswa_id}")
async def read_siswa(siswa_id: int):
    siswa = get_siswa_by_id(siswa_id)
    
    if siswa is None:
        raise HTTPException(
            status_code=404,
            detail=f"Siswa dengan ID {siswa_id} tidak ditemukan"
        )
    
    return {
        "success": True,
        "message": "Siswa ditemukan",
        "data": siswa
    }
```

**Test:**
```bash
curl http://127.0.0.1:8000/api/siswa/1
```

**Response:**
```json
{
  "success": true,
  "message": "Siswa ditemukan",
  "data": {
    "id": 1,
    "nama": "Edy Cole",
    "email": "edycoleee@gmail.com"
  }
}
```

---

### UPDATE - Update Data

```python
def update_siswa(siswa_id: int, nama: str, email: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE siswa SET nama = ?, email = ? WHERE id = ?",
        (nama, email, siswa_id)
    )
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0
```

**Endpoint:**
```python
@app.put("/api/siswa/{siswa_id}")
async def update_siswa_data(siswa_id: int, siswa: SiswaUpdate):
    # Cek apakah siswa exists
    existing = get_siswa_by_id(siswa_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    
    try:
        success = update_siswa(siswa_id, siswa.nama, siswa.email)
        updated = get_siswa_by_id(siswa_id)
        
        return {
            "success": True,
            "message": "Siswa berhasil diupdate",
            "data": updated
        }
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail=f"Email {siswa.email} sudah digunakan"
        )
```

**Test:**
```bash
curl -X PUT http://127.0.0.1:8000/api/siswa/1 \
  -H "Content-Type: application/json" \
  -d '{"nama": "Edy Cole Updated", "email": "edy.updated@gmail.com"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Siswa berhasil diupdate",
  "data": {
    "id": 1,
    "nama": "Edy Cole Updated",
    "email": "edy.updated@gmail.com"
  }
}
```

---

### DELETE - Delete Data

```python
def delete_siswa(siswa_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM siswa WHERE id = ?", (siswa_id,))
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0
```

**Endpoint:**
```python
@app.delete("/api/siswa/{siswa_id}")
async def delete_siswa_data(siswa_id: int):
    # Cek apakah siswa exists
    existing = get_siswa_by_id(siswa_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    
    success = delete_siswa(siswa_id)
    
    return {
        "success": True,
        "message": f"Siswa dengan ID {siswa_id} berhasil dihapus",
        "data": None
    }
```

**Test:**
```bash
curl -X DELETE http://127.0.0.1:8000/api/siswa/1
```

**Response:**
```json
{
  "success": true,
  "message": "Siswa dengan ID 1 berhasil dihapus",
  "data": null
}
```

---

## 3. Pydantic Models untuk Validation

### SiswaCreate (POST Request)

```python
from pydantic import BaseModel, EmailStr, Field

class SiswaCreate(BaseModel):
    nama: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Automatic email validation
```

**Validation:**
- `nama`: Required, minimum 1 character
- `email`: Required, valid email format
- Auto return 422 jika validation gagal

### SiswaUpdate (PUT Request)

```python
class SiswaUpdate(BaseModel):
    nama: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
```

**Same validation as Create**

### SiswaResponse

```python
class SiswaResponse(BaseModel):
    id: int
    nama: str
    email: str
```

**For documentation and type safety**

---

## 4. Error Handling

### HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Success (GET, PUT, DELETE) |
| 201 | Created | Success (POST) |
| 400 | Bad Request | Validation error, duplicate email |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Pydantic validation error |
| 500 | Internal Server Error | Database error, unexpected error |

### Error Response Format

```python
try:
    # operation
except sqlite3.IntegrityError:
    raise HTTPException(
        status_code=400,
        detail="Email sudah digunakan"
    )
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Error: {str(e)}"
    )
```

**Error Response:**
```json
{
  "detail": "Email sudah digunakan"
}
```

---

## 5. SQL Injection Prevention

### ❌ WRONG - Vulnerable to SQL Injection

```python
# JANGAN LAKUKAN INI!
cursor.execute(f"SELECT * FROM siswa WHERE email = '{email}'")
```

### ✅ CORRECT - Using Parameterized Queries

```python
# Gunakan parameter placeholders (?)
cursor.execute(
    "SELECT * FROM siswa WHERE email = ?",
    (email,)
)
```

**Benefits:**
- ✅ Prevents SQL injection attacks
- ✅ Automatic escaping
- ✅ Type safety

---

## 6. Database Lifecycle

### Startup Event

```python
@app.on_event("startup")
async def startup_event():
    """Initialize database when app starts"""
    init_db()
    print("🚀 FastAPI app started with SQLite database")
```

### Shutdown Event

```python
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when app shuts down"""
    print("👋 FastAPI app shutting down")
```

---

## 7. Testing CRUD Operations

### Test Sequence

```bash
# 1. Create siswa
curl -X POST http://127.0.0.1:8000/api/siswa/ \
  -H "Content-Type: application/json" \
  -d '{"nama": "Test User", "email": "test@example.com"}'

# 2. Read all
curl http://127.0.0.1:8000/api/siswa/

# 3. Read one
curl http://127.0.0.1:8000/api/siswa/1

# 4. Update
curl -X PUT http://127.0.0.1:8000/api/siswa/1 \
  -H "Content-Type: application/json" \
  -d '{"nama": "Updated User", "email": "updated@example.com"}'

# 5. Delete
curl -X DELETE http://127.0.0.1:8000/api/siswa/1
```

### Testing dengan Swagger UI

1. Buka http://127.0.0.1:8000/docs
2. Lihat semua endpoint CRUD
3. Test langsung dari browser
4. Lihat request/response schema

---

## 8. Comparison: Raw SQL vs ORM

| Aspect | Raw SQL | SQLAlchemy ORM |
|--------|---------|----------------|
| **Learning Curve** | Easy | Medium |
| **Control** | Full control | Abstracted |
| **Performance** | Optimal | Good |
| **Flexibility** | Very flexible | Less flexible |
| **Type Safety** | Manual | Built-in |
| **Complex Queries** | Easy | Can be complex |
| **Migrations** | Manual | Alembic |

**When to use Raw SQL:**
- ✅ Simple CRUD operations
- ✅ Need full SQL control
- ✅ Optimizing specific queries
- ✅ Learning SQL fundamentals

**When to use ORM:**
- ✅ Complex relationships
- ✅ Need migrations
- ✅ Multiple databases
- ✅ Large team projects

---

## 9. Best Practices

### 1. Always Close Connections

```python
conn = get_db_connection()
try:
    # operations
finally:
    conn.close()
```

### 2. Use Transactions for Multiple Operations

```python
conn = get_db_connection()
try:
    cursor.execute("INSERT ...")
    cursor.execute("UPDATE ...")
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```

### 3. Validate Input with Pydantic

```python
class SiswaCreate(BaseModel):
    nama: str = Field(..., min_length=1)
    email: EmailStr  # Auto validation
```

### 4. Consistent Response Format

```python
{
    "success": bool,
    "message": str,
    "data": any
}
```

### 5. Proper Error Handling

```python
try:
    # operation
except sqlite3.IntegrityError:
    # Handle duplicate
except Exception as e:
    # Handle unexpected errors
```

---

## 10. File Structure

```
fast-dasar/
├── main.py              # FastAPI app with CRUD endpoints
├── database.py          # Database helper functions
├── models.py            # Pydantic models
├── siswa.db            # SQLite database (auto-created)
├── requirements.txt     # Dependencies
├── router.md           # Week 1a documentation
├── crud.md             # Week 1b documentation (this file)
└── venv/               # Virtual environment
```

---

## 11. Complete CRUD Workflow

```
┌─────────────┐
│   CLIENT    │
└──────┬──────┘
       │
       │ HTTP Request
       ▼
┌─────────────────────────┐
│   FastAPI Endpoint      │
│   - Validate with       │
│     Pydantic            │
│   - Handle errors       │
└──────┬──────────────────┘
       │
       │ Call function
       ▼
┌─────────────────────────┐
│   database.py           │
│   - Raw SQL queries     │
│   - Connection mgmt     │
└──────┬──────────────────┘
       │
       │ Execute SQL
       ▼
┌─────────────────────────┐
│   SQLite Database       │
│   - siswa table         │
│   - Auto-increment ID   │
└──────┬──────────────────┘
       │
       │ Return data
       ▼
┌─────────────────────────┐
│   JSON Response         │
│   - success: bool       │
│   - message: str        │
│   - data: any           │
└─────────────────────────┘
```

---

## 12. Quick Reference

### HTTP Methods & CRUD

```
POST   /api/siswa/        → CREATE
GET    /api/siswa/        → READ ALL
GET    /api/siswa/{id}    → READ ONE
PUT    /api/siswa/{id}    → UPDATE
DELETE /api/siswa/{id}    → DELETE
```

### SQL Commands

```sql
-- Create
INSERT INTO siswa (nama, email) VALUES (?, ?)

-- Read All
SELECT id, nama, email FROM siswa ORDER BY id

-- Read One
SELECT id, nama, email FROM siswa WHERE id = ?

-- Update
UPDATE siswa SET nama = ?, email = ? WHERE id = ?

-- Delete
DELETE FROM siswa WHERE id = ?

-- Count
SELECT COUNT(*) FROM siswa
```

---

## 🎯 Key Takeaways

### ✅ Yang Sudah Dipelajari:

1. **SQLite dengan Raw SQL**
   - Create table dengan constraints
   - CRUD operations dengan parameterized queries
   - SQL injection prevention

2. **Database Connection Management**
   - Row factory untuk dict-like access
   - Proper connection closing
   - Error handling

3. **FastAPI Integration**
   - Startup/shutdown events
   - Path parameters
   - Status codes
   - HTTPException

4. **Pydantic Validation**
   - EmailStr validation
   - Field constraints
   - Auto 422 errors

5. **RESTful API Design**
   - Proper HTTP methods
   - Consistent response format
   - Error responses

### 🚀 Next Steps (Week 2a):

- SQLAlchemy ORM instead of raw SQL
- Database relationships (1-to-many, many-to-many)
- Database migrations with Alembic
- Advanced queries (JOIN, GROUP BY, etc)
- Pagination for large datasets

---

**Completed**: February 5, 2026  
**Duration**: Week 1b  
**Status**: ✅ CRUD Operations dengan SQLite Completed
