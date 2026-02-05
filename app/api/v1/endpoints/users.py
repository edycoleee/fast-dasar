"""
User Endpoints
CRUD operations for users
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.core import get_logger
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas import StandardResponse, success_response
from app.services.user_service import UserService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=StandardResponse[List[UserResponse]], status_code=status.HTTP_200_OK)
def read_all_users(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all users
    Requires authentication
    """
    logger.info(f"Fetching all users - Requested by: {current_user.email}")
    users = UserService.get_all_users(db)
    return success_response(f"Retrieved {len(users)} users successfully", users)


@router.get("/{user_id}", response_model=StandardResponse[UserResponse], status_code=status.HTTP_200_OK)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get user by ID
    Requires authentication
    """
    logger.info(f"Fetching user {user_id} - Requested by: {current_user.email}")
    user = UserService.get_user_by_id(db, user_id)
    return success_response(f"User {user_id} retrieved successfully", user)


@router.post("/", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create new user
    Requires authentication
    """
    logger.info(f"Creating new user: {user.email} - Requested by: {current_user.email}")
    new_user = UserService.create_user(db, user)
    return success_response(f"User {user.email} created successfully", new_user)


@router.put("/{user_id}", response_model=StandardResponse[UserResponse], status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update user
    Requires authentication
    """
    logger.info(f"Updating user {user_id} - Requested by: {current_user.email}")
    updated_user = UserService.update_user(db, user_id, user)
    return success_response(f"User {user_id} updated successfully", updated_user)


@router.delete("/{user_id}", response_model=StandardResponse[dict], status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete user
    Requires admin role
    """
    from app.core.authorization import require_admin
    
    # Check admin permission
    require_admin(current_user)
    
    logger.info(f"Deleting user {user_id} - Requested by: {current_user.email}")
    UserService.delete_user(db, user_id)
    return success_response(f"User {user_id} deleted successfully", {"deleted_user_id": user_id})
