"""
Portfolio service for business logic related to portfolio operations.
Implements the service layer pattern for business logic.
"""

from typing import Dict, List, Optional, Any

from riskoptimizer.core.exceptions import ValidationError, NotFoundError
from riskoptimizer.core.logging import get_logger
from riskoptimizer.infrastructure.database.repositories.portfolio_repository import portfolio_repository
from riskoptimizer.infrastructure.database.repositories.user_repository import user_repository
from riskoptimizer.infrastructure.database.session import get_db_session
from riskoptimizer.infrastructure.cache.redis_cache import redis_cache
from riskoptimizer.utils.cache_utils import cache_result, cache_invalidate

logger = get_logger(__name__)


class PortfolioService:
    """Service for portfolio-related business logic."""
    
    def __init__(self):
        """Initialize portfolio service."""
        self.portfolio_repo = portfolio_repository
        self.user_repo = user_repository
        self.cache = redis_cache
    
    @cache_result("portfolio", ttl=300)  # Cache for 5 minutes
    def get_portfolio_by_address(self, user_address: str) -> Dict[str, Any]:
        """
        Get portfolio by user address.
        
        Args:
            user_address: User wallet address
            
        Returns:
            Portfolio data with allocations
            
        Raises:
            ValidationError: If user address is invalid
            NotFoundError: If portfolio not found
        """
        # Validate input
        if not user_address or not isinstance(user_address, str):
            raise ValidationError("User address is required", "user_address", user_address)
        
        # Check cache first
        cache_key = f"portfolio:{user_address}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.debug(f"Portfolio cache hit for address {user_address}")
            return cached_data
        
        # Get from database
        with get_db_session() as session:
            try:
                portfolio_data = self.portfolio_repo.get_portfolio_with_allocations(user_address, session)
                
                # Cache the result for 5 minutes
                self.cache.set(cache_key, portfolio_data, ttl=300)
                
                logger.info(f"Retrieved portfolio for address {user_address}")
                return portfolio_data
            except NotFoundError:
                logger.warning(f"Portfolio not found for address {user_address}")
                raise
    
    @cache_invalidate("portfolio")
    def save_portfolio(self, user_address: str, allocations: Dict[str, float], 
                       name: str = "Default Portfolio") -> Dict[str, Any]:
        """
        Save portfolio for a user.
        
        Args:
            user_address: User wallet address
            allocations: Dictionary mapping asset symbols to percentages
            name: Portfolio name
            
        Returns:
            Saved portfolio data
            
        Raises:
            ValidationError: If input data is invalid
        """
        # Validate input
        self._validate_portfolio_input(user_address, allocations, name)
        
        # Normalize allocations
        normalized_allocations = self._normalize_allocations(allocations)
        
        with get_db_session() as session:
            # Save portfolio
            portfolio_data = self.portfolio_repo.save_portfolio_with_allocations(
                user_address, normalized_allocations, name, session
            )
            
            # Invalidate cache
            cache_key = f"portfolio:{user_address}"
            self.cache.delete(cache_key)
            
            # Cache the new data
            self.cache.set(cache_key, portfolio_data, ttl=300)
            
            logger.info(f"Saved portfolio for address {user_address} with {len(normalized_allocations)} assets")
            return portfolio_data
    
    def create_portfolio(self, user_id: int, user_address: str, name: str = "Default Portfolio",
                         description: str = None) -> Dict[str, Any]:
        """
        Create a new portfolio for a user.
        
        Args:
            user_id: User ID
            user_address: User wallet address
            name: Portfolio name
            description: Portfolio description
            
        Returns:
            Created portfolio data
            
        Raises:
            ValidationError: If input data is invalid
        """
        # Validate input
        if not user_id or not isinstance(user_id, int):
            raise ValidationError("User ID is required", "user_id", user_id)
        
        if not user_address or not isinstance(user_address, str):
            raise ValidationError("User address is required", "user_address", user_address)
        
        if not name or not isinstance(name, str):
            raise ValidationError("Portfolio name is required", "name", name)
        
        with get_db_session() as session:
            # Check if user exists
            user = self.user_repo.get_by_id(user_id, session)
            if not user:
                raise NotFoundError(f"User {user_id} not found", "user", str(user_id))
            
            # Create portfolio
            portfolio = self.portfolio_repo.create(user_id, user_address, name, description, session)
            
            # Prepare response
            portfolio_data = {
                "id": portfolio.id,
                "user_id": portfolio.user_id,
                "user_address": portfolio.user_address,
                "name": portfolio.name,
                "description": portfolio.description,
                "total_value": portfolio.total_value,
                "created_at": portfolio.created_at.isoformat(),
                "updated_at": portfolio.updated_at.isoformat()
            }
            
            logger.info(f"Created portfolio {portfolio.id} for user {user_id}")
            return portfolio_data
    
    def update_portfolio(self, portfolio_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            data: Dictionary with fields to update
            
        Returns:
            Updated portfolio data
            
        Raises:
            ValidationError: If input data is invalid
            NotFoundError: If portfolio not found
        """
        # Validate input
        if not portfolio_id or not isinstance(portfolio_id, int):
            raise ValidationError("Portfolio ID is required", "portfolio_id", portfolio_id)
        
        if not data or not isinstance(data, dict):
            raise ValidationError("Update data is required", "data", data)
        
        # Validate allowed fields
        allowed_fields = {"name", "description", "total_value"}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            raise ValidationError(f"Invalid fields: {', '.join(invalid_fields)}", "data", data)
        
        with get_db_session() as session:
            # Update portfolio
            portfolio = self.portfolio_repo.update(portfolio_id, data, session)
            
            # Invalidate cache if user_address is available
            if portfolio.user_address:
                cache_key = f"portfolio:{portfolio.user_address}"
                self.cache.delete(cache_key)
            
            # Prepare response
            portfolio_data = {
                "id": portfolio.id,
                "user_id": portfolio.user_id,
                "user_address": portfolio.user_address,
                "name": portfolio.name,
                "description": portfolio.description,
                "total_value": portfolio.total_value,
                "created_at": portfolio.created_at.isoformat(),
                "updated_at": portfolio.updated_at.isoformat()
            }
            
            logger.info(f"Updated portfolio {portfolio_id}")
            return portfolio_data
    
    def delete_portfolio(self, portfolio_id: int) -> bool:
        """
        Delete portfolio.
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValidationError: If portfolio ID is invalid
        """
        # Validate input
        if not portfolio_id or not isinstance(portfolio_id, int):
            raise ValidationError("Portfolio ID is required", "portfolio_id", portfolio_id)
        
        with get_db_session() as session:
            # Get portfolio to invalidate cache
            portfolio = self.portfolio_repo.get_by_id(portfolio_id, session)
            
            # Delete portfolio
            deleted = self.portfolio_repo.delete(portfolio_id, session)
            
            # Invalidate cache if portfolio existed
            if deleted and portfolio and portfolio.user_address:
                cache_key = f"portfolio:{portfolio.user_address}"
                self.cache.delete(cache_key)
            
            if deleted:
                logger.info(f"Deleted portfolio {portfolio_id}")
            else:
                logger.warning(f"Portfolio {portfolio_id} not found for deletion")
            
            return deleted
    
    def get_user_portfolios(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all portfolios for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of portfolio data
            
        Raises:
            ValidationError: If user ID is invalid
        """
        # Validate input
        if not user_id or not isinstance(user_id, int):
            raise ValidationError("User ID is required", "user_id", user_id)
        
        with get_db_session() as session:
            # Get portfolios
            portfolios = self.portfolio_repo.get_by_user_id(user_id, session)
            
            # Prepare response
            portfolio_list = []
            for portfolio in portfolios:
                portfolio_data = {
                    "id": portfolio.id,
                    "user_id": portfolio.user_id,
                    "user_address": portfolio.user_address,
                    "name": portfolio.name,
                    "description": portfolio.description,
                    "total_value": portfolio.total_value,
                    "created_at": portfolio.created_at.isoformat(),
                    "updated_at": portfolio.updated_at.isoformat()
                }
                portfolio_list.append(portfolio_data)
            
            logger.info(f"Retrieved {len(portfolio_list)} portfolios for user {user_id}")
            return portfolio_list
    
    def _validate_portfolio_input(self, user_address: str, allocations: Dict[str, float], name: str) -> None:
        """
        Validate portfolio input data.
        
        Args:
            user_address: User wallet address
            allocations: Asset allocations
            name: Portfolio name
            
        Raises:
            ValidationError: If input data is invalid
        """
        # Validate user address
        if not user_address or not isinstance(user_address, str):
            raise ValidationError("User address is required", "user_address", user_address)
        
        # Validate allocations
        if not allocations or not isinstance(allocations, dict):
            raise ValidationError("Allocations are required", "allocations", allocations)
        
        if len(allocations) == 0:
            raise ValidationError("At least one allocation is required", "allocations", allocations)
        
        # Validate allocation values
        for asset, percentage in allocations.items():
            if not isinstance(asset, str) or not asset.strip():
                raise ValidationError(f"Invalid asset symbol: {asset}", "allocations", allocations)
            
            if not isinstance(percentage, (int, float)) or percentage < 0 or percentage > 100:
                raise ValidationError(f"Invalid percentage for {asset}: {percentage}", "allocations", allocations)
        
        # Validate name
        if not name or not isinstance(name, str):
            raise ValidationError("Portfolio name is required", "name", name)
    
    def _normalize_allocations(self, allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize allocations to ensure they sum to 100%.
        
        Args:
            allocations: Asset allocations
            
        Returns:
            Normalized allocations
        """
        total = sum(allocations.values())
        
        if total == 0:
            raise ValidationError("Total allocation cannot be zero", "allocations", allocations)
        
        # If total is not 100%, normalize to 100%
        if abs(total - 100.0) > 0.01:  # Allow small floating point differences
            logger.warning(f"Normalizing allocations from {total}% to 100%")
            normalized = {asset: (percentage / total) * 100 for asset, percentage in allocations.items()}
            return normalized
        
        return allocations


# Singleton instance
portfolio_service = PortfolioService()

