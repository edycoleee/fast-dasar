from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "FastAPI is running!",
        "docs": "/docs",
        "redoc": "/redoc",
    }


def test_halo_get():
    response = client.get("/api/halo/")
    assert response.status_code == 200
    assert response.json() == {"message": "Halo! Welcome to FastAPI"}


def test_halo_post():
    payload = {"nama": "Sultan", "handphone": "08123456789"}
    response = client.post("/api/halo/", json=payload)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Halo Sultan!",
        "nama": "Sultan",
        "handphone": "08123456789",
    }


def test_halo_post_validation_error():
    payload = {"nama": "Sultan"}
    response = client.post("/api/halo/", json=payload)
    assert response.status_code == 422
