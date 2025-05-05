# code/backend/tests/test_services.py
import pytest
import numpy as np
import pandas as pd
import math # Import math for isnan
from unittest.mock import patch, MagicMock

# Assuming RiskMetrics is in services.quant_analysis
# Adjust import path if necessary
from services.quant_analysis import RiskMetrics

# Test RiskMetrics.calculate_var
def test_calculate_var():
    """Test the Value at Risk calculation."""
    returns = [0.01, -0.02, 0.03, -0.01, 0.02, 0.005, -0.005]
    # Expected values recalculated based on numpy/scipy
    expected_var_95 = -0.02224716
    expected_var_99 = -0.03324024

    var_95 = RiskMetrics.calculate_var(returns, confidence=0.95)
    var_99 = RiskMetrics.calculate_var(returns, confidence=0.99)

    assert isinstance(var_95, float)
    # Use approx with slightly higher tolerance if needed, but try exact first
    assert var_95 == pytest.approx(expected_var_95, abs=1e-4)
    assert var_99 == pytest.approx(expected_var_99, abs=1e-5)

def test_calculate_var_empty_returns():
    """Test VaR calculation with empty returns list should return NaN."""
    # np.mean and np.std of empty list produce RuntimeWarning and return nan
    # The function should return nan in this case
    with pytest.warns(RuntimeWarning):
        result = RiskMetrics.calculate_var([])
        assert math.isnan(result)

# Test RiskMetrics.efficient_frontier
# Patch the pypfopt.EfficientFrontier where it's imported inside the method
@patch("pypfopt.EfficientFrontier") 
def test_efficient_frontier(mock_ef):
    """Test the efficient frontier calculation delegates correctly."""
    mock_returns = pd.Series([0.1, 0.2], index=["A", "B"])
    mock_cov = pd.DataFrame([[0.1, 0.05], [0.05, 0.2]], index=["A", "B"], columns=["A", "B"])
    
    mock_ef_instance = MagicMock()
    mock_ef_instance.max_sharpe.return_value = None # Modifies inplace
    mock_ef_instance.clean_weights.return_value = {"A": 0.6, "B": 0.4}
    mock_ef.return_value = mock_ef_instance

    weights = RiskMetrics.efficient_frontier(mock_returns, mock_cov)

    assert weights == {"A": 0.6, "B": 0.4}
    # The call happens inside the function, using the imported name
    mock_ef.assert_called_once_with(mock_returns, mock_cov)
    mock_ef_instance.max_sharpe.assert_called_once()
    mock_ef_instance.clean_weights.assert_called_once()

# Add more tests for edge cases if necessary

