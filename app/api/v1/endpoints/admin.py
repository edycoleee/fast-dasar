"""
Admin Endpoints
Admin-only operations
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.core.authorization import require_admin
from app.core import get_logger
from app.schemas.user import UserResponse, UpdateRole
from app.schemas import StandardResponse, success_response
from app.services.user_service import UserService

router = APIRouter()
logger = get_logger(__name__)


@router.patch("/{user_id}/role", response_model=StandardResponse[UserResponse], status_code=status.HTTP_200_OK)
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
    
    logger.info(f"Updating user {user_id} role to {role_data.role} - Requested by: {current_user.email}")
    
    # Update role
    updated_user = UserService.update_user_role(db, user_id, role_data.role)
    
    return success_response(f"User {user_id} role updated to {role_data.role} successfully", updated_user)
