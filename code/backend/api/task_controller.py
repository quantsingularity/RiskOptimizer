"""
Task management API endpoints for monitoring and controlling asynchronous tasks.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from tasks.celery_app import (
    celery_app, get_task_status, cancel_task, get_active_tasks, 
    get_scheduled_tasks, get_worker_stats, task_result_manager
)
from tasks import risk_tasks, portfolio_tasks, report_tasks, maintenance_tasks

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.post("/risk/monte-carlo")
async def start_monte_carlo_simulation(
    portfolio_data: Dict,
    num_simulations: int = 10000,
    time_horizon: int = 252
):
    """Start Monte Carlo simulation task."""
    try:
        task = risk_tasks.monte_carlo_simulation.delay(
            portfolio_data, num_simulations, time_horizon
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "monte_carlo_simulation",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/var-cvar")
async def start_var_cvar_calculation(
    portfolio_data: Dict,
    confidence_levels: List[float] = [0.95, 0.99]
):
    """Start VaR/CVaR calculation task."""
    try:
        task = risk_tasks.calculate_var_cvar.delay(
            portfolio_data, confidence_levels
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "var_cvar_calculation",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/efficient-frontier")
async def start_efficient_frontier_calculation(
    assets_data: Dict,
    num_portfolios: int = 10000
):
    """Start efficient frontier calculation task."""
    try:
        task = risk_tasks.efficient_frontier_calculation.delay(
            assets_data, num_portfolios
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "efficient_frontier_calculation",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/stress-test")
async def start_stress_test(
    portfolio_data: Dict,
    stress_scenarios: List[Dict]
):
    """Start portfolio stress test task."""
    try:
        task = risk_tasks.stress_test_portfolio.delay(
            portfolio_data, stress_scenarios
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "stress_test",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio/optimize")
async def start_portfolio_optimization(
    assets_data: Dict,
    optimization_params: Dict
):
    """Start portfolio optimization task."""
    try:
        task = portfolio_tasks.optimize_portfolio.delay(
            assets_data, optimization_params
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "portfolio_optimization",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio/rebalance")
async def start_portfolio_rebalancing(
    current_portfolio: Dict,
    target_weights: Dict,
    rebalancing_params: Dict
):
    """Start portfolio rebalancing analysis task."""
    try:
        task = portfolio_tasks.rebalance_portfolio.delay(
            current_portfolio, target_weights, rebalancing_params
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "portfolio_rebalancing",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio/performance-analysis")
async def start_performance_analysis(
    portfolio_data: Dict,
    benchmark_data: Dict,
    analysis_period: Dict
):
    """Start portfolio performance analysis task."""
    try:
        task = portfolio_tasks.analyze_portfolio_performance.delay(
            portfolio_data, benchmark_data, analysis_period
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "performance_analysis",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports/portfolio")
async def start_portfolio_report_generation(
    portfolio_data: Dict,
    report_config: Dict
):
    """Start portfolio report generation task."""
    try:
        task = report_tasks.generate_portfolio_report.delay(
            portfolio_data, report_config
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "portfolio_report",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports/risk")
async def start_risk_report_generation(
    risk_analysis_data: Dict,
    report_config: Dict
):
    """Start risk report generation task."""
    try:
        task = report_tasks.generate_risk_report.delay(
            risk_analysis_data, report_config
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "risk_report",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/portfolio")
async def start_portfolio_data_export(
    portfolio_data: Dict,
    export_config: Dict
):
    """Start portfolio data export task."""
    try:
        task = report_tasks.export_portfolio_data.delay(
            portfolio_data, export_config
        )
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "portfolio_export",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/status")
async def get_task_status_endpoint(task_id: str):
    """Get the status of a specific task."""
    try:
        task_result = get_task_status(task_id)
        
        # Get additional progress information
        progress_data = task_result_manager.get_task_progress(task_id)
        metadata = task_result_manager.get_task_metadata(task_id)
        
        response_data = {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None,
            "progress": progress_data,
            "metadata": metadata
        }
        
        if task_result.failed():
            response_data["error"] = str(task_result.info)
        
        return {
            "status": "success",
            "data": response_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/result")
async def get_task_result(task_id: str):
    """Get the result of a completed task."""
    try:
        task_result = get_task_status(task_id)
        
        if not task_result.ready():
            raise HTTPException(status_code=202, detail="Task not yet completed")
        
        if task_result.failed():
            raise HTTPException(status_code=500, detail=f"Task failed: {task_result.info}")
        
        return {
            "status": "success",
            "data": {
                "task_id": task_id,
                "result": task_result.result,
                "completed_at": task_result.date_done
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def cancel_task_endpoint(task_id: str):
    """Cancel a running task."""
    try:
        cancel_task(task_id)
        
        return {
            "status": "success",
            "data": {
                "task_id": task_id,
                "message": "Task cancellation requested",
                "cancelled_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active")
async def get_active_tasks_endpoint():
    """Get list of currently active tasks."""
    try:
        active_tasks = get_active_tasks()
        
        return {
            "status": "success",
            "data": {
                "active_tasks": active_tasks,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scheduled")
async def get_scheduled_tasks_endpoint():
    """Get list of scheduled tasks."""
    try:
        scheduled_tasks = get_scheduled_tasks()
        
        return {
            "status": "success",
            "data": {
                "scheduled_tasks": scheduled_tasks,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workers/stats")
async def get_worker_stats_endpoint():
    """Get Celery worker statistics."""
    try:
        worker_stats = get_worker_stats()
        
        return {
            "status": "success",
            "data": {
                "worker_stats": worker_stats,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance/cleanup")
async def start_cleanup_task():
    """Start maintenance cleanup task."""
    try:
        task = maintenance_tasks.cleanup_expired_tasks.delay()
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "cleanup_expired_tasks",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance/health-check")
async def start_health_check_task():
    """Start system health check task."""
    try:
        task = maintenance_tasks.system_health_check.delay()
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "system_health_check",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance/cache-warmup")
async def start_cache_warmup_task():
    """Start cache warmup task."""
    try:
        task = maintenance_tasks.cache_warmup.delay()
        
        return {
            "status": "success",
            "data": {
                "task_id": task.id,
                "task_type": "cache_warmup",
                "status": "PENDING",
                "submitted_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/stats")
async def get_queue_stats():
    """Get queue statistics and health information."""
    try:
        # Get queue lengths and worker information
        inspect = celery_app.control.inspect()
        
        # Get reserved tasks (queued tasks)
        reserved = inspect.reserved()
        
        # Get active tasks
        active = inspect.active()
        
        # Calculate queue statistics
        queue_stats = {}
        total_queued = 0
        total_active = 0
        
        if reserved:
            for worker, tasks in reserved.items():
                total_queued += len(tasks)
        
        if active:
            for worker, tasks in active.items():
                total_active += len(tasks)
        
        queue_stats = {
            "total_queued_tasks": total_queued,
            "total_active_tasks": total_active,
            "reserved_tasks_by_worker": reserved,
            "active_tasks_by_worker": active,
            "queue_health": "healthy" if total_queued < 1000 else "degraded"
        }
        
        return {
            "status": "success",
            "data": {
                "queue_stats": queue_stats,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

