// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PortfolioLedger {
    // Define the structure for a transaction log
    struct Transaction {
        uint256 timestamp;
        address indexed userAddress;
        string transactionType; // e.g., "BUY", "SELL", "REBALANCE"
        string assetTicker;
        uint256 quantity;
        uint256 price;
        string notes;
    }

    // Array to store all transactions
    Transaction[] public transactions;

    // Event to log when a new transaction is recorded
    event TransactionLogged(
        uint256 indexed transactionId,
        address indexed userAddress,
        string transactionType,
        string assetTicker,
        uint256 quantity
    );

    // Function to record a new transaction
    function recordTransaction(
        address _userAddress,
        string memory _transactionType,
        string memory _assetTicker,
        uint256 _quantity,
        uint256 _price,
        string memory _notes
    ) public {
        // Add the new transaction to the array
        transactions.push(
            Transaction(
                block.timestamp,
                _userAddress,
                _transactionType,
                _assetTicker,
                _quantity,
                _price,
                _notes
            )
        );

        // Emit an event for easy off-chain indexing
        emit TransactionLogged(
            transactions.length - 1,
            _userAddress,
            _transactionType,
            _assetTicker,
            _quantity
        );
    }

    // Function to get the total number of transactions
    function getTransactionCount() public view returns (uint256) {
        return transactions.length;
    }
}
