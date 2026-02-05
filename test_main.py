"""
Unit Test untuk FastAPI Basic Router

Menggunakan:
- pytest: Framework testing (seperti Jest di Node.js, unittest di Flask)
- TestClient: FastAPI testing client (tidak perlu server berjalan)

Cara menjalankan:
    pytest test_main.py -v
    pytest test_main.py -v --cov  # dengan coverage
"""

import pytest
from fastapi.testclient import TestClient
from main import app


# Fixture untuk test client
@pytest.fixture
def client():
    """Buat test client untuk setiap test"""
    return TestClient(app)


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
        
    def test_halo_get_response_structure(self, client):
        """Test struktur response /api/halo/ sesuai spec"""
        response = client.get("/api/halo/")
        data = response.json()
        
        # Assert memiliki key yang benar
        assert "success" in data
        assert "message" in data
        assert "data" in data
        
        # Assert tipe data yang benar
        assert isinstance(data["success"], bool)
        assert isinstance(data["message"], str)
        assert isinstance(data["data"], list)


class TestSiswaEndpoint:
    """Test untuk endpoint /api/siswa/"""
    
    def test_siswa_get_success(self, client):
        """Test GET /api/siswa/ mengembalikan response yang benar"""
        response = client.get("/api/siswa/")
        
        # Assert status code
        assert response.status_code == 200
        
        # Assert response body
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Get from siswa API"
        
    def test_siswa_get_data_structure(self, client):
        """Test struktur data siswa sesuai spec"""
        response = client.get("/api/siswa/")
        data = response.json()
        
        # Assert data adalah list dan tidak kosong
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # Assert data siswa pertama memiliki field yang benar
        siswa = data["data"][0]
        assert "no" in siswa
        assert "nama" in siswa
        assert "email" in siswa
        
        # Assert tipe data yang benar
        assert isinstance(siswa["no"], int)
        assert isinstance(siswa["nama"], str)
        assert isinstance(siswa["email"], str)
        
    def test_siswa_get_data_content(self, client):
        """Test konten data siswa sesuai yang diharapkan"""
        response = client.get("/api/siswa/")
        data = response.json()
        
        siswa = data["data"][0]
        assert siswa["no"] == 1
        assert siswa["nama"] == "Edy"
        assert siswa["email"] == "edycoleee@gmail.com"


class TestRootEndpoint:
    """Test untuk root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test GET / mengembalikan info API"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "redoc" in data


class TestNotFoundEndpoint:
    """Test untuk endpoint yang tidak ada"""
    
    def test_endpoint_not_found(self, client):
        """Test endpoint yang tidak ada mengembalikan 404"""
        response = client.get("/api/tidak-ada/")
        
        assert response.status_code == 404
        
    def test_wrong_method(self, client):
        """Test method yang salah (POST ke GET endpoint)"""
        response = client.post("/api/halo/")
        
        # POST /api/halo/ ada dan butuh body, jadi return 422 (validation error)
        # Bukan 405 karena endpoint POST memang ada
        assert response.status_code == 422


# Bonus: Test untuk endpoint POST /api/halo/ (dari kode sebelumnya)
class TestHaloPostEndpoint:
    """Test untuk endpoint POST /api/halo/"""
    
    def test_halo_post_success(self, client):
        """Test POST /api/halo/ dengan data valid"""
        payload = {
            "nama": "John Doe",
            "handphone": "081234567890"
        }
        
        response = client.post("/api/halo/", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "John Doe" in data["message"]
        assert data["nama"] == "John Doe"
        assert data["handphone"] == "081234567890"
        
    def test_halo_post_missing_field(self, client):
        """Test POST /api/halo/ dengan field yang hilang"""
        payload = {
            "nama": "John Doe"
            # handphone missing
        }
        
        response = client.post("/api/halo/", json=payload)
        
        # Pydantic validation error
        assert response.status_code == 422
        
    def test_halo_post_wrong_type(self, client):
        """Test POST /api/halo/ dengan tipe data salah"""
        payload = {
            "nama": 123,  # Seharusnya string
            "handphone": "081234567890"
        }
        
        response = client.post("/api/halo/", json=payload)
        
        # Pydantic akan convert atau return error
        # Tergantung konfigurasi, bisa 200 atau 422
        assert response.status_code in [200, 422]
