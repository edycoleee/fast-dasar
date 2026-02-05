"""
Authentication Endpoints
Login, logout, and protected dashboard
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.core import get_logger
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserResponse
from app.schemas import StandardResponse, success_response
from app.services.auth_service import AuthService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/login", response_model=StandardResponse[LoginResponse], status_code=status.HTTP_200_OK)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint
    
    - **email**: User email
    - **password**: User password
    - Returns: JWT access token and user info
    """
    logger.info(f"Login attempt for email: {login_data.email}")
    result = AuthService.login(db, login_data)
    logger.info(f"User logged in successfully: {login_data.email}")
    return success_response("Login successful", result)


@router.post("/logout", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    Logout endpoint
    
    Note: With JWT, logout is handled on client side by removing the token.
    This endpoint is just for confirmation and can be used for logging purposes.
    """
    logger.info(f"User logged out: {current_user.email}")
    return success_response(
        f"User {current_user.nama} logged out successfully. Please remove the JWT token from client storage",
        {"user": current_user.nama}
    )


@router.get("/dashboard", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
def dashboard(current_user: UserResponse = Depends(get_current_user)):
    """
    Protected dashboard endpoint
    Requires valid JWT token
    """
    logger.info(f"Dashboard accessed by: {current_user.email}")
    dashboard_data = {
        "user": {
            "id": current_user.id,
            "nama": current_user.nama,
            "email": current_user.email,
            "role": current_user.role
        },
        "permissions": {
            "can_create": True,
            "can_read": True,
            "can_update": True,
            "can_delete": current_user.role == "admin",
            "can_manage_roles": current_user.role == "admin"
        }
    }
    return success_response(f"Welcome to dashboard, {current_user.nama}!", dashboard_data)
