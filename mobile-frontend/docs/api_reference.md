# API Reference

## Overview

This document provides a comprehensive reference for the RiskOptimizer API endpoints. The API follows RESTful principles and uses JSON for request and response payloads.

## Base URL

- **Development**: `http://localhost:5000/api`
- **Staging**: `https://staging-api.riskoptimizer.com/api`
- **Production**: `https://api.riskoptimizer.com/api`

## Authentication

Most API endpoints require authentication. The API uses JWT (JSON Web Tokens) for authentication.

### Obtaining a Token

```
POST /auth/login
```

**Request Body:**

```json
{
    "email": "user@example.com",
    "password": "your_password"
}
```

**Response:**

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
}
```

### Using the Token

Include the token in the Authorization header for all authenticated requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### User Management

#### Get User Profile

```
GET /users/profile
```

**Response:**

```json
{
    "id": "user123",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00Z",
    "preferences": {
        "risk_tolerance": "moderate",
        "investment_horizon": "long_term"
    }
}
```

#### Update User Profile

```
PUT /users/profile
```

**Request Body:**

```json
{
    "name": "John Smith",
    "preferences": {
        "risk_tolerance": "high",
        "investment_horizon": "medium_term"
    }
}
```

**Response:**

```json
{
    "id": "user123",
    "email": "user@example.com",
    "name": "John Smith",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-04-20T14:25:00Z",
    "preferences": {
        "risk_tolerance": "high",
        "investment_horizon": "medium_term"
    }
}
```

### Portfolio Management

#### List Portfolios

```
GET /portfolios
```

**Response:**

```json
{
    "portfolios": [
        {
            "id": "portfolio123",
            "name": "Retirement Fund",
            "created_at": "2025-02-10T09:15:00Z",
            "total_value": 125000.5,
            "currency": "USD",
            "risk_score": 0.65
        },
        {
            "id": "portfolio456",
            "name": "Growth Investments",
            "created_at": "2025-03-05T14:30:00Z",
            "total_value": 75000.25,
            "currency": "USD",
            "risk_score": 0.82
        }
    ],
    "count": 2
}
```

#### Get Portfolio Details

```
GET /portfolios/{portfolio_id}
```

**Response:**

```json
{
    "id": "portfolio123",
    "name": "Retirement Fund",
    "description": "Long-term retirement investment portfolio",
    "created_at": "2025-02-10T09:15:00Z",
    "updated_at": "2025-04-18T11:20:00Z",
    "total_value": 125000.5,
    "currency": "USD",
    "risk_score": 0.65,
    "assets": [
        {
            "id": "asset123",
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": 50,
            "purchase_price": 150.25,
            "current_price": 175.5,
            "value": 8775.0,
            "allocation_percentage": 7.02,
            "performance": 16.81
        },
        {
            "id": "asset456",
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "quantity": 30,
            "purchase_price": 220.75,
            "current_price": 280.3,
            "value": 8409.0,
            "allocation_percentage": 6.73,
            "performance": 26.98
        }
    ],
    "performance": {
        "daily": 1.2,
        "weekly": 2.5,
        "monthly": 3.8,
        "yearly": 12.5,
        "since_inception": 25.0
    }
}
```

#### Create Portfolio

```
POST /portfolios
```

**Request Body:**

```json
{
    "name": "Tech Investments",
    "description": "Portfolio focused on technology sector",
    "currency": "USD"
}
```

**Response:**

```json
{
    "id": "portfolio789",
    "name": "Tech Investments",
    "description": "Portfolio focused on technology sector",
    "created_at": "2025-04-25T10:30:00Z",
    "total_value": 0.0,
    "currency": "USD",
    "risk_score": 0.0,
    "assets": []
}
```

#### Add Asset to Portfolio

```
POST /portfolios/{portfolio_id}/assets
```

**Request Body:**

```json
{
    "symbol": "GOOGL",
    "quantity": 10,
    "purchase_price": 2750.5,
    "purchase_date": "2025-04-20T00:00:00Z"
}
```

**Response:**

```json
{
    "id": "asset789",
    "symbol": "GOOGL",
    "name": "Alphabet Inc.",
    "quantity": 10,
    "purchase_price": 2750.5,
    "current_price": 2800.25,
    "value": 28002.5,
    "allocation_percentage": 22.4,
    "performance": 1.81,
    "purchase_date": "2025-04-20T00:00:00Z"
}
```

### Optimization

#### Get Optimization Recommendations

```
POST /optimization/recommendations
```

**Request Body:**

```json
{
    "portfolio_id": "portfolio123",
    "risk_tolerance": "moderate",
    "investment_horizon": "long_term",
    "constraints": {
        "max_allocation_per_asset": 0.2,
        "min_allocation_per_asset": 0.05,
        "excluded_sectors": ["Energy", "Tobacco"]
    }
}
```

**Response:**

```json
{
    "portfolio_id": "portfolio123",
    "current_risk_score": 0.65,
    "optimized_risk_score": 0.58,
    "expected_return": 0.12,
    "sharpe_ratio": 1.8,
    "recommendations": [
        {
            "symbol": "AAPL",
            "current_allocation": 0.0702,
            "recommended_allocation": 0.1,
            "action": "buy",
            "quantity_change": 15
        },
        {
            "symbol": "MSFT",
            "current_allocation": 0.0673,
            "recommended_allocation": 0.08,
            "action": "buy",
            "quantity_change": 5
        },
        {
            "symbol": "XOM",
            "current_allocation": 0.05,
            "recommended_allocation": 0.0,
            "action": "sell",
            "quantity_change": -25
        }
    ],
    "efficient_frontier": [
        { "risk": 0.2, "return": 0.05 },
        { "risk": 0.3, "return": 0.07 },
        { "risk": 0.4, "return": 0.09 },
        { "risk": 0.5, "return": 0.11 },
        { "risk": 0.6, "return": 0.13 },
        { "risk": 0.7, "return": 0.15 },
        { "risk": 0.8, "return": 0.18 }
    ]
}
```

### Risk Analysis

#### Get Risk Metrics

```
GET /risk/metrics/{portfolio_id}
```

**Response:**

```json
{
    "portfolio_id": "portfolio123",
    "volatility": 0.15,
    "sharpe_ratio": 1.8,
    "sortino_ratio": 2.1,
    "max_drawdown": 0.12,
    "var_95": 0.08,
    "var_99": 0.12,
    "beta": 1.05,
    "alpha": 0.02,
    "r_squared": 0.85,
    "risk_contribution": [
        { "symbol": "AAPL", "contribution": 0.25 },
        { "symbol": "MSFT", "contribution": 0.2 },
        { "symbol": "AMZN", "contribution": 0.3 },
        { "symbol": "BND", "contribution": 0.1 },
        { "symbol": "VTI", "contribution": 0.15 }
    ]
}
```

### Blockchain Integration

#### Get Transaction History

```
GET /blockchain/transactions/{portfolio_id}
```

**Response:**

```json
{
    "portfolio_id": "portfolio123",
    "transactions": [
        {
            "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "block_number": 12345678,
            "timestamp": "2025-04-10T15:30:00Z",
            "action": "buy",
            "symbol": "AAPL",
            "quantity": 10,
            "price": 175.5,
            "value": 1755.0,
            "status": "confirmed"
        },
        {
            "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "block_number": 12345680,
            "timestamp": "2025-04-15T09:45:00Z",
            "action": "sell",
            "symbol": "MSFT",
            "quantity": 5,
            "price": 280.3,
            "value": 1401.5,
            "status": "confirmed"
        }
    ],
    "count": 2
}
```

#### Verify Portfolio Integrity

```
GET /blockchain/verify/{portfolio_id}
```

**Response:**

```json
{
    "portfolio_id": "portfolio123",
    "verified": true,
    "last_verification": "2025-04-25T10:15:00Z",
    "blockchain": "Ethereum",
    "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
    "merkle_root": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
}
```

### Market Data

#### Get Asset Price History

```
GET /market/history/{symbol}?period=1y&interval=1d
```

**Parameters:**

- `period`: Time period (1d, 1w, 1m, 3m, 6m, 1y, 5y)
- `interval`: Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1w)

**Response:**

```json
{
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "period": "1y",
    "interval": "1d",
    "currency": "USD",
    "data": [
        {
            "timestamp": "2024-04-25T00:00:00Z",
            "open": 170.5,
            "high": 175.25,
            "low": 169.75,
            "close": 173.5,
            "volume": 75000000
        },
        {
            "timestamp": "2024-04-26T00:00:00Z",
            "open": 173.75,
            "high": 176.5,
            "low": 172.25,
            "close": 175.0,
            "volume": 68000000
        },
        // Additional data points...
        {
            "timestamp": "2025-04-24T00:00:00Z",
            "open": 174.25,
            "high": 178.5,
            "low": 173.75,
            "close": 177.5,
            "volume": 82000000
        }
    ],
    "summary": {
        "change_percentage": 4.11,
        "high": 190.25,
        "low": 140.75,
        "average": 165.3
    }
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests.

### Common Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Request validation failed
- `500 Internal Server Error`: Server-side error

### Error Response Format

```json
{
    "error": {
        "code": "invalid_parameters",
        "message": "One or more parameters are invalid",
        "details": [
            {
                "field": "risk_tolerance",
                "message": "Must be one of: low, moderate, high"
            }
        ]
    }
}
```

## Rate Limiting

API requests are subject to rate limiting to ensure fair usage and system stability.

- Standard users: 100 requests per minute
- Premium users: 500 requests per minute

Rate limit information is included in the response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1619355600
```

## Versioning

The API is versioned to ensure backward compatibility. The current version is v1.

To specify a version, include it in the URL path:

```
https://api.riskoptimizer.com/api/v1/portfolios
```

## Webhooks

The API supports webhooks for real-time notifications of events.

### Available Events

- `portfolio.created`
- `portfolio.updated`
- `asset.added`
- `asset.removed`
- `transaction.confirmed`
- `optimization.completed`

### Webhook Configuration

```
POST /webhooks
```

**Request Body:**

```json
{
    "url": "https://your-server.com/webhook",
    "events": ["portfolio.created", "transaction.confirmed"],
    "secret": "your_webhook_secret"
}
```

**Response:**

```json
{
    "id": "webhook123",
    "url": "https://your-server.com/webhook",
    "events": ["portfolio.created", "transaction.confirmed"],
    "created_at": "2025-04-25T10:30:00Z",
    "status": "active"
}
```
