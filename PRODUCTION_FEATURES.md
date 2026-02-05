# Production Features Implementation

Implementasi fitur-fitur production-ready untuk FastAPI:
1. **Logging System** - Monitoring dengan file app.log
2. **Error Handling** - Reliability dengan custom exceptions
3. **Standard Response** - Konsistensi format response {success, message, data}

## 📋 Table of Contents
- [1. Logging System](#1-logging-system)
- [2. Error Handling](#2-error-handling)
- [3. Standard Response Format](#3-standard-response-format)
- [4. Usage Examples](#4-usage-examples)
- [5. Testing](#5-testing)

---

## 1. Logging System

### 📁 File: `app/core/logging_config.py`

**Features:**
- ✅ Rotating file handler (10MB max, 5 backups)
- ✅ Dual logging: `logs/app.log` (all logs) dan `logs/error.log` (errors only)
- ✅ Console output untuk development
- ✅ Structured format dengan timestamp

**Format Log:**
```
2026-02-05 21:35:41 - module_name - LEVEL - message
```

**Setup:**
```python
from app.core import setup_logging, get_logger

# Di main.py (sudah implemented)
setup_logging()
logger = get_logger(__name__)

# Di endpoints/services
logger = get_logger(__name__)
logger.info("User logged in")
logger.warning("Invalid data")
logger.error("Database error", exc_info=True)
```

**Log Levels:**
- `INFO` - Normal operations (login, CRUD operations)
- `WARNING` - Validation failures, business logic warnings
- `ERROR` - Exceptions, database errors

**Log Files:**
- `logs/app.log` - All logs (rotating, max 10MB, keep 5 backups)
- `logs/error.log` - Error level only
- Console - All logs during development

---

## 2. Error Handling

### 📁 File: `app/core/exceptions.py`

**Custom Exception Hierarchy:**
```
AppException (base)
├── AuthenticationException
│   ├── InvalidCredentialsException
│   ├── InvalidTokenException
│   └── InsufficientPermissionsException
├── ResourceNotFoundException
│   └── UserNotFoundException
├── ValidationException
│   ├── DuplicateResourceException
│   └── DuplicateEmailException
├── BusinessLogicException
└── DatabaseException
```

**Exception Properties:**
- `message` - Human-readable error message
- `status_code` - HTTP status code (404, 401, 400, etc.)
- `details` - Optional additional context

**Usage in Services:**
```python
from app.core.exceptions import UserNotFoundException, InvalidCredentialsException

# Raise custom exceptions
raise UserNotFoundException(user_id=123)
raise InvalidCredentialsException()
raise DuplicateEmailException(email="user@example.com")
```

**Global Exception Handlers (main.py):**
```python
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.message, exc.status_code)
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response("Internal server error")
    )
```

---

## 3. Standard Response Format

### 📁 File: `app/schemas/response.py`

**Success Response:**
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "id": 1,
    "nama": "John Doe",
    "email": "john@example.com"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "User not found",
  "data": null,
  "error": {
    "code": 404,
    "details": {...}
  }
}
```

**Helper Functions:**
```python
from app.schemas import success_response, error_response

# Success
return success_response("User created successfully", user_data)

# Error
return error_response("Invalid credentials", 401)
```

**Endpoint Implementation:**
```python
from app.schemas import StandardResponse, success_response

@router.get("/users", response_model=StandardResponse[List[UserResponse]])
def get_users(db: Session = Depends(get_db)):
    users = UserService.get_all_users(db)
    return success_response(f"Retrieved {len(users)} users", users)
```

---

## 4. Usage Examples

### Complete Endpoint Example:

```python
from fastapi import APIRouter, Depends, status
from app.core import get_logger
from app.core.exceptions import UserNotFoundException
from app.schemas import StandardResponse, success_response

logger = get_logger(__name__)
router = APIRouter()

@router.get("/{user_id}", response_model=StandardResponse[UserResponse])
def get_user(user_id: int, db: Session = Depends(get_db)):
    # 1. Log the request
    logger.info(f"Fetching user {user_id}")
    
    # 2. Service call (raises custom exception if not found)
    user = UserService.get_user_by_id(db, user_id)
    
    # 3. Return standard response
    return success_response(f"User {user_id} retrieved", user)
```

### Service Layer Example:

```python
from app.core import get_logger
from app.core.exceptions import UserNotFoundException, DatabaseException

logger = get_logger(__name__)

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        try:
            logger.info(f"Fetching user with id: {user_id}")
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.warning(f"User {user_id} not found")
                raise UserNotFoundException(user_id=user_id)
            
            logger.info(f"User {user_id} found: {user.email}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise DatabaseException(f"Error fetching user: {str(e)}")
```

---

## 5. Testing

### Test Logging:
```bash
# Run test script
python test_logging.py

# Check logs
cat logs/app.log
cat logs/error.log
```

### Test with FastAPI:
```bash
# Start server
uvicorn main:app --reload

# Test endpoints
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Check logs
tail -f logs/app.log
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "nama": "Admin User",
      "email": "admin@example.com",
      "role": "admin"
    }
  }
}
```

---

## 📊 Benefits

### 1. **Logging**
- ✅ Easy debugging and monitoring
- ✅ Audit trail untuk security
- ✅ Performance monitoring
- ✅ Error tracking

### 2. **Error Handling**
- ✅ Consistent error responses
- ✅ Better error messages
- ✅ Proper HTTP status codes
- ✅ Easy exception tracking

### 3. **Standard Response**
- ✅ Konsistensi API responses
- ✅ Easy frontend integration
- ✅ Clear success/error indication
- ✅ Better API documentation

---

## 🔧 Configuration

### Log Rotation:
Edit `app/core/logging_config.py`:
```python
file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5  # Keep 5 old files
)
```

### Custom Exception:
Add to `app/core/exceptions.py`:
```python
class CustomException(AppException):
    """Custom exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
```

---

## 📝 Files Modified

**New Files:**
- `app/core/logging_config.py` - Logging configuration
- `app/core/exceptions.py` - Custom exceptions
- `app/schemas/response.py` - Standard response schemas

**Updated Files:**
- `main.py` - Added exception handlers & logging
- `app/core/__init__.py` - Export logging & exceptions
- `app/schemas/__init__.py` - Export response schemas
- `app/services/auth_service.py` - Added logging & exceptions
- `app/services/user_service.py` - Added logging & exceptions
- `app/api/v1/endpoints/auth.py` - Standard responses & logging
- `app/api/v1/endpoints/users.py` - Standard responses & logging
- `app/api/v1/endpoints/admin.py` - Standard responses & logging

---

## 🚀 Next Steps

1. **Add More Logging:**
   - Log request/response bodies
   - Add request ID tracking
   - Implement structured logging (JSON)

2. **Enhance Error Handling:**
   - Add more specific exceptions
   - Implement error codes
   - Add detailed error context

3. **Response Enhancements:**
   - Add pagination metadata
   - Include request timing
   - Add API version info

4. **Monitoring:**
   - Integrate with monitoring tools (Prometheus, Grafana)
   - Add health check endpoints
   - Implement metrics collection

---

## 📚 References

- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Pydantic Models](https://docs.pydantic.dev/latest/)

---

**Created:** 2026-02-05  
**Version:** 1.0  
**Status:** ✅ Implemented & Tested
