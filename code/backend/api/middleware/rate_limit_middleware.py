"""
Rate limiting middleware for the API.
Implements rate limiting to prevent abuse of the API.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

from flask import Response, g, jsonify, request
from riskoptimizer.core.config import config
from riskoptimizer.core.exceptions import RateLimitError, RiskOptimizerException
from riskoptimizer.core.logging import get_logger
from riskoptimizer.infrastructure.cache.redis_cache import redis_cache

logger = get_logger(__name__)


def create_error_response(error: RiskOptimizerException) -> Dict[str, Any]:
    """
    Create standardized error response.

    Args:
        error: Exception instance

    Returns:
        Standardized error response dictionary
    """
    return {"status": "error", "error": error.to_dict()}


def get_rate_limit_key(endpoint: str) -> str:
    """
    Get rate limit cache key for the current request.

    Args:
        endpoint: API endpoint name

    Returns:
        Cache key for rate limiting
    """
    # Get client IP
    client_ip = request.remote_addr

    # Get user ID if authenticated
    user_id = getattr(g, "user", {}).get("id", "anonymous")

    # Create cache key
    return f"rate_limit:{endpoint}:{user_id}:{client_ip}"


def rate_limit(requests_per_minute: int = None, burst: int = None) -> Callable:
    """
    Decorator to apply rate limiting to API endpoints.

    Args:
        requests_per_minute: Maximum number of requests per minute (default: from config)
        burst: Maximum burst size (default: from config)

    Returns:
        Decorated function
    """
    # Use config values if not specified
    if requests_per_minute is None:
        requests_per_minute = config.security.rate_limit_requests_per_minute

    if burst is None:
        burst = config.security.rate_limit_burst

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Get endpoint name
                endpoint = request.endpoint or "unknown"

                # Get rate limit key
                key = get_rate_limit_key(endpoint)

                # Get current timestamp
                now = int(time.time())

                # Get current window start time (1 minute window)
                window_start = now - 60

                # Get request count in current window
                count = redis_cache.get(key) or []

                # Filter out old requests
                count = [ts for ts in count if ts > window_start]

                # Check if rate limit exceeded
                if len(count) >= requests_per_minute:
                    # Check if burst limit exceeded
                    if len(count) >= burst:
                        logger.warning(
                            f"Rate limit exceeded for {endpoint}: {len(count)} requests in last minute"
                        )

                        # Calculate reset time
                        reset_time = count[0] + 60 - now

                        # Create rate limit error
                        error = RateLimitError(
                            f"Rate limit exceeded. Maximum {requests_per_minute} requests per minute allowed.",
                            reset_time=reset_time,
                            limit=requests_per_minute,
                        )

                        # Add rate limit headers
                        response = jsonify(create_error_response(error))
                        response.headers["X-RateLimit-Limit"] = str(requests_per_minute)
                        response.headers["X-RateLimit-Remaining"] = "0"
                        response.headers["X-RateLimit-Reset"] = str(reset_time)
                        response.headers["Retry-After"] = str(reset_time)

                        return response, 429

                # Add current request timestamp
                count.append(now)

                # Update cache with TTL of 1 minute
                redis_cache.set(key, count, ttl=60)

                # Add rate limit headers to response
                response = func(*args, **kwargs)

                # If response is a tuple (response, status_code)
                if isinstance(response, tuple) and len(response) == 2:
                    response_obj, status_code = response

                    # If response is a Response object
                    if isinstance(response_obj, Response):
                        response_obj.headers["X-RateLimit-Limit"] = str(
                            requests_per_minute
                        )
                        response_obj.headers["X-RateLimit-Remaining"] = str(
                            max(0, requests_per_minute - len(count))
                        )

                        return response_obj, status_code

                return response

            except Exception as e:
                logger.error(f"Error in rate limit middleware: {str(e)}", exc_info=True)
                return func(*args, **kwargs)

        return wrapper

    return decorator


def apply_rate_limiting(app) -> None:
    """
    Apply rate limiting to all API endpoints.

    Args:
        app: Flask application instance
    """
    # Get all API endpoints
    for rule in app.url_map.iter_rules():
        endpoint = app.view_functions.get(rule.endpoint)

        # Skip static files and non-API endpoints
        if rule.rule.startswith("/static") or not rule.rule.startswith("/api"):
            continue

        # Apply rate limiting
        if endpoint:
            app.view_functions[rule.endpoint] = rate_limit()(endpoint)
