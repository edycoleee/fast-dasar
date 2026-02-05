# 🚀 Quick Implementation Guide - Priority Improvements

## 1️⃣ Database Migrations dengan Alembic (Priority: CRITICAL)

### Setup Alembic
```bash
# Install
pip install alembic

# Initialize
alembic init alembic

# Update alembic.ini
# sqlalchemy.url = postgresql://user:pass@localhost/dbname
```

### Configure Alembic
```python
# alembic/env.py
from app.db.base import Base
from app.models.user import User  # Import all models

target_metadata = Base.metadata

# In run_migrations_offline() and run_migrations_online()
# Use settings.DATABASE_URL
```

### Create & Run Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Integration
```python
# main.py - Remove init_db(), migrations handle this now
# @app.on_event("startup")
# def on_startup():
#     init_db()  # ❌ Remove this
```

---

## 2️⃣ Comprehensive Testing (Priority: HIGH)

### Setup pytest
```bash
pip install pytest pytest-asyncio pytest-cov httpx faker
```

### Project Structure
```
tests/
├── __init__.py
├── conftest.py          # Fixtures
├── test_auth.py         # Auth tests
├── test_users.py        # User CRUD tests
├── test_admin.py        # Admin tests
└── test_services.py     # Service layer tests
```

### conftest.py
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.core.deps import get_db
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token(client):
    # Create admin user
    client.post("/api/v1/users/", json={
        "nama": "Admin",
        "email": "admin@test.com",
        "password": "admin123",
        "role": "admin"
    })
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    return response.json()["access_token"]
```

### test_auth.py
```python
def test_login_success(client):
    # Create user first
    client.post("/api/v1/users/", json={
        "nama": "Test User",
        "email": "test@test.com",
        "password": "test123",
        "role": "user"
    })
    
    # Test login
    response = client.post("/api/v1/auth/login", json={
        "email": "test@test.com",
        "password": "test123"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrong"
    })
    assert response.status_code == 401

def test_dashboard_protected(client):
    response = client.get("/api/v1/auth/dashboard")
    assert response.status_code == 401

def test_dashboard_with_token(client, admin_token):
    response = client.get(
        "/api/v1/auth/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
```

### Run Tests
```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_auth.py -v

# Watch mode
pytest-watch
```

---

## 3️⃣ Structured Logging (Priority: HIGH)

### Setup Logging
```python
# app/core/logging_config.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Create logs directory
Path("logs").mkdir(exist_ok=True)

def setup_logging():
    """Configure application logging"""
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating by size)
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10_000_000,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger
```

### Use in Application
```python
# main.py
from app.core.logging_config import setup_logging

logger = setup_logging()

@app.on_event("startup")
def on_startup():
    logger.info("🚀 Starting FastAPI application...")
    logger.info(f"📦 Project: {settings.PROJECT_NAME} v{settings.VERSION}")
    init_db()
    logger.info("✅ Application started successfully")

# app/services/auth_service.py
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> dict:
        logger.info(f"Login attempt for: {login_data.email}")
        
        try:
            user = AuthService.authenticate_user(db, login_data)
            logger.info(f"User {user.email} logged in successfully")
            return {...}
        except Exception as e:
            logger.error(f"Login failed for {login_data.email}: {str(e)}")
            raise
```

---

## 4️⃣ Custom Error Handling (Priority: HIGH)

### Create Custom Exceptions
```python
# app/core/exceptions.py
class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserNotFoundException(AppException):
    def __init__(self, user_id: int = None, email: str = None):
        identifier = f"ID {user_id}" if user_id else f"email {email}"
        super().__init__(f"User with {identifier} not found", 404)

class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__("Invalid email or password", 401)

class InsufficientPermissionsException(AppException):
    def __init__(self, required_role: str = "admin"):
        super().__init__(f"Insufficient permissions. Required role: {required_role}", 403)

class DuplicateEmailException(AppException):
    def __init__(self, email: str):
        super().__init__(f"Email {email} is already registered", 400)
```

### Register Exception Handlers
```python
# main.py
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )
```

### Use in Services
```python
# app/services/user_service.py
from app.core.exceptions import UserNotFoundException, DuplicateEmailException

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException(user_id=user_id)
        return user
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        existing = UserService.get_user_by_email(db, user.email)
        if existing:
            raise DuplicateEmailException(user.email)
        # ... create user
```

---

## 5️⃣ Health Check Endpoint (Priority: HIGH)

### Create Health Check
```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from app.core.deps import get_db

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for monitoring
    Returns application and database status
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    # Check Redis (if implemented)
    # try:
    #     redis_client.ping()
    #     health_status["checks"]["redis"] = "connected"
    # except Exception as e:
    #     health_status["checks"]["redis"] = f"error: {str(e)}"
    
    return health_status

# Liveness probe (simple)
@router.get("/health/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

# Readiness probe (with dependencies)
@router.get("/health/ready")
async def readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready"}
        )
```

### Add to Router
```python
# app/api/v1/api.py
from app.api.v1.endpoints import health

api_router.include_router(health.router, prefix="/health", tags=["Health"])
```

---

## 📦 Updated requirements.txt

```txt
# Web Framework
fastapi==0.110.0
uvicorn[standard]==0.27.1
pydantic==2.6.1
pydantic-settings==2.2.1
email-validator==2.1.0

# Database ORM
sqlalchemy==2.0.27
alembic==1.13.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Testing
pytest==8.0.0
pytest-asyncio==0.23.5
pytest-cov==4.1.0
httpx==0.26.0
faker==22.7.0

# Utilities
python-multipart==0.0.9
```

---

## 🎯 Implementation Checklist

### Week 1
- [ ] Setup Alembic migrations
- [ ] Configure logging system
- [ ] Add health check endpoint
- [ ] Create custom exception handlers

### Week 2  
- [ ] Write comprehensive tests (pytest)
- [ ] Add test coverage reporting
- [ ] Setup CI/CD pipeline (GitHub Actions)
- [ ] Code quality tools (black, isort)

### Week 3
- [ ] Migrate to PostgreSQL
- [ ] Setup Redis caching
- [ ] Implement refresh tokens
- [ ] Add rate limiting

---

## 📝 Quick Commands

```bash
# Run with logging
uvicorn main:app --reload --log-level info

# Run tests with coverage
pytest --cov=app --cov-report=html

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Check health
curl http://localhost:8000/api/v1/health

# Format code
black app/
isort app/

# Type checking
mypy app/
```

---

**Next Step**: Start with Alembic migrations! 🚀
