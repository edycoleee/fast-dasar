import uuid
from conftest import client


# Helper function untuk generate unique email
def generate_unique_email():
    """Generate unique email untuk setiap test"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


# ==================== Test Root Endpoint ====================

def test_root(client):
    """Test GET / endpoint - informasi API"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Siswa CRUD API is running!"
    assert data["version"] == "2.0.0"
    assert data["database"] == "SQLAlchemy ORM"
    assert "endpoints" in data
    assert "total_siswa" in data


def test_health_check(client):
    """Test GET /api/health endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "total_siswa" in data


# ==================== Test HALO Endpoints ====================

def test_halo_get(client):
    """Test GET /api/v1/halo/ - simple greeting"""
    response = client.get("/api/v1/halo/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Get from Halo API"
    assert isinstance(data["data"], list)


def test_halo_post(client):
    """Test POST /api/v1/halo/ - greeting dengan nama dan handphone"""
    payload = {
        "nama": "Edy Santoso",
        "handphone": "08123456789"
    }
    response = client.post("/api/v1/halo/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Halo Edy Santoso!"
    assert data["nama"] == "Edy Santoso"
    assert data["handphone"] == "08123456789"


# ==================== Test READ (GET) Endpoints ====================

def test_get_all_siswa(client):
    """Test GET /api/v1/siswa/ - mendapatkan semua siswa"""
    response = client.get("/api/v1/siswa/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert isinstance(data["data"], list)


def test_get_siswa_by_nonexistent_id(client):
    """Test GET /api/v1/siswa/{id} - siswa tidak ditemukan"""
    response = client.get("/api/v1/siswa/99999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] is not None


# ==================== Test CREATE (POST) Endpoint ====================

def test_create_siswa_success(client):
    """Test POST /api/v1/siswa/ - tambah siswa baru"""
    payload = {
        "nama": "Budi Santoso",
        "email": generate_unique_email()  # Use unique email
    }
    response = client.post("/api/v1/siswa/", json=payload)
    assert response.status_code == 201  # HTTP 201 Created
    data = response.json()
    assert data["nama"] == "Budi Santoso"
    assert data["email"] == payload["email"]
    assert "id" in data


def test_create_siswa_missing_field(client):
    """Test POST /api/v1/siswa/ - field yang hilang (validation error)"""
    payload = {
        "nama": "Budi Santoso"
        # email missing
    }
    response = client.post("/api/v1/siswa/", json=payload)
    assert response.status_code == 422  # Validation error


def test_create_siswa_invalid_email(client):
    """Test POST /api/v1/siswa/ - email tidak valid"""
    payload = {
        "nama": "Budi Santoso",
        "email": "invalid-email"  # Not a valid email
    }
    response = client.post("/api/v1/siswa/", json=payload)
    assert response.status_code == 422  # Validation error


def test_create_siswa_duplicate_email(client):
    """Test POST /api/v1/siswa/ - email sudah terdaftar"""
    email = generate_unique_email()
    
    # Create first siswa
    payload1 = {
        "nama": "Siswa Pertama",
        "email": email
    }
    response1 = client.post("/api/v1/siswa/", json=payload1)
    assert response1.status_code == 201
    
    # Try to create second siswa dengan email yang sama
    payload2 = {
        "nama": "Siswa Kedua",
        "email": email  # Same email
    }
    response2 = client.post("/api/v1/siswa/", json=payload2)
    assert response2.status_code == 400  # Bad Request - duplicate email


# ==================== Test UPDATE (PUT) Endpoint ====================

def test_update_siswa_nonexistent(client):
    """Test PUT /api/v1/siswa/{id} - siswa tidak ditemukan"""
    payload = {
        "nama": "Updated Name",
        "email": generate_unique_email()
    }
    response = client.put("/api/v1/siswa/99999", json=payload)
    assert response.status_code == 404


def test_update_siswa_missing_field(client):
    """Test PUT /api/v1/siswa/{id} - field yang hilang"""
    payload = {
        "nama": "Updated Name"
        # email missing
    }
    response = client.put("/api/v1/siswa/1", json=payload)
    assert response.status_code == 422  # Validation error


# ==================== Test DELETE Endpoint ====================

def test_delete_siswa_nonexistent(client):
    """Test DELETE /api/v1/siswa/{id} - siswa tidak ditemukan"""
    response = client.delete("/api/v1/siswa/99999")
    assert response.status_code == 404


# ==================== Integration Test ====================

def test_crud_workflow(client):
    """Test workflow lengkap: CREATE -> READ -> UPDATE -> DELETE"""
    
    # 1. CREATE - Tambah siswa baru
    create_payload = {
        "nama": "Test Student",
        "email": generate_unique_email()  # Use unique email
    }
    create_response = client.post("/api/v1/siswa/", json=create_payload)
    assert create_response.status_code == 201
    siswa_id = create_response.json()["id"]
    
    # 2. READ - Ambil siswa yang baru dibuat
    read_response = client.get(f"/api/v1/siswa/{siswa_id}")
    assert read_response.status_code == 200
    assert read_response.json()["nama"] == "Test Student"
    
    # 3. UPDATE - Update data siswa
    update_payload = {
        "nama": "Updated Student",
        "email": generate_unique_email()  # Use unique email for update
    }
    update_response = client.put(f"/api/v1/siswa/{siswa_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["nama"] == "Updated Student"
    
    # 4. DELETE - Hapus siswa
    delete_response = client.delete(f"/api/v1/siswa/{siswa_id}")
    assert delete_response.status_code == 200
    
    # 5. Verify - Pastikan siswa sudah tidak ada
    verify_response = client.get(f"/api/v1/siswa/{siswa_id}")
    assert verify_response.status_code == 404

