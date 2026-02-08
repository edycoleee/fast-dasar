from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ==================== Test Root Endpoint ====================

def test_root():
    """Test GET / endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "FastAPI is running!"
    assert "docs" in data
    assert "redoc" in data


# ==================== Test Halo GET Endpoint ====================

def test_halo_get():
    """Test GET /api/v1/halo/ endpoint"""
    response = client.get("/api/v1/halo/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Get from Halo API"
    assert isinstance(data["data"], list)


# ==================== Test Halo POST Endpoint ====================

def test_halo_post_success():
    """Test POST /api/v1/halo/ dengan data valid"""
    payload = {"nama": "Sultan", "handphone": "08123456789"}
    response = client.post("/api/v1/halo/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Halo Sultan!"
    assert data["nama"] == "Sultan"
    assert data["handphone"] == "08123456789"


def test_halo_post_validation_error_missing_handphone():
    """Test POST /api/v1/halo/ tanpa field handphone"""
    payload = {"nama": "Sultan"}
    response = client.post("/api/v1/halo/", json=payload)
    assert response.status_code == 422  # Validation error


def test_halo_post_validation_error_missing_nama():
    """Test POST /api/v1/halo/ tanpa field nama"""
    payload = {"handphone": "08123456789"}
    response = client.post("/api/v1/halo/", json=payload)
    assert response.status_code == 422  # Validation error


def test_halo_post_validation_error_empty_payload():
    """Test POST /api/v1/halo/ dengan payload kosong"""
    response = client.post("/api/v1/halo/", json={})
    assert response.status_code == 422  # Validation error


# ==================== Test Siswa GET Endpoint ====================

def test_siswa_get():
    """Test GET /api/v1/siswa/ endpoint"""
    response = client.get("/api/v1/siswa/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Get from siswa API"
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    
    # Check struktur data siswa
    siswa = data["data"][0]
    assert "no" in siswa
    assert "nama" in siswa
    assert "email" in siswa
    assert siswa["nama"] == "Edy"
    assert siswa["email"] == "edycoleee@gmail.com"

