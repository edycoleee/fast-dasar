"""
Authentication Service
Business logic for authentication
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.core.security import verify_password, create_access_token


class AuthService:
    """Service for authentication business logic"""
    
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> User:
        """
        Authenticate user with email and password
        Returns user if valid, raises HTTPException if invalid
        """
        # Get user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
    
    @staticmethod
    def create_user_token(user: User) -> str:
        """Create JWT token for user"""
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role
        }
        return create_access_token(data=token_data)
    
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> dict:
        """
        Login user
        Returns dict with token and user info
        """
        # Authenticate
        user = AuthService.authenticate_user(db, login_data)
        
        # Create token
        access_token = AuthService.create_user_token(user)
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "nama": user.nama,
                "email": user.email,
                "role": user.role
            }
        }
