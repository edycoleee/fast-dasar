# Belajar FastAPI - Panduan Tahapan

FastAPI adalah framework modern Python yang menggabungkan kecepatan Node.js dengan kemudahan Flask, plus type safety dan auto-documentation!

---

## 📚 Tahapan Belajar FastAPI

### **Tahap 1: Konsep Dasar**

#### Perbedaan dengan Flask & Node.js:

| Aspek | Flask | Node.js/Express | FastAPI |
|-------|-------|-----------------|---------|
| Type Hints | ❌ Tidak wajib | ❌ Tidak (pakai TS) | ✅ Wajib & otomatis validasi |
| Async/Await | ⚠️ Manual setup | ✅ Native | ✅ Native |
| Validasi Data | Manual (Flask-RESTful) | Manual (Joi, etc) | ✅ Otomatis (Pydantic) |
| Dokumentasi API | Manual (Swagger) | Manual (Swagger) | ✅ Auto-generate |
| Performance | ~20k req/s | ~30k req/s | ~40k req/s |

#### Yang Mirip:
```python
# Flask
@app.route('/api/halo/', methods=['GET'])
def halo():
    return {"message": "Halo"}

# Express (Node.js)
app.get('/api/halo/', (req, res) => {
    res.json({message: "Halo"});
});

# FastAPI
@app.get("/api/halo/")
async def halo():
    return {"message": "Halo"}
```

---

### **Tahap 2: Pydantic Models (Keunggulan Utama FastAPI)**

```python
# Ini yang membedakan FastAPI!
class HaloRequest(BaseModel):
    nama: str           # Wajib string
    handphone: str      # Wajib string
    umur: int = 0       # Opsional dengan default

# FastAPI otomatis validasi:
# ✅ Cek tipe data
# ✅ Convert jika perlu
# ✅ Return error 422 jika tidak valid
```

**Bandingkan dengan Flask:**
```python
# Flask - manual validation
data = request.get_json()
if not data or 'nama' not in data:
    return {"error": "nama required"}, 400
nama = data['nama']
```

**Bandingkan dengan Express:**
```javascript
// Express - perlu library tambahan
const { body, validationResult } = require('express-validator');

app.post('/api/halo/', 
  body('nama').isString(),
  (req, res) => {
    const errors = validationResult(req);
    // manual handling...
  }
);
```

---

### **Tahap 3: Instalasi & Menjalankan**

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

**Perbedaan dengan Flask/Node:**
```bash
# Flask
flask run

# Node.js
node app.js
# atau: nodemon app.js

# FastAPI
uvicorn main:app --reload
# --reload: auto-restart saat file berubah (seperti nodemon)
```

---

### **Tahap 4: Testing API**

#### 1. **Gunakan Interactive Docs (GRATIS!)**

Buka browser:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

Ini otomatis di-generate! Tidak perlu setup Swagger manual seperti di Flask/Express.

#### 2. **Gunakan cURL:**

```bash
# GET request
curl http://127.0.0.1:8000/api/halo/

# POST request
curl -X POST http://127.0.0.1:8000/api/halo/ \
  -H "Content-Type: application/json" \
  -d '{"nama": "Edy", "handphone": "08111111"}'
```

#### 3. **Gunakan Python requests:**

```python
import requests

# GET
response = requests.get("http://127.0.0.1:8000/api/halo/")
print(response.json())

# POST
data = {"nama": "Edy", "handphone": "08111111"}
response = requests.post("http://127.0.0.1:8000/api/halo/", json=data)
print(response.json())
```

#### 4. **Gunakan Unit test :**

FastAPI menyediakan `TestClient` untuk testing yang mudah:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test GET endpoint
def test_halo_get():
    response = client.get("/api/halo/")
    assert response.status_code == 200
    assert response.json() == {"message": "Halo! Welcome to FastAPI"}

# Test POST endpoint
def test_halo_post():
    payload = {"nama": "Sultan", "handphone": "08123456789"}
    response = client.post("/api/halo/", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Halo Sultan!"

# Test validasi (error handling)
def test_halo_post_validation_error():
    payload = {"nama": "Sultan"}  # handphone missing
    response = client.post("/api/halo/", json=payload)
    assert response.status_code == 422  # Validation error
```

**Menjalankan test:**

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

**Perbedaan dengan Flask/Express:**

| Framework | Testing Library | Setup |
|-----------|-----------------|-------|
| Flask | `pytest` + `client` | Perlu setup app context |
| Express | `jest` / `mocha` + `supertest` | Setup server manually |
| FastAPI | `pytest` + `TestClient` | Paling simple & clean! |

---

### **Tahap 5: Konsep Lanjutan (Next Steps)**

Setelah menguasai dasar, lanjutkan dengan:

1. **Path Parameters & Query Parameters**
   ```python
   @app.get("/users/{user_id}")
   async def get_user(user_id: int, skip: int = 0):
       pass
   ```

2. **Database Integration** (SQLAlchemy/Tortoise ORM)
   ```python
   from sqlalchemy import create_engine
   # Mirip dengan Sequelize di Node.js
   ```

3. **Authentication (JWT)**
   ```python
   from fastapi.security import OAuth2PasswordBearer
   ```

4. **Dependency Injection**
   ```python
   # Konsep unik FastAPI - sangat powerful!
   @app.get("/items/")
   async def read_items(commons: dict = Depends(common_parameters)):
       pass
   ```

5. **Background Tasks**
   ```python
   from fastapi import BackgroundTasks
   # Untuk email, logging, etc
   ```

6. **WebSockets**
   ```python
   @app.websocket("/ws")
   async def websocket_endpoint(websocket: WebSocket):
       pass
   ```

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# Open browser
# Docs: http://127.0.0.1:8000/docs
# API: http://127.0.0.1:8000/api/halo/
```

---

## 📖 Resources

- **Official Docs**: https://fastapi.tiangolo.com/
- **Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **GitHub**: https://github.com/tiangolo/fastapi

---

## 💡 Tips untuk Developer Flask/Node.js

1. **Async is Optional**: Bisa pakai `def` biasa kalau tidak perlu async
   ```python
   @app.get("/sync")
   def sync_endpoint():  # Tanpa async, tetap jalan
       return {"message": "OK"}
   ```

2. **Type Hints is Key**: Manfaatkan type hints untuk validasi otomatis

3. **Pydantic = Joi + Class Validator**: Satu library untuk semua validasi

4. **Dependency Injection**: Konsep baru yang sangat berguna untuk reusable code

5. **Auto Docs**: Jangan lupa dokumentasikan dengan docstring, otomatis masuk ke Swagger!

---

## 🎓 Learning Path

```
Week 1: Basic CRUD ← Anda di sini
Week 2: Database Integration (SQLAlchemy)
Week 3: Authentication & Authorization
Week 4: Advanced Features (WebSocket, Background Tasks)
Week 5: Testing & Deployment
```

Selamat belajar! 🚀
