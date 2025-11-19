"""
Performance monitoring utilities for tracking API performance metrics.
Provides utilities for monitoring response times, throughput, and resource usage.
"""

import time
from collections import defaultdict, deque
from functools import wraps
from typing import Any, Callable, Dict, List

import psutil
from flask import g, request
from riskoptimizer.core.logging import get_logger
from riskoptimizer.infrastructure.cache.redis_cache import redis_cache

logger = get_logger(__name__)


class PerformanceMetrics:
    """Collect and store performance metrics."""

    def __init__(self, max_samples: int = 1000):
        """
        Initialize performance metrics collector.

        Args:
            max_samples: Maximum number of samples to keep in memory
        """
        self.max_samples = max_samples
        self.response_times = defaultdict(lambda: deque(maxlen=max_samples))
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.start_time = time.time()

    def record_request(
        self, endpoint: str, method: str, response_time: float, status_code: int
    ) -> None:
        """
        Record a request metric.

        Args:
            endpoint: API endpoint
            method: HTTP method
            response_time: Response time in seconds
            status_code: HTTP status code
        """
        key = f"{method}:{endpoint}"

        # Record response time
        self.response_times[key].append(response_time)

        # Increment request count
        self.request_counts[key] += 1

        # Record errors
        if status_code >= 400:
            self.error_counts[key] += 1

    def get_endpoint_stats(self, endpoint: str, method: str) -> Dict[str, Any]:
        """
        Get statistics for a specific endpoint.

        Args:
            endpoint: API endpoint
            method: HTTP method

        Returns:
            Dictionary with endpoint statistics
        """
        key = f"{method}:{endpoint}"
        response_times = list(self.response_times[key])

        if not response_times:
            return {
                "endpoint": endpoint,
                "method": method,
                "request_count": 0,
                "error_count": 0,
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "error_rate": 0,
            }

        request_count = self.request_counts[key]
        error_count = self.error_counts[key]

        return {
            "endpoint": endpoint,
            "method": method,
            "request_count": request_count,
            "error_count": error_count,
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "error_rate": error_count / request_count if request_count > 0 else 0,
        }

    def get_all_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all endpoints.

        Returns:
            List of endpoint statistics
        """
        stats = []
        all_keys = set(self.response_times.keys()) | set(self.request_counts.keys())

        for key in all_keys:
            method, endpoint = key.split(":", 1)
            stats.append(self.get_endpoint_stats(endpoint, method))

        # Sort by request count descending
        stats.sort(key=lambda x: x["request_count"], reverse=True)
        return stats

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system performance statistics.

        Returns:
            Dictionary with system statistics
        """
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Get memory usage
            memory = psutil.virtual_memory()

            # Get disk usage
            disk = psutil.disk_usage("/")

            # Calculate uptime
            uptime = time.time() - self.start_time

            return {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
                "uptime": uptime,
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}", exc_info=True)
            return {"error": str(e)}


# Global metrics instance
metrics = PerformanceMetrics()


def monitor_performance(func: Callable) -> Callable:
    """
    Decorator to monitor endpoint performance.

    Args:
        func: Function to monitor

    Returns:
        Decorated function
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()

        try:
            # Execute function
            result = func(*args, **kwargs)

            # Calculate response time
            response_time = time.time() - start_time

            # Get status code
            status_code = 200
            if isinstance(result, tuple) and len(result) == 2:
                _, status_code = result

            # Record metrics
            endpoint = request.endpoint or "unknown"
            method = request.method
            metrics.record_request(endpoint, method, response_time, status_code)

            # Store in request context for logging
            g.response_time = response_time

            return result

        except Exception:
            # Calculate response time for errors
            response_time = time.time() - start_time

            # Record error metrics
            endpoint = request.endpoint or "unknown"
            method = request.method
            metrics.record_request(endpoint, method, response_time, 500)

            # Store in request context for logging
            g.response_time = response_time

            raise

    return wrapper


class CachePerformanceMonitor:
    """Monitor cache performance metrics."""

    def __init__(self):
        """
        Initialize cache performance monitor.
        """
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_errors = 0

    def record_hit(self) -> None:
        """
        Record a cache hit.
        """
        self.cache_hits += 1

    def record_miss(self) -> None:
        """
        Record a cache miss.
        """
        self.cache_misses += 1

    def record_error(self) -> None:
        """
        Record a cache error.
        """
        self.cache_errors += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_errors": self.cache_errors,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "miss_rate": 1 - hit_rate,
        }

    def reset_stats(self) -> None:
        """
        Reset cache statistics.
        """
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_errors = 0


# Global cache monitor instance
cache_monitor = CachePerformanceMonitor()


def get_performance_report() -> Dict[str, Any]:
    """
    Generate a comprehensive performance report.

    Returns:
        Dictionary with performance report
    """
    try:
        # Get endpoint statistics
        endpoint_stats = metrics.get_all_stats()

        # Get system statistics
        system_stats = metrics.get_system_stats()

        # Get cache statistics
        cache_stats = cache_monitor.get_stats()

        # Get Redis health
        redis_healthy = redis_cache.health_check()

        return {
            "timestamp": time.time(),
            "endpoints": endpoint_stats,
            "system": system_stats,
            "cache": cache_stats,
            "redis_healthy": redis_healthy,
        }
    except Exception as e:
        logger.error(f"Error generating performance report: {e}", exc_info=True)
        return {"error": str(e)}


def apply_performance_monitoring(app) -> None:
    """
    Apply performance monitoring to all API endpoints.

    Args:
        app: Flask application instance
    """
    # Apply monitoring to all API endpoints
    for rule in app.url_map.iter_rules():
        endpoint = app.view_functions.get(rule.endpoint)

        # Skip static files and non-API endpoints
        if rule.rule.startswith("/static") or not rule.rule.startswith("/api"):
            continue

        # Apply performance monitoring
        if endpoint:
            app.view_functions[rule.endpoint] = monitor_performance(endpoint)

    # Add performance monitoring to request/response cycle
    @app.before_request
    def before_request() -> None:
        """Record request start time."""
        g.request_start_time = time.time()

    @app.after_request
    def after_request(response):
        """
        Log request completion with performance metrics.
        """
        if hasattr(g, "request_start_time"):
            response_time = time.time() - g.request_start_time

            # Add performance headers
            response.headers["X-Response-Time"] = f"{response_time:.3f}s"

            # Log performance
            logger.info(
                f"Request completed: {request.method} {request.path}",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "request_id": getattr(g, "request_id", None),
                },
            )

        return response
