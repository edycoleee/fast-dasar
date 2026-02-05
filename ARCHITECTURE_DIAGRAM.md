# 🏗️ Architecture Diagram

## Clean Architecture - Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT / BROWSER                         │
│                   (Web, Mobile, Desktop App)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         │ (JSON + JWT Token)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FASTAPI APP                              │
│                         (main.py)                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    MIDDLEWARE LAYER                       │   │
│  │  • CORS Middleware                                        │   │
│  │  • JWT Middleware (Optional)                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Route to API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
│                    (app/api/v1/endpoints/)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   auth.py    │  │   users.py   │  │   admin.py   │          │
│  │              │  │              │  │              │          │
│  │ • login      │  │ • GET /users │  │ • update     │          │
│  │ • logout     │  │ • POST /user │  │   role       │          │
│  │ • dashboard  │  │ • PUT /user  │  │              │          │
│  │              │  │ • DELETE     │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          │  Depends on     │  Depends on     │  Depends on
          │  Dependencies   │  Dependencies   │  Dependencies
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DEPENDENCIES LAYER                            │
│                      (app/core/deps.py)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • get_db() ──────► Database Session                      │   │
│  │ • get_current_user() ──► JWT Validation ──► User Object  │   │
│  │ • require_admin() ──────► RBAC Check                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────┬───────────────┬──────────────────┬────────────────────┘
          │               │                  │
          │               │                  │
          ▼               ▼                  ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────────────┐
│  CORE UTILITIES │ │   SERVICES   │ │   AUTHORIZATION        │
│  (app/core/)    │ │  (app/       │ │   (app/core/           │
│                 │ │   services/) │ │    authorization.py)   │
│ ┌─────────────┐ │ │              │ │                        │
│ │ security.py │ │ │ ┌──────────┐ │ │ • require_admin()      │
│ │             │ │ │ │  user    │ │ │ • require_role()       │
│ │ • hash      │ │ │ │ _service │ │ │ • is_admin()           │
│ │   password  │ │ │ │          │ │ │                        │
│ │ • verify    │ │ │ │ • create │ │ │                        │
│ │   password  │ │ │ │ • read   │ │ │                        │
│ │ • create    │ │ │ │ • update │ │ │                        │
│ │   token     │ │ │ │ • delete │ │ │                        │
│ │ • decode    │ │ │ │ • role   │ │ │                        │
│ │   token     │ │ │ └────┬─────┘ │ │                        │
│ └─────────────┘ │ │      │       │ │                        │
│                 │ │ ┌────▼─────┐ │ │                        │
│ ┌─────────────┐ │ │ │  auth    │ │ │                        │
│ │  config.py  │ │ │ │ _service │ │ │                        │
│ │             │ │ │ │          │ │ │                        │
│ │ • Settings  │ │ │ │ • login  │ │ │                        │
│ │ • ENV vars  │ │ │ │ • auth   │ │ │                        │
│ │ • JWT cfg   │ │ │ │ • token  │ │ │                        │
│ └─────────────┘ │ │ └────┬─────┘ │ │                        │
└─────────────────┘ └──────┼───────┘ └────────────────────────┘
                           │
                           │ Uses Models & DB
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VALIDATION LAYER                             │
│                      (app/schemas/)                              │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │    user.py       │         │    auth.py       │              │
│  │                  │         │                  │              │
│  │ • UserCreate     │         │ • LoginRequest   │              │
│  │ • UserUpdate     │         │ • LoginResponse  │              │
│  │ • UserResponse   │         │ • Token          │              │
│  │ • UpdateRole     │         │ • TokenData      │              │
│  └──────────────────┘         └──────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Validates data for
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MODELS LAYER                               │
│                      (app/models/)                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       user.py                             │   │
│  │                                                           │   │
│  │  User Model (SQLAlchemy):                                │   │
│  │  • id: Integer (Primary Key)                             │   │
│  │  • nama: String                                           │   │
│  │  • email: String (Unique)                                 │   │
│  │  • password: String (Hashed)                              │   │
│  │  • role: String (admin/user)                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ ORM Mapping
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                              │
│                        (app/db/)                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       base.py                             │   │
│  │                                                           │   │
│  │  • Engine (SQLAlchemy)                                    │   │
│  │  • SessionLocal (DB Session Factory)                      │   │
│  │  • Base (Declarative Base)                                │   │
│  │  • init_db() (Auto create tables)                         │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQL Operations
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE                                 │
│                    SQLite / PostgreSQL                           │
│                                                                  │
│  Table: users                                                    │
│  ┌────┬─────────┬──────────────────┬──────────┬────────┐       │
│  │ id │  nama   │      email       │ password │  role  │       │
│  ├────┼─────────┼──────────────────┼──────────┼────────┤       │
│  │ 1  │ Admin   │ admin@test.com   │ $2b$...  │ admin  │       │
│  │ 2  │ User    │ user@test.com    │ $2b$...  │ user   │       │
│  └────┴─────────┴──────────────────┴──────────┴────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Login Flow
```
Client
  │
  ├─► POST /api/v1/auth/login
  │   { email, password }
  │
  ▼
API Layer (auth.py)
  │
  ├─► AuthService.login()
  │
  ▼
Auth Service
  │
  ├─► authenticate_user()
  │   ├─► Query User from DB
  │   └─► verify_password()
  │
  ├─► create_user_token()
  │   └─► create_access_token() (JWT)
  │
  ▼
Response
  {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "user": {...}
  }
```

### 2. Protected Endpoint Flow
```
Client
  │
  ├─► GET /api/v1/auth/dashboard
  │   Header: Authorization: Bearer eyJ...
  │
  ▼
Dependencies
  │
  ├─► get_current_user()
  │   ├─► extract_bearer_token()
  │   ├─► decode_access_token()
  │   ├─► Query User from DB
  │   └─► Return User object
  │
  ▼
API Layer (auth.py)
  │
  ├─► dashboard(current_user)
  │
  ▼
Response
  {
    "message": "Welcome...",
    "user": {...},
    "permissions": {...}
  }
```

### 3. CRUD Flow (Admin Only)
```
Client
  │
  ├─► DELETE /api/v1/users/2
  │   Header: Authorization: Bearer eyJ...
  │
  ▼
Dependencies
  │
  ├─► get_current_user() → User object
  ├─► require_admin() → Check role
  │
  ▼
API Layer (users.py)
  │
  ├─► delete_user(id, current_user)
  │
  ▼
User Service
  │
  ├─► UserService.delete_user()
  │   ├─► Query User from DB
  │   ├─► Delete User
  │   └─► Commit
  │
  ▼
Response
  {
    "message": "User deleted"
  }
```

## Layer Responsibilities

### 1. API Layer
- Handle HTTP requests/responses
- Route to appropriate handlers
- Validate input with Pydantic
- Inject dependencies

### 2. Services Layer
- Business logic
- Coordinate between models
- Error handling
- Reusable operations

### 3. Models Layer
- Database schema
- ORM mappings
- Table definitions

### 4. Schemas Layer
- Request validation
- Response serialization
- Type safety

### 5. Core Layer
- Configuration
- Security utilities
- Dependencies
- Authorization

### 6. Database Layer
- Connection management
- Session handling
- Table creation

## Security Flow

```
Password Hashing (Registration):
plaintext → bcrypt.hash() → $2b$12$...

Password Verification (Login):
plaintext + hash → bcrypt.verify() → True/False

JWT Creation (Login):
{ email, user_id, role } → jose.jwt.encode() → eyJ...

JWT Validation (Protected Endpoints):
token → jose.jwt.decode() → { email, user_id, role }
      → Query DB → User object
```

## RBAC Flow

```
Request → get_current_user() → User object
                                   │
                                   ├─► Check role
                                   │
                                   ▼
                           ┌─────────────┐
                           │ role check  │
                           └─────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
              ┌──────────┐            ┌──────────┐
              │  admin   │            │   user   │
              └────┬─────┘            └────┬─────┘
                   │                       │
                   │                       │
            ┌──────▼──────┐         ┌──────▼──────┐
            │ Full CRUD   │         │ CRU only    │
            │ + Role Mgmt │         │ (no Delete) │
            └─────────────┘         └─────────────┘
```

---

**Architecture**: Clean, Modular, Scalable
**Pattern**: Dependency Injection + Service Layer
**Security**: JWT + RBAC + Password Hashing
