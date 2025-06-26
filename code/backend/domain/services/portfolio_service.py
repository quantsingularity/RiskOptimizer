
from typing import Dict, List, Optional, Any
from decimal import Decimal, getcontext

from riskoptimizer.core.exceptions import ValidationError, NotFoundError
from riskoptimizer.core.logging import get_logger
from riskoptimizer.infrastructure.database.repositories.portfolio_repository import portfolio_repository
from riskoptimizer.infrastructure.database.repositories.user_repository import user_repository
from riskoptimizer.infrastructure.database.session import get_db_session
from riskoptimizer.infrastructure.cache.redis_cache import redis_cache
from riskoptimizer.utils.cache_utils import cache_result, cache_invalidate
from riskoptimizer.domain.services.audit_service import audit_service

logger = get_logger(__name__)

# Set precision for Decimal calculations globally for this module
getcontext().prec = 28

class PortfolioService:
    """
    Service for managing user portfolios and their allocations.

    This service handles operations such as retrieving, saving, creating, updating,
    and deleting portfolios. It integrates with the database repository for data
    persistence, Redis for caching, and the audit service for logging financial actions.
    """
    
    def __init__(self):
        """
        Initializes the PortfolioService with necessary repositories and services.
        """
        self.portfolio_repo = portfolio_repository
        self.user_repo = user_repository
        self.cache = redis_cache
        self.audit_service = audit_service
    
    @cache_result("portfolio", ttl=300)  # Cache for 5 minutes
    def get_portfolio_by_address(self, user_address: str) -> Dict[str, Any]:
        """
        Retrieves a user's portfolio and its allocations by their wallet address.
        
        Args:
            user_address: The blockchain wallet address of the user.
            
        Returns:
            A dictionary containing the portfolio data, including total value and allocations.
            
        Raises:
            ValidationError: If the user address is invalid.
            NotFoundError: If no portfolio is found for the given address.
        """
        # Validate input user address
        if not user_address or not isinstance(user_address, str):
            raise ValidationError("User address is required", "user_address", user_address)
        
        # Check if the portfolio data is available in cache
        cache_key = f"portfolio:{user_address}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.debug(f"Portfolio cache hit for address {user_address}")
            # Convert Decimal strings back to Decimal objects from cached data
            if "total_value" in cached_data:
                cached_data["total_value"] = Decimal(cached_data["total_value"])
            if "allocations" in cached_data:
                for alloc in cached_data["allocations"]:
                    alloc["percentage"] = Decimal(alloc["percentage"])
                    if alloc["amount"] is not None:
                        alloc["amount"] = Decimal(alloc["amount"])
                    if alloc["current_price"] is not None:
                        alloc["current_price"] = Decimal(alloc["current_price"])
            return cached_data
        
        # If not in cache, retrieve from the database
        with get_db_session() as session:
            try:
                portfolio_data = self.portfolio_repo.get_portfolio_with_allocations(user_address, session)
                
                # Cache the retrieved result (convert Decimals to strings for JSON serialization)
                serializable_portfolio_data = portfolio_data.copy()
                if "total_value" in serializable_portfolio_data:
                    serializable_portfolio_data["total_value"] = str(serializable_portfolio_data["total_value"])
                if "allocations" in serializable_portfolio_data:
                    serializable_portfolio_data["allocations"] = [{
                        k: str(v) if isinstance(v, Decimal) else v for k, v in alloc.items()
                    } for alloc in serializable_portfolio_data["allocations"]]

                self.cache.set(cache_key, serializable_portfolio_data, ttl=300)
                
                logger.info(f"Retrieved portfolio for address {user_address}")
                return portfolio_data
            except NotFoundError:
                logger.warning(f"Portfolio not found for address {user_address}")
                raise # Re-raise NotFoundError to be handled by the controller
    
    @cache_invalidate("portfolio") # Invalidate cache related to portfolios upon saving
    def save_portfolio(self, user_address: str, allocations: Dict[str, float], 
                       name: str = "Default Portfolio") -> Dict[str, Any]:
        """
        Saves or updates a user's portfolio allocations.
        
        If a portfolio for the user address exists, it updates its allocations.
        Otherwise, it creates a new portfolio.
        
        Args:
            user_address: The blockchain wallet address of the user.
            allocations: A dictionary mapping asset symbols (e.g., "BTC") to their
                         percentage allocations (e.g., 60.0 for 60%).
            name: An optional name for the portfolio. Defaults to "Default Portfolio".
            
        Returns:
            A dictionary containing the saved or updated portfolio data.
            
        Raises:
            ValidationError: If input data (user_address, allocations, name) is invalid.
        """
        # Validate input data for the portfolio
        self._validate_portfolio_input(user_address, allocations, name)
        
        # Normalize allocations to ensure they sum to 100% and convert to Decimal for precision
        normalized_allocations = self._normalize_allocations(allocations)
        decimal_allocations = {k: Decimal(str(v)) for k, v in normalized_allocations.items()}
        
        with get_db_session() as session:
            # Save the portfolio and its allocations to the database
            portfolio_data = self.portfolio_repo.save_portfolio_with_allocations(
                user_address, decimal_allocations, name, session
            )
            
            # Log the action for auditing purposes
            user = self.user_repo.get_by_wallet_address(user_address, session)
            user_id = user.id if user else None # Get user ID if user exists
            self.audit_service.log_action(user_id=user_id, action_type="PORTFOLIO_SAVED", entity_type="PORTFOLIO", entity_id=portfolio_data.get("portfolio_id"), details={"user_address": user_address, "name": name, "allocations": {k: str(v) for k, v in decimal_allocations.items()}})

            logger.info(f"Saved portfolio for address {user_address} with {len(decimal_allocations)} assets")
            return portfolio_data
    
    def create_portfolio(self, user_id: int, user_address: str, name: str = "Default Portfolio",
                         description: str = None) -> Dict[str, Any]:
        """
        Creates a new portfolio for a specified user.
        
        Args:
            user_id: The ID of the user for whom the portfolio is being created.
            user_address: The blockchain wallet address to associate with the new portfolio.
            name: The name of the new portfolio. Defaults to "Default Portfolio".
            description: An optional description for the portfolio.
            
        Returns:
            A dictionary containing the newly created portfolio's data.
            
        Raises:
            ValidationError: If input data (user_id, user_address, name) is invalid.
            NotFoundError: If the specified user does not exist.
        """
        # Validate input parameters
        if not user_id or not isinstance(user_id, int):
            raise ValidationError("User ID is required and must be an integer.", "user_id", user_id)
        
        if not user_address or not isinstance(user_address, str):
            raise ValidationError("User address is required and must be a string.", "user_address", user_address)
        
        if not name or not isinstance(name, str):
            raise ValidationError("Portfolio name is required and must be a string.", "name", name)
        
        with get_db_session() as session:
            # Check if the user exists in the database
            user = self.user_repo.get_by_id(user_id, session)
            if not user:
                raise NotFoundError(f"User {user_id} not found", "user", str(user_id))
            
            # Create the portfolio record in the database
            portfolio = self.portfolio_repo.create(user_id, user_address, name, description, session)
            
            # Prepare response, ensuring Decimal types are converted to string for JSON serialization
            portfolio_data = {
                "id": portfolio.id,
                "user_id": portfolio.user_id,
                "user_address": portfolio.user_address,
                "name": portfolio.name,
                "description": portfolio.description,
                "total_value": str(portfolio.total_value) if isinstance(portfolio.total_value, Decimal) else portfolio.total_value,
                "created_at": portfolio.created_at.isoformat(),
                "updated_at": portfolio.updated_at.isoformat()
            }
            
            # Log the portfolio creation action for auditing
            self.audit_service.log_action(user_id=user_id, action_type="PORTFOLIO_CREATED", entity_type="PORTFOLIO", entity_id=portfolio.id, details={"name": name, "user_address": user_address, "description": description})

            logger.info(f"Created portfolio {portfolio.id} for user {user_id}")
            return portfolio_data
    
    def update_portfolio(self, portfolio_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing portfolio's details.
        
        Args:
            portfolio_id: The ID of the portfolio to update.
            data: A dictionary containing the fields to update (e.g., "name", "description", "total_value").
            
        Returns:
            A dictionary containing the updated portfolio data.
            
        Raises:
            ValidationError: If input data (portfolio_id or update data) is invalid.
            NotFoundError: If the portfolio with the given ID is not found.
        """
        # Validate input parameters
        if not portfolio_id or not isinstance(portfolio_id, int):
            raise ValidationError("Portfolio ID is required and must be an integer.", "portfolio_id", portfolio_id)
        
        if not data or not isinstance(data, dict) or not data:
            raise ValidationError("Update data is required and must be a non-empty dictionary.", "data", data)
        
        # Define allowed fields for update and process the input data
        allowed_fields = {"name", "description", "total_value"}
        processed_data = {}
        for key, value in data.items():
            if key not in allowed_fields:
                raise ValidationError(f"Invalid field for update: {key}", "data", data)
            if key == "total_value":
                try:
                    # Convert total_value to Decimal for precise financial calculations
                    processed_data[key] = Decimal(str(value))
                except Exception:
                    raise ValidationError("Total value must be a valid number.", "total_value", value)
            else:
                processed_data[key] = value

        with get_db_session() as session:
            # Retrieve the old portfolio data for audit logging before updating
            old_portfolio = self.portfolio_repo.get_by_id(portfolio_id, session)
            if not old_portfolio:
                raise NotFoundError(f"Portfolio {portfolio_id} not found", "portfolio", str(portfolio_id))

            # Update the portfolio in the database
            portfolio = self.portfolio_repo.update(portfolio_id, processed_data, session)
            
            # Invalidate the cache for this specific portfolio if its user address is known
            if portfolio and portfolio.user_address:
                cache_key = f"portfolio:{portfolio.user_address}"
                self.cache.delete(cache_key)
            
            # Prepare response, ensuring Decimal types are converted to string for JSON serialization
            portfolio_data = {
                "id": portfolio.id,
                "user_id": portfolio.user_id,
                "user_address": portfolio.user_address,
                "name": portfolio.name,
                "description": portfolio.description,
                "total_value": str(portfolio.total_value) if isinstance(portfolio.total_value, Decimal) else portfolio.total_value,
                "created_at": portfolio.created_at.isoformat(),
                "updated_at": portfolio.updated_at.isoformat()
            }
            
            # Log the portfolio update action for auditing
            self.audit_service.log_action(user_id=portfolio.user_id, action_type="PORTFOLIO_UPDATED", entity_type="PORTFOLIO", entity_id=portfolio.id, details={"old_data": {k: str(getattr(old_portfolio, k)) for k in processed_data.keys() if hasattr(old_portfolio, k)}, "new_data": {k: str(v) for k, v in processed_data.items()}})

            logger.info(f"Updated portfolio {portfolio_id}")
            return portfolio_data
    
    def delete_portfolio(self, portfolio_id: int) -> bool:
        """
        Deletes a portfolio from the system.
        
        Args:
            portfolio_id: The ID of the portfolio to delete.
            
        Returns:
            True if the portfolio was successfully deleted, False if not found.
            
        Raises:
            ValidationError: If the portfolio ID is invalid.
        """
        # Validate input portfolio ID
        if not portfolio_id or not isinstance(portfolio_id, int):
            raise ValidationError("Portfolio ID is required and must be an integer.", "portfolio_id", portfolio_id)
        
        with get_db_session() as session:
            # Get portfolio details before deletion for cache invalidation and audit logging
            portfolio = self.portfolio_repo.get_by_id(portfolio_id, session)
            
            # Attempt to delete the portfolio from the database
            deleted = self.portfolio_repo.delete(portfolio_id, session)
            
            # Invalidate the cache if the portfolio was successfully deleted and its user address is known
            if deleted and portfolio and portfolio.user_address:
                cache_key = f"portfolio:{portfolio.user_address}"
                self.cache.delete(cache_key)
            
            if deleted:
                logger.info(f"Deleted portfolio {portfolio_id}")
                # Log the portfolio deletion action for auditing
                self.audit_service.log_action(user_id=portfolio.user_id, action_type="PORTFOLIO_DELETED", entity_type="PORTFOLIO", entity_id=portfolio.id, details={"portfolio_id": portfolio.id, "name": portfolio.name, "user_address": portfolio.user_address})
            else:
                logger.warning(f"Portfolio {portfolio_id} not found for deletion")
            
            return deleted
    
    def get_user_portfolios(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all portfolios associated with a specific user ID.
        
        Args:
            user_id: The ID of the user whose portfolios are to be retrieved.
            
        Returns:
            A list of dictionaries, each representing a portfolio belonging to the user.
            
        Raises:
            ValidationError: If the user ID is invalid.
        """
        # Validate input user ID
        if not user_id or not isinstance(user_id, int):
            raise ValidationError("User ID is required and must be an integer.", "user_id", user_id)
        
        with get_db_session() as session:
            # Retrieve portfolios for the user from the database
            portfolios = self.portfolio_repo.get_by_user_id(user_id, session)
            
            # Prepare response, ensuring Decimal types are converted to string for JSON serialization
            portfolio_list = []
            for portfolio in portfolios:
                portfolio_data = {
                    "id": portfolio.id,
                    "user_id": portfolio.user_id,
                    "user_address": portfolio.user_address,
                    "name": portfolio.name,
                    "description": portfolio.description,
                    "total_value": str(portfolio.total_value) if isinstance(portfolio.total_value, Decimal) else portfolio.total_value,
                    "created_at": portfolio.created_at.isoformat(),
                    "updated_at": portfolio.updated_at.isoformat()
                }
                portfolio_list.append(portfolio_data)
            
            logger.info(f"Retrieved {len(portfolio_list)} portfolios for user {user_id}")
            return portfolio_list
    
    def _validate_portfolio_input(self, user_address: str, allocations: Dict[str, float], name: str) -> None:
        """
        Internal helper method to validate common portfolio input parameters.
        
        Args:
            user_address: The user's wallet address.
            allocations: The asset allocations dictionary.
            name: The portfolio name.
            
        Raises:
            ValidationError: If any of the input parameters are invalid.
        """
        # Validate user address
        if not user_address or not isinstance(user_address, str):
            raise ValidationError("User address is required and must be a string.", "user_address", user_address)
        
        # Validate allocations dictionary
        if not allocations or not isinstance(allocations, dict):
            raise ValidationError("Allocations are required and must be a dictionary.", "allocations", allocations)
        
        if len(allocations) == 0:
            raise ValidationError("At least one allocation is required.", "allocations", allocations)
        
        # Validate each allocation entry
        for asset, percentage in allocations.items():
            if not isinstance(asset, str) or not asset.strip():
                raise ValidationError(f"Invalid asset symbol: {asset}. Asset symbol must be a non-empty string.", "allocations", allocations)
            
            try:
                # Attempt to convert to Decimal to validate if it's a valid number
                Decimal(str(percentage))
            except Exception:
                raise ValidationError(f"Invalid percentage for asset {asset}. Must be a valid number.", "allocations", allocations)
            
            if not (0 <= percentage <= 100):
                raise ValidationError(f"Percentage for asset {asset} must be between 0 and 100.", "allocations", allocations)
        
        # Validate portfolio name
        if not name or not isinstance(name, str) or not name.strip():
            raise ValidationError("Portfolio name is required and must be a non-empty string.", "name", name)

    def _normalize_allocations(self, allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Normalizes portfolio allocations so that their sum is 100%.
        
        Args:
            allocations: A dictionary of asset allocations.
            
        Returns:
            A new dictionary with normalized allocations.
            
        Raises:
            ValidationError: If the sum of allocations is zero, preventing normalization.
        """
        total_percentage = sum(allocations.values())
        if total_percentage == 0:
            raise ValidationError("Total allocation percentage cannot be zero.", "allocations", allocations)
        
        # Normalize each allocation by dividing by the total percentage
        normalized = {asset: (percentage / total_percentage) * 100 for asset, percentage in allocations.items()}
        return normalized


# Singleton instance of PortfolioService for application-wide use
portfolio_service = PortfolioService()


