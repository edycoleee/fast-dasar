# 🔄 Migration Guide: Old Structure → Clean Architecture

## 📊 Before & After

### OLD Structure (Monolithic)
```
fast-dasar/
├── main.py                    # 597 lines - Everything here!
├── db_sqlalchemy.py           # Database + Models
├── schemas.py                 # All Pydantic schemas
├── auth_utils.py              # Password + JWT
├── authorization.py           # RBAC logic
├── middleware.py              # Middleware
└── test_*.py                  # Tests
```

**Problems:**
- ❌ 597 lines dalam satu file (main.py)
- ❌ Sulit mencari code
- ❌ Hard to test individual components
- ❌ Tight coupling antar komponen
- ❌ Susah untuk scaling
- ❌ Team collaboration difficult

### NEW Structure (Clean Architecture)
```
fast-dasar/
├── app/
│   ├── api/v1/endpoints/      # 3 files: auth, users, admin
│   ├── core/                  # 4 files: config, security, deps, auth
│   ├── db/                    # 2 files: base, session
│   ├── models/                # 1 file: user
│   ├── schemas/               # 2 files: user, auth
│   ├── services/              # 2 files: user_service, auth_service
│   └── middleware/            # 1 file: jwt_middleware
├── main.py                    # 113 lines - Clean!
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

**Benefits:**
- ✅ Clean separation of concerns
- ✅ Easy to find & modify code
- ✅ Individual components testable
- ✅ Loose coupling
- ✅ Easy to scale
- ✅ Team can work in parallel
- ✅ Docker-ready

## 🔀 File Mapping

### OLD → NEW

| OLD File | NEW Location | Purpose |
|----------|--------------|---------|
| `main.py` (endpoints) | `app/api/v1/endpoints/*.py` | API routes |
| `main.py` (app init) | `main.py` | App initialization |
| `db_sqlalchemy.py` (config) | `app/db/base.py` | Database setup |
| `db_sqlalchemy.py` (models) | `app/models/user.py` | SQLAlchemy models |
| `schemas.py` | `app/schemas/user.py` + `auth.py` | Pydantic schemas |
| `auth_utils.py` | `app/core/security.py` | JWT & password |
| `authorization.py` | `app/core/authorization.py` | RBAC logic |
| `middleware.py` | `app/middleware/jwt_middleware.py` | Middleware |
| - | `app/core/config.py` | **NEW**: Settings |
| - | `app/core/deps.py` | **NEW**: Dependencies |
| - | `app/services/*.py` | **NEW**: Business logic |

## 📝 Code Migration Examples

### Example 1: Endpoint
**OLD** (main.py):
```python
@app.post("/api/v1/auth/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "user": user}
```

**NEW** (app/api/v1/endpoints/auth.py):
```python
@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, login_data)
```

**Business Logic** (app/services/auth_service.py):
```python
class AuthService:
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> dict:
        user = authenticate_user(db, login_data)
        token = create_user_token(user)
        return {...}
```

### Example 2: Configuration
**OLD** (hardcoded):
```python
SECRET_KEY = "09d25e094faa..."
ALGORITHM = "HS256"
DATABASE_URL = "sqlite:///./siswa.db"
```

**NEW** (app/core/config.py):
```python
class Settings(BaseSettings):
    SECRET_KEY: str = "default..."
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./app/siswa.db"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

### Example 3: Dependencies
**OLD** (main.py):
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    return user
```

**NEW** (app/core/deps.py):
```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "Invalid authentication")
    return user
```

## 🚀 Migration Steps

### Step 1: Backup Old Code
```bash
mkdir misc
mv *.py misc/ (except main.py)
```

### Step 2: Create New Structure
```bash
mkdir -p app/{api/v1/endpoints,core,db,models,schemas,services,middleware}
```

### Step 3: Move & Refactor
1. ✅ Database config → `app/db/base.py`
2. ✅ Models → `app/models/user.py`
3. ✅ Schemas → `app/schemas/*.py`
4. ✅ Auth utils → `app/core/security.py`
5. ✅ RBAC → `app/core/authorization.py`
6. ✅ Endpoints → `app/api/v1/endpoints/*.py`
7. ✅ Business logic → `app/services/*.py`

### Step 4: Create New Files
1. ✅ `app/core/config.py` - Settings
2. ✅ `app/core/deps.py` - Dependencies
3. ✅ `app/api/v1/api.py` - Router aggregation
4. ✅ All `__init__.py` files

### Step 5: Update Main
Replace monolithic main.py with clean version

### Step 6: Add Docker Support
1. ✅ Create `Dockerfile`
2. ✅ Create `docker-compose.yml`
3. ✅ Create `.env.example`
4. ✅ Create `.dockerignore`

### Step 7: Test
```bash
uvicorn main:app --reload
# Check http://localhost:8000/docs
```

## 🎯 Key Changes

### 1. Imports
**OLD:**
```python
from db_sqlalchemy import User, SessionLocal
from schemas import UserCreate, LoginRequest
from auth_utils import hash_password, create_access_token
```

**NEW:**
```python
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest
from app.core.security import hash_password, create_access_token
from app.db.session import SessionLocal
```

### 2. Configuration
**OLD:** Hardcoded values
**NEW:** Environment-based with `pydantic-settings`

### 3. Business Logic
**OLD:** In endpoints
**NEW:** In services layer

### 4. Database
**OLD:** `db_sqlalchemy.py`
**NEW:** `app/db/base.py` + `app/db/session.py`

### 5. Routers
**OLD:** All in main.py
**NEW:** Organized in `app/api/v1/endpoints/`

## ✅ Verification Checklist

After migration, verify:

- [ ] Application starts without errors
- [ ] Database initializes automatically
- [ ] All endpoints accessible via /docs
- [ ] Authentication works (login)
- [ ] Protected endpoints require token
- [ ] RBAC permissions working
- [ ] CRUD operations functioning
- [ ] Environment variables loading

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Check `__init__.py` files exist in all folders

### Issue: Import errors
**Solution:** Use absolute imports: `from app.models.user import User`

### Issue: Settings not loading
**Solution:** Install `pydantic-settings`: `pip install pydantic-settings`

### Issue: Database path
**Solution:** Update DATABASE_URL in `.env` or `app/core/config.py`

## 📈 Benefits Gained

### Code Organization
- 597 lines → Multiple focused files
- Easy navigation
- Clear responsibility

### Maintainability
- Easy to find bugs
- Simple to add features
- Clear testing targets

### Scalability
- Add new endpoints easily
- Extend functionality
- Team collaboration

### Docker Ready
- Clean structure
- Environment configuration
- Production deployment

## 🎓 Learning Resources

- [Clean Architecture.md](CLEAN_ARCHITECTURE.md) - Full documentation
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - What was built
- [README.md](README.md) - Usage guide

---

**Migration Status**: ✅ COMPLETE

Selamat! Anda sekarang memiliki aplikasi dengan Clean Architecture yang production-ready! 🎉
