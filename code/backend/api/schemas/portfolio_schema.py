"""
Portfolio schema for request validation.
Provides validation functions for portfolio-related API requests.
"""

from typing import Dict, Any, List
from riskoptimizer.core.exceptions import ValidationError


def validate_portfolio_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate portfolio save request data.
    
    Args:
        data: Request data
        
    Returns:
        Validated data
        
    Raises:
        ValidationError: If validation fails
    """
    # Check required fields
    if 'user_address' not in data:
        raise ValidationError("User address is required", "user_address")
    
    if 'allocations' not in data:
        raise ValidationError("Allocations are required", "allocations")
    
    # Validate user address
    user_address = data['user_address']
    if not isinstance(user_address, str) or not user_address.strip():
        raise ValidationError("User address must be a non-empty string", "user_address", user_address)
    
    # Validate allocations
    allocations = data['allocations']
    if not isinstance(allocations, dict):
        raise ValidationError("Allocations must be a dictionary", "allocations", allocations)
    
    if len(allocations) == 0:
        raise ValidationError("At least one allocation is required", "allocations", allocations)
    
    # Validate allocation values
    for asset, percentage in allocations.items():
        if not isinstance(asset, str) or not asset.strip():
            raise ValidationError(f"Invalid asset symbol: {asset}", "allocations", asset)
        
        if not isinstance(percentage, (int, float)):
            raise ValidationError(f"Percentage for {asset} must be a number", "allocations", percentage)
        
        if percentage < 0 or percentage > 100:
            raise ValidationError(f"Percentage for {asset} must be between 0 and 100", "allocations", percentage)
    
    # Validate optional fields
    if 'name' in data:
        name = data['name']
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Portfolio name must be a non-empty string", "name", name)
    
    # Return validated data
    validated_data = {
        'user_address': user_address,
        'allocations': allocations
    }
    
    if 'name' in data:
        validated_data['name'] = data['name']
    
    return validated_data


def validate_portfolio_update_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate portfolio update request data.
    
    Args:
        data: Request data
        
    Returns:
        Validated data
        
    Raises:
        ValidationError: If validation fails
    """
    # Check if data is empty
    if not data:
        raise ValidationError("Update data is required")
    
    # Validate allowed fields
    allowed_fields = {"name", "description", "total_value"}
    invalid_fields = set(data.keys()) - allowed_fields
    if invalid_fields:
        raise ValidationError(f"Invalid fields: {', '.join(invalid_fields)}", "data")
    
    # Validate name if present
    if 'name' in data:
        name = data['name']
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Portfolio name must be a non-empty string", "name", name)
    
    # Validate description if present
    if 'description' in data:
        description = data['description']
        if description is not None and not isinstance(description, str):
            raise ValidationError("Portfolio description must be a string", "description", description)
    
    # Validate total_value if present
    if 'total_value' in data:
        total_value = data['total_value']
        if not isinstance(total_value, (int, float)):
            raise ValidationError("Total value must be a number", "total_value", total_value)
        
        if total_value < 0:
            raise ValidationError("Total value cannot be negative", "total_value", total_value)
    
    # Return validated data
    return data

