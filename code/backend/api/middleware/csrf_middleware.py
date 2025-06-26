
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
    return secrets.token_urlsafe(32) # Using token_urlsafe for better URL-safe tokens


def csrf_protect(exempt_methods: List[str] = None) -> Callable:
    """
    Decorator to apply CSRF protection to API endpoints.
    
    Args:
        exempt_methods: List of HTTP methods exempt from CSRF protection (default: GET, HEAD, OPTIONS)
        
    Returns:
        Decorated function
    """
    if exempt_methods is None:
        exempt_methods = ["GET", "HEAD", "OPTIONS"]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Skip CSRF check for exempt methods
            if request.method in exempt_methods:
                return func(*args, **kwargs)
            
            # Skip CSRF check in testing mode (only if explicitly enabled for testing)
            if current_app.testing and config.environment == "testing":
                return func(*args, **kwargs)
            
            # Get CSRF token from header
            csrf_token = request.headers.get("X-CSRF-Token")
            
            # Get CSRF token from session (or g object in Flask context)
            session_token = getattr(g, "csrf_token", None)
            
            # Check if CSRF token is valid
            if not csrf_token or not session_token or csrf_token != session_token:
                logger.warning(f"CSRF token validation failed for {request.endpoint}. Provided: {csrf_token}, Expected: {session_token}")
                
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
        """
        Generate CSRF token for each request.
        The token is stored in the `g` object and added to response headers.
        """
        # Only generate for API endpoints that are not GET/HEAD/OPTIONS
        # This ensures that a token is always available for forms/mutating requests
        if request.path.startswith("/api") and request.method not in ["GET", "HEAD", "OPTIONS"]:
            if not hasattr(g, "csrf_token") or g.csrf_token is None:
                g.csrf_token = generate_csrf_token()
            logger.debug(f"Generated CSRF token: {g.csrf_token}")
        
    # Add CSRF token to response headers
    @app.after_request
    def after_request(response: Response) -> Response:
        """
        Add CSRF token to response headers for API endpoints.
        """
        # Only add for API endpoints
        if request.path.startswith("/api"):
            if hasattr(g, "csrf_token") and g.csrf_token is not None:
                response.headers["X-CSRF-Token"] = g.csrf_token
                response.headers["Access-Control-Expose-Headers"] = "X-CSRF-Token" # Expose header for frontend
        
        return response
    
    # Apply CSRF protection to all API endpoints
    # This approach iterates through all rules and applies the decorator.
    # It's important to ensure this is done after all blueprints are registered.
    # A more robust way might be to apply it directly to blueprints or specific routes.
    # For now, we'll keep the existing logic but ensure it's correctly applied.
    for rule in app.url_map.iter_rules():
        # Skip static files and non-API endpoints
        if rule.rule.startswith("/static") or not rule.rule.startswith("/api"):
            continue
        
        # Apply CSRF protection only to methods that are not exempt
        # This requires modifying the endpoint function directly, which can be tricky.
        # A better approach for Flask is to use a decorator on the route functions themselves.
        # However, to maintain the existing structure, we'll modify the view_functions map.
        endpoint = app.view_functions.get(rule.endpoint)
        if endpoint and rule.methods and any(method not in ["GET", "HEAD", "OPTIONS"] for method in rule.methods):
            # Check if the endpoint is already decorated to avoid double-wrapping
            # This is a simple check and might not catch all cases of prior decoration.
            if not hasattr(endpoint, "__wrapped__") or endpoint.__wrapped__ != csrf_protect().__wrapped__:
                app.view_functions[rule.endpoint] = csrf_protect()(endpoint)



