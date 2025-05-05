# code/backend/tests/test_integration.py
import pytest
import json
from unittest.mock import patch

# Basic integration test to ensure the app loads and a simple endpoint works
def test_app_loads_and_index_works(client):
    """Test if the Flask app loads and the index route is accessible."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"RiskOptimizer API is running" in response.data

# Example integration test for a flow (e.g., save then get portfolio from DB)
# This requires mocking the database interaction within the integration test context
@patch("app.db") # Mock the database object used in the app
def test_save_and_get_portfolio_db_integration(mock_db, client):
    """Test saving a portfolio via API and then retrieving it."""
    # --- Setup Mock DB Behavior ---
    # Use a dictionary to simulate database storage for this test
    mock_db_storage = {}

    def mock_save_portfolio(user_address, allocations):
        # Simulate saving data
        mock_db_storage[user_address] = allocations
        return True # Indicate success

    def mock_get_portfolio(user_address):
        # Simulate retrieving data
        if user_address in mock_db_storage:
            # Format data as the endpoint expects the DB function to return
            allocations = mock_db_storage[user_address]
            return [{'asset_symbol': symbol, 'percentage': percentage} 
                    for symbol, percentage in allocations.items()]
        else:
            return None # Simulate not found

    # Assign mock functions to the db object's methods
    mock_db.save_portfolio.side_effect = mock_save_portfolio
    mock_db.get_portfolio.side_effect = mock_get_portfolio

    # --- Test Save Portfolio --- 
    user_addr = "0xIntegrationTest"
    portfolio_to_save = {"BTC": 0.6, "ETH": 0.4}
    save_request_data = {
        "user_address": user_addr,
        "allocations": portfolio_to_save
    }
    save_response = client.post("/api/portfolio/save", json=save_request_data)
    assert save_response.status_code == 200
    assert save_response.get_json()["status"] == "success"
    
    # Verify save_portfolio was called correctly
    mock_db.save_portfolio.assert_called_once_with(user_addr, portfolio_to_save)

    # --- Test Get Portfolio --- 
    get_response = client.get(f"/api/portfolio/db/{user_addr}")
    assert get_response.status_code == 200
    get_data = get_response.get_json()
    assert get_data["status"] == "success"
    assert get_data["portfolio"]["user_address"] == user_addr
    # Check if retrieved assets and allocations match saved data (order might differ)
    retrieved_allocations = dict(zip(get_data["portfolio"]["assets"], get_data["portfolio"]["allocations"]))
    assert retrieved_allocations == portfolio_to_save

    # Verify get_portfolio was called correctly
    mock_db.get_portfolio.assert_called_once_with(user_addr)

# Add more integration tests as needed, focusing on interactions between components
# For example, test the optimization endpoint with mocked data fetching and calculation
# Consider testing error handling across multiple components if relevant

