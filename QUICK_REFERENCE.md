# 🚀 Quick Reference - Production Features

## 📝 Logging

```python
# Import
from app.core import get_logger

# Setup (di module)
logger = get_logger(__name__)

# Usage
logger.info("Normal operation")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)

# Logs location
# logs/app.log - all logs
# logs/error.log - errors only
```

---

## ⚠️ Error Handling

```python
# Import
from app.core.exceptions import (
    UserNotFoundException,
    InvalidCredentialsException,
    DuplicateEmailException,
    DatabaseException
)

# Raise exceptions
raise UserNotFoundException(user_id=123)
raise InvalidCredentialsException()
raise DuplicateEmailException(email="user@example.com")
raise DatabaseException("Connection failed")

# Caught automatically by global handler
# Returns proper error response
# Logged automatically
```

---

## ✅ Standard Responses

```python
# Import
from app.schemas import StandardResponse, success_response

# Success response
@router.get("/users", response_model=StandardResponse[List[UserResponse]])
def get_users(db: Session = Depends(get_db)):
    users = UserService.get_all_users(db)
    return success_response("Users retrieved", users)

# Response format:
{
  "success": true,
  "message": "Users retrieved",
  "data": [...]
}
```

---

## 🔧 Common Patterns

### Endpoint Template:
```python
from fastapi import APIRouter, Depends, status
from app.core import get_logger
from app.schemas import StandardResponse, success_response

logger = get_logger(__name__)
router = APIRouter()

@router.get("/{id}", response_model=StandardResponse[ItemResponse])
def get_item(id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching item {id}")
    item = Service.get_by_id(db, id)
    return success_response(f"Item {id} retrieved", item)
```

### Service Template:
```python
from app.core import get_logger
from app.core.exceptions import UserNotFoundException, DatabaseException

logger = get_logger(__name__)

class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int):
        logger.info(f"Fetching user {user_id}")
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.warning(f"User {user_id} not found")
                raise UserNotFoundException(user_id=user_id)
            
            logger.info(f"User {user_id} found")
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}", exc_info=True)
            raise DatabaseException(f"Error: {e}")
```

---

## 🎯 Best Practices

### Logging Levels:
- **INFO** - Normal operations, successful actions
- **WARNING** - Validation failures, business logic warnings
- **ERROR** - Exceptions, database errors

### When to Log:
✅ Request received  
✅ Business operation started  
✅ Validation failed  
✅ Exception occurred  
✅ Operation completed  

❌ Don't log passwords  
❌ Don't log sensitive data  
❌ Don't log in loops (use summary)  

### Exception Handling:
✅ Use specific exceptions  
✅ Raise in services, handle in main  
✅ Include context in message  
✅ Log with exc_info=True for stack trace  

---

## 📚 Available Exceptions

```python
# Authentication
InvalidCredentialsException()
InvalidTokenException()
InsufficientPermissionsException()

# Resources
ResourceNotFoundException("User", "ID 123")
UserNotFoundException(user_id=123)
UserNotFoundException(email="user@example.com")

# Validation
ValidationException("Invalid data", {"field": "error"})
DuplicateEmailException(email="user@example.com")

# Business Logic
BusinessLogicException("Business rule violated")

# Database
DatabaseException("Connection failed")
```

---

## 🔍 Debugging

### Check Logs:
```bash
# Tail app logs
tail -f logs/app.log

# Check errors only
tail -f logs/error.log

# Search for user 123
grep "user 123" logs/app.log

# Count errors today
grep "ERROR" logs/app.log | wc -l
```

### Test Response Format:
```bash
curl http://localhost:8000/api/v1/users/1 | jq .

# Expected:
{
  "success": true,
  "message": "User 1 retrieved successfully",
  "data": {...}
}
```

---

## ⚡ Quick Commands

```bash
# Start server with logs
uvicorn main:app --reload

# Test logging
python test_logging.py

# Quick test
python quick_test.py

# Check log size
ls -lh logs/

# View latest logs
tail -20 logs/app.log
```

---

## 📋 Checklist for New Endpoint

- [ ] Import `get_logger` from `app.core`
- [ ] Create logger: `logger = get_logger(__name__)`
- [ ] Add logging: `logger.info(f"Operation: {param}")`
- [ ] Use `StandardResponse[DataType]` for response_model
- [ ] Return `success_response(message, data)`
- [ ] Raise custom exceptions instead of HTTPException
- [ ] Test response format
- [ ] Check logs written

---

## 🎨 Example Flow

```
1. Request arrives
   ↓
2. Endpoint logs request
   logger.info("Fetching user 123")
   ↓
3. Service processes
   - Query database
   - Validate data
   - Log warnings if needed
   ↓
4. Service raises exception (if error)
   raise UserNotFoundException(user_id=123)
   ↓
5. Global handler catches exception
   - Logs error
   - Returns error_response
   ↓
6. Success: Return standard response
   return success_response("Success", data)
   ↓
7. Response:
   {
     "success": true/false,
     "message": "...",
     "data": {...}
   }
   ↓
8. Check logs:
   tail -f logs/app.log
```

---

**Quick Links:**
- Full Documentation: [PRODUCTION_FEATURES.md](PRODUCTION_FEATURES.md)
- Implementation Summary: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- Checklist: [CHECKLIST.md](CHECKLIST.md)
