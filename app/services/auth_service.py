"""
Authentication Service
Business logic for authentication
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.core.security import verify_password, create_access_token
from app.core.exceptions import InvalidCredentialsException
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication business logic"""
    
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> User:
        """
        Authenticate user with email and password
        Returns user if valid, raises InvalidCredentialsException if invalid
        """
        logger.info(f"Authentication attempt for email: {login_data.email}")
        
        # Get user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            logger.warning(f"Authentication failed: User not found - {login_data.email}")
            raise InvalidCredentialsException()
        
        # Verify password
        if not verify_password(login_data.password, user.password):
            logger.warning(f"Authentication failed: Invalid password - {login_data.email}")
            raise InvalidCredentialsException()
        
        logger.info(f"Authentication successful for user: {user.email} (ID: {user.id})")
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
        logger.info(f"Login attempt for: {login_data.email}")
        
        try:
            # Authenticate
            user = AuthService.authenticate_user(db, login_data)
            
            # Create token
            access_token = AuthService.create_user_token(user)
            
            logger.info(f"Login successful for user: {user.email} (ID: {user.id}, Role: {user.role})")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "nama": user.nama,
                    "email": user.email,
                    "role": user.role
                }
            }
        except Exception as e:
            logger.error(f"Login failed for {login_data.email}: {str(e)}")
            raise
