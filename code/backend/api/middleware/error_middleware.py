"""
Error handling middleware for the API.
Provides centralized error handling for all API endpoints.
"""

import traceback
from typing import Dict, Any, Callable, Tuple

from flask import Flask, Blueprint, request, jsonify, Response, current_app, g
import werkzeug.exceptions as werkzeug_exceptions

from riskoptimizer.core.exceptions import RiskOptimizerException
from riskoptimizer.core.logging import get_logger

logger = get_logger(__name__)


def create_error_response(error: Exception) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error: Exception instance
        
    Returns:
        Standardized error response dictionary
    """
    if isinstance(error, RiskOptimizerException):
        # Use custom exception's to_dict method
        error_data = error.to_dict()
    elif isinstance(error, werkzeug_exceptions.HTTPException):
        # Handle Werkzeug HTTP exceptions
        error_data = {
            "code": f"HTTP_{error.code}",
            "message": error.description,
            "details": {}
        }
    else:
        # Handle generic exceptions
        error_data = {
            "code": "INTERNAL_ERROR",
            "message": str(error) or "An unexpected error occurred",
            "details": {}
        }
        
        # Add traceback in development mode
        if current_app.debug:
            error_data["details"]["traceback"] = traceback.format_exc()
    
    return {
        "status": "error",
        "error": error_data
    }


def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(RiskOptimizerException)
    def handle_risk_optimizer_exception(error: RiskOptimizerException) -> Response:
        """Handle custom RiskOptimizer exceptions."""
        status_code = 500
        
        # Map exception types to status codes
        if error.__class__.__name__ == "ValidationError":
            status_code = 400
        elif error.__class__.__name__ == "AuthenticationError":
            status_code = 401
        elif error.__class__.__name__ == "AuthorizationError":
            status_code = 403
        elif error.__class__.__name__ == "NotFoundError":
            status_code = 404
        elif error.__class__.__name__ == "ConflictError":
            status_code = 409
        elif error.__class__.__name__ == "RateLimitError":
            status_code = 429
        elif error.__class__.__name__ == "CalculationError":
            status_code = 422
        
        logger.error(f"{error.__class__.__name__}: {str(error)}", exc_info=True)
        response = create_error_response(error)
        return jsonify(response), status_code
    
    @app.errorhandler(werkzeug_exceptions.HTTPException)
    def handle_http_exception(error: werkzeug_exceptions.HTTPException) -> Response:
        """Handle Werkzeug HTTP exceptions."""
        logger.error(f"HTTP Exception {error.code}: {error.description}", exc_info=True)
        response = create_error_response(error)
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception) -> Response:
        """Handle generic exceptions."""
        logger.critical(f"Unhandled exception: {str(error)}", exc_info=True)
        response = create_error_response(error)
        return jsonify(response), 500
    
    @app.errorhandler(404)
    def handle_not_found(error: werkzeug_exceptions.NotFound) -> Response:
        """Handle 404 Not Found errors."""
        logger.warning(f"Not Found: {request.path}")
        response = create_error_response(error)
        return jsonify(response), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error: werkzeug_exceptions.MethodNotAllowed) -> Response:
        """Handle 405 Method Not Allowed errors."""
        logger.warning(f"Method Not Allowed: {request.method} {request.path}")
        response = create_error_response(error)
        return jsonify(response), 405
    
    @app.errorhandler(500)
    def handle_server_error(error: werkzeug_exceptions.InternalServerError) -> Response:
        """Handle 500 Internal Server Error."""
        logger.critical(f"Internal Server Error: {str(error)}", exc_info=True)
        response = create_error_response(error)
        return jsonify(response), 500


def error_handling_middleware(app: Flask) -> None:
    """
    Register error handling middleware for the Flask application.
    
    Args:
        app: Flask application instance
    """
    register_error_handlers(app)
    
    @app.before_request
    def before_request() -> None:
        """Set up request context."""
        # Generate request ID if not already set
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            import uuid
            request_id = str(uuid.uuid4())
        
        # Store request ID in g for access in other parts of the application
        g.request_id = request_id
        
        # Add request ID to logger context
        logger.info(f"Request started: {request.method} {request.path}",
                   extra={"request_id": request_id, "method": request.method, "path": request.path})
    
    @app.after_request
    def after_request(response: Response) -> Response:
        """Log after request and add headers."""
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Log response
        logger.info(f"Request completed: {request.method} {request.path} {response.status_code}",
                   extra={"request_id": getattr(g, 'request_id', None),
                          "method": request.method,
                          "path": request.path,
                          "status_code": response.status_code})
        
        return response

