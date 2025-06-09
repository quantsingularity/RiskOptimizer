"""
Authentication controller for handling user authentication API endpoints.
Implements user registration, login, token refresh, and logout.
"""

from typing import Dict, Any, Tuple
from flask import Blueprint, request, jsonify, Response, g

from riskoptimizer.core.exceptions import ValidationError, AuthenticationError, RiskOptimizerException
from riskoptimizer.core.logging import get_logger
from riskoptimizer.domain.services.auth_service import auth_service
from riskoptimizer.api.schemas.auth_schema import (
    validate_login_request, validate_register_request, validate_refresh_token_request
)

logger = get_logger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


def create_success_response(data: Any, message: str = None, meta: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create standardized success response.
    
    Args:
        data: Response data
        message: Optional success message
        meta: Optional metadata
        
    Returns:
        Standardized response dictionary
    """
    response = {
        "status": "success",
        "data": data
    }
    
    if message:
        response["message"] = message
    
    if meta:
        response["meta"] = meta
    
    return response


def create_error_response(error: RiskOptimizerException) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error: Exception instance
        
    Returns:
        Standardized error response dictionary
    """
    return {
        "status": "error",
        "error": error.to_dict()
    }


@auth_bp.route('/register', methods=['POST'])
def register() -> Response:
    """
    Register a new user.
    
    Returns:
        User data and authentication tokens
    """
    try:
        logger.info("User registration request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Validate request data
        validated_data = validate_register_request(data)
        
        # Register user
        user_data, tokens = auth_service.register_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            wallet_address=validated_data.get('wallet_address')
        )
        
        # Create success response
        response = create_success_response(
            data={
                "user": user_data,
                "tokens": tokens
            },
            message="User registered successfully"
        )
        
        logger.info(f"User registered successfully: {validated_data['email']}")
        return jsonify(response), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error during registration: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except RiskOptimizerException as e:
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500


@auth_bp.route('/login', methods=['POST'])
def login() -> Response:
    """
    Authenticate a user and issue tokens.
    
    Returns:
        User data and authentication tokens
    """
    try:
        logger.info("User login request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Validate request data
        validated_data = validate_login_request(data)
        
        # Authenticate user
        user_data, tokens = auth_service.authenticate_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Create success response
        response = create_success_response(
            data={
                "user": user_data,
                "tokens": tokens
            },
            message="User authenticated successfully"
        )
        
        logger.info(f"User authenticated successfully: {validated_data['email']}")
        return jsonify(response), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error during login: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except AuthenticationError as e:
        logger.warning(f"Authentication error: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 401
        
    except RiskOptimizerException as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token() -> Response:
    """
    Refresh access token using a valid refresh token.
    
    Returns:
        New access token
    """
    try:
        logger.info("Token refresh request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Validate request data
        validated_data = validate_refresh_token_request(data)
        
        # Refresh token
        tokens = auth_service.refresh_access_token(validated_data['refresh_token'])
        
        # Create success response
        response = create_success_response(
            data=tokens,
            message="Access token refreshed successfully"
        )
        
        logger.info("Access token refreshed successfully")
        return jsonify(response), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error during token refresh: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except AuthenticationError as e:
        logger.warning(f"Authentication error during token refresh: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 401
        
    except RiskOptimizerException as e:
        logger.error(f"Error during token refresh: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500


@auth_bp.route('/logout', methods=['POST'])
def logout() -> Response:
    """
    Logout a user by blacklisting their tokens.
    
    Returns:
        Success message
    """
    try:
        logger.info("User logout request received")
        
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationError("Missing or invalid Authorization header")
        
        # Extract access token
        access_token = auth_header.split(' ')[1]
        
        # Get refresh token from request body
        data = request.get_json()
        if not data or 'refresh_token' not in data:
            raise ValidationError("Refresh token is required", "refresh_token")
        
        refresh_token = data['refresh_token']
        
        # Logout user
        auth_service.logout_user(access_token, refresh_token)
        
        # Create success response
        response = create_success_response(
            data={},
            message="User logged out successfully"
        )
        
        logger.info("User logged out successfully")
        return jsonify(response), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error during logout: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except AuthenticationError as e:
        logger.warning(f"Authentication error during logout: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 401
        
    except RiskOptimizerException as e:
        logger.error(f"Error during logout: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error during logout: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500

