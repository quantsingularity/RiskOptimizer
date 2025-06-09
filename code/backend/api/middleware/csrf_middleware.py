"""
CSRF protection middleware for the API.
Implements CSRF protection to prevent cross-site request forgery attacks.
"""

import secrets
from functools import wraps
from typing import Callable, Dict, Any, List, Optional

from flask import request, jsonify, Response, g, current_app

from riskoptimizer.core.exceptions import SecurityError, RiskOptimizerException
from riskoptimizer.core.logging import get_logger
from riskoptimizer.core.config import config

logger = get_logger(__name__)


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


def generate_csrf_token() -> str:
    """
    Generate a CSRF token.
    
    Returns:
        CSRF token
    """
    return secrets.token_hex(32)


def csrf_protect(exempt_methods: List[str] = None) -> Callable:
    """
    Decorator to apply CSRF protection to API endpoints.
    
    Args:
        exempt_methods: List of HTTP methods exempt from CSRF protection (default: GET, HEAD, OPTIONS)
        
    Returns:
        Decorated function
    """
    if exempt_methods is None:
        exempt_methods = ['GET', 'HEAD', 'OPTIONS']
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Skip CSRF check for exempt methods
            if request.method in exempt_methods:
                return func(*args, **kwargs)
            
            # Skip CSRF check in testing mode
            if current_app.testing and config.environment == 'testing':
                return func(*args, **kwargs)
            
            # Get CSRF token from header
            csrf_token = request.headers.get('X-CSRF-Token')
            
            # Get CSRF token from session
            session_token = getattr(g, 'csrf_token', None)
            
            # Check if CSRF token is valid
            if not csrf_token or not session_token or csrf_token != session_token:
                logger.warning(f"CSRF token validation failed for {request.endpoint}")
                
                error = SecurityError("CSRF token validation failed", "CSRF_ERROR")
                response = jsonify(create_error_response(error))
                
                return response, 403
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def apply_csrf_protection(app) -> None:
    """
    Apply CSRF protection to all API endpoints.
    
    Args:
        app: Flask application instance
    """
    # Generate CSRF token for each request
    @app.before_request
    def before_request() -> None:
        """Generate CSRF token for each request."""
        # Skip for non-API endpoints
        if not request.path.startswith('/api'):
            return
        
        # Generate CSRF token if not already set
        if not hasattr(g, 'csrf_token'):
            g.csrf_token = generate_csrf_token()
    
    # Add CSRF token to response headers
    @app.after_request
    def after_request(response: Response) -> Response:
        """Add CSRF token to response headers."""
        # Skip for non-API endpoints
        if not request.path.startswith('/api'):
            return response
        
        # Add CSRF token to response headers
        if hasattr(g, 'csrf_token'):
            response.headers['X-CSRF-Token'] = g.csrf_token
        
        return response
    
    # Apply CSRF protection to all API endpoints
    for rule in app.url_map.iter_rules():
        endpoint = app.view_functions.get(rule.endpoint)
        
        # Skip static files and non-API endpoints
        if rule.rule.startswith('/static') or not rule.rule.startswith('/api'):
            continue
        
        # Apply CSRF protection
        if endpoint:
            app.view_functions[rule.endpoint] = csrf_protect()(endpoint)

