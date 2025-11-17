"""
Portfolio Tracking Tests for RiskOptimizer

This module contains automated tests for the portfolio tracking functionality,
including both backend database operations and blockchain integration.
"""

import json
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
# Import services to test
from services.ai_optimization import (AIOptimizationService,
                                      optimization_service)
from services.blockchain_service import BlockchainService


class TestPortfolioTracking:
    """Test suite for portfolio tracking functionality"""

    @pytest.fixture
    def sample_portfolio(self):
        """Sample portfolio data for testing"""
        return {
            "user_address": "0x1234567890123456789012345678901234567890",
            "assets": ["BTC", "ETH", "AAPL", "MSFT", "GOOGL"],
            "allocations": [0.25, 0.25, 0.20, 0.15, 0.15],
        }

    @pytest.fixture
    def sample_market_data(self):
        """Sample market data for testing"""
        # Create synthetic data
        dates = pd.date_range(start="2022-01-01", end="2023-01-01", freq="B")
        assets = ["BTC", "ETH", "AAPL", "MSFT", "GOOGL", "market_index"]

        np.random.seed(42)
        data = pd.DataFrame(index=dates)

        for asset in assets:
            # Generate random price series
            volatility = 0.03 if asset in ["BTC", "ETH"] else 0.015
            returns = np.random.normal(0.0005, volatility, size=len(dates))
            prices = 100 * np.cumprod(1 + returns)
            data[asset] = prices

        return data

    def test_portfolio_optimization(self, sample_market_data):
        """Test portfolio optimization with AI models"""
        # Initialize optimization service
        optimizer = AIOptimizationService()

        # Set risk tolerance
        risk_tolerance = 5
        optimizer.optimizer.risk_tolerance = risk_tolerance

        # Run optimization
        result = optimizer.optimize_portfolio(sample_market_data, risk_tolerance)

        # Verify result structure
        assert "optimized_allocation" in result
        assert "performance_metrics" in result
        assert "expected_return" in result["performance_metrics"]
        assert "volatility" in result["performance_metrics"]
        assert "sharpe_ratio" in result["performance_metrics"]

        # Verify allocations sum to approximately 1
        allocations = result["optimized_allocation"]
        assert sum(allocations.values()) > 0.99
        assert sum(allocations.values()) < 1.01

        # Verify all assets have allocations
        for asset in sample_market_data.columns:
            if asset != "market_index":
                assert asset in allocations

    def test_risk_simulation(self, sample_market_data, sample_portfolio):
        """Test Monte Carlo risk simulation"""
        # Initialize optimization service
        optimizer = AIOptimizationService()

        # Create portfolio weights dictionary
        weights = {
            asset: alloc
            for asset, alloc in zip(
                sample_portfolio["assets"], sample_portfolio["allocations"]
            )
        }

        # Run simulation
        result = optimizer.run_risk_simulation(sample_market_data, weights)

        # Verify result structure
        assert "risk_metrics" in result
        assert "simulation_summary" in result
        assert "expected_final_value" in result["risk_metrics"]
        assert "value_at_risk_95" in result["risk_metrics"]
        assert "value_at_risk_99" in result["risk_metrics"]
        assert "max_drawdown" in result["risk_metrics"]

        # Verify simulation summary
        assert "initial_value" in result["simulation_summary"]
        assert "percentiles" in result["simulation_summary"]
        assert "p50" in result["simulation_summary"]["percentiles"]

        # Verify risk metrics are reasonable
        assert result["risk_metrics"]["expected_final_value"] > 0
        assert result["risk_metrics"]["value_at_risk_95"] > 0
        assert result["risk_metrics"]["value_at_risk_99"] > 0
        assert 0 <= result["risk_metrics"]["max_drawdown"] <= 1

    @patch("services.blockchain_service.Web3")
    def test_blockchain_portfolio_retrieval(self, mock_web3, sample_portfolio):
        """Test portfolio retrieval from blockchain"""
        # Mock Web3 and contract functions
        mock_contract = MagicMock()
        mock_contract.functions.getPortfolio.return_value.call.return_value = (
            sample_portfolio["assets"],
            [
                int(alloc * 10000) for alloc in sample_portfolio["allocations"]
            ],  # Convert to basis points
        )

        mock_web3.return_value.eth.contract.return_value = mock_contract
        mock_web3.return_value.is_connected.return_value = True
        mock_web3.return_value.is_address.return_value = True
        mock_web3.to_checksum_address = lambda x: x

        # Initialize blockchain service with mocked Web3
        service = BlockchainService()

        # Get portfolio
        result = service.get_portfolio(sample_portfolio["user_address"])

        # Verify result
        assert result is not None
        assert result["user_address"] == sample_portfolio["user_address"]
        assert result["assets"] == sample_portfolio["assets"]

        # Verify allocations (allowing for small floating point differences)
        for i, alloc in enumerate(result["allocations"]):
            assert abs(alloc - sample_portfolio["allocations"][i]) < 0.0001

    @patch("services.blockchain_service.Web3")
    def test_blockchain_portfolio_update(self, mock_web3, sample_portfolio):
        """Test portfolio update on blockchain"""
        # Mock Web3 and contract functions
        mock_contract = MagicMock()
        mock_tx_hash = MagicMock()
        mock_tx_hash.hex.return_value = "0xabcdef1234567890"

        mock_receipt = MagicMock()
        mock_receipt.status = 1
        mock_receipt.blockNumber = 12345
        mock_receipt.gasUsed = 100000

        mock_web3.return_value.eth.send_raw_transaction.return_value = mock_tx_hash
        mock_web3.return_value.eth.wait_for_transaction_receipt.return_value = (
            mock_receipt
        )
        mock_web3.return_value.eth.contract.return_value = mock_contract
        mock_web3.return_value.is_connected.return_value = True
        mock_web3.return_value.is_address.return_value = True
        mock_web3.to_checksum_address = lambda x: x

        # Mock account for transaction signing
        mock_account = MagicMock()
        mock_account.address = sample_portfolio["user_address"]

        # Initialize blockchain service with mocked Web3
        service = BlockchainService()
        service.account = mock_account

        # Update portfolio
        result = service.update_portfolio(
            sample_portfolio["user_address"],
            sample_portfolio["assets"],
            sample_portfolio["allocations"],
        )

        # Verify result
        assert result is not None
        assert result["tx_hash"] == "0xabcdef1234567890"
        assert result["status"] == "success"
        assert result["block_number"] == 12345
        assert result["gas_used"] == 100000

    def test_portfolio_optimization_with_risk_tolerance(self, sample_market_data):
        """Test portfolio optimization with different risk tolerance levels"""
        # Initialize optimization service
        optimizer = AIOptimizationService()

        # Test with low risk tolerance
        low_risk_result = optimizer.optimize_portfolio(sample_market_data, 2)

        # Test with high risk tolerance
        high_risk_result = optimizer.optimize_portfolio(sample_market_data, 8)

        # Verify risk-return tradeoff
        # Higher risk tolerance should lead to higher expected return and volatility
        assert (
            high_risk_result["performance_metrics"]["expected_return"]
            >= low_risk_result["performance_metrics"]["expected_return"]
        )
        assert (
            high_risk_result["performance_metrics"]["volatility"]
            >= low_risk_result["performance_metrics"]["volatility"]
        )

    @patch("services.blockchain_service.Web3")
    def test_multi_network_support(self, mock_web3):
        """Test blockchain service with multiple networks"""
        # Mock Web3
        mock_web3.return_value.is_connected.return_value = True

        # Initialize blockchain service
        service = BlockchainService(network="ethereum")

        # Get supported networks
        networks = service.get_supported_networks()

        # Verify networks
        assert "ethereum" in networks
        assert "polygon" in networks
        assert "goerli" in networks

        # Test network switching
        mock_web3.return_value.is_connected.return_value = True
        result = service.switch_network("polygon")
        assert result is True
        assert service.network == "polygon"

    def test_integrated_portfolio_optimization_and_tracking(
        self, sample_market_data, sample_portfolio
    ):
        """Test integration between AI optimization and blockchain tracking"""
        # Initialize services
        ai_service = AIOptimizationService()

        # Mock blockchain service
        blockchain_service = MagicMock()
        blockchain_service.update_portfolio.return_value = {
            "tx_hash": "0xabcdef1234567890",
            "status": "success",
        }

        # Run optimization
        optimization_result = ai_service.optimize_portfolio(sample_market_data, 5)

        # Extract optimized allocation
        optimized_weights = optimization_result["optimized_allocation"]
        assets = list(optimized_weights.keys())
        allocations = list(optimized_weights.values())

        # Update portfolio on blockchain
        blockchain_result = blockchain_service.update_portfolio(
            sample_portfolio["user_address"], assets, allocations
        )

        # Verify blockchain update was called with optimized portfolio
        blockchain_service.update_portfolio.assert_called_once()
        assert blockchain_result["status"] == "success"

        # Verify integration flow works end-to-end
        assert len(assets) > 0
        assert len(allocations) > 0
        assert sum(allocations) > 0.99
        assert sum(allocations) < 1.01
