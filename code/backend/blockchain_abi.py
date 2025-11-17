# PortfolioTracker ABI
PORTFOLIO_TRACKER_ABI = [
    {
        "inputs": [
            {"internalType": "string[]", "name": "_assets", "type": "string[]"},
            {"internalType": "uint256[]", "name": "_allocations", "type": "uint256[]"},
        ],
        "name": "updatePortfolio",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "getPortfolio",
        "outputs": [
            {"internalType": "string[]", "name": "", "type": "string[]"},
            {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            }
        ],
        "name": "PortfolioUpdated",
        "type": "event",
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            },
            {
                "indexed": false,
                "internalType": "string",
                "name": "asset",
                "type": "string",
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "newAllocation",
                "type": "uint256",
            },
        ],
        "name": "AssetRebalanced",
        "type": "event",
    },
]

# RiskManagement ABI
RISK_MANAGEMENT_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "getRiskProfile",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    }
]
