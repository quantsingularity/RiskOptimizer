"""
Authentication service for JWT token management and user authentication.
Implements secure authentication with JWT tokens and password hashing.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from riskoptimizer.core.config import config
from riskoptimizer.core.exceptions import AuthenticationError, ValidationError
from riskoptimizer.core.logging import get_logger
from riskoptimizer.infrastructure.database.repositories.user_repository import user_repository
from riskoptimizer.infrastructure.database.session import get_db_session
from riskoptimizer.infrastructure.cache.redis_cache import redis_cache

logger = get_logger(__name__)


class AuthService:
    """Service for authentication and JWT token management."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.user_repo = user_repository
        self.cache = redis_cache
        self.secret_key = config.security.jwt_secret_key
        self.access_token_expires = config.security.jwt_access_token_expires
        self.refresh_token_expires = config.security.jwt_refresh_token_expires
        self.password_rounds = config.security.password_hash_rounds
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
            
        Raises:
            ValidationError: If password is invalid
        """
        if not password or not isinstance(password, str):
            raise ValidationError("Password is required", "password")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long", "password")
        
        # Hash password with bcrypt
        salt = bcrypt.gensalt(rounds=self.password_rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}", exc_info=True)
            return False
    
    def generate_tokens(self, user_id: int, email: str, role: str) -> Dict[str, str]:
        """
        Generate access and refresh tokens for a user.
        
        Args:
            user_id: User ID
            email: User email
            role: User role
            
        Returns:
            Dictionary with access and refresh tokens
        """
        now = datetime.utcnow()
        
        # Generate access token
        access_payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(seconds=self.access_token_expires)
        }
        access_token = jwt.encode(access_payload, self.secret_key, algorithm='HS256')
        
        # Generate refresh token
        refresh_payload = {
            'user_id': user_id,
            'email': email,
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(seconds=self.refresh_token_expires)
        }
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm='HS256')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': self.access_token_expires
        }
    
    def verify_token(self, token: str, token_type: str = 'access') -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token
            token_type: Type of token ('access' or 'refresh')
            
        Returns:
            Decoded token payload
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            # Check if token is blacklisted
            if self.is_token_blacklisted(token):
                raise AuthenticationError("Token has been revoked")
            
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Verify token type
            if payload.get('type') != token_type:
                raise AuthenticationError(f"Invalid token type: expected {token_type}")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Generate a new access token using a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        # Verify refresh token
        payload = self.verify_token(refresh_token, 'refresh')
        
        # Get user from database
        with get_db_session() as session:
            user = self.user_repo.get_by_id(payload['user_id'], session)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")
            
            # Generate new access token
            tokens = self.generate_tokens(user.id, user.email, user.role)
            
            # Return only the access token
            return {
                'access_token': tokens['access_token'],
                'token_type': 'Bearer',
                'expires_in': self.access_token_expires
            }
    
    def blacklist_token(self, token: str) -> None:
        """
        Add a token to the blacklist.
        
        Args:
            token: JWT token to blacklist
        """
        try:
            # Decode token to get expiration time
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'], options={"verify_exp": False})
            exp = payload.get('exp')
            
            if exp:
                # Calculate TTL for cache entry
                exp_datetime = datetime.utcfromtimestamp(exp)
                ttl = int((exp_datetime - datetime.utcnow()).total_seconds())
                
                if ttl > 0:
                    # Add token to blacklist cache
                    cache_key = f"blacklist:{token}"
                    self.cache.set(cache_key, True, ttl=ttl)
                    
                    logger.info(f"Token blacklisted for {ttl} seconds")
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}", exc_info=True)
    
    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token: JWT token to check
            
        Returns:
            True if token is blacklisted, False otherwise
        """
        try:
            cache_key = f"blacklist:{token}"
            return self.cache.exists(cache_key)
        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}", exc_info=True)
            return False
    
    def authenticate_user(self, email: str, password: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (user_data, tokens)
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If input is invalid
        """
        # Validate input
        if not email or not isinstance(email, str):
            raise ValidationError("Email is required", "email")
        
        if not password or not isinstance(password, str):
            raise ValidationError("Password is required", "password")
        
        with get_db_session() as session:
            # Get user by email
            user = self.user_repo.get_by_email(email, session)
            if not user:
                raise AuthenticationError("Invalid email or password")
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationError("User account is inactive")
            
            # Verify password
            if not self.verify_password(password, user.hashed_password):
                raise AuthenticationError("Invalid email or password")
            
            # Generate tokens
            tokens = self.generate_tokens(user.id, user.email, user.role)
            
            # Prepare user data
            user_data = {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'wallet_address': user.wallet_address,
                'role': user.role,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
            
            logger.info(f"User authenticated successfully: {email}")
            return user_data, tokens
    
    def register_user(self, email: str, username: str, password: str, 
                      wallet_address: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Register a new user.
        
        Args:
            email: User email
            username: Username
            password: User password
            wallet_address: User wallet address (optional)
            
        Returns:
            Tuple of (user_data, tokens)
            
        Raises:
            ValidationError: If input is invalid
            ConflictError: If user already exists
        """
        # Validate input
        if not email or not isinstance(email, str):
            raise ValidationError("Email is required", "email")
        
        if not username or not isinstance(username, str):
            raise ValidationError("Username is required", "username")
        
        if not password or not isinstance(password, str):
            raise ValidationError("Password is required", "password")
        
        # Hash password
        hashed_password = self.hash_password(password)
        
        with get_db_session() as session:
            # Create user
            user = self.user_repo.create(
                email=email,
                username=username,
                hashed_password=hashed_password,
                wallet_address=wallet_address,
                session=session
            )
            
            # Generate tokens
            tokens = self.generate_tokens(user.id, user.email, user.role)
            
            # Prepare user data
            user_data = {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'wallet_address': user.wallet_address,
                'role': user.role,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
            
            logger.info(f"User registered successfully: {email}")
            return user_data, tokens
    
    def logout_user(self, access_token: str, refresh_token: str) -> None:
        """
        Logout a user by blacklisting their tokens.
        
        Args:
            access_token: User's access token
            refresh_token: User's refresh token
        """
        # Blacklist both tokens
        self.blacklist_token(access_token)
        self.blacklist_token(refresh_token)
        
        logger.info("User logged out successfully")


# Singleton instance
auth_service = AuthService()

