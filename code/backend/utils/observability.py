import json
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

from flask import g, has_request_context, request
from riskoptimizer.core.logging import get_logger

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)

logger = get_logger(__name__)


class CorrelationIdFilter:
    """Filter to add correlation ID to log records."""

    def filter(self, record):
        """Add correlation ID to log record."""
        # Get correlation ID from context
        corr_id = correlation_id.get()

        # If no correlation ID in context, try to get from Flask g
        if not corr_id and has_request_context():
            corr_id = getattr(g, "correlation_id", None)

        # Add correlation ID to record
        record.correlation_id = corr_id or "unknown"

        return True


class StructuredLogger:
    """Structured logger with correlation ID support."""

    def __init__(self, name: str):
        """
        Initialize structured logger.

        Args:
            name: Logger name
        """
        self.logger = get_logger(name)

        # Add correlation ID filter
        correlation_filter = CorrelationIdFilter()
        self.logger.addFilter(correlation_filter)

    def _create_log_entry(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Create structured log entry.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional log data

        Returns:
            Structured log entry
        """
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "correlation_id": correlation_id.get()
            or getattr(g, "correlation_id", None),
            "service": "riskoptimizer",
        }

        # Add request context if available
        if has_request_context():
            entry.update(
                {
                    "request": {
                        "method": request.method,
                        "path": request.path,
                        "remote_addr": request.remote_addr,
                        "user_agent": request.headers.get("User-Agent"),
                        "request_id": getattr(g, "request_id", None),
                    }
                }
            )

            # Add user context if available
            if hasattr(g, "user") and g.user:
                entry["user"] = {
                    "id": g.user.get("id"),
                    "email": g.user.get("email"),
                    "role": g.user.get("role"),
                }

        # Add additional data
        if kwargs:
            entry["data"] = kwargs

        return entry

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        entry = self._create_log_entry("DEBUG", message, **kwargs)
        self.logger.debug(json.dumps(entry))

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        entry = self._create_log_entry("INFO", message, **kwargs)
        self.logger.info(json.dumps(entry))

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        entry = self._create_log_entry("WARNING", message, **kwargs)
        self.logger.warning(json.dumps(entry))

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        entry = self._create_log_entry("ERROR", message, **kwargs)
        self.logger.error(json.dumps(entry))

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        entry = self._create_log_entry("CRITICAL", message, **kwargs)
        self.logger.critical(json.dumps(entry))


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.

    Returns:
        Correlation ID
    """
    return str(uuid.uuid4())


def set_correlation_id(corr_id: str) -> None:
    """
    Set correlation ID in context.

    Args:
        corr_id: Correlation ID
    """
    correlation_id.set(corr_id)

    # Also set in Flask g for backward compatibility
    if has_request_context():
        g.correlation_id = corr_id


def get_correlation_id() -> Optional[str]:
    """
    Get current correlation ID.

    Returns:
        Current correlation ID or None
    """
    corr_id = correlation_id.get()

    # Fallback to Flask g
    if not corr_id and has_request_context():
        corr_id = getattr(g, "correlation_id", None)

    return corr_id


def log_request_start(method: str, path: str, **kwargs) -> None:
    """
    Log request start.

    Args:
        method: HTTP method
        path: Request path
        **kwargs: Additional log data
    """
    structured_logger = StructuredLogger(__name__)
    structured_logger.info(
        f"Request started: {method} {path}",
        request_method=method,
        request_path=path,
        **kwargs,
    )


def log_request_end(
    method: str, path: str, status_code: int, response_time: float, **kwargs
) -> None:
    """
    Log request end.

    Args:
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        response_time: Response time in seconds
        **kwargs: Additional log data
    """
    structured_logger = StructuredLogger(__name__)
    structured_logger.info(
        f"Request completed: {method} {path} - {status_code}",
        request_method=method,
        request_path=path,
        status_code=status_code,
        response_time=response_time,
        **kwargs,
    )


def log_error(error: Exception, context: str = None, **kwargs) -> None:
    """
    Log error with context.

    Args:
        error: Exception instance
        context: Error context
        **kwargs: Additional log data
    """
    structured_logger = StructuredLogger(__name__)
    structured_logger.error(
        f"Error occurred: {str(error)}",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context,
        **kwargs,
    )


def log_business_event(event_type: str, event_data: Dict[str, Any], **kwargs) -> None:
    """
    Log business event.

    Args:
        event_type: Type of business event
        event_data: Event data
        **kwargs: Additional log data
    """
    structured_logger = StructuredLogger(__name__)
    structured_logger.info(
        f"Business event: {event_type}",
        event_type=event_type,
        event_data=event_data,
        **kwargs,
    )


def log_security_event(
    event_type: str, severity: str, details: Dict[str, Any], **kwargs
) -> None:
    """
    Log security event.

    Args:
        event_type: Type of security event
        severity: Event severity (low, medium, high, critical)
        details: Event details
        **kwargs: Additional log data
    """
    structured_logger = StructuredLogger(__name__)

    # Use appropriate log level based on severity
    if severity in ["critical", "high"]:
        log_func = structured_logger.critical
    elif severity == "medium":
        log_func = structured_logger.warning
    else:
        log_func = structured_logger.info

    log_func(
        f"Security event: {event_type}",
        event_type=event_type,
        severity=severity,
        security_event=True,
        details=details,
        **kwargs,
    )


def apply_correlation_middleware(app) -> None:
    """
    Apply correlation ID middleware to Flask app.

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request() -> None:
        """Generate correlation ID for each request."""
        # Check if correlation ID is provided in headers
        corr_id = request.headers.get("X-Correlation-ID")

        # Generate new correlation ID if not provided
        if not corr_id:
            corr_id = generate_correlation_id()

        # Set correlation ID in context and Flask g
        set_correlation_id(corr_id)

        # Generate request ID
        g.request_id = str(uuid.uuid4())

        # Log request start
        log_request_start(
            request.method,
            request.path,
            request_id=g.request_id,
            correlation_id=corr_id,
        )

    @app.after_request
    def after_request(response):
        """Add correlation ID to response headers and log request completion."""
        # Add correlation ID to response headers
        corr_id = get_correlation_id()
        if corr_id:
            response.headers["X-Correlation-ID"] = corr_id

        # Add request ID to response headers
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id

        # Log request completion
        response_time = getattr(g, "response_time", 0)
        log_request_end(
            request.method,
            request.path,
            response.status_code,
            response_time,
            request_id=getattr(g, "request_id", None),
            correlation_id=corr_id,
        )

        return response
