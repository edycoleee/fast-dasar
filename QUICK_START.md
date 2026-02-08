# 🚀 Clean Code Architecture - Quick Start Guide

## What Changed?

The FastAPI application has been refactored from a single monolithic file to a clean, modular architecture:

### Before (Monolithic)
```
main.py (281 lines)
  └─ All endpoints mixed together
  └─ Database logic mixed with API logic
  └─ Hard to test and extend
```

### After (Modular)
```
main.py (95 lines) - Only app setup
  └─ Clean, organized imports
  └─ Health check endpoint
  └─ Routes to api_router
  
app/
  ├─ database.py - All database operations
  ├─ models.py - Pydantic validation models
  └─ api/v1/
      ├─ api.py - Router aggregator
      └─ endpoints/
          ├─ halo.py - Greeting endpoints
          └─ siswa.py - CRUD endpoints
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Run All Tests
```bash
pytest tests/test_main.py -v
```

### Run Specific Test
```bash
pytest tests/test_main.py::test_create_siswa_success -v
```

### Run with Coverage
```bash
pytest tests/test_main.py --cov=app --cov-report=html
```

## API Endpoints

### 🎉 Halo API (Learning)
```bash
# Get greeting list
GET /api/v1/halo/

# Post personalized greeting
POST /api/v1/halo/
{
  "nama": "Edy Santoso",
  "handphone": "08123456789"
}
```

### 📚 Siswa API (CRUD)

**Create Student (HTTP 201)**
```bash
POST /api/v1/siswa/
{
  "nama": "Budi Santoso",
  "email": "budi@example.com"
}
```

**Get All Students**
```bash
GET /api/v1/siswa/
```

**Get Student by ID**
```bash
GET /api/v1/siswa/1
```

**Update Student**
```bash
PUT /api/v1/siswa/1
{
  "nama": "Budi Updated",
  "email": "budi.new@example.com"
}
```

**Delete Student**
```bash
DELETE /api/v1/siswa/1
```

### 🏥 Health Check
```bash
# API Health
GET /api/health

# Root Info
GET /
```

## Understanding the Architecture

### 1. **Entry Point** (`main.py`)
- Initializes FastAPI app
- Sets up lifespan (startup/shutdown)
- Includes all routers
- Provides root and health endpoints

### 2. **Router Aggregator** (`app/api/v1/api.py`)
- Combines all endpoint routers
- Adds `/api/v1` prefix to all routes
- Can add versioning for future APIs (`/api/v2/`, etc.)

### 3. **Endpoint Routers**
- **`halo.py`**: Simple greeting endpoints (learning)
- **`siswa.py`**: Complete CRUD operations

### 4. **Database Layer** (`app/database.py`)
- Raw SQL operations (for learning)
- No ORM dependencies
- Functions: init_db, CRUD operations, count

### 5. **Validation Models** (`app/models.py`)
- Pydantic models for request/response validation
- Automatic schema generation for OpenAPI docs
- Type hints for IDE support

## File Structure

```
fast-dasar/
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
├── pytest.ini                        # Pytest configuration
├── ARCHITECTURE.md                   # Detailed architecture docs
├── QUICK_START.md                    # This file
├── siswa.db                          # SQLite database (auto-created)
│
├── app/                              # Application package
│   ├── __init__.py                   # Package marker
│   ├── database.py                   # Database operations
│   ├── models.py                     # Pydantic models
│   └── api/
│       ├── __init__.py               # Package marker
│       └── v1/
│           ├── __init__.py           # Package marker
│           ├── api.py                # Router aggregator
│           └── endpoints/
│               ├── __init__.py       # Package marker
│               ├── halo.py           # Halo endpoints
│               └── siswa.py          # Siswa CRUD endpoints
│
└── tests/                            # Test package
    ├── conftest.py                   # Pytest fixtures & configuration
    ├── test_main.py                  # 14 integration tests
    └── __init__.py                   # Package marker
```

## Key Improvements

### ✅ Separation of Concerns
- Endpoints don't know about database details
- Database doesn't know about HTTP responses
- Models handle validation independently

### ✅ Scalability
- Easy to add new endpoints (create new file in endpoints/)
- Easy to add new API versions (/api/v2/, etc.)
- Easy to test each component independently

### ✅ Maintainability
- Each module has a single responsibility
- Clear import structure
- Easy to find and modify code

### ✅ Testing
- 14 comprehensive tests
- Tests organized by endpoint
- Uses TestClient for integration testing
- UUID-based unique data for test isolation

### ✅ Documentation
- FastAPI auto-generates OpenAPI docs
- Code has detailed docstrings
- Examples in ARCHITECTURE.md and README.md

## Common Tasks

### Add a New Endpoint
1. Create new file in `app/api/v1/endpoints/`
2. Define router and functions
3. Import in `app/api/v1/api.py`
4. Write tests in `tests/test_main.py`

### Add a New Database Function
1. Add SQL function in `app/database.py`
2. Use in endpoint router
3. Write test for the function

### Modify Validation
1. Update Pydantic models in `app/models.py`
2. FastAPI automatically updates OpenAPI schema
3. Write test for new validation

### Run in Production
```bash
# Use gunicorn with uvicorn workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Test Results

All 14 tests passing ✅:
- 2 Root/Health endpoint tests
- 2 Halo endpoint tests
- 10 Siswa CRUD tests (create, read, update, delete, validation, integration)

## Environment

- Python 3.11.2
- FastAPI 0.109.0
- Pydantic 2.5.3
- Pytest 7.4.4
- SQLite3 (included with Python)

## Next Steps

1. ✅ Understand the modular structure
2. ✅ Run the server and test endpoints
3. ✅ Review test cases to understand expected behavior
4. 📝 Add authentication/authorization
5. 📝 Add pagination for list endpoints
6. 📝 Add database migrations
7. 📝 Add logging and monitoring
8. 📝 Deploy to production

## Troubleshooting

### ModuleNotFoundError
Ensure you're in the project root and conftest.py has correct path setup.

### Database Lock Error
Remove `siswa.db` file and restart the server to recreate it.

### Port Already in Use
Use different port: `uvicorn main:app --port 8001`

### Tests Failing
- Clear __pycache__: `find . -type d -name __pycache__ -exec rm -r {} +`
- Remove siswa.db: `rm siswa.db`
- Run pytest: `pytest tests/test_main.py -v`

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

**Ready to start?** Run `uvicorn main:app --reload` and visit http://localhost:8000/docs! 🎉
