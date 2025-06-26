
import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from riskoptimizer.core.config import config


class SensitiveDataFilter(logging.Filter):
    """
    A logging filter to redact sensitive information from log records.
    """
    SENSITIVE_KEYS = ["password", "secret_key", "jwt_secret_key", "refresh_token", "access_token", "wallet_address"]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Redact sensitive information from the log record message and extra attributes.
        """
        # Redact from message if it contains sensitive data
        for key in self.SENSITIVE_KEYS:
            if key in record.msg.lower():
                record.msg = "[REDACTED]"
                break
        
        # Redact from extra attributes
        if hasattr(record, "extra") and record.extra:
            for key in self.SENSITIVE_KEYS:
                if key in record.extra:
                    record.extra[key] = "[REDACTED]"
        
        return True


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.
        Adds common context fields like `request_id` and `user_id`.
        """
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
            "environment": config.environment,
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

        # Add request_id and user_id if available (from g or context adapter)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address

        return json.dumps(log_data)


class ContextAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds context to log records.
    This ensures that context (like request_id, user_id) is always available.
    """
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log record by adding context.
        """
        # Ensure extra dict exists
        if "extra" not in kwargs or not isinstance(kwargs["extra"], dict):
            kwargs["extra"] = {}
        
        # Add context from adapter to extra
        if self.extra:
            kwargs["extra"].update(self.extra)
            
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
        
        # Add sensitive data filter to prevent logging of sensitive info
        logger.addFilter(SensitiveDataFilter())
        
    # Return logger with context adapter
    return ContextAdapter(logger, context or {})


def configure_logging() -> None:
    """
    Configure root logger with JSON formatting and sensitive data filtering.
    """
    root_logger = logging.getLogger()
    
    # Remove existing handlers to prevent duplicate logs
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
    
    # Add sensitive data filter
    root_logger.addFilter(SensitiveDataFilter())


class LoggerMixin:
    """
    Mixin class that adds logging capabilities to a class.
    Automatically includes class name in log context.
    """
    @property
    def logger(self) -> logging.LoggerAdapter:
        """
        Get logger for the class.
        """
        if not hasattr(self, "_logger"):
            context = {"class": self.__class__.__name__}
            self._logger = get_logger(self.__class__.__module__, context)
        return self._logger


