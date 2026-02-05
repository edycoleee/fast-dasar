"""
Admin Endpoints
Admin-only operations
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.core.authorization import require_admin
from app.schemas.user import UserResponse, UpdateRole
from app.services.user_service import UserService

router = APIRouter()


@router.patch("/{user_id}/role", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user_role(
    user_id: int,
    role_data: UpdateRole,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update user role (admin only)
    
    - **user_id**: ID of user to update
    - **role**: New role (admin or user)
    - Requires admin role
    """
    # Check admin permission
    require_admin(current_user)
    
    # Update role
    updated_user = UserService.update_user_role(db, user_id, role_data.role)
    
    return updated_user
