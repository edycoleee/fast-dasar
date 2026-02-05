"""
FastAPI Application
Main entry point with clean architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.base import init_db
from app.middleware.jwt_middleware import JWTMiddleware


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    FastAPI application with JWT Authentication and Role-Based Access Control (RBAC)
    
    ## Features
    - JWT Authentication
    - Password hashing with bcrypt
    - Role-based authorization (admin/user)
    - Clean architecture
    - SQLAlchemy ORM
    
    ## Authentication
    1. Login with email/password at `/api/v1/auth/login`
    2. Get JWT access token
    3. Use token in Authorization header: `Bearer <token>`
    
    ## Roles
    - **Admin**: Full CRUD + role management
    - **User**: Create, Read, Update (no Delete)
    """,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Login, logout, and dashboard operations"
        },
        {
            "name": "Users",
            "description": "User CRUD operations"
        },
        {
            "name": "Admin",
            "description": "Admin-only operations (role management)"
        }
    ]
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# JWT Middleware (optional - can be removed if using dependency injection only)
# app.add_middleware(JWTMiddleware)


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Root endpoint"""
    return {
        "message": "FastAPI with JWT Authentication & RBAC",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "login": f"{settings.API_V1_PREFIX}/auth/login",
            "dashboard": f"{settings.API_V1_PREFIX}/auth/dashboard",
            "users": f"{settings.API_V1_PREFIX}/users",
            "admin": f"{settings.API_V1_PREFIX}/admin"
        }
    }


# Startup event
@app.on_event("startup")
def on_startup():
    """Initialize database on startup"""
    print("🚀 Starting FastAPI application...")
    print(f"📦 Project: {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"🗄️  Database: {settings.DATABASE_URL}")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔗 API v1: http://localhost:8000{settings.API_V1_PREFIX}")


# Shutdown event
@app.on_event("shutdown")
def on_shutdown():
    """Cleanup on shutdown"""
    print("👋 Shutting down FastAPI application...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
