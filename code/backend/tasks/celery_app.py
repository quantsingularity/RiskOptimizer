"""
Celery application configuration for RiskOptimizer.
Handles asynchronous task processing for heavy computations.
"""

from celery import Celery
from celery.schedules import crontab
import os
import redis
from kombu import Queue

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# Create Celery app
celery_app = Celery(
    'riskoptimizer',
    broker=REDIS_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        'tasks.risk_tasks',
        'tasks.portfolio_tasks',
        'tasks.report_tasks',
        'tasks.maintenance_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        'tasks.risk_tasks.*': {'queue': 'risk_calculations'},
        'tasks.portfolio_tasks.*': {'queue': 'portfolio_operations'},
        'tasks.report_tasks.*': {'queue': 'report_generation'},
        'tasks.maintenance_tasks.*': {'queue': 'maintenance'},
    },
    
    # Queue configuration
    task_default_queue='default',
    task_queues=(
        Queue('default', routing_key='default'),
        Queue('risk_calculations', routing_key='risk'),
        Queue('portfolio_operations', routing_key='portfolio'),
        Queue('report_generation', routing_key='reports'),
        Queue('maintenance', routing_key='maintenance'),
    ),
    
    # Task execution settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task result settings
    result_expires=3600,  # 1 hour
    task_track_started=True,
    task_send_sent_event=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-expired-tasks': {
            'task': 'tasks.maintenance_tasks.cleanup_expired_tasks',
            'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
        },
        'update-market-data': {
            'task': 'tasks.maintenance_tasks.update_market_data',
            'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        },
        'generate-daily-reports': {
            'task': 'tasks.report_tasks.generate_daily_reports',
            'schedule': crontab(minute=0, hour=8),  # Daily at 8 AM
        },
        'cache-warmup': {
            'task': 'tasks.maintenance_tasks.cache_warmup',
            'schedule': crontab(minute=0, hour=6),  # Daily at 6 AM
        },
    },
)

# Task monitoring configuration
celery_app.conf.update(
    worker_send_task_events=True,
    task_send_sent_event=True,
    worker_hijack_root_logger=False,
    worker_log_color=False,
)

# Redis connection for task monitoring
redis_client = redis.Redis.from_url(REDIS_URL)

def get_task_status(task_id):
    """Get the status of a task by ID."""
    return celery_app.AsyncResult(task_id)

def cancel_task(task_id):
    """Cancel a task by ID."""
    celery_app.control.revoke(task_id, terminate=True)

def get_active_tasks():
    """Get list of active tasks."""
    inspect = celery_app.control.inspect()
    return inspect.active()

def get_scheduled_tasks():
    """Get list of scheduled tasks."""
    inspect = celery_app.control.inspect()
    return inspect.scheduled()

def get_worker_stats():
    """Get worker statistics."""
    inspect = celery_app.control.inspect()
    return inspect.stats()

# Task result storage utilities
class TaskResultManager:
    """Manages task results and provides utilities for task monitoring."""
    
    def __init__(self):
        self.redis_client = redis_client
    
    def store_task_progress(self, task_id, progress_data):
        """Store task progress information."""
        key = f"task_progress:{task_id}"
        self.redis_client.hset(key, mapping=progress_data)
        self.redis_client.expire(key, 3600)  # Expire after 1 hour
    
    def get_task_progress(self, task_id):
        """Get task progress information."""
        key = f"task_progress:{task_id}"
        return self.redis_client.hgetall(key)
    
    def store_task_metadata(self, task_id, metadata):
        """Store task metadata."""
        key = f"task_metadata:{task_id}"
        self.redis_client.hset(key, mapping=metadata)
        self.redis_client.expire(key, 86400)  # Expire after 24 hours
    
    def get_task_metadata(self, task_id):
        """Get task metadata."""
        key = f"task_metadata:{task_id}"
        return self.redis_client.hgetall(key)
    
    def cleanup_expired_task_data(self):
        """Clean up expired task data."""
        # This is handled by Redis TTL, but can be extended for custom cleanup
        pass

# Global task result manager instance
task_result_manager = TaskResultManager()

# Error handling for tasks
class TaskError(Exception):
    """Base exception for task errors."""
    pass

class TaskTimeoutError(TaskError):
    """Exception raised when a task times out."""
    pass

class TaskValidationError(TaskError):
    """Exception raised when task input validation fails."""
    pass

# Task decorators
def task_with_progress(bind=True, **kwargs):
    """Decorator for tasks that report progress."""
    def decorator(func):
        @celery_app.task(bind=bind, **kwargs)
        def wrapper(self, *args, **kwargs):
            try:
                # Store initial task metadata
                task_result_manager.store_task_metadata(
                    self.request.id,
                    {
                        'task_name': func.__name__,
                        'started_at': str(datetime.utcnow()),
                        'status': 'STARTED'
                    }
                )
                
                # Execute the task
                result = func(self, *args, **kwargs)
                
                # Update completion metadata
                task_result_manager.store_task_metadata(
                    self.request.id,
                    {
                        'completed_at': str(datetime.utcnow()),
                        'status': 'SUCCESS'
                    }
                )
                
                return result
                
            except Exception as exc:
                # Update error metadata
                task_result_manager.store_task_metadata(
                    self.request.id,
                    {
                        'failed_at': str(datetime.utcnow()),
                        'status': 'FAILURE',
                        'error': str(exc)
                    }
                )
                raise
        
        return wrapper
    return decorator

# Import datetime for metadata timestamps
from datetime import datetime

if __name__ == '__main__':
    celery_app.start()

