# Week 2a: CRUD dengan SQLAlchemy ORM

## 📚 Pelajaran: Database Integration dengan SQLAlchemy

### 🎯 Tujuan Pembelajaran
Memahami cara menggunakan **SQLAlchemy ORM** (Object-Relational Mapping) untuk CRUD operations, menggantikan raw SQL dengan pendekatan object-oriented yang lebih powerful.

---

## 1. Apa itu ORM?

### Object-Relational Mapping (ORM)

**ORM** adalah teknik programming yang menghubungkan:
- **Object** (Python classes/objects) ↔️ **Relational Database** (Tables/Rows)

```
Python Object          Database Table
┌─────────────┐       ┌──────────────┐
│   siswa     │  ↔️   │    siswa     │
│             │       │              │
│ id = 1      │       │ id = 1       │
│ nama = "Edy"│       │ nama = "Edy" │
│ email = "..│       │ email = "... │
└─────────────┘       └──────────────┘
```

### Kenapa Pakai ORM?

| Aspek | Raw SQL | SQLAlchemy ORM |
|-------|---------|----------------|
| **Code Style** | String SQL | Python objects |
| **Type Safety** | ❌ Manual | ✅ Auto |
| **IDE Support** | ⚠️ Limited | ✅ Full autocomplete |
| **Relationships** | Manual JOIN | ✅ Auto relationships |
| **Database Agnostic** | ❌ DB-specific | ✅ Support multi-DB |
| **Migrations** | Manual | ✅ Alembic integration |
| **Learning Curve** | Easy | Medium |

---

## 2. Setup SQLAlchemy

### Install Dependencies

```bash
pip install sqlalchemy==2.0.25
```

### File Structure

```
fast-dasar/
├── db_sqlalchemy.py    # Database setup & models
├── schemas.py          # Pydantic schemas (request/response)
├── main.py            # FastAPI endpoints
└── siswa_orm.db       # SQLite database (auto-created)
```

**Separation of Concerns:**
- `db_sqlalchemy.py` → SQLAlchemy models (database layer)
- `schemas.py` → Pydantic models (API layer)  
- `main.py` → FastAPI endpoints (controller layer)

---

## 3. Database Setup (`db_sqlalchemy.py`)

### Create Engine & Session

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database URL
DATABASE_URL = "sqlite:///./siswa_orm.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Untuk SQLite
)

# SessionLocal untuk membuat DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk models
Base = declarative_base()
```

**Penjelasan:**
- `engine`: Koneksi ke database
- `SessionLocal`: Factory untuk membuat sessions
- `Base`: Base class untuk semua models

### Define Model

```python
from sqlalchemy import Column, Integer, String

class Siswa(Base):
    """SQLAlchemy Model untuk tabel siswa"""
    __tablename__ = "siswa"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
```

**Mapping:**
```python
# Python Class    →    Database Table
Siswa             →    CREATE TABLE siswa (
  .id             →      id INTEGER PRIMARY KEY,
  .nama           →      nama VARCHAR(100) NOT NULL,
  .email          →      email VARCHAR(100) UNIQUE NOT NULL
)                 →    )
```

### Initialize Database

```python
def init_db():
    """Create semua tables"""
    Base.metadata.create_all(bind=engine)
```

### Dependency Injection

```python
def get_db():
    """
    Dependency untuk mendapatkan DB session
    Otomatis close setelah request selesai
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Usage di FastAPI:**
```python
@app.get("/api/siswa/")
async def read_siswa(db: Session = Depends(get_db)):
    # db sudah ready to use!
    siswa = db.query(Siswa).all()
    return siswa
```

---

## 4. Pydantic Schemas (`schemas.py`)

### Kenapa Pisah dari SQLAlchemy Model?

**SQLAlchemy Model** = Database representation  
**Pydantic Schema** = API request/response representation

```python
# SQLAlchemy Model (database.py)
class Siswa(Base):
    __tablename__ = "siswa"
    id = Column(Integer, primary_key=True)
    nama = Column(String(100))
    email = Column(String(100))

# Pydantic Schema (schemas.py)  
class SiswaCreate(BaseModel):
    nama: str
    email: EmailStr  # Validation!

class SiswaResponse(BaseModel):
    id: int
    nama: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)  # Baca dari SQLAlchemy object
```

### Base Schema

```python
from pydantic import BaseModel, EmailStr, Field

class SiswaBase(BaseModel):
    """Base schema - shared fields"""
    nama: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
```

### Request Schemas

```python
class SiswaCreate(SiswaBase):
    """Untuk POST request - tidak ada id"""
    pass

class SiswaUpdate(SiswaBase):
    """Untuk PUT request - tidak ada id"""
    pass
```

### Response Schema

```python
class SiswaResponse(SiswaBase):
    """Untuk response - include id dari database"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)
```

**`from_attributes=True`** memungkinkan Pydantic membaca dari SQLAlchemy object:
```python
# SQLAlchemy object
db_siswa = Siswa(id=1, nama="Edy", email="edy@example.com")

# Convert ke Pydantic otomatis
return SiswaResponse.from_orm(db_siswa)  # ✅ Works!
```

---

## 5. CRUD Operations dengan SQLAlchemy

### CREATE - Insert Data

```python
@app.post("/api/siswa/", response_model=SiswaResponse)
async def create_siswa(siswa: SiswaCreate, db: Session = Depends(get_db)):
    try:
        # 1. Buat instance SQLAlchemy model
        db_siswa = Siswa(
            nama=siswa.nama,
            email=siswa.email
        )
        
        # 2. Add ke session
        db.add(db_siswa)
        
        # 3. Commit ke database
        db.commit()
        
        # 4. Refresh untuk get generated fields (id)
        db.refresh(db_siswa)
        
        return db_siswa  # Pydantic auto-convert!
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email sudah digunakan")
```

**Equivalent SQL:**
```sql
INSERT INTO siswa (nama, email) VALUES ('Edy', 'edy@example.com');
SELECT * FROM siswa WHERE id = LAST_INSERT_ID();
```

**Langkah-langkah:**
1. **Create object** → `Siswa(...)`
2. **Add to session** → `db.add()`
3. **Commit transaction** → `db.commit()`
4. **Refresh object** → `db.refresh()` untuk mendapatkan id

---

### READ ALL - Query All Data

```python
@app.get("/api/siswa/", response_model=List[SiswaResponse])
async def read_all_siswa(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    siswa_list = db.query(Siswa).offset(skip).limit(limit).all()
    return siswa_list
```

**Equivalent SQL:**
```sql
SELECT * FROM siswa LIMIT 100 OFFSET 0;
```

**Query Methods:**
```python
db.query(Siswa).all()              # Get all
db.query(Siswa).first()            # Get first
db.query(Siswa).count()            # Count rows
db.query(Siswa).offset(10).limit(5).all()  # Pagination
```

---

### READ ONE - Query by ID

```python
@app.get("/api/siswa/{siswa_id}", response_model=SiswaResponse)
async def read_siswa(siswa_id: int, db: Session = Depends(get_db)):
    siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
    
    if siswa is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    
    return siswa
```

**Equivalent SQL:**
```sql
SELECT * FROM siswa WHERE id = 1 LIMIT 1;
```

**Filter Methods:**
```python
db.query(Siswa).filter(Siswa.id == 1).first()
db.query(Siswa).filter(Siswa.nama == "Edy").all()
db.query(Siswa).filter(Siswa.email.like("%@gmail.com")).all()
```

---

### UPDATE - Update Data

```python
@app.put("/api/siswa/{siswa_id}", response_model=SiswaResponse)
async def update_siswa(
    siswa_id: int,
    siswa_update: SiswaUpdate,
    db: Session = Depends(get_db)
):
    try:
        # 1. Query siswa
        siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
        
        if siswa is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        # 2. Update attributes
        siswa.nama = siswa_update.nama
        siswa.email = siswa_update.email
        
        # 3. Commit changes
        db.commit()
        
        # 4. Refresh object
        db.refresh(siswa)
        
        return siswa
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email sudah digunakan")
```

**Equivalent SQL:**
```sql
UPDATE siswa SET nama = 'Edy Updated', email = 'edy@new.com' WHERE id = 1;
SELECT * FROM siswa WHERE id = 1;
```

**Alternative - Update Without Loading:**
```python
# Lebih cepat untuk bulk update
db.query(Siswa).filter(Siswa.id == siswa_id).update({
    "nama": siswa_update.nama,
    "email": siswa_update.email
})
db.commit()
```

---

### DELETE - Delete Data

```python
@app.delete("/api/siswa/{siswa_id}")
async def delete_siswa(siswa_id: int, db: Session = Depends(get_db)):
    # 1. Query siswa
    siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
    
    if siswa is None:
        raise HTTPException(status_code=404, detail="Not found")
    
    # 2. Delete object
    db.delete(siswa)
    
    # 3. Commit changes
    db.commit()
    
    return {"success": True, "message": "Siswa dihapus"}
```

**Equivalent SQL:**
```sql
DELETE FROM siswa WHERE id = 1;
```

**Alternative - Delete Without Loading:**
```python
# Lebih cepat untuk bulk delete
db.query(Siswa).filter(Siswa.id == siswa_id).delete()
db.commit()
```

---

## 6. Advanced Queries

### Search with LIKE

```python
@app.get("/api/siswa/search/")
async def search_siswa(q: str, db: Session = Depends(get_db)):
    from sqlalchemy import or_
    
    siswa_list = db.query(Siswa).filter(
        or_(
            Siswa.nama.contains(q),      # LIKE '%q%'
            Siswa.email.contains(q)
        )
    ).all()
    
    return siswa_list
```

**Equivalent SQL:**
```sql
SELECT * FROM siswa 
WHERE nama LIKE '%search%' OR email LIKE '%search%';
```

### Filter Operators

```python
# Equal
db.query(Siswa).filter(Siswa.id == 1)

# Not Equal
db.query(Siswa).filter(Siswa.id != 1)

# Greater Than
db.query(Siswa).filter(Siswa.id > 10)

# IN
db.query(Siswa).filter(Siswa.id.in_([1, 2, 3]))

# LIKE
db.query(Siswa).filter(Siswa.nama.like("%Edy%"))

# AND
db.query(Siswa).filter(Siswa.id > 1, Siswa.nama == "Edy")

# OR
from sqlalchemy import or_
db.query(Siswa).filter(or_(Siswa.id == 1, Siswa.id == 2))
```

### Order By

```python
# ASC
db.query(Siswa).order_by(Siswa.nama).all()

# DESC
db.query(Siswa).order_by(Siswa.nama.desc()).all()

# Multiple
db.query(Siswa).order_by(Siswa.nama, Siswa.email.desc()).all()
```

---

## 7. Dependency Injection Pattern

### Apa itu Dependency Injection?

FastAPI otomatis **inject** dependencies ke function parameters.

```python
# Tanpa Dependency Injection (manual)
@app.get("/api/siswa/")
async def read_siswa():
    db = SessionLocal()  # Manual create
    try:
        siswa = db.query(Siswa).all()
        return siswa
    finally:
        db.close()  # Manual close

# Dengan Dependency Injection (otomatis)
@app.get("/api/siswa/")
async def read_siswa(db: Session = Depends(get_db)):
    siswa = db.query(Siswa).all()
    return siswa  # db.close() otomatis dipanggil!
```

### Benefits:

✅ **Auto cleanup** - Session otomatis closed  
✅ **Reusable** - Bisa dipakai di banyak endpoints  
✅ **Testable** - Mudah di-mock untuk testing  
✅ **Type safe** - IDE autocomplete works

---

## 8. Transaction Management

### Auto-Rollback on Error

```python
try:
    # Operations
    db.add(siswa)
    db.commit()
except IntegrityError:
    db.rollback()  # Undo changes
    raise HTTPException(...)
```

### Multiple Operations in One Transaction

```python
try:
    # Create siswa
    siswa1 = Siswa(nama="Edy", email="edy@example.com")
    siswa2 = Siswa(nama="John", email="john@example.com")
    
    db.add(siswa1)
    db.add(siswa2)
    
    # Both commit together or both rollback
    db.commit()
except:
    db.rollback()
    raise
```

---

## 9. Comparison: Raw SQL vs SQLAlchemy

### CREATE Operation

```python
# Raw SQL
cursor.execute(
    "INSERT INTO siswa (nama, email) VALUES (?, ?)",
    (nama, email)
)
siswa_id = cursor.lastrowid
conn.commit()

# SQLAlchemy ORM
db_siswa = Siswa(nama=nama, email=email)
db.add(db_siswa)
db.commit()
db.refresh(db_siswa)  # Auto get id
```

### READ Operation

```python
# Raw SQL
cursor.execute("SELECT * FROM siswa WHERE id = ?", (siswa_id,))
row = cursor.fetchone()
siswa = dict(row) if row else None

# SQLAlchemy ORM
siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
```

### UPDATE Operation

```python
# Raw SQL
cursor.execute(
    "UPDATE siswa SET nama = ?, email = ? WHERE id = ?",
    (nama, email, siswa_id)
)
conn.commit()

# SQLAlchemy ORM
siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
siswa.nama = nama
siswa.email = email
db.commit()
```

### DELETE Operation

```python
# Raw SQL
cursor.execute("DELETE FROM siswa WHERE id = ?", (siswa_id,))
conn.commit()

# SQLAlchemy ORM
siswa = db.query(Siswa).filter(Siswa.id == siswa_id).first()
db.delete(siswa)
db.commit()
```

---

## 10. Testing CRUD dengan SQLAlchemy

### Test Sequence

```bash
# 1. Create siswa dengan SQLAlchemy
curl -X POST http://127.0.0.1:8000/api/siswa/ \
  -H "Content-Type: application/json" \
  -d '{"nama": "Edy ORM", "email": "edy.orm@gmail.com"}'

# Response:
{
  "id": 1,
  "nama": "Edy ORM",
  "email": "edy.orm@gmail.com"
}

# 2. Read all dengan pagination
curl "http://127.0.0.1:8000/api/siswa/?skip=0&limit=10"

# 3. Read one by ID
curl http://127.0.0.1:8000/api/siswa/1

# 4. Search siswa
curl "http://127.0.0.1:8000/api/siswa/search/?q=Edy"

# 5. Update siswa
curl -X PUT http://127.0.0.1:8000/api/siswa/1 \
  -H "Content-Type: application/json" \
  -d '{"nama": "Edy Updated", "email": "edy.updated@gmail.com"}'

# 6. Delete siswa
curl -X DELETE http://127.0.0.1:8000/api/siswa/1
```

### Check Health

```bash
curl http://127.0.0.1:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "orm": "SQLAlchemy",
  "total_siswa": 5
}
```

---

## 11. Best Practices

### 1. Always Use Sessions Properly

```python
# ✅ Good - dengan Depends
@app.get("/api/siswa/")
async def read_siswa(db: Session = Depends(get_db)):
    return db.query(Siswa).all()

# ❌ Bad - manual session management
@app.get("/api/siswa/")
async def read_siswa():
    db = SessionLocal()
    result = db.query(Siswa).all()
    db.close()  # Bisa lupa!
    return result
```

### 2. Use Response Models

```python
# ✅ Good - type safe
@app.get("/api/siswa/", response_model=List[SiswaResponse])

# ❌ Bad - no validation
@app.get("/api/siswa/")
```

### 3. Handle Exceptions Properly

```python
try:
    db.add(siswa)
    db.commit()
except IntegrityError:
    db.rollback()  # Important!
    raise HTTPException(...)
```

### 4. Use Indexes for Performance

```python
class Siswa(Base):
    __tablename__ = "siswa"
    
    id = Column(Integer, primary_key=True, index=True)  # ✅ Indexed
    email = Column(String, unique=True, index=True)     # ✅ Indexed for search
    nama = Column(String)  # No index needed
```

### 5. Separate Concerns

```
db_sqlalchemy.py  → Database models
schemas.py        → API schemas
main.py          → Business logic
```

---

## 12. Migration ke Production

### SQLite → PostgreSQL/MySQL

SQLAlchemy mendukung multiple databases:

```python
# Development - SQLite
DATABASE_URL = "sqlite:///./siswa.db"

# Production - PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Production - MySQL
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

**Kode tetap sama!** Hanya ganti DATABASE_URL.

### Database Migrations dengan Alembic

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create siswa table"

# Apply migration
alembic upgrade head
```

---

## 13. Performance Tips

### N+1 Query Problem

```python
# ❌ Bad - N+1 queries
siswa_list = db.query(Siswa).all()
for siswa in siswa_list:
    # Setiap loop = 1 query (jika ada relationship)
    print(siswa.kelas.nama)

# ✅ Good - Eager loading
from sqlalchemy.orm import joinedload

siswa_list = db.query(Siswa).options(
    joinedload(Siswa.kelas)
).all()
```

### Bulk Operations

```python
# ❌ Bad - Multiple commits
for data in bulk_data:
    siswa = Siswa(**data)
    db.add(siswa)
    db.commit()  # Slow!

# ✅ Good - Single commit
siswa_list = [Siswa(**data) for data in bulk_data]
db.bulk_save_objects(siswa_list)
db.commit()  # Fast!
```

---

## 14. Comparison Table

| Feature | Raw SQL (Week 1b) | SQLAlchemy ORM (Week 2a) |
|---------|------------------|-------------------------|
| **Query Style** | String SQL | Python objects |
| **Type Safety** | ❌ Manual | ✅ Auto |
| **IDE Support** | ⚠️ Limited | ✅ Full autocomplete |
| **Learning Curve** | Easy | Medium |
| **Flexibility** | ✅ Very flexible | ⚠️ Some limitations |
| **Database Agnostic** | ❌ No | ✅ Yes (SQLite, PostgreSQL, MySQL) |
| **Relationships** | Manual JOIN | ✅ Auto relationships |
| **Migrations** | Manual SQL | ✅ Alembic |
| **Performance** | ✅ Optimal | ✅ Good (with proper usage) |
| **Error Prone** | ⚠️ SQL injection risk | ✅ Safe |

---

## 15. When to Use What?

### Use Raw SQL When:
- ✅ Simple CRUD only
- ✅ Learning SQL fundamentals
- ✅ Need maximum performance
- ✅ Complex custom queries
- ✅ Small project

### Use SQLAlchemy ORM When:
- ✅ Complex relationships (1-to-many, many-to-many)
- ✅ Need database portability
- ✅ Large team project
- ✅ Need migrations (Alembic)
- ✅ Want type safety & IDE support
- ✅ Production-ready application

---

## 🎯 Key Takeaways

### ✅ Yang Sudah Dipelajari:

1. **SQLAlchemy Setup**
   - Create engine & session
   - Define models dengan declarative_base
   - Dependency injection dengan get_db()

2. **ORM Operations**
   - CREATE: db.add() + commit()
   - READ: db.query().filter().all()
   - UPDATE: modify object + commit()
   - DELETE: db.delete() + commit()

3. **Advanced Features**
   - Pagination dengan offset/limit
   - Search dengan filter & OR
   - Transaction management
   - Error handling dengan rollback

4. **Best Practices**
   - Separation of concerns (models vs schemas)
   - Dependency injection
   - Proper exception handling
   - Use indexes for performance

5. **Production Ready**
   - Database agnostic (SQLite → PostgreSQL/MySQL)
   - Ready for Alembic migrations
   - Type safe dengan Pydantic schemas

---

## 🚀 Next Steps (Week 2b)

- Middleware untuk logging & error handling
- CORS configuration
- Rate limiting
- Request/Response logging
- Custom exception handlers

---

## 📁 Complete File Structure

```
fast-dasar/
├── main.py              # FastAPI endpoints dengan SQLAlchemy
├── db_sqlalchemy.py     # Database setup & models
├── schemas.py           # Pydantic schemas
├── siswa_orm.db        # SQLite database (SQLAlchemy)
├── requirements.txt     # Dependencies (+ sqlalchemy)
├── router.md           # Week 1a: Basic routing
├── crud.md             # Week 1b: Raw SQL
├── CRUDSQL.md          # Week 2a: SQLAlchemy (this file)
└── venv/               # Virtual environment
```

---

**Completed**: February 5, 2026  
**Duration**: Week 2a  
**Status**: ✅ CRUD dengan SQLAlchemy ORM Completed  
**Database**: SQLite with SQLAlchemy ORM
