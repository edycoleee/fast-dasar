"""
Authorization Utilities
Role-Based Access Control (RBAC) untuk FastAPI
"""

from fastapi import HTTPException, status, Request
from typing import List, Optional


# ==================== ROLE CONSTANTS ====================

class Role:
    """Role constants"""
    ADMIN = "admin"
    USER = "user"


# ==================== PERMISSION CHECKER ====================

def get_current_user(request: Request) -> dict:
    """
    Get current user dari request.state
    Di-set oleh JWT middleware
    
    Returns:
        User dict dengan id, nama, email, role
    
    Raises:
        HTTPException 401 jika user tidak authenticated
    """
    user = getattr(request.state, "user", None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_role(request: Request, required_roles: List[str]):
    """
    Check apakah user punya role yang required
    
    Args:
        request: FastAPI Request object
        required_roles: List of allowed roles (e.g., ["admin"] atau ["admin", "user"])
    
    Raises:
        HTTPException 401 jika not authenticated
        HTTPException 403 jika role tidak sesuai
    
    Example:
        require_role(request, [Role.ADMIN])  # Hanya admin
        require_role(request, [Role.ADMIN, Role.USER])  # Admin atau user
    """
    # Get current user
    user = get_current_user(request)
    
    # Check role
    user_role = user.get("role")
    
    if user_role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required role: {', '.join(required_roles)}. Your role: {user_role}"
        )


def require_admin(request: Request):
    """
    Shortcut untuk require admin role
    
    Raises:
        HTTPException 403 jika bukan admin
    """
    require_role(request, [Role.ADMIN])


def require_authenticated(request: Request):
    """
    Check apakah user authenticated (any role)
    
    Raises:
        HTTPException 401 jika not authenticated
    """
    get_current_user(request)


def is_admin(request: Request) -> bool:
    """
    Check apakah current user adalah admin
    
    Returns:
        True jika admin, False jika bukan
    """
    try:
        user = get_current_user(request)
        return user.get("role") == Role.ADMIN
    except HTTPException:
        return False


def is_owner_or_admin(request: Request, resource_user_id: int) -> bool:
    """
    Check apakah user adalah owner dari resource atau admin
    
    Args:
        request: FastAPI Request
        resource_user_id: ID user yang memiliki resource
    
    Returns:
        True jika user adalah owner atau admin
    """
    try:
        user = get_current_user(request)
        
        # Admin bisa akses semua
        if user.get("role") == Role.ADMIN:
            return True
        
        # User hanya bisa akses milik sendiri
        return user.get("id") == resource_user_id
    
    except HTTPException:
        return False


# ==================== PERMISSION DECORATORS ====================

def check_permission(required_roles: List[str] = None):
    """
    Decorator untuk check permission
    
    Usage:
        @check_permission([Role.ADMIN])
        async def delete_siswa(...):
            ...
    
    Note: Lebih baik pakai require_role() langsung di endpoint
          untuk lebih explicit
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request = kwargs.get("request")
            if not request:
                raise HTTPException(500, "Request object not found")
            
            # Check role
            if required_roles:
                require_role(request, required_roles)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
