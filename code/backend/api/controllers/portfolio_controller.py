"""
Portfolio controller for handling portfolio-related API endpoints.
Implements RESTful API design with proper error handling.
"""

from typing import Dict, Any, List
from flask import Blueprint, request, jsonify, Response

from riskoptimizer.core.exceptions import ValidationError, NotFoundError, RiskOptimizerException
from riskoptimizer.core.logging import get_logger
from riskoptimizer.domain.services.portfolio_service import portfolio_service
from riskoptimizer.api.schemas.portfolio_schema import (
    validate_portfolio_request, validate_portfolio_update_request
)
from riskoptimizer.api.middleware.auth_middleware import jwt_required, optional_jwt
from riskoptimizer.utils.pagination import create_paginated_response

logger = get_logger(__name__)

# Create blueprint
portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/v1/portfolios')


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


@portfolio_bp.route('/<user_address>', methods=['GET'])
@optional_jwt
def get_portfolio(user_address: str) -> Response:
    """
    Get portfolio by user address.
    
    Args:
        user_address: User wallet address
        
    Returns:
        Portfolio data with allocations
    """
    try:
        logger.info(f"Get portfolio request for address: {user_address}")
        
        # Get portfolio from service
        portfolio_data = portfolio_service.get_portfolio_by_address(user_address)
        
        # Create success response
        response = create_success_response(
            data=portfolio_data,
            message="Portfolio retrieved successfully"
        )
        
        logger.info(f"Portfolio retrieved successfully for address: {user_address}")
        return jsonify(response), 200
        
    except NotFoundError as e:
        logger.warning(f"Portfolio not found for address {user_address}: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 404
        
    except ValidationError as e:
        logger.warning(f"Validation error for address {user_address}: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except RiskOptimizerException as e:
        logger.error(f"Error getting portfolio for address {user_address}: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error getting portfolio for address {user_address}: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500


@portfolio_bp.route('', methods=['POST'])
@jwt_required()
def save_portfolio() -> Response:
    """
    Save portfolio for a user.
    
    Returns:
        Saved portfolio data
    """
    try:
        logger.info("Save portfolio request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Validate request data
        validated_data = validate_portfolio_request(data)
        
        # Save portfolio
        portfolio_data = portfolio_service.save_portfolio(
            user_address=validated_data['user_address'],
            allocations=validated_data['allocations'],
            name=validated_data.get('name', 'Default Portfolio')
        )
        
        # Create success response
        response = create_success_response(
            data=portfolio_data,
            message="Portfolio saved successfully"
        )
        
        logger.info(f"Portfolio saved successfully for address: {validated_data['user_address']}")
        return jsonify(response), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error saving portfolio: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except RiskOptimizerException as e:
        logger.error(f"Error saving portfolio: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error saving portfolio: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500


@portfolio_bp.route('/<int:portfolio_id>', methods=['PUT'])
@jwt_required()
def update_portfolio(portfolio_id: int) -> Response:
    """
    Update portfolio.
    
    Args:
        portfolio_id: Portfolio ID
        
    Returns:
        Updated portfolio data
    """
    try:
        logger.info(f"Update portfolio request for ID: {portfolio_id}")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Validate request data
        validated_data = validate_portfolio_update_request(data)
        
        # Update portfolio
        portfolio_data = portfolio_service.update_portfolio(portfolio_id, validated_data)
        
        # Create success response
        response = create_success_response(
            data=portfolio_data,
            message="Portfolio updated successfully"
        )
        
        logger.info(f"Portfolio updated successfully for ID: {portfolio_id}")
        return jsonify(response), 200
        
    except NotFoundError as e:
        logger.warning(f"Portfolio not found for ID {portfolio_id}: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 404
        
    except ValidationError as e:
        logger.warning(f"Validation error updating portfolio {portfolio_id}: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except RiskOptimizerException as e:
        logger.error(f"Error updating portfolio {portfolio_id}: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error updating portfolio {portfolio_id}: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500


@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio(portfolio_id: int) -> Response:
    """
    Delete portfolio.
    
    Args:
        portfolio_id: Portfolio ID
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Delete portfolio request for ID: {portfolio_id}")
        
        # Delete portfolio
        deleted = portfolio_service.delete_portfolio(portfolio_id)
        
        if not deleted:
            raise NotFoundError(f"Portfolio {portfolio_id} not found", "portfolio", str(portfolio_id))
        
        # Create success response
        response = create_success_response(
            data={"portfolio_id": portfolio_id},
            message="Portfolio deleted successfully"
        )
        
        logger.info(f"Portfolio deleted successfully for ID: {portfolio_id}")
        return jsonify(response), 200
        
    except NotFoundError as e:
        logger.warning(f"Portfolio not found for ID {portfolio_id}: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 404
        
    except ValidationError as e:
        logger.warning(f"Validation error deleting portfolio {portfolio_id}: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except RiskOptimizerException as e:
        logger.error(f"Error deleting portfolio {portfolio_id}: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error deleting portfolio {portfolio_id}: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500


@portfolio_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_portfolios(user_id: int) -> Response:
    """
    Get all portfolios for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List of user portfolios
    """
    try:
        logger.info(f"Get user portfolios request for user ID: {user_id}")
        
        # Get user portfolios with pagination
        portfolios = portfolio_service.get_user_portfolios(user_id)
        
        # Create paginated response
        response = create_paginated_response(
            portfolios,
            transform_func=lambda p: p  # No transformation needed
        )
        
        logger.info(f"Retrieved portfolios for user ID: {user_id}")
        return jsonify(response), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error getting portfolios for user {user_id}: {str(e)}")
        response = create_error_response(e)
        return jsonify(response), 400
        
    except RiskOptimizerException as e:
        logger.error(f"Error getting portfolios for user {user_id}: {str(e)}", exc_info=True)
        response = create_error_response(e)
        return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Unexpected error getting portfolios for user {user_id}: {str(e)}", exc_info=True)
        error = RiskOptimizerException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
        response = create_error_response(error)
        return jsonify(response), 500

