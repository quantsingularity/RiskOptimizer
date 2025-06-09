"""
Logging configuration for the RiskOptimizer application.
Provides structured logging with JSON format and context.
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from riskoptimizer.core.config import config


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if available
        if hasattr(record, "extra") and record.extra:
            log_data.update(record.extra)

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add request_id if available
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)


class ContextAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context to log records."""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process log record by adding context."""
        # Initialize extra dict if not present
        kwargs.setdefault("extra", {})
        
        # Add extra context from adapter
        if self.extra:
            # Create a new dict to avoid modifying the original
            extra = kwargs["extra"].copy()
            extra.update({"extra": self.extra})
            kwargs["extra"] = extra
            
        return msg, kwargs


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> logging.LoggerAdapter:
    """
    Get a logger with the specified name and context.
    
    Args:
        name: Logger name
        context: Optional context dictionary to add to all log records
        
    Returns:
        Logger adapter with context
    """
    logger = logging.getLogger(name)
    
    # Only configure the logger if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Set debug level in development
        if config.environment == "development" and config.api.debug:
            logger.setLevel(logging.DEBUG)
            
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        
    # Return logger with context adapter
    return ContextAdapter(logger, context or {})


def configure_logging() -> None:
    """Configure root logger with JSON formatting."""
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Set log level based on environment
    if config.environment == "development" and config.api.debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
        
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)


class LoggerMixin:
    """Mixin class that adds logging capabilities to a class."""
    
    @property
    def logger(self) -> logging.LoggerAdapter:
        """Get logger for the class."""
        if not hasattr(self, "_logger"):
            context = {"class": self.__class__.__name__}
            self._logger = get_logger(self.__class__.__module__, context)
        return self._logger

