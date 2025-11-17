import json
import os

from web3 import Web3

# --- Configuration and Mock Data ---

# Mock Ganache/local Ethereum node URL
GANACHE_URL = "http://127.0.0.1:8545"

# Mock Contract Address (This would be the address after deployment)
MOCK_CONTRACT_ADDRESS = "0x9fE46736679d2D9a65F0992F2272E2fA8C57Bf70"

# Mock ABI (Simplified for demonstration)
MOCK_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "_userAddress", "type": "address"},
            {"internalType": "string", "name": "_transactionType", "type": "string"},
            {"internalType": "string", "name": "_assetTicker", "type": "string"},
            {"internalType": "uint256", "name": "_quantity", "type": "uint256"},
            {"internalType": "uint256", "name": "_price", "type": "uint256"},
            {"internalType": "string", "name": "_notes", "type": "string"},
        ],
        "name": "recordTransaction",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getTransactionCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# --- Web3 Integration Functions ---


def get_web3_instance():
    """Initializes and returns a Web3 instance connected to the mock node."""
    try:
        w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

        if w3.is_connected():
            print(f"Successfully connected to Ethereum node at {GANACHE_URL}")
            return w3
        else:
            print(f"Failed to connect to Ethereum node at {GANACHE_URL}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None


def record_trade_on_blockchain(
    w3: Web3,
    user_address: str,
    tx_type: str,
    ticker: str,
    quantity: float,
    price: float,
    notes: str,
):
    """
    Records a trade or rebalancing event on the mock blockchain ledger.
    """
    if not w3:
        print("Cannot record transaction: Web3 connection failed.")
        return

    # Convert float to integer for Solidity (e.g., using 18 decimal places)
    quantity_wei = w3.to_wei(quantity, "ether")
    price_wei = w3.to_wei(price, "ether")

    # Get the contract instance
    contract = w3.eth.contract(address=MOCK_CONTRACT_ADDRESS, abi=MOCK_ABI)

    # Mock transaction parameters
    # In a real scenario, the user_address would be the sender and would need to sign the transaction.
    # For this mock, we use the first available account as the sender (deployer/operator).
    try:
        sender_account = w3.eth.accounts[0]
    except IndexError:
        print(
            "Error: No accounts found. Ensure your local node (e.g., Ganache) is running."
        )
        return

    print(f"\nRecording transaction from {sender_account}...")

    # Build the transaction
    tx = contract.functions.recordTransaction(
        user_address, tx_type, ticker, quantity_wei, price_wei, notes
    ).build_transaction(
        {
            "from": sender_account,
            "nonce": w3.eth.get_transaction_count(sender_account),
            "gas": 2000000,  # High gas limit for safety in mock
        }
    )

    # Mock sending and waiting for transaction receipt
    # In a real scenario, this would be signed and sent. Here we just print the mock call.
    print(f"Mock Transaction Built (would be sent to the network):")
    print(
        f"  Function: recordTransaction('{user_address}', '{tx_type}', '{ticker}', {quantity_wei}, {price_wei}, '{notes}')"
    )

    # Mock successful transaction hash
    mock_tx_hash = "0x" + os.urandom(32).hex()
    print(f"  Mock Transaction Hash: {mock_tx_hash}")

    # Mock confirmation
    print("Transaction successfully recorded on the mock blockchain.")


def get_ledger_count(w3: Web3):
    """Retrieves the total number of transactions recorded."""
    if not w3:
        return 0

    contract = w3.eth.contract(address=MOCK_CONTRACT_ADDRESS, abi=MOCK_ABI)

    # Mock call to a view function
    try:
        count = contract.functions.getTransactionCount().call()
        print(f"Total transactions on the mock ledger: {count}")
        return count
    except Exception as e:
        print(f"Mock call failed (ensure mock contract is deployed): {e}")
        # Return a mock count if the call fails
        return 3  # Mocking 3 existing transactions


def run_blockchain_integration():
    """Main function to run the blockchain integration components."""
    print("Starting Blockchain Integration Service (Mocking local node connection)...")

    w3 = get_web3_instance()

    # Mock User ID (Decentralized Identity Placeholder)
    # In a real system, this would be a DID or a wallet address derived from a decentralized identity protocol.
    mock_user_did = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

    # 1. Check existing count
    initial_count = get_ledger_count(w3)

    # 2. Record a mock rebalancing event
    record_trade_on_blockchain(
        w3,
        user_address=mock_user_did,
        tx_type="REBALANCE",
        ticker="MSFT",
        quantity=50.0,
        price=450.0,
        notes="Rebalance to Max Sharpe weights.",
    )

    # 3. Check new count (mocked)
    print(f"\nMock ledger count after recording: {initial_count + 1}")

    print("\nBlockchain Integration Service finished.")


if __name__ == "__main__":
    run_blockchain_integration()
