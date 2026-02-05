"""
Authentication Endpoints
Login, logout, and protected dashboard
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
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
    return AuthService.login(db, login_data)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    Logout endpoint
    
    Note: With JWT, logout is handled on client side by removing the token.
    This endpoint is just for confirmation and can be used for logging purposes.
    """
    return {
        "message": f"User {current_user.nama} logged out successfully",
        "note": "Please remove the JWT token from client storage"
    }


@router.get("/dashboard", response_model=dict, status_code=status.HTTP_200_OK)
def dashboard(current_user: UserResponse = Depends(get_current_user)):
    """
    Protected dashboard endpoint
    Requires valid JWT token
    """
    return {
        "message": f"Welcome to dashboard, {current_user.nama}!",
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
