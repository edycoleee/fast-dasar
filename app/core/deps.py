"""
Core Dependencies
FastAPI dependencies for dependency injection
"""

from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User


# ==================== DATABASE ====================

def get_db() -> Generator:
    """
    Database session dependency
    
    Yields:
        SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== AUTHENTICATION ====================

def get_current_user(request: Request) -> dict:
    """
    Get current authenticated user from request state
    Set by JWT middleware
    
    Returns:
        User dict with id, nama, email, role
    
    Raises:
        HTTPException 401 if not authenticated
    """
    user = getattr(request.state, "user", None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current active user (can be extended with active/inactive check)
    
    Args:
        current_user: Current user from get_current_user
    
    Returns:
        Active user dict
    """
    # Here you can add checks for user.is_active, etc
    return current_user
