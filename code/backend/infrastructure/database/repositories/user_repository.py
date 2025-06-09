"""
User repository for database operations related to users.
Implements the repository pattern for data access.
"""

from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from riskoptimizer.core.exceptions import DatabaseError, NotFoundError, ConflictError
from riskoptimizer.core.logging import get_logger
from riskoptimizer.infrastructure.database.models import User
from riskoptimizer.infrastructure.database.session import get_db_session

logger = get_logger(__name__)


class UserRepository:
    """Repository for user-related database operations."""
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize repository with optional session.
        
        Args:
            session: SQLAlchemy session (optional)
        """
        self._session = session
    
    def _get_session(self, session: Optional[Session] = None) -> Session:
        """
        Get session for database operations.
        
        Args:
            session: SQLAlchemy session (optional)
            
        Returns:
            SQLAlchemy session
        """
        return session or self._session
    
    def get_by_id(self, user_id: int, session: Optional[Session] = None) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            session: SQLAlchemy session (optional)
            
        Returns:
            User or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            user = db.query(User).filter(User.id == user_id).first()
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by ID: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to get user: {str(e)}")
    
    def get_by_email(self, email: str, session: Optional[Session] = None) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            session: SQLAlchemy session (optional)
            
        Returns:
            User or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            user = db.query(User).filter(User.email == email).first()
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by email: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to get user: {str(e)}")
    
    def get_by_username(self, username: str, session: Optional[Session] = None) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            session: SQLAlchemy session (optional)
            
        Returns:
            User or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            user = db.query(User).filter(User.username == username).first()
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by username: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to get user: {str(e)}")
    
    def get_by_wallet_address(self, wallet_address: str, session: Optional[Session] = None) -> Optional[User]:
        """
        Get user by wallet address.
        
        Args:
            wallet_address: User wallet address
            session: SQLAlchemy session (optional)
            
        Returns:
            User or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            user = db.query(User).filter(User.wallet_address == wallet_address).first()
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by wallet address: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to get user: {str(e)}")
    
    def create(self, email: str, username: str, hashed_password: str, wallet_address: Optional[str] = None,
               role: str = "user", session: Optional[Session] = None) -> User:
        """
        Create a new user.
        
        Args:
            email: User email
            username: Username
            hashed_password: Hashed password
            wallet_address: User wallet address (optional)
            role: User role
            session: SQLAlchemy session (optional)
            
        Returns:
            Created user
            
        Raises:
            ConflictError: If user with email, username, or wallet address already exists
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            
            # Create user
            user = User(
                email=email,
                username=username,
                hashed_password=hashed_password,
                wallet_address=wallet_address,
                role=role
            )
            
            db.add(user)
            db.flush()  # Flush to get the ID
            
            logger.info(f"Created user {user.id} with email {email}")
            return user
        except IntegrityError as e:
            logger.error(f"Error creating user (conflict): {str(e)}", exc_info=True)
            if "email" in str(e).lower():
                raise ConflictError(f"User with email {email} already exists", "user")
            elif "username" in str(e).lower():
                raise ConflictError(f"User with username {username} already exists", "user")
            elif "wallet_address" in str(e).lower():
                raise ConflictError(f"User with wallet address {wallet_address} already exists", "user")
            else:
                raise ConflictError("User already exists", "user")
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    def update(self, user_id: int, data: Dict[str, Any], session: Optional[Session] = None) -> User:
        """
        Update user.
        
        Args:
            user_id: User ID
            data: Dictionary with fields to update
            session: SQLAlchemy session (optional)
            
        Returns:
            Updated user
            
        Raises:
            NotFoundError: If user not found
            ConflictError: If update violates unique constraints
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise NotFoundError(f"User {user_id} not found", "user", str(user_id))
            
            # Update fields
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            db.flush()
            
            logger.info(f"Updated user {user_id}")
            return user
        except NotFoundError:
            raise
        except IntegrityError as e:
            logger.error(f"Error updating user (conflict): {str(e)}", exc_info=True)
            if "email" in str(e).lower():
                raise ConflictError(f"User with email {data.get('email')} already exists", "user")
            elif "username" in str(e).lower():
                raise ConflictError(f"User with username {data.get('username')} already exists", "user")
            elif "wallet_address" in str(e).lower():
                raise ConflictError(f"User with wallet address {data.get('wallet_address')} already exists", "user")
            else:
                raise ConflictError("Update violates unique constraints", "user")
        except SQLAlchemyError as e:
            logger.error(f"Error updating user: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to update user: {str(e)}")
    
    def delete(self, user_id: int, session: Optional[Session] = None) -> bool:
        """
        Delete user.
        
        Args:
            user_id: User ID
            session: SQLAlchemy session (optional)
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Delete user (cascade will delete related entities)
            db.delete(user)
            db.flush()
            
            logger.info(f"Deleted user {user_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to delete user: {str(e)}")
    
    def get_all(self, skip: int = 0, limit: int = 100, session: Optional[Session] = None) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            session: SQLAlchemy session (optional)
            
        Returns:
            List of users
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            users = db.query(User).offset(skip).limit(limit).all()
            return users
        except SQLAlchemyError as e:
            logger.error(f"Error getting all users: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to get users: {str(e)}")
    
    def count(self, session: Optional[Session] = None) -> int:
        """
        Count total number of users.
        
        Args:
            session: SQLAlchemy session (optional)
            
        Returns:
            Total number of users
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db = self._get_session(session)
            count = db.query(User).count()
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error counting users: {str(e)}", exc_info=True)
            raise DatabaseError(f"Failed to count users: {str(e)}")


# Singleton instance
user_repository = UserRepository()

