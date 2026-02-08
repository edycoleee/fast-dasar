import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Base, SiswaORM, get_db
from main import app
from fastapi.testclient import TestClient


# Testing database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db dependency untuk testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create test database and drop after test"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create test client dengan testing database"""
    # Override dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    yield client
    
    # Drop tables setelah test
    Base.metadata.drop_all(bind=engine)
    
    # Clear overrides
    app.dependency_overrides.clear()

