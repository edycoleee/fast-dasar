# SQLAlchemy Cheat Sheet

## Quick Reference

### Import
```python
from app.database import get_db, SiswaORM, SessionLocal
from fastapi import Depends
from sqlalchemy.orm import Session
```

### Create Record
```python
@router.post("/")
async def create_siswa(siswa: SiswaCreate, db: Session = Depends(get_db)):
    new_siswa = SiswaORM(nama=siswa.nama, email=siswa.email)
    db.add(new_siswa)
    db.commit()
    db.refresh(new_siswa)
    return new_siswa
```

### Read All Records
```python
@router.get("/")
async def get_all_siswa(db: Session = Depends(get_db)):
    return db.query(SiswaORM).all()
```

### Read One Record by ID
```python
@router.get("/{siswa_id}")
async def get_siswa(siswa_id: int, db: Session = Depends(get_db)):
    return db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
```

### Read by Other Attributes
```python
# By email
siswa = db.query(SiswaORM).filter(SiswaORM.email == "test@example.com").first()

# Multiple conditions
siswa = db.query(SiswaORM).filter(
    SiswaORM.nama == "John",
    SiswaORM.email == "john@example.com"
).first()

# OR condition
from sqlalchemy import or_
siswa = db.query(SiswaORM).filter(
    or_(SiswaORM.email == "a@test.com", SiswaORM.email == "b@test.com")
).all()
```

### Update Record
```python
@router.put("/{siswa_id}")
async def update_siswa(siswa_id: int, data: SiswaUpdate, db: Session = Depends(get_db)):
    siswa = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
    if siswa:
        siswa.nama = data.nama
        siswa.email = data.email
        db.commit()
        db.refresh(siswa)
    return siswa
```

### Delete Record
```python
@router.delete("/{siswa_id}")
async def delete_siswa(siswa_id: int, db: Session = Depends(get_db)):
    siswa = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first()
    if siswa:
        db.delete(siswa)
        db.commit()
        return {"success": True}
    return {"success": False}
```

### Count Records
```python
total = db.query(SiswaORM).count()
```

### Pagination
```python
skip = 0
limit = 10
siswa_list = db.query(SiswaORM).offset(skip).limit(limit).all()
```

### Sorting
```python
from sqlalchemy import desc

# Sort ascending
siswa_list = db.query(SiswaORM).order_by(SiswaORM.nama).all()

# Sort descending
siswa_list = db.query(SiswaORM).order_by(desc(SiswaORM.id)).all()
```

### Error Handling
```python
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

try:
    db.add(new_record)
    db.commit()
except IntegrityError as e:
    db.rollback()
    raise HTTPException(status_code=400, detail="Duplicate entry")
```

### Check Existence
```python
exists = db.query(SiswaORM).filter(SiswaORM.id == siswa_id).first() is not None
```

### Bulk Operations
```python
# Multiple inserts
siswa_list = [
    SiswaORM(nama="John", email="john@example.com"),
    SiswaORM(nama="Jane", email="jane@example.com"),
]
db.add_all(siswa_list)
db.commit()
```

### Raw SQL (if needed)
```python
from sqlalchemy import text

result = db.execute(
    text("SELECT * FROM siswa WHERE nama = :nama"),
    {"nama": "John"}
).all()
```

## Model Definition

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class SiswaORM(Base):
    __tablename__ = "siswa"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    
    # Optional: timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Testing with SQLAlchemy

```python
# conftest.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# test_main.py
def test_create_siswa(client):
    response = client.post("/siswa/", json={"nama": "Test", "email": "test@example.com"})
    assert response.status_code == 201
```

## Common Patterns

### Create if Not Exists
```python
siswa = db.query(SiswaORM).filter(SiswaORM.email == email).first()
if not siswa:
    siswa = SiswaORM(nama=nama, email=email)
    db.add(siswa)
    db.commit()
    db.refresh(siswa)
return siswa
```

### Update or Create
```python
siswa = db.query(SiswaORM).filter(SiswaORM.email == email).first()
if siswa:
    siswa.nama = nama
else:
    siswa = SiswaORM(nama=nama, email=email)
    db.add(siswa)
db.commit()
db.refresh(siswa)
return siswa
```

### Transaction Rollback
```python
try:
    db.add(new_record)
    db.commit()
except Exception as e:
    db.rollback()
    raise
```

### Refresh Object
```python
siswa = SiswaORM(nama="John", email="john@example.com")
db.add(siswa)
db.commit()
db.refresh(siswa)  # Get auto-generated ID
print(siswa.id)
```

## Database Configuration

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./siswa.db"
# or PostgreSQL: "postgresql://user:password@localhost/dbname"
# or MySQL: "mysql+pymysql://user:password@localhost/dbname"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite only
    echo=False  # Set True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Useful SQLAlchemy Methods

| Method | Purpose |
|--------|---------|
| `db.query()` | Create query object |
| `.filter()` | Add WHERE clause |
| `.all()` | Get all results |
| `.first()` | Get first result |
| `.one()` | Get exactly one (error if not) |
| `.count()` | Get row count |
| `.order_by()` | Add ORDER BY |
| `.limit()` | Add LIMIT |
| `.offset()` | Add OFFSET |
| `db.add()` | Mark for insert |
| `db.add_all()` | Mark multiple for insert |
| `db.commit()` | Commit transaction |
| `db.rollback()` | Rollback transaction |
| `db.delete()` | Mark for delete |
| `db.refresh()` | Refresh object from DB |

---

For full documentation, see `SQLALCHEMY_MIGRATION.md`
