# SQLAlchemy Migration Guide

## Overview

Proyek ini telah dimigrasikan dari menggunakan **raw SQL queries** ke **SQLAlchemy ORM (Object Relational Mapper)**. Migrasi ini meningkatkan keamanan, maintainability, dan skalabilitas aplikasi.

## Perubahan Utama

### 1. Database Layer

#### Before (Raw SQL)
```python
# app/database.py - Raw SQL
def insert_siswa(nama: str, email: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO siswa (nama, email) VALUES (?, ?)",
        (nama, email)
    )
    siswa_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return siswa_id
```

#### After (SQLAlchemy ORM)
```python
# app/database.py - SQLAlchemy ORM
def insert_siswa(db: Session, nama: str, email: str) -> SiswaORM:
    siswa = SiswaORM(nama=nama, email=email)
    db.add(siswa)
    db.commit()
    db.refresh(siswa)
    return siswa
```

### 2. ORM Models

#### New - SiswaORM Model
```python
# app/database.py
class SiswaORM(Base):
    """SQLAlchemy ORM model untuk tabel siswa"""
    __tablename__ = "siswa"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
```

### 3. Endpoint Changes

#### Before (Raw SQL)
```python
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SiswaResponse)
async def create_siswa(siswa: SiswaCreate):
    try:
        siswa_id = insert_siswa(siswa.nama, siswa.email)
        new_siswa = get_siswa_by_id(siswa_id)
        return new_siswa
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, ...)
```

#### After (SQLAlchemy)
```python
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SiswaResponse)
async def create_siswa(siswa: SiswaCreate, db: Session = Depends(get_db)):
    try:
        existing_email = get_siswa_by_email(db, siswa.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, ...)
        
        new_siswa = insert_siswa(db, siswa.nama, siswa.email)
        return new_siswa
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, ...)
```

## Benefits of SQLAlchemy

### 1. **SQL Injection Prevention**
- ORM secara otomatis handles parameter escaping
- Tidak ada string concatenation untuk queries
- Parameterized queries built-in

### 2. **Type Safety**
- ORM models dengan type hints
- IDE autocomplete support
- Better error messages

### 3. **Relationship Support**
- Mudah menambah foreign keys dan relationships
- Lazy loading dan eager loading options
- Cascade deletes otomatis

### 4. **Query Simplification**
```python
# Raw SQL
cursor.execute("SELECT * FROM siswa WHERE id = ?", (siswa_id,))
row = cursor.fetchone()
siswa = dict(row) if row else None

# SQLAlchemy
siswa = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
```

### 5. **Better Testing**
- Dependency injection dengan `get_db()`
- Easy to mock database dengan test fixtures
- Transactional test isolation

## Project Structure

```
app/
├── database.py          # SQLAlchemy config + ORM models + CRUD functions
├── models.py            # Pydantic schemas (request/response)
├── api/
│   └── v1/
│       ├── api.py       # Router aggregator
│       └── endpoints/
│           ├── siswa.py # CRUD endpoints
│           └── halo.py  # Greeting endpoints
├── core/
├── middleware/
├── schemas/
└── services/

main.py                 # FastAPI app + lifespan
requirements.txt        # Dependencies
```

## Migration Checklist

✅ Install SQLAlchemy 2.0.23
✅ Create ORM models in `app/database.py`
✅ Setup database engine dan SessionLocal
✅ Create `get_db()` dependency
✅ Update all CRUD functions to use ORM
✅ Update endpoints to use `Depends(get_db)`
✅ Update test fixtures (conftest.py)
✅ Update test functions to use client fixture
✅ Remove raw SQL queries
✅ Test all endpoints
✅ Verify all 14 tests pass

## How to Use

### Starting the Server
```bash
uvicorn main:app --reload
```

### Running Tests
```bash
pytest tests/test_main.py -v
```

### Accessing API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Patterns

### Create Record
```python
new_siswa = SiswaORM(nama=nama, email=email)
db.add(new_siswa)
db.commit()
db.refresh(new_siswa)
```

### Read Record
```python
siswa = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
```

### Update Record
```python
siswa = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
if siswa:
    siswa.nama = new_nama
    siswa.email = new_email
    db.commit()
    db.refresh(siswa)
```

### Delete Record
```python
siswa = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
if siswa:
    db.delete(siswa)
    db.commit()
```

### Query All Records
```python
siswa_list = db.query(SiswaORM).all()
```

## Testing with SQLAlchemy

### Test Fixture Setup
```python
# tests/conftest.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, ...)

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
```

### Test Usage
```python
def test_create_siswa(client):
    payload = {"nama": "Test", "email": "test@example.com"}
    response = client.post("/api/v1/siswa/", json=payload)
    assert response.status_code == 201
```

## Performance Optimization Tips

1. **Add Indexes**
   ```python
   email = Column(String(100), nullable=False, unique=True, index=True)
   ```

2. **Eager Loading**
   ```python
   from sqlalchemy.orm import joinedload
   siswa = db.query(SiswaORM).options(joinedload(...)).first()
   ```

3. **Pagination**
   ```python
   siswa_list = db.query(SiswaORM).offset(skip).limit(limit).all()
   ```

4. **Query Optimization**
   ```python
   siswa_count = db.query(SiswaORM).count()
   ```

## Next Steps

### Future Enhancements
- [ ] Add SQLAlchemy relationships (FK to other tables)
- [ ] Implement pagination in endpoints
- [ ] Add sorting and filtering capabilities
- [ ] Database migrations with Alembic
- [ ] Add soft deletes
- [ ] Implement auditing (created_at, updated_at)

## Resources

- [SQLAlchemy Official Docs](https://docs.sqlalchemy.org/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [FastAPI with SQLAlchemy](https://fastapi.tiangolo.com/advanced/sql-databases/)

## Summary

Migrasi dari raw SQL ke SQLAlchemy memberikan:
- ✅ Better security (SQL injection prevention)
- ✅ Cleaner code (less boilerplate)
- ✅ Type safety (better IDE support)
- ✅ Easier testing (dependency injection)
- ✅ Future-proof (easier to add features)

**Status**: ✅ Migration Complete - All 14 tests passing
