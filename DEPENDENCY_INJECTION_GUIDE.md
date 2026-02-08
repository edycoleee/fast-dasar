# Dependency Injection di FastAPI

## Pengenalan

**Dependency Injection (DI)** adalah design pattern yang memisahkan "apa yang diperlukan" dari "cara mendapatkannya". FastAPI membuat DI menjadi **mudah dan powerful** dibanding framework lain.

---

## Perbandingan: FastAPI vs Flask vs Node.js

### 1️⃣ **Node.js (Express.js)** - Middleware Pattern

```javascript
// Node.js: Database passed through middleware
const express = require('express');
const app = express();

// Middleware untuk attach database ke request
app.use((req, res, next) => {
    req.db = new Database();  // Manual setup
    next();
});

// Endpoint harus akses req.db secara manual
app.post('/siswa', (req, res) => {
    const db = req.db;  // ❌ Implicit, harus tahu req memiliki db
    const siswa = new Siswa(req.body.nama, req.body.email);
    db.save(siswa);
    res.json(siswa);
});

// Masalah:
// ❌ Tidak jelas apa dependencies-nya dari function signature
// ❌ Type checking sulit
// ❌ Testing perlu mock req object
// ❌ Bisa lupa attach db di middleware tertentu
```

### 2️⃣ **Flask** - Manual Parameter Passing

```python
# Flask: Database passed sebagai parameter global
from flask import Flask, request, g
import sqlite3

app = Flask(__name__)

# Get database per request
def get_db():
    db = g.pop('db', None)
    if db is None:
        db = sqlite3.connect('siswa.db')
        g.db = db
    return db

# Endpoint harus panggil get_db() manual
@app.route('/siswa', methods=['POST'])
def create_siswa():
    db = get_db()  # ❌ Manual call, easy to forget
    siswa_data = request.json
    db.execute("INSERT INTO siswa ...")
    return jsonify(siswa)

# Masalah:
# ❌ Boilerplate: setiap endpoint harus panggil get_db()
# ❌ Tidak type-safe
# ❌ Global state (g object) - thread-safety issues
# ❌ Testing perlu setup context manager
```

### 3️⃣ **FastAPI** - Dependency Injection (✅ Modern)

```python
# FastAPI: Dependencies declared explicitly in function signature
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, SiswaORM

router = APIRouter()

# Dependencies declared explicitly dengan type hints
@router.post('/siswa')
async def create_siswa(
    siswa: SiswaCreate,
    db: Session = Depends(get_db)  # ✅ Clear, explicit dependency
):
    new_siswa = SiswaORM(nama=siswa.nama, email=siswa.email)
    db.add(new_siswa)
    db.commit()
    db.refresh(new_siswa)
    return new_siswa

# Keuntungan:
# ✅ Dependencies explicit di function signature
# ✅ Type-safe (db: Session dengan type hint)
# ✅ IDE autocomplete works perfectly
# ✅ Auto documentation in Swagger
# ✅ Easy to test (override dependency)
# ✅ Dependency resolved automatically
```

---

## Bagaimana Dependency Injection Bekerja?

### Konsep Dasar

```python
# Step 1: Define dependency function
def get_db():
    """Callable yang mengembalikan database session"""
    db = SessionLocal()
    try:
        yield db  # Endpoint receives this
    finally:
        db.close()  # Cleanup after endpoint done

# Step 2: Declare dependency di endpoint
@app.post('/siswa')
async def create_siswa(
    siswa: SiswaCreate,
    db: Session = Depends(get_db)  # ← Magic happens here!
):
    # db sudah ready, tidak perlu instantiate manual
    db.add(...)
    db.commit()

# Step 3: FastAPI automatically:
# 1. Detects "db: Session = Depends(get_db)"
# 2. Calls get_db()
# 3. Gets the yielded db
# 4. Passes db ke endpoint
# 5. Cleanup saat endpoint selesai
```

### Execution Flow

```
Request masuk ke create_siswa()
    ↓
FastAPI detects: db: Session = Depends(get_db)
    ↓
FastAPI calls: get_db()
    ↓
get_db() yields: db = SessionLocal()
    ↓
Endpoint menerima: db (SQLAlchemy Session)
    ↓
Endpoint berjalan:
    new_siswa = SiswaORM(...)
    db.add(new_siswa)
    db.commit()
    ↓
Endpoint selesai (return)
    ↓
FastAPI continues: finally block di get_db()
    ↓
get_db() executes: db.close()
    ↓
Response sent to client
```

---

## Perbedaan Jelas: 3 Framework

| Aspek | Node.js | Flask | FastAPI |
|-------|---------|-------|---------|
| **Deklarasi Dependency** | Global middleware | Manual function call | Explicit parameter |
| **Type Safety** | ❌ No types | ⚠️ Manual checking | ✅ Full type hints |
| **Cleanup** | Manual in middleware | teardown handlers | Automatic with yield |
| **IDE Support** | ❌ Basic | ⚠️ Limited | ✅ Full autocomplete |
| **Documentation** | Manual | Manual | ✅ Auto Swagger |
| **Testing** | Mock req object | Context manager | Override dependency |
| **Thread Safety** | ⚠️ Be careful | ⚠️ Global g object | ✅ Request-scoped |
| **Boilerplate** | Minimal | Moderate | ✅ Minimal |

---

## Implementasi Detail di FastAPI

### 1. Simple Dependency (Tidak ada resource cleanup)

```python
# Dependency tanpa yield (tidak perlu cleanup)
def get_current_user(token: str) -> User:
    """Extract user dari token"""
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.get('/profile')
async def get_profile(user: User = Depends(get_current_user)):
    return {"user": user.name}
```

### 2. Resource Dependency (Dengan cleanup)

```python
# Dependency dengan resource management (yield)
from sqlalchemy.orm import Session

def get_db():
    """Database session dengan auto-cleanup"""
    db = SessionLocal()
    try:
        yield db  # Endpoint receives this
    finally:
        db.close()  # Auto cleanup

@app.post('/siswa')
async def create_siswa(
    siswa: SiswaCreate,
    db: Session = Depends(get_db)  # ← Database auto-managed
):
    db.add(SiswaORM(...))
    db.commit()
    return siswa
```

### 3. Chained Dependencies (Multiple levels)

```python
# Level 1: Get database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Level 2: Get user dari database
def get_current_user(
    db: Session = Depends(get_db)  # ← Depends on get_db
) -> User:
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401)
    return user

# Level 3: Use dalam endpoint
@app.get('/profile')
async def get_profile(
    user: User = Depends(get_current_user)  # ← Depends on get_current_user
):
    return {"name": user.name}

# FastAPI automatically resolves:
# get_profile → depends on get_current_user → depends on get_db
```

### 4. Optional Dependencies

```python
from typing import Optional

def get_optional_db() -> Optional[Session]:
    """Optional database session"""
    try:
        db = SessionLocal()
        yield db
    except:
        yield None
    finally:
        if db:
            db.close()

@app.get('/data')
async def get_data(db: Optional[Session] = Depends(get_optional_db)):
    if db:
        # Database available
        data = db.query(...)
    else:
        # Fallback
        data = []
    return data
```

---

## Mengapa FastAPI lebih baik?

### Masalah Node.js Approach

```javascript
// ❌ Node.js: Implicit dependencies
app.post('/siswa', (req, res) => {
    const db = req.db;  // Dari mana db ini? Tidak jelas!
    // Jika middleware tidak attach db:
    // → TypeError: Cannot read property 'db' of undefined
    // → Hard to debug
    // → No IDE hints
});
```

### Masalah Flask Approach

```python
# ❌ Flask: Must remember to call get_db()
@app.route('/siswa', methods=['POST'])
def create_siswa():
    db = get_db()  # Mudah lupa
    # Jika lupa:
    # → AttributeError: 'NoneType' object has no attribute 'query'
    # → Every endpoint punya boilerplate yang sama

# Boilerplate repeatition:
@app.route('/endpoint1', methods=['GET'])
def endpoint1():
    db = get_db()  # Repeat
    ...

@app.route('/endpoint2', methods=['POST'])
def endpoint2():
    db = get_db()  # Repeat
    ...

@app.route('/endpoint3', methods=['DELETE'])
def endpoint3():
    db = get_db()  # Repeat
    ...
```

### Solusi FastAPI

```python
# ✅ FastAPI: Explicit, type-safe, no boilerplate
@router.get('/endpoint1')
async def endpoint1(db: Session = Depends(get_db)):
    # db auto-injected, type-safe, IDE knows about it
    ...

@router.post('/endpoint2')
async def endpoint2(db: Session = Depends(get_db)):
    # Same pattern, consistent, clean
    ...

@router.delete('/endpoint3')
async def endpoint3(db: Session = Depends(get_db)):
    # Auto-documented, auto-cleanup, perfect for testing
    ...
```

---

## Testing: Dependency Override

### Node.js Testing

```javascript
// ❌ Node.js: Must mock entire req object
app.post('/siswa', (req, res) => {
    const db = req.db;
    db.save(req.body);
});

// Test - Messy:
describe('create_siswa', () => {
    it('should create siswa', () => {
        const mockDb = {
            save: jest.fn()
        };
        const mockReq = {
            db: mockDb,           // ❌ Manual mock req
            body: { nama: 'John' }
        };
        const mockRes = { json: jest.fn() };
        
        create_siswa(mockReq, mockRes);
        expect(mockDb.save).toHaveBeenCalled();
    });
});
```

### Flask Testing

```python
# ⚠️ Flask: Context manager required
@app.route('/siswa', methods=['POST'])
def create_siswa():
    db = g.get('db')
    db.save(request.json)

# Test - Context required:
def test_create_siswa():
    with app.app_context():  # ❌ Context boilerplate
        with app.test_request_context():  # ❌ More boilerplate
            g.db = mock_db
            response = create_siswa()
            assert response.status == 200
```

### FastAPI Testing ✅ Cleanest

```python
# ✅ FastAPI: Simple dependency override
def override_get_db():
    """Mock database for testing"""
    return MockDatabase()

@app.post('/siswa')
async def create_siswa(db: Session = Depends(get_db)):
    db.add(SiswaORM(...))
    db.commit()
    return siswa

# Test - Super clean:
def test_create_siswa(client):
    # Override dependency before making request
    app.dependency_overrides[get_db] = override_get_db
    
    response = client.post('/siswa', json={"nama": "John", "email": "john@example.com"})
    
    assert response.status_code == 201
    
    # Cleanup overrides
    app.dependency_overrides.clear()
```

---

## Contoh Praktis: Authentication + Database

### Node.js Way

```javascript
// Middleware-based (implicit)
app.use((req, res, next) => {
    req.db = new Database();
    next();
});

app.use((req, res, next) => {
    const token = req.headers.authorization;
    if (!token) return res.status(401).send('No token');
    req.user = verifyToken(token);
    next();
});

app.post('/siswa', (req, res) => {
    // Dependencies hidden in req object
    const { db, user } = req;
    if (!user) return res.status(401).send('Unauthorized');
    db.save(req.body);
    res.json(...);
});
```

### Flask Way

```python
# Manual function calls (repetitive)
@app.route('/siswa', methods=['POST'])
def create_siswa():
    db = get_db()  # Manual
    user = get_current_user()  # Manual
    
    if not user:
        abort(401)
    
    db.add(Siswa(...))
    db.commit()
    
    return jsonify(...)
```

### FastAPI Way ✅

```python
# Explicit, type-safe, auto-documented
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.post('/siswa')
async def create_siswa(
    siswa: SiswaCreate,
    user: User = Depends(get_current_user),  # ← Auth automatic
    db: Session = Depends(get_db)             # ← Database automatic
):
    # All dependencies resolved, type-safe, well-documented
    new_siswa = SiswaORM(nama=siswa.nama, email=siswa.email)
    db.add(new_siswa)
    db.commit()
    db.refresh(new_siswa)
    return new_siswa

# Automatic Swagger documentation shows:
# - Required header: Authorization token
# - Request body: SiswaCreate model
# - Returns: SiswaResponse model
# - Can fail with: 401 Unauthorized
```

---

## Best Practices

### 1. Keep Dependencies Focused

```python
# ✅ GOOD: Each dependency does one thing
def get_db():
    """Just get database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    """Just get user from token"""
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401)
    return user

# ❌ BAD: Dependency does too much
def get_everything(request: Request):
    db = get_db()
    user = verify_token(request)
    config = load_config()
    cache = get_redis()
    # Too many responsibilities!
    return {"db": db, "user": user, "config": config, "cache": cache}
```

### 2. Use Type Hints

```python
# ✅ GOOD: Clear type hints
@router.get('/siswa/{id}')
async def get_siswa(
    id: int,  # Type hint: int
    db: Session = Depends(get_db)  # Type hint: Session
) -> SiswaResponse:  # Type hint: return type
    siswa = db.query(SiswaORM).filter(SiswaORM.id == id).first()
    return siswa

# ❌ BAD: No type hints
@router.get('/siswa/{id}')
async def get_siswa(id, db=Depends(get_db)):
    # Hard to understand what types are expected
    siswa = db.query(...).first()
    return siswa
```

### 3. Error Handling in Dependencies

```python
# ✅ GOOD: Dependencies handle their own errors
def get_current_user(token: str = Header(...)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    
    try:
        user = decode_token(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user

# ❌ BAD: Push error handling to endpoint
def get_current_user(token: str = Header(...)):
    # Returns None on error - bad practice
    try:
        return decode_token(token)
    except:
        return None

@router.get('/profile')
async def get_profile(user = Depends(get_current_user)):
    if not user:  # ❌ Must check manually in endpoint
        raise HTTPException(status_code=401)
    ...
```

### 4. Resource Cleanup with Try/Finally

```python
# ✅ GOOD: Guaranteed cleanup
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Always called

# ⚠️ BAD: Cleanup might not happen
def get_db():
    db = SessionLocal()
    yield db
    db.close()  # Won't execute if exception before yield
```

---

## Kesimpulan

| Aspek | Node.js | Flask | FastAPI |
|-------|---------|-------|---------|
| **Clarity** | ⚠️ Implicit | ⚠️ Manual | ✅ Explicit |
| **Type Safety** | ❌ No | ⚠️ Optional | ✅ Full |
| **Boilerplate** | ✅ Min | ⚠️ Medium | ✅ Min |
| **Testing** | ⚠️ Complex | ⚠️ Medium | ✅ Simple |
| **Documentation** | ❌ Manual | ❌ Manual | ✅ Auto |
| **Error Handling** | ⚠️ Manual | ⚠️ Manual | ✅ Built-in |
| **Performance** | ✅ Fast | ✅ Good | ✅ Fast |

### 🎯 FastAPI Dependency Injection adalah **modern, clean, dan powerful**

---

## Resources

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Advanced Dependencies](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)
- [Dependency Injection Pattern](https://en.wikipedia.org/wiki/Dependency_injection)

---

## Ringkasan

```python
# FastAPI DI dalam satu pattern:

# 1. Define dependency (dengan resource management)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Declare di endpoint (explicit, type-safe)
@router.post('/siswa')
async def create_siswa(
    siswa: SiswaCreate,
    db: Session = Depends(get_db)  # ← Magic!
):
    # 3. Use dependency (clean, no boilerplate)
    db.add(SiswaORM(...))
    db.commit()
    
    # 4. Cleanup automatic (handled by FastAPI)

# Hasilnya: Clean code, type-safe, easy to test! ✨
```
