"""
RiskOptimizer Backend Package
"""

__version__ = "2.0.0"
__author__ = "RiskOptimizer Team"
__email__ = "team@riskoptimizer.com"
__description__ = "Advanced Financial Risk Management and Portfolio Optimization System"

# Package metadata
PACKAGE_NAME = "riskoptimizer-backend"
API_VERSION = "v1"
SUPPORTED_PYTHON_VERSIONS = ["3.11", "3.12"]

# Application constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_CACHE_TTL = 3600  # 1 hour

# Risk calculation constants
DEFAULT_CONFIDENCE_LEVELS = [0.95, 0.99]
DEFAULT_MONTE_CARLO_SIMULATIONS = 10000
DEFAULT_TIME_HORIZON = 252  # Trading days in a year
MAX_PORTFOLIO_ASSETS = 100

# Optimization constants
OPTIMIZATION_METHODS = [
    "mean_variance",
    "risk_parity",
    "minimum_variance",
    "maximum_sharpe",
    "black_litterman",
]

# Task queue constants
TASK_QUEUES = {
    "default": "default",
    "risk_calculations": "risk_calculations",
    "portfolio_operations": "portfolio_operations",
    "report_generation": "report_generation",
    "maintenance": "maintenance",
}

# Export main components
from .core.config import get_settings
from .core.exceptions import RiskOptimizerException
from .core.logging import get_logger

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "get_settings",
    "RiskOptimizerException",
    "get_logger",
]
