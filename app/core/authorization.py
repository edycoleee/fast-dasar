"""
Authorization utilities
Role-Based Access Control (RBAC)
"""

from fastapi import HTTPException, status, Request
from typing import List

from app.core.deps import get_current_user


# ==================== ROLE CONSTANTS ====================

class Role:
    """Role constants"""
    ADMIN = "admin"
    USER = "user"


# ==================== PERMISSION CHECKERS ====================

def require_role(request: Request, required_roles: List[str]):
    """
    Check if user has required role
    
    Args:
        request: FastAPI Request
        required_roles: List of allowed roles
    
    Raises:
        HTTPException 401 if not authenticated
        HTTPException 403 if insufficient permissions
    """
    user = get_current_user(request)
    user_role = user.get("role")
    
    if user_role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required role: {', '.join(required_roles)}. Your role: {user_role}"
        )


def require_admin(request: Request):
    """Require admin role"""
    require_role(request, [Role.ADMIN])


def is_admin(request: Request) -> bool:
    """Check if current user is admin"""
    try:
        user = get_current_user(request)
        return user.get("role") == Role.ADMIN
    except HTTPException:
        return False
