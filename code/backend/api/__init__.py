"""
API package initialization
"""

from .controllers.auth_controller import router as auth_router
from .controllers.portfolio_controller import router as portfolio_router  
from .controllers.risk_controller import router as risk_router
from .controllers.monitoring_controller import router as monitoring_router
from .controllers.task_controller import router as task_router

# Export all routers
__all__ = [
    "auth_router",
    "portfolio_router", 
    "risk_router",
    "monitoring_router",
    "task_router"
]

