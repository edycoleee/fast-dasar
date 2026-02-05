"""
User Service
Business logic for user operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from app.core.exceptions import (
    UserNotFoundException,
    DuplicateEmailException,
    DatabaseException
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user business logic"""
    
    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """Get all users"""
        logger.info("Fetching all users")
        users = db.query(User).all()
        logger.info(f"Found {len(users)} users")
        return users
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID, raises UserNotFoundException if not found"""
        logger.info(f"Fetching user by ID: {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found: ID {user_id}")
            raise UserNotFoundException(user_id=user_id)
        logger.info(f"User found: {user.email} (ID: {user.id})")
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create new user"""
        logger.info(f"Creating new user: {user.email}")
        
        # Check if email already exists
        existing_user = UserService.get_user_by_email(db, user.email)
        if existing_user:
            logger.warning(f"User creation failed: Email already exists - {user.email}")
            raise DuplicateEmailException(user.email)
        
        try:
            # Hash password
            hashed_password = hash_password(user.password)
            
            # Create user
            db_user = User(
                nama=user.nama,
                email=user.email,
                password=hashed_password,
                role=user.role
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User created successfully: {db_user.email} (ID: {db_user.id}, Role: {db_user.role})")
            return db_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"User creation failed: {str(e)}")
            raise DatabaseException(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """Update user"""
        logger.info(f"Updating user: ID {user_id}")
        
        db_user = UserService.get_user_by_id(db, user_id)
        
        # Check if new email already exists
        if user_update.email != db_user.email:
            existing_user = UserService.get_user_by_email(db, user_update.email)
            if existing_user:
                logger.warning(f"Update failed: Email already exists - {user_update.email}")
                raise DuplicateEmailException(user_update.email)
        
        try:
            # Update fields
            db_user.nama = user_update.nama
            db_user.email = user_update.email
            
            # Update password if provided
            if user_update.password:
                db_user.password = hash_password(user_update.password)
                logger.info(f"Password updated for user: {db_user.email}")
            
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User updated successfully: {db_user.email} (ID: {db_user.id})")
            return db_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"User update failed: {str(e)}")
            raise DatabaseException(f"Failed to update user: {str(e)}")
    
    @stalogger.info(f"Deleting user: ID {user_id}")
        
        db_user = UserService.get_user_by_id(db, user_id)
        
        try:
            db.delete(db_user)
            db.commit()
            logger.info(f"User deleted successfully: {db_user.email} (ID: {user_id})")
            
        except Exception as e:
            db.rollback()
            logger.error(f"User deletion failed: {str(e)}")
            raise DatabaseException(f"Failed to delete user: {str(e)}")
    
    @staticmethod
    def update_user_role(db: Session, user_id: int, new_role: str) -> User:
        """Update user role (admin only)"""
        logger.info(f"Updating role for user ID {user_id} to: {new_role}")
        
        db_user = UserService.get_user_by_id(db, user_id)
        
        try:
            old_role = db_user.role
            db_user.role = new_role
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Role updated successfully for user {db_user.email}: {old_role} -> {new_role}")
            return db_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Role update failed: {str(e)}")
            raise DatabaseException(f"Failed to update user role: {str(e)}")
        db.refresh(db_user)
        
        return db_user
