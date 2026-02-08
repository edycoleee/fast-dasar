# Belajar FastAPI - Panduan Tahapan

## 🎯 Untuk Anda yang Sudah Familiar dengan Flask & Node.js

FastAPI adalah framework modern Python yang menggabungkan kecepatan Node.js dengan kemudahan Flask, plus type safety dan auto-documentation!

---

## Belajar FastAPI

### **Router - Mengorganisir Endpoints**

#### Apa itu Router?

Router adalah cara untuk **mengorganisir dan mengelompokkan endpoint** yang terkait. Ibaratnya seperti folder - kita tidak menyimpan semua file di folder akar, tapi diorganisir ke subfolder berdasarkan kategori.

**Tanpa Router (buruk untuk project besar):**
```python
from fastapi import FastAPI

app = FastAPI()

# Semua endpoint di satu file - berantakan!
@app.get("/halo/")
async def halo():
    pass

@app.post("/halo/")
async def halo_post():
    pass

@app.get("/siswa/")
async def siswa():
    pass

@app.get("/user/")
async def user():
    pass

@app.post("/user/")
async def user_post():
    pass

# ... ratusan endpoint lagi - CHAOS! 🤯
```

**Dengan Router (baik dan rapi):**
```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Router untuk Halo endpoints
halo_router = APIRouter(prefix="/halo", tags=["Halo"])

@halo_router.get("/")
async def halo():
    pass

@halo_router.post("/")
async def halo_post():
    pass

# Router untuk Siswa endpoints
siswa_router = APIRouter(prefix="/siswa", tags=["Siswa"])

@siswa_router.get("/")
async def siswa():
    pass

# Gabungkan semua router ke app
app.include_router(halo_router)
app.include_router(siswa_router)
```

#### Keuntungan Router:

| Aspek | Tanpa Router | Dengan Router |
|-------|--------------|---------------|
| **Organisasi** | Berantakan | Rapi & modular |
| **Reusability** | Sulit | Mudah |
| **Maintainability** | Susah di-maintain | Mudah di-maintain |
| **Skala besar** | Buruk | Sempurna |
| **Team work** | Konflik merge | Minimal konflik |

#### Parameter Router Penting:

```python
router = APIRouter(
    prefix="/api/v1/siswa",        # Prefix URL
    tags=["Siswa"],                # Tag di docs
    responses={404: {"description": "Not found"}},  # Dokumentasi
)
```

- **prefix**: URL base untuk semua endpoint di router ini
  - Jika endpoint punya `/`, URL akhir: `/api/v1/siswa/`
  - Menghemat pengetikan dan konsisten! ✅

- **tags**: Untuk mengelompokkan di dokumentasi Swagger/ReDoc
  - Membuat docs lebih rapi

#### Struktur Folder Recommended:

```
project/
├── main.py                 (main entry point)
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── halo.py      (router halo)
│   │   │   │   └── siswa.py     (router siswa)
│   │   │   └── api.py           (aggregator router)
│   ├── models/             (database models)
│   ├── schemas/            (pydantic models)
│   ├── services/           (business logic)
│   └── core/               (config, settings)
└── tests/
    └── test_main.py
```

#### Contoh Implementasi:

**File: app/api/v1/endpoints/halo.py**
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/halo", tags=["Halo"])

class HaloRequest(BaseModel):
    nama: str
    handphone: str

@router.get("/")
async def halo_get():
    """Dapatkan ucapan halo"""
    return {"success": True, "message": "Get from Halo API", "data": []}

@router.post("/")
async def halo_post(data: HaloRequest):
    """Kirim nama dan handphone"""
    return {
        "message": f"Halo {data.nama}!",
        "nama": data.nama,
        "handphone": data.handphone
    }
```

**File: app/api/v1/endpoints/siswa.py**
```python
from fastapi import APIRouter

router = APIRouter(prefix="/siswa", tags=["Siswa"])

@router.get("/")
async def siswa_get():
    """Dapatkan data siswa"""
    return {
        "success": True,
        "message": "Get from siswa API",
        "data": [
            {"no": 1, "nama": "Edy", "email": "edycoleee@gmail.com"}
        ]
    }
```

**File: app/api/v1/api.py**
```python
from fastapi import APIRouter
from app.api.v1.endpoints import halo, siswa

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(halo.router)
api_router.include_router(siswa.router)
```

**File: main.py**
```python
from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(
    title="Halo API",
    description="API sederhana untuk belajar FastAPI",
    version="1.0.0"
)

# Include router
app.include_router(api_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "FastAPI is running!"}
```

#### Hasil dengan Router:

Sekarang URL endpoint adalah:
- `/api/v1/halo/` (GET & POST)
- `/api/v1/siswa/` (GET)

Dan di dokumentasi Swagger, semua endpoint sudah terorganisir per tag! 📚

#### Perbedaan dengan Flask & Node.js:

| Framework | Router | Syntax |
|-----------|--------|--------|
| **Flask** | Blueprint | `@blueprint.route()` |
| **Express (Node.js)** | Router | `router.get()` / `router.post()` |
| **FastAPI** | APIRouter | `router.get()` / `router.post()` |

Semuanya konsep yang sama - hanya nama dan syntax yang beda! ✨

---

### **Instalasi & Menjalankan**

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


---

### **Testing API**

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

---

### **Troubleshooting Pytest**

#### Problem: `ModuleNotFoundError: No module named 'main'`

**Apa yang terjadi?**

Saat menjalankan pytest, Anda mungkin mendapat error:
```
E   ModuleNotFoundError: No module named 'main'
```

Ini terjadi karena pytest tidak bisa menemukan module `main.py` dari directory `tests/`.

**Penyebab:**

- Python path tidak dikonfigurasi dengan benar
- Directory `tests/` bukan package (tidak ada `__init__.py`)
- Pytest tidak tahu harus cari file dari directory mana

**Solusi yang Sudah Diterapkan:**

Saya sudah menambahkan 3 file konfigurasi:

#### 1. **[pytest.ini](pytest.ini)** - Konfigurasi Pytest

```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**Penjelasan:**
- `pythonpath = .`: Tambahkan root directory ke Python path
- `testpaths = tests`: Pytest hanya cari test di folder `tests/`
- `python_files = test_*.py`: Hanya file dengan prefix `test_` yang dianggap test file

#### 2. **[tests/conftest.py](tests/conftest.py)** - Setup Path

```python
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

**Penjelasan:**
- `conftest.py` dijalankan otomatis oleh pytest sebelum menjalankan test
- Menambahkan project root ke `sys.path` agar bisa import `main`
- Ini memastikan pytest bisa menemukan module di root directory

#### 3. **[tests/__init__.py](tests/__init__.py)** - Make Tests a Package

File kosong, tapi penting untuk membuat `tests` menjadi Python package.

**Hasil:**

Sekarang pytest bisa menemukan module `main` dan menjalankan semua test dengan benar! ✅

```bash
$ pytest -v
collected 7 items

tests/test_main.py::test_root PASSED
tests/test_main.py::test_halo_get PASSED
tests/test_main.py::test_halo_post_success PASSED
...
====== 7 passed in 0.84s ======
```

---

#### Perbedaan Konfigurasi di Framework Lain:

| Framework | Solusi | File Konfigurasi |
|-----------|--------|------------------|
| **Flask** | Pakai `pytest-flask` fixture | `conftest.py` |
| **FastAPI** | Pakai `TestClient` + path setup | `pytest.ini` + `conftest.py` |
| **Express (Node.js)** | Pakai `jest` + setup file | `jest.config.js` |

FastAPI approach kita **lebih simple dan clean** karena TestClient langsung bisa test tanpa perlu setup kompleks! 🎉

---
