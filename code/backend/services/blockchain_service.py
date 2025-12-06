"""
Blockchain Integration Service for RiskOptimizer Backend

This service provides integration with blockchain smart contracts for:
1. Portfolio tracking on the blockchain
2. Risk management calculations
3. Transaction handling and verification
4. Multi-chain support for portfolio diversification

It connects the backend API with Ethereum and other blockchain networks.
"""

import json
import os

# Load environment variables
from dotenv import load_dotenv
from eth_account import Account
from web3 import HTTPProvider, Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

from core.logging import get_logger

logger = get_logger(__name__)

load_dotenv()

# Contract ABIs
PORTFOLIO_TRACKER_ABI = json.loads(
    """
[
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "string",
          "name": "asset",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "newAllocation",
          "type": "uint256"
        }
      ],
      "name": "AssetRebalanced",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        }
      ],
      "name": "PortfolioUpdated",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "user",
          "type": "address"
        }
      ],
      "name": "getPortfolio",
      "outputs": [
        {
          "internalType": "string[]",
          "name": "",
          "type": "string[]"
        },
        {
          "internalType": "uint256[]",
          "name": "",
          "type": "uint256[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "portfolios",
      "outputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string[]",
          "name": "_assets",
          "type": "string[]"
        },
        {
          "internalType": "uint256[]",
          "name": "_allocations",
          "type": "uint256[]"
        }
      ],
      "name": "updatePortfolio",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
]
"""
)

RISK_MANAGEMENT_ABI = json.loads(
    """
[
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_priceFeed",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "lookbackDays",
          "type": "uint256"
        }
      ],
      "name": "calculateVolatility",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
]
"""
)

# Default contract addresses (these would be environment variables in production)
DEFAULT_PORTFOLIO_TRACKER_ADDRESS = os.getenv(
    "PORTFOLIO_TRACKER_ADDRESS", "0x1234567890123456789012345678901234567890"
)
DEFAULT_RISK_MANAGEMENT_ADDRESS = os.getenv(
    "RISK_MANAGEMENT_ADDRESS", "0x0987654321098765432109876543210987654321"
)

# Network configurations
NETWORKS = {
    "ethereum": {
        "name": "Ethereum Mainnet",
        "rpc_url": os.getenv(
            "ETH_RPC_URL", "https://mainnet.infura.io/v3/your-infura-key"
        ),
        "chain_id": 1,
        "explorer": "https://etherscan.io",
    },
    "polygon": {
        "name": "Polygon Mainnet",
        "rpc_url": os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
        "chain_id": 137,
        "explorer": "https://polygonscan.com",
    },
    "arbitrum": {
        "name": "Arbitrum One",
        "rpc_url": os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc"),
        "chain_id": 42161,
        "explorer": "https://arbiscan.io",
    },
    "optimism": {
        "name": "Optimism",
        "rpc_url": os.getenv("OPTIMISM_RPC_URL", "https://mainnet.optimism.io"),
        "chain_id": 10,
        "explorer": "https://optimistic.etherscan.io",
    },
    "goerli": {
        "name": "Goerli Testnet",
        "rpc_url": os.getenv(
            "GOERLI_RPC_URL", "https://goerli.infura.io/v3/your-infura-key"
        ),
        "chain_id": 5,
        "explorer": "https://goerli.etherscan.io",
    },
}


class BlockchainService:
    """Service for blockchain integration and smart contract interaction"""

    def __init__(self, network="ethereum"):
        """
        Initialize the blockchain service

        Args:
            network: Network to connect to (default: ethereum)
        """
        self.network = network
        self.network_config = NETWORKS.get(network, NETWORKS["ethereum"])

        # Connect to blockchain
        self.w3 = Web3(HTTPProvider(self.network_config["rpc_url"]))

        # Add middleware for POA networks like Polygon
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Set gas price strategy
        self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)

        # Initialize contract instances
        self.portfolio_tracker = self.w3.eth.contract(
            address=Web3.to_checksum_address(DEFAULT_PORTFOLIO_TRACKER_ADDRESS),
            abi=PORTFOLIO_TRACKER_ABI,
        )

        self.risk_management = self.w3.eth.contract(
            address=Web3.to_checksum_address(DEFAULT_RISK_MANAGEMENT_ADDRESS),
            abi=RISK_MANAGEMENT_ABI,
        )

        # Load private key if available
        self.account = None
        private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
        if private_key:
            self.account = Account.from_key(private_key)

    def is_connected(self):
        """Check if connected to blockchain network"""
        return self.w3.is_connected()

    def get_network_info(self):
        """Get information about the connected network"""
        return {
            "name": self.network_config["name"],
            "chain_id": self.network_config["chain_id"],
            "connected": self.is_connected(),
            "latest_block": self.w3.eth.block_number if self.is_connected() else None,
            "gas_price": self.w3.eth.gas_price if self.is_connected() else None,
        }

    def validate_address(self, address):
        """Validate Ethereum address format"""
        return self.w3.is_address(address)

    def get_portfolio(self, address):
        """
        Get portfolio from blockchain

        Args:
            address: User's Ethereum address

        Returns:
            Dictionary with portfolio data
        """
        if not self.validate_address(address):
            raise ValueError("Invalid Ethereum address")

        try:
            assets, allocations = self.portfolio_tracker.functions.getPortfolio(
                Web3.to_checksum_address(address)
            ).call()

            # Format allocations as percentages
            allocations_pct = [allocation / 10000 for allocation in allocations]

            return {
                "user_address": address,
                "assets": assets,
                "allocations": allocations_pct,
                "source": "blockchain",
                "network": self.network_config["name"],
            }
        except Exception as e:
            logger.info(f"Error getting portfolio from blockchain: {e}")
            return None

    def update_portfolio(self, address, assets, allocations_pct):
        """
        Update portfolio on blockchain

        Args:
            address: User's Ethereum address
            assets: List of asset symbols
            allocations_pct: List of allocation percentages (0-100)

        Returns:
            Transaction hash if successful, None otherwise
        """
        if not self.account:
            raise ValueError("Private key not configured for transaction signing")

        if not self.validate_address(address):
            raise ValueError("Invalid Ethereum address")

        if len(assets) != len(allocations_pct):
            raise ValueError("Assets and allocations must have the same length")

        # Convert percentages to basis points (0-10000)
        allocations_bp = [int(pct * 100) for pct in allocations_pct]

        # Ensure allocations sum to 100%
        if sum(allocations_bp) != 10000:
            raise ValueError("Allocations must sum to 100%")

        try:
            # Build transaction
            tx = self.portfolio_tracker.functions.updatePortfolio(
                assets, allocations_bp
            ).build_transaction(
                {
                    "from": self.account.address,
                    "nonce": self.w3.eth.get_transaction_count(self.account.address),
                    "gas": 2000000,
                    "gasPrice": self.w3.eth.gas_price,
                }
            )

            # Sign transaction
            signed_tx = self.account.sign_transaction(tx)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            return {
                "tx_hash": tx_hash.hex(),
                "status": "success" if receipt.status == 1 else "failed",
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "explorer_url": f"{self.network_config['explorer']}/tx/{tx_hash.hex()}",
            }
        except Exception as e:
            logger.info(f"Error updating portfolio on blockchain: {e}")
            return None

    def calculate_volatility(self, lookback_days=30):
        """
        Calculate market volatility using on-chain risk management contract

        Args:
            lookback_days: Number of days to look back

        Returns:
            Volatility value
        """
        try:
            volatility = self.risk_management.functions.calculateVolatility(
                lookback_days
            ).call()
            return volatility
        except Exception as e:
            logger.info(f"Error calculating volatility on blockchain: {e}")
            return None

    def get_transaction_history(self, address, limit=10):
        """
        Get transaction history for an address

        Args:
            address: User's Ethereum address
            limit: Maximum number of transactions to return

        Returns:
            List of transactions
        """
        if not self.validate_address(address):
            raise ValueError("Invalid Ethereum address")

        try:
            # Get latest block number
            latest_block = self.w3.eth.block_number

            # Get portfolio updated events
            portfolio_filter = (
                self.portfolio_tracker.events.PortfolioUpdated.create_filter(
                    fromBlock=latest_block - 10000,  # Look back 10000 blocks
                    toBlock="latest",
                    argument_filters={"owner": Web3.to_checksum_address(address)},
                )
            )

            events = portfolio_filter.get_all_entries()

            # Format events
            transactions = []
            for event in events[:limit]:
                block = self.w3.eth.get_block(event["blockNumber"])
                tx = self.w3.eth.get_transaction(event["transactionHash"])

                transactions.append(
                    {
                        "tx_hash": event["transactionHash"].hex(),
                        "block_number": event["blockNumber"],
                        "timestamp": block["timestamp"],
                        "event": "PortfolioUpdated",
                        "gas_used": tx["gas"],
                        "explorer_url": f"{self.network_config['explorer']}/tx/{event['transactionHash'].hex()}",
                    }
                )

            return transactions
        except Exception as e:
            logger.info(f"Error getting transaction history: {e}")
            return []

    def get_gas_estimate(self, assets, allocations_pct):
        """
        Estimate gas for portfolio update

        Args:
            assets: List of asset symbols
            allocations_pct: List of allocation percentages (0-100)

        Returns:
            Estimated gas amount
        """
        if not self.account:
            raise ValueError("Private key not configured for transaction signing")

        # Convert percentages to basis points (0-10000)
        allocations_bp = [int(pct * 100) for pct in allocations_pct]

        try:
            gas_estimate = self.portfolio_tracker.functions.updatePortfolio(
                assets, allocations_bp
            ).estimate_gas({"from": self.account.address})

            return gas_estimate
        except Exception as e:
            logger.info(f"Error estimating gas: {e}")
            return None

    def switch_network(self, network):
        """
        Switch to a different blockchain network

        Args:
            network: Network name

        Returns:
            True if successful, False otherwise
        """
        if network not in NETWORKS:
            raise ValueError(f"Unsupported network: {network}")

        try:
            self.network = network
            self.network_config = NETWORKS[network]

            # Connect to new network
            self.w3 = Web3(HTTPProvider(self.network_config["rpc_url"]))

            # Add middleware for POA networks
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Set gas price strategy
            self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)

            # Reinitialize contract instances with new network
            self.portfolio_tracker = self.w3.eth.contract(
                address=Web3.to_checksum_address(DEFAULT_PORTFOLIO_TRACKER_ADDRESS),
                abi=PORTFOLIO_TRACKER_ABI,
            )

            self.risk_management = self.w3.eth.contract(
                address=Web3.to_checksum_address(DEFAULT_RISK_MANAGEMENT_ADDRESS),
                abi=RISK_MANAGEMENT_ABI,
            )

            return self.is_connected()
        except Exception as e:
            logger.info(f"Error switching network: {e}")
            return False

    def get_supported_networks(self):
        """Get list of supported blockchain networks"""
        return {
            network: {
                "name": config["name"],
                "chain_id": config["chain_id"],
                "explorer": config["explorer"],
            }
            for network, config in NETWORKS.items()
        }


# Create singleton instance
blockchain_service = BlockchainService(
    network=os.getenv("DEFAULT_BLOCKCHAIN_NETWORK", "ethereum")
)
