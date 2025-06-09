"""
Risk service for business logic related to risk calculations.
Implements the service layer pattern for business logic.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy.stats import norm

from riskoptimizer.core.exceptions import ValidationError, CalculationError
from riskoptimizer.core.logging import get_logger
from riskoptimizer.infrastructure.cache.redis_cache import redis_cache
from riskoptimizer.utils.cache_utils import memoize

logger = get_logger(__name__)


class RiskService:
    """Service for risk-related business logic."""
    
    def __init__(self):
        """Initialize risk service."""
        self.cache = redis_cache
    
    @memoize(ttl=3600)  # Cache for 1 hour
    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR) for a given set of returns.
        
        Args:
            returns: List of historical returns
            confidence: Confidence level (default: 0.95)
            
        Returns:
            Value at Risk
            
        Raises:
            ValidationError: If input data is invalid
            CalculationError: If calculation fails
        """
        # Validate input
        self._validate_returns(returns)
        self._validate_confidence(confidence)
        
        try:
            # Check cache
            cache_key = f"var:{hash(tuple(returns))}:{confidence}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"VaR cache hit for {len(returns)} returns at {confidence} confidence")
                return cached_result
            
            # Calculate VaR
            returns_array = np.array(returns)
            mean = np.mean(returns_array)
            std = np.std(returns_array)
            z_score = norm.ppf(1 - confidence)
            var = float(mean + z_score * std)
            
            # Cache result for 1 hour
            self.cache.set(cache_key, var, ttl=3600)
            
            logger.info(f"Calculated VaR: {var} for {len(returns)} returns at {confidence} confidence")
            return var
        except Exception as e:
            logger.error(f"Error calculating VaR: {str(e)}", exc_info=True)
            raise CalculationError(f"Failed to calculate VaR: {str(e)}", "var")
    
    def calculate_cvar(self, returns: List[float], confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) for a given set of returns.
        
        Args:
            returns: List of historical returns
            confidence: Confidence level (default: 0.95)
            
        Returns:
            Conditional Value at Risk
            
        Raises:
            ValidationError: If input data is invalid
            CalculationError: If calculation fails
        """
        # Validate input
        self._validate_returns(returns)
        self._validate_confidence(confidence)
        
        try:
            # Check cache
            cache_key = f"cvar:{hash(tuple(returns))}:{confidence}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"CVaR cache hit for {len(returns)} returns at {confidence} confidence")
                return cached_result
            
            # Calculate VaR first
            var = self.calculate_var(returns, confidence)
            
            # Calculate CVaR
            returns_array = np.array(returns)
            tail_returns = returns_array[returns_array <= var]
            
            if len(tail_returns) == 0:
                raise CalculationError("No returns below VaR threshold", "cvar")
            
            cvar = float(np.mean(tail_returns))
            
            # Cache result for 1 hour
            self.cache.set(cache_key, cvar, ttl=3600)
            
            logger.info(f"Calculated CVaR: {cvar} for {len(returns)} returns at {confidence} confidence")
            return cvar
        except CalculationError:
            raise
        except Exception as e:
            logger.error(f"Error calculating CVaR: {str(e)}", exc_info=True)
            raise CalculationError(f"Failed to calculate CVaR: {str(e)}", "cvar")
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio for a given set of returns.
        
        Args:
            returns: List of historical returns
            risk_free_rate: Risk-free rate (default: 0.0)
            
        Returns:
            Sharpe ratio
            
        Raises:
            ValidationError: If input data is invalid
            CalculationError: If calculation fails
        """
        # Validate input
        self._validate_returns(returns)
        
        if not isinstance(risk_free_rate, (int, float)):
            raise ValidationError("Risk-free rate must be a number", "risk_free_rate", risk_free_rate)
        
        try:
            # Check cache
            cache_key = f"sharpe:{hash(tuple(returns))}:{risk_free_rate}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Sharpe ratio cache hit for {len(returns)} returns with {risk_free_rate} risk-free rate")
                return cached_result
            
            # Calculate Sharpe ratio
            returns_array = np.array(returns)
            excess_returns = returns_array - risk_free_rate
            mean_excess_return = np.mean(excess_returns)
            std_excess_return = np.std(excess_returns)
            
            if std_excess_return == 0:
                raise CalculationError("Standard deviation of excess returns is zero", "sharpe_ratio")
            
            sharpe_ratio = float(mean_excess_return / std_excess_return)
            
            # Cache result for 1 hour
            self.cache.set(cache_key, sharpe_ratio, ttl=3600)
            
            logger.info(f"Calculated Sharpe ratio: {sharpe_ratio} for {len(returns)} returns")
            return sharpe_ratio
        except CalculationError:
            raise
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {str(e)}", exc_info=True)
            raise CalculationError(f"Failed to calculate Sharpe ratio: {str(e)}", "sharpe_ratio")
    
    def calculate_max_drawdown(self, returns: List[float]) -> float:
        """
        Calculate maximum drawdown for a given set of returns.
        
        Args:
            returns: List of historical returns
            
        Returns:
            Maximum drawdown
            
        Raises:
            ValidationError: If input data is invalid
            CalculationError: If calculation fails
        """
        # Validate input
        self._validate_returns(returns)
        
        try:
            # Check cache
            cache_key = f"max_drawdown:{hash(tuple(returns))}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Max drawdown cache hit for {len(returns)} returns")
                return cached_result
            
            # Convert returns to cumulative returns
            returns_array = np.array(returns)
            wealth_index = (1 + returns_array).cumprod()
            
            # Calculate running maximum
            running_max = np.maximum.accumulate(wealth_index)
            
            # Calculate drawdown
            drawdown = (wealth_index - running_max) / running_max
            
            # Get maximum drawdown
            max_drawdown = float(np.min(drawdown))
            
            # Cache result for 1 hour
            self.cache.set(cache_key, max_drawdown, ttl=3600)
            
            logger.info(f"Calculated max drawdown: {max_drawdown} for {len(returns)} returns")
            return max_drawdown
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {str(e)}", exc_info=True)
            raise CalculationError(f"Failed to calculate max drawdown: {str(e)}", "max_drawdown")
    
    def calculate_portfolio_risk_metrics(self, returns: List[float], confidence: float = 0.95,
                                         risk_free_rate: float = 0.0) -> Dict[str, float]:
        """
        Calculate comprehensive risk metrics for a portfolio.
        
        Args:
            returns: List of historical returns
            confidence: Confidence level for VaR and CVaR
            risk_free_rate: Risk-free rate for Sharpe ratio
            
        Returns:
            Dictionary with risk metrics
            
        Raises:
            ValidationError: If input data is invalid
            CalculationError: If calculation fails
        """
        # Validate input
        self._validate_returns(returns)
        self._validate_confidence(confidence)
        
        if not isinstance(risk_free_rate, (int, float)):
            raise ValidationError("Risk-free rate must be a number", "risk_free_rate", risk_free_rate)
        
        try:
            # Check cache
            cache_key = f"risk_metrics:{hash(tuple(returns))}:{confidence}:{risk_free_rate}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Risk metrics cache hit for {len(returns)} returns")
                return cached_result
            
            # Calculate metrics
            returns_array = np.array(returns)
            mean_return = float(np.mean(returns_array))
            volatility = float(np.std(returns_array))
            var = self.calculate_var(returns, confidence)
            cvar = self.calculate_cvar(returns, confidence)
            sharpe_ratio = self.calculate_sharpe_ratio(returns, risk_free_rate)
            max_drawdown = self.calculate_max_drawdown(returns)
            
            # Prepare result
            metrics = {
                "expected_return": mean_return,
                "volatility": volatility,
                "value_at_risk": var,
                "conditional_var": cvar,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown
            }
            
            # Cache result for 1 hour
            self.cache.set(cache_key, metrics, ttl=3600)
            
            logger.info(f"Calculated risk metrics for {len(returns)} returns")
            return metrics
        except (ValidationError, CalculationError):
            raise
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}", exc_info=True)
            raise CalculationError(f"Failed to calculate risk metrics: {str(e)}", "risk_metrics")
    
    @memoize(ttl=86400)  # Cache for 1 day
    def calculate_efficient_frontier(self, returns: Dict[str, List[float]], 
                                     min_weight: float = 0.0, max_weight: float = 1.0,
                                     risk_free_rate: float = 0.0, points: int = 20) -> List[Dict[str, Any]]:
        """
        Calculate efficient frontier for a set of assets.
        
        Args:
            returns: Dictionary mapping asset symbols to historical returns
            min_weight: Minimum weight for each asset
            max_weight: Maximum weight for each asset
            risk_free_rate: Risk-free rate
            points: Number of points on the efficient frontier
            
        Returns:
            List of points on the efficient frontier
            
        Raises:
            ValidationError: If input data is invalid
            CalculationError: If calculation fails
        """
        try:
            # Import here to avoid circular imports
            from pypfopt import EfficientFrontier
            from pypfopt import risk_models
            from pypfopt import expected_returns
        except ImportError:
            logger.error("PyPortfolioOpt library not installed", exc_info=True)
            raise CalculationError("Required library PyPortfolioOpt not installed", "efficient_frontier")
        
        # Validate input
        if not returns or not isinstance(returns, dict):
            raise ValidationError("Returns dictionary is required", "returns", returns)
        
        if len(returns) < 2:
            raise ValidationError("At least two assets are required", "returns", returns)
        
        for asset, asset_returns in returns.items():
            self._validate_returns(asset_returns)
        
        if not isinstance(min_weight, (int, float)) or min_weight < 0 or min_weight > 1:
            raise ValidationError("Minimum weight must be between 0 and 1", "min_weight", min_weight)
        
        if not isinstance(max_weight, (int, float)) or max_weight < 0 or max_weight > 1:
            raise ValidationError("Maximum weight must be between 0 and 1", "max_weight", max_weight)
        
        if min_weight > max_weight:
            raise ValidationError("Minimum weight cannot be greater than maximum weight", "min_weight", min_weight)
        
        if not isinstance(points, int) or points < 2:
            raise ValidationError("Number of points must be at least 2", "points", points)
        
        try:
            # Check cache
            cache_key = f"efficient_frontier:{hash(tuple((k, tuple(v)) for k, v in sorted(returns.items())))}:{min_weight}:{max_weight}:{risk_free_rate}:{points}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Efficient frontier cache hit for {len(returns)} assets")
                return cached_result
            
            # Convert returns to numpy arrays
            assets = list(returns.keys())
            returns_matrix = np.array([returns[asset] for asset in assets]).T
            
            # Calculate expected returns and covariance matrix
            mean_returns = np.array([np.mean(returns_matrix[:, i]) for i in range(len(assets))])
            cov_matrix = np.cov(returns_matrix.T)
            
            # Create efficient frontier
            ef = EfficientFrontier(mean_returns, cov_matrix)
            
            # Add weight constraints
            ef.add_constraint(lambda w: w >= min_weight)
            ef.add_constraint(lambda w: w <= max_weight)
            
            # Calculate efficient frontier points
            frontier_points = []
            
            # Get minimum volatility portfolio
            ef.min_volatility()
            min_vol_weights = ef.clean_weights()
            min_vol_performance = ef.portfolio_performance()
            frontier_points.append({
                "type": "min_volatility",
                "expected_return": float(min_vol_performance[0]),
                "volatility": float(min_vol_performance[1]),
                "sharpe_ratio": float(min_vol_performance[2]),
                "weights": {asset: float(min_vol_weights.get(asset, 0)) for asset in assets}
            })
            
            # Reset efficient frontier
            ef = EfficientFrontier(mean_returns, cov_matrix)
            ef.add_constraint(lambda w: w >= min_weight)
            ef.add_constraint(lambda w: w <= max_weight)
            
            # Get maximum Sharpe ratio portfolio
            ef.max_sharpe(risk_free_rate=risk_free_rate)
            max_sharpe_weights = ef.clean_weights()
            max_sharpe_performance = ef.portfolio_performance()
            frontier_points.append({
                "type": "max_sharpe",
                "expected_return": float(max_sharpe_performance[0]),
                "volatility": float(max_sharpe_performance[1]),
                "sharpe_ratio": float(max_sharpe_performance[2]),
                "weights": {asset: float(max_sharpe_weights.get(asset, 0)) for asset in assets}
            })
            
            # Generate efficient frontier points
            min_return = min_vol_performance[0]
            max_return = max(mean_returns)
            target_returns = np.linspace(min_return, max_return, points)
            
            for target_return in target_returns:
                ef = EfficientFrontier(mean_returns, cov_matrix)
                ef.add_constraint(lambda w: w >= min_weight)
                ef.add_constraint(lambda w: w <= max_weight)
                
                try:
                    ef.efficient_return(target_return)
                    weights = ef.clean_weights()
                    performance = ef.portfolio_performance()
                    
                    frontier_points.append({
                        "type": "efficient_return",
                        "target_return": float(target_return),
                        "expected_return": float(performance[0]),
                        "volatility": float(performance[1]),
                        "sharpe_ratio": float(performance[2]),
                        "weights": {asset: float(weights.get(asset, 0)) for asset in assets}
                    })
                except Exception as e:
                    logger.warning(f"Could not calculate efficient frontier point for return {target_return}: {str(e)}")
                    continue
            
            # Cache result for 1 day
            self.cache.set(cache_key, frontier_points, ttl=86400)
            
            logger.info(f"Calculated efficient frontier with {len(frontier_points)} points for {len(assets)} assets")
            return frontier_points
        except Exception as e:
            logger.error(f"Error calculating efficient frontier: {str(e)}", exc_info=True)
            raise CalculationError(f"Failed to calculate efficient frontier: {str(e)}", "efficient_frontier")
    
    def _validate_returns(self, returns: List[float]) -> None:
        """
        Validate returns data.
        
        Args:
            returns: List of historical returns
            
        Raises:
            ValidationError: If returns data is invalid
        """
        if not returns:
            raise ValidationError("Returns data is required", "returns", returns)
        
        if not isinstance(returns, list):
            raise ValidationError("Returns must be a list", "returns", returns)
        
        if len(returns) < 2:
            raise ValidationError("At least two data points are required", "returns", returns)
        
        for i, value in enumerate(returns):
            if not isinstance(value, (int, float)):
                raise ValidationError(f"Return at index {i} is not a number: {value}", "returns", value)
    
    def _validate_confidence(self, confidence: float) -> None:
        """
        Validate confidence level.
        
        Args:
            confidence: Confidence level
            
        Raises:
            ValidationError: If confidence level is invalid
        """
        if not isinstance(confidence, (int, float)):
            raise ValidationError("Confidence level must be a number", "confidence", confidence)
        
        if confidence <= 0 or confidence >= 1:
            raise ValidationError("Confidence level must be between 0 and 1 (exclusive)", "confidence", confidence)


# Singleton instance
risk_service = RiskService()

