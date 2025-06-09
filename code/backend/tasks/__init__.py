"""
Tasks package initialization
"""

from .celery_app import celery_app
from .risk_tasks import (
    monte_carlo_simulation,
    calculate_var_cvar,
    efficient_frontier_calculation,
    stress_test_portfolio,
    calculate_portfolio_metrics
)
from .portfolio_tasks import (
    optimize_portfolio,
    rebalance_portfolio,
    analyze_portfolio_performance,
    update_portfolio_data
)
from .report_tasks import (
    generate_portfolio_report,
    generate_risk_report,
    export_portfolio_data
)
from .maintenance_tasks import (
    cleanup_expired_tasks,
    update_market_data,
    cache_warmup,
    system_health_check
)

__all__ = [
    "celery_app",
    "monte_carlo_simulation",
    "calculate_var_cvar", 
    "efficient_frontier_calculation",
    "stress_test_portfolio",
    "calculate_portfolio_metrics",
    "optimize_portfolio",
    "rebalance_portfolio",
    "analyze_portfolio_performance",
    "update_portfolio_data",
    "generate_portfolio_report",
    "generate_risk_report", 
    "export_portfolio_data",
    "cleanup_expired_tasks",
    "update_market_data",
    "cache_warmup",
    "system_health_check"
]

