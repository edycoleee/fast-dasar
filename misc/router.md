# Week 1a: Router Basic & Unit Testing

## 📚 Pelajaran: Routing di FastAPI

### 🎯 Tujuan Pembelajaran
Memahami cara membuat routing dasar di FastAPI dan melakukan unit testing untuk memastikan endpoint berfungsi dengan baik.

---

## 1. Router Basic - Membuat Endpoint

### Endpoint 1: GET /api/halo/

```python
@app.get("/api/halo/")
async def halo_get():
    """
    Endpoint GET sederhana yang mengembalikan pesan halo.
    
    Mirip dengan:
    - Flask: @app.route('/api/halo/', methods=['GET'])
    - Express: app.get('/api/halo/', ...)
    """
    return {
        "success": True, 
        "message": "Get from Halo API", 
        "data": []
    }
```

**Response:**
```json
{
  "success": true,
  "message": "Get from Halo API",
  "data": []
}
```

### Endpoint 2: GET /api/siswa/

```python
@app.get("/api/siswa/")
async def siswa_get():
    """
    Endpoint GET yang mengembalikan data siswa.
    
    Untuk tahap belajar ini, data masih hardcoded.
    Nanti akan diganti dengan database (Week 1b - SQLite).
    """
    return {
        "success": True, 
        "message": "Get from siswa API", 
        "data": [
            {
                "no": 1, 
                "nama": "Edy", 
                "email": "edycoleee@gmail.com"
            }
        ]
    }
```

**Response:**
```json
{
  "success": true,
  "message": "Get from siswa API",
  "data": [
    {
      "no": 1,
      "nama": "Edy",
      "email": "edycoleee@gmail.com"
    }
  ]
}
```

### Endpoint 3: POST /api/halo/

```python
from pydantic import BaseModel

class HaloRequest(BaseModel):
    nama: str
    handphone: str

@app.post("/api/halo/", response_model=HaloResponse)
async def halo_post(data: HaloRequest):
    """
    Endpoint POST yang menerima data nama dan handphone.
    
    Perbedaan dengan Flask/Express:
    - Tidak perlu manual parsing request.json atau req.body
    - Pydantic otomatis validasi tipe data
    - Auto-generate OpenAPI documentation
    """
    return {
        "message": f"Halo {data.nama}!",
        "nama": data.nama,
        "handphone": data.handphone
    }
```

**Request Body:**
```json
{
  "nama": "John Doe",
  "handphone": "081234567890"
}
```

**Response:**
```json
{
  "message": "Halo John Doe!",
  "nama": "John Doe",
  "handphone": "081234567890"
}
```

---

## 2. Struktur Response yang Konsisten

### Best Practice: Format Response

Untuk menjaga konsistensi, gunakan format response yang seragam:

```python
{
    "success": bool,      # Status operasi
    "message": str,       # Pesan deskriptif
    "data": list/dict     # Data actual
}
```

**Contoh Success Response:**
```json
{
    "success": true,
    "message": "Data retrieved successfully",
    "data": [...]
}
```

**Contoh Error Response:**
```json
{
    "success": false,
    "message": "Data not found",
    "data": []
}
```

---

## 3. Testing API

### A. Manual Testing dengan cURL

```bash
# Test GET endpoint halo
curl http://127.0.0.1:8000/api/halo/

# Test GET endpoint siswa
curl http://127.0.0.1:8000/api/siswa/

# Test POST endpoint halo
curl -X POST http://127.0.0.1:8000/api/halo/ \
  -H "Content-Type: application/json" \
  -d '{"nama": "John", "handphone": "081234567890"}'
```

### B. Testing dengan Swagger UI

FastAPI menyediakan dokumentasi interaktif otomatis:

1. Buka browser: http://127.0.0.1:8000/docs
2. Klik endpoint yang ingin di-test
3. Klik "Try it out"
4. Isi parameter (jika ada)
5. Klik "Execute"

**Keunggulan:**
- ✅ Tidak perlu install Postman atau tools lain
- ✅ Otomatis di-generate dari kode
- ✅ Bisa test langsung dari browser
- ✅ Dokumentasi selalu sync dengan kode

---

## 4. Unit Testing dengan Pytest

### Setup Testing

**Install dependencies:**
```bash
pip install pytest httpx pytest-cov
```

**requirements.txt:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3

# Testing
pytest==7.4.4
httpx==0.24.1
pytest-cov==4.1.0
```

### Struktur Test File

```python
"""
test_main.py
Unit Test untuk FastAPI Basic Router
"""

import pytest
from fastapi.testclient import TestClient
from main import app

# Fixture untuk test client
@pytest.fixture
def client():
    """Buat test client untuk setiap test"""
    return TestClient(app)
```

### Test Class Organization

```python
class TestHaloEndpoint:
    """Test untuk endpoint /api/halo/"""
    
    def test_halo_get_success(self, client):
        """Test GET /api/halo/ mengembalikan response yang benar"""
        response = client.get("/api/halo/")
        
        # Assert status code
        assert response.status_code == 200
        
        # Assert response body
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Get from Halo API"
        assert data["data"] == []
```

### Jenis-jenis Test

#### 1. Test Success Case
```python
def test_siswa_get_success(self, client):
    """Test endpoint berhasil mengembalikan data"""
    response = client.get("/api/siswa/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

#### 2. Test Response Structure
```python
def test_siswa_get_data_structure(self, client):
    """Test struktur data sesuai spec"""
    response = client.get("/api/siswa/")
    data = response.json()
    
    # Assert memiliki key yang benar
    assert "success" in data
    assert "message" in data
    assert "data" in data
    
    # Assert data siswa memiliki field yang benar
    siswa = data["data"][0]
    assert "no" in siswa
    assert "nama" in siswa
    assert "email" in siswa
```

#### 3. Test Data Content
```python
def test_siswa_get_data_content(self, client):
    """Test konten data sesuai yang diharapkan"""
    response = client.get("/api/siswa/")
    data = response.json()
    
    siswa = data["data"][0]
    assert siswa["no"] == 1
    assert siswa["nama"] == "Edy"
    assert siswa["email"] == "edycoleee@gmail.com"
```

#### 4. Test Validation Error
```python
def test_halo_post_missing_field(self, client):
    """Test POST dengan field yang hilang"""
    payload = {"nama": "John Doe"}  # handphone missing
    
    response = client.post("/api/halo/", json=payload)
    
    # Pydantic validation error
    assert response.status_code == 422
```

#### 5. Test 404 Not Found
```python
def test_endpoint_not_found(self, client):
    """Test endpoint yang tidak ada"""
    response = client.get("/api/tidak-ada/")
    
    assert response.status_code == 404
```

### Menjalankan Test

```bash
# Run all tests
pytest test_main.py -v

# Run specific test class
pytest test_main.py::TestSiswaEndpoint -v

# Run specific test method
pytest test_main.py::TestSiswaEndpoint::test_siswa_get_success -v

# Run with coverage
pytest test_main.py -v --cov=main --cov-report=term-missing

# Run with coverage HTML report
pytest test_main.py --cov=main --cov-report=html
```

### Test Output

```
=================================== test session starts ===================================
platform darwin -- Python 3.11.0, pytest-9.0.2, pluggy-1.6.0
collected 11 items

test_main.py::TestHaloEndpoint::test_halo_get_success PASSED                        [  9%]
test_main.py::TestHaloEndpoint::test_halo_get_response_structure PASSED             [ 18%]
test_main.py::TestSiswaEndpoint::test_siswa_get_success PASSED                      [ 27%]
test_main.py::TestSiswaEndpoint::test_siswa_get_data_structure PASSED               [ 36%]
test_main.py::TestSiswaEndpoint::test_siswa_get_data_content PASSED                 [ 45%]
test_main.py::TestRootEndpoint::test_root_endpoint PASSED                           [ 54%]
test_main.py::TestNotFoundEndpoint::test_endpoint_not_found PASSED                  [ 63%]
test_main.py::TestNotFoundEndpoint::test_wrong_method PASSED                        [ 72%]
test_main.py::TestHaloPostEndpoint::test_halo_post_success PASSED                   [ 81%]
test_main.py::TestHaloPostEndpoint::test_halo_post_missing_field PASSED             [ 90%]
test_main.py::TestHaloPostEndpoint::test_halo_post_wrong_type PASSED                [100%]

===================================== tests coverage ======================================
Name      Stmts   Miss  Cover   Missing
---------------------------------------
main.py      22      0   100%
---------------------------------------
TOTAL        22      0   100%
=================================== 11 passed in 0.23s ====================================
```

**✅ 11 tests passed with 100% code coverage!**

---

## 5. Perbandingan dengan Framework Lain

### Routing Comparison

| Framework | Route Definition | Request Data | Validation |
|-----------|-----------------|--------------|------------|
| **Flask** | `@app.route('/api/halo/', methods=['GET'])` | `request.get_json()` | Manual |
| **Express** | `app.get('/api/halo/', (req, res) => {})` | `req.body` | Manual (Joi, etc) |
| **FastAPI** | `@app.get("/api/halo/")` | Function parameter | Auto (Pydantic) |

### Testing Comparison

| Framework | Testing Library | Test Client | Async Support |
|-----------|----------------|-------------|---------------|
| **Flask** | unittest/pytest | `app.test_client()` | ⚠️ Limited |
| **Express** | Jest/Mocha | supertest | ✅ Yes |
| **FastAPI** | pytest | `TestClient(app)` | ✅ Yes |

---

## 6. Key Takeaways

### ✅ Yang Sudah Dipelajari:

1. **Basic Routing**
   - GET endpoint untuk retrieve data
   - POST endpoint untuk submit data
   - Response format yang konsisten

2. **Pydantic Validation**
   - Automatic data validation
   - Type safety
   - Clear error messages (422)

3. **Auto Documentation**
   - Swagger UI otomatis
   - ReDoc otomatis
   - OpenAPI schema

4. **Unit Testing**
   - Setup pytest dengan TestClient
   - Test success cases
   - Test validation errors
   - Test edge cases (404, wrong method)
   - Code coverage 100%

### 🎯 Best Practices:

1. **Gunakan async/await** untuk performance yang lebih baik
2. **Konsisten dengan response format** untuk memudahkan frontend
3. **Selalu buat unit test** untuk setiap endpoint
4. **Dokumentasikan endpoint** dengan docstring
5. **Validasi input** dengan Pydantic models

### 🚀 Next Steps (Week 1b):

- CRUD operations (Create, Read, Update, Delete)
- Database integration dengan SQLite
- SQLAlchemy ORM
- Error handling yang lebih baik
- Response models

---

## 7. Cheatsheet

### FastAPI Decorators

```python
@app.get("/path")          # GET request
@app.post("/path")         # POST request
@app.put("/path")          # PUT request
@app.patch("/path")        # PATCH request
@app.delete("/path")       # DELETE request
```

### Pytest Assertions

```python
assert value == expected           # Equality
assert "key" in dict              # Membership
assert response.status_code == 200 # Status code
assert isinstance(data, list)      # Type checking
```

### HTTP Status Codes

```
200 OK                    # Success
201 Created              # Resource created
400 Bad Request          # Client error
404 Not Found            # Resource not found
422 Unprocessable Entity # Validation error
500 Internal Server Error # Server error
```

---

## 📁 File Structure

```
fast-dasar/
├── main.py              # FastAPI application
├── test_main.py         # Unit tests
├── requirements.txt     # Dependencies
├── README.md           # Project documentation
├── router.md           # Router learning notes (this file)
├── .gitignore          # Git ignore rules
└── venv/               # Virtual environment
```

---

## 🔗 Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pytest Docs**: https://docs.pytest.org/
- **Pydantic Docs**: https://docs.pydantic.dev/

---

**Completed**: February 5, 2026  
**Duration**: Week 1a  
**Status**: ✅ Router Basic & Unit Testing Completed with 100% Coverage
