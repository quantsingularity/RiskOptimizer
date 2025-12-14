"""
API package initialization
"""

from .controllers.auth_controller import auth_bp
from .controllers.monitoring_controller import monitoring_bp
from .controllers.portfolio_controller import portfolio_bp
from .controllers.risk_controller import risk_bp

# Export all blueprints
__all__ = [
    "auth_bp",
    "portfolio_bp",
    "risk_bp",
    "monitoring_bp",
]
