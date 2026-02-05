"""
FastAPI Application
Main entry point with clean architecture
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core import setup_logging, get_logger, AppException
from app.schemas import error_response
from app.api.v1.api import api_router
from app.db.base import init_db
from app.middleware.jwt_middleware import JWTMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)


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


# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    logger.error(f"AppException: {exc.message} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.message, exc.status_code)
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(exc)} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            "Internal server error. Please try again later.",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    )


# JWT Middleware (optional - can be removed if using dependency injection only)
# app.add_middleware(JWTMiddleware)


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
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
    logger.info("🚀 Starting FastAPI application...")
    logger.info(f"📦 Project: {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"🗄️  Database: {settings.DATABASE_URL}")
    
    # Initialize database
    init_db()
    logger.info("✅ Database initialized")
    
    logger.info(f"📚 API Docs: http://localhost:8000/docs")
    logger.info(f"🔗 API v1: http://localhost:8000{settings.API_V1_PREFIX}")


# Shutdown event
@app.on_event("shutdown")
def on_shutdown():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down FastAPI application...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
