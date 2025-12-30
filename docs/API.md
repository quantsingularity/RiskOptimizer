# API Reference

Complete API reference for RiskOptimizer v1.0.0.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
    - [Authentication](#authentication-endpoints)
    - [Risk Calculations](#risk-calculation-endpoints)
    - [Portfolio Management](#portfolio-management-endpoints)
    - [Monitoring](#monitoring-endpoints)

## Base URL

```
Development: http://localhost:5000
Production: https://api.riskoptimizer.io
```

All API endpoints are versioned and prefixed with `/api/v1`.

## Authentication

RiskOptimizer uses JWT (JSON Web Token) based authentication.

### Authentication Flow

1. Register or login to obtain tokens
2. Include access token in `Authorization` header
3. Refresh token before expiry
4. Logout to invalidate tokens

### Headers

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

## Response Format

### Success Response

```json
{
    "status": "success",
    "message": "Optional success message",
    "data": {},
    "meta": {}
}
```

### Error Response

```json
{
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message",
        "field": "field_name",
        "details": {}
    }
}
```

## Error Handling

| HTTP Code | Error Type            | Description                       |
| --------- | --------------------- | --------------------------------- |
| 400       | Bad Request           | Invalid request data              |
| 401       | Unauthorized          | Missing or invalid authentication |
| 403       | Forbidden             | Insufficient permissions          |
| 404       | Not Found             | Resource not found                |
| 422       | Validation Error      | Data validation failed            |
| 429       | Too Many Requests     | Rate limit exceeded               |
| 500       | Internal Server Error | Server-side error                 |
| 503       | Service Unavailable   | Service temporarily unavailable   |

## Rate Limiting

**Default Limits:**

- 60 requests per minute per IP
- 1000 requests per hour per authenticated user

**Headers:**

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

## Endpoints

### Authentication Endpoints

#### Register User

| Method | Path                    | Description                 | Auth required |
| ------ | ----------------------- | --------------------------- | ------------- |
| POST   | `/api/v1/auth/register` | Register a new user account | No            |

**Request Body:**

| Name           | Type   | Required? | Default | Description                                                          | Example                                   |
| -------------- | ------ | --------- | ------- | -------------------------------------------------------------------- | ----------------------------------------- |
| email          | string | Yes       | -       | User's email address                                                 | user@example.com                          |
| username       | string | Yes       | -       | Unique username                                                      | john_doe                                  |
| password       | string | Yes       | -       | Password (min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special) | SecureP@ss123                             |
| wallet_address | string | No        | null    | Optional blockchain wallet                                           | 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb |

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "SecureP@ss123"
  }'
```

**Example Response:**

```json
{
    "status": "success",
    "message": "User registered successfully",
    "data": {
        "user_id": 1,
        "email": "user@example.com",
        "username": "john_doe",
        "created_at": "2025-01-01T00:00:00Z"
    }
}
```

---

#### Login

| Method | Path                 | Description                     | Auth required |
| ------ | -------------------- | ------------------------------- | ------------- |
| POST   | `/api/v1/auth/login` | Authenticate and receive tokens | No            |

**Request Body:**

| Name     | Type   | Required? | Default | Description     | Example          |
| -------- | ------ | --------- | ------- | --------------- | ---------------- |
| email    | string | Yes       | -       | User's email    | user@example.com |
| password | string | Yes       | -       | User's password | SecureP@ss123    |

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecureP@ss123"
  }'
```

**Example Response:**

```json
{
    "status": "success",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "expires_in": 3600,
        "token_type": "Bearer",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "john_doe"
        }
    }
}
```

---

#### Refresh Token

| Method | Path                   | Description          | Auth required               |
| ------ | ---------------------- | -------------------- | --------------------------- |
| POST   | `/api/v1/auth/refresh` | Refresh access token | No (requires refresh token) |

**Request Body:**

| Name          | Type   | Required? | Default | Description                    | Example                    |
| ------------- | ------ | --------- | ------- | ------------------------------ | -------------------------- |
| refresh_token | string | Yes       | -       | Valid refresh token from login | eyJ0eXAiOiJKV1QiLCJhbGc... |

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

---

#### Logout

| Method | Path                  | Description                 | Auth required |
| ------ | --------------------- | --------------------------- | ------------- |
| POST   | `/api/v1/auth/logout` | Logout and blacklist tokens | Yes           |

**Request Body:**

| Name          | Type   | Required? | Default | Description                | Example                    |
| ------------- | ------ | --------- | ------- | -------------------------- | -------------------------- |
| refresh_token | string | Yes       | -       | Refresh token to blacklist | eyJ0eXAiOiJKV1QiLCJhbGc... |

---

### Risk Calculation Endpoints

#### Calculate VaR

| Method | Path               | Description             | Auth required |
| ------ | ------------------ | ----------------------- | ------------- |
| POST   | `/api/v1/risk/var` | Calculate Value at Risk | Yes           |

**Request Body:**

| Name       | Type         | Required? | Default | Description                | Example                     |
| ---------- | ------------ | --------- | ------- | -------------------------- | --------------------------- |
| returns    | array[float] | Yes       | -       | List of historical returns | [-0.02, 0.01, -0.015, 0.03] |
| confidence | float        | No        | 0.95    | Confidence level (0-1)     | 0.95                        |

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/risk/var \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "returns": [-0.02, 0.01, -0.015, 0.03, -0.01],
    "confidence": 0.95
  }'
```

**Example Response:**

```json
{
    "status": "success",
    "data": {
        "var": -0.0234,
        "confidence": 0.95,
        "interpretation": "At 95% confidence, max expected loss is 2.34%"
    }
}
```

---

#### Calculate CVaR

| Method | Path                | Description               | Auth required |
| ------ | ------------------- | ------------------------- | ------------- |
| POST   | `/api/v1/risk/cvar` | Calculate Conditional VaR | Yes           |

**Request Body:**

| Name       | Type         | Required? | Default | Description                | Example               |
| ---------- | ------------ | --------- | ------- | -------------------------- | --------------------- |
| returns    | array[float] | Yes       | -       | List of historical returns | [-0.02, 0.01, -0.015] |
| confidence | float        | No        | 0.95    | Confidence level (0-1)     | 0.95                  |

---

#### Calculate Sharpe Ratio

| Method | Path                        | Description            | Auth required |
| ------ | --------------------------- | ---------------------- | ------------- |
| POST   | `/api/v1/risk/sharpe-ratio` | Calculate Sharpe ratio | Yes           |

**Request Body:**

| Name           | Type         | Required? | Default | Description           | Example             |
| -------------- | ------------ | --------- | ------- | --------------------- | ------------------- |
| returns        | array[float] | Yes       | -       | List of returns       | [0.01, 0.02, 0.015] |
| risk_free_rate | float        | No        | 0.02    | Annual risk-free rate | 0.02                |

---

#### Calculate Maximum Drawdown

| Method | Path                        | Description            | Auth required |
| ------ | --------------------------- | ---------------------- | ------------- |
| POST   | `/api/v1/risk/max-drawdown` | Calculate max drawdown | Yes           |

**Request Body:**

| Name    | Type         | Required? | Default | Description     | Example              |
| ------- | ------------ | --------- | ------- | --------------- | -------------------- |
| returns | array[float] | Yes       | -       | List of returns | [0.01, -0.02, -0.01] |

---

#### Calculate Risk Metrics

| Method | Path                   | Description                          | Auth required |
| ------ | ---------------------- | ------------------------------------ | ------------- |
| POST   | `/api/v1/risk/metrics` | Calculate comprehensive risk metrics | Yes           |

**Request Body:**

| Name           | Type         | Required? | Default | Description      | Example             |
| -------------- | ------------ | --------- | ------- | ---------------- | ------------------- |
| returns        | array[float] | Yes       | -       | List of returns  | [0.01, 0.02, -0.01] |
| confidence     | float        | No        | 0.95    | Confidence level | 0.95                |
| risk_free_rate | float        | No        | 0.02    | Risk-free rate   | 0.02                |

**Example Response:**

```json
{
    "status": "success",
    "data": {
        "var": -0.0234,
        "cvar": -0.0267,
        "sharpe_ratio": 1.25,
        "max_drawdown": -0.089,
        "volatility": 0.048,
        "mean_return": 0.015
    }
}
```

---

#### Calculate Efficient Frontier

| Method | Path                              | Description                         | Auth required |
| ------ | --------------------------------- | ----------------------------------- | ------------- |
| POST   | `/api/v1/risk/efficient-frontier` | Calculate efficient frontier points | Yes           |

**Request Body:**

| Name           | Type    | Required? | Default | Description                | Example                                       |
| -------------- | ------- | --------- | ------- | -------------------------- | --------------------------------------------- |
| returns        | object  | Yes       | -       | Asset returns (dict)       | {"AAPL": [0.01, 0.02], "MSFT": [0.015, 0.01]} |
| num_portfolios | integer | No        | 100     | Number of portfolio points | 100                                           |

---

### Portfolio Management Endpoints

#### Create Portfolio

| Method | Path                | Description            | Auth required |
| ------ | ------------------- | ---------------------- | ------------- |
| POST   | `/api/v1/portfolio` | Create a new portfolio | Yes           |

**Request Body:**

| Name        | Type          | Required? | Default | Description           | Example                              |
| ----------- | ------------- | --------- | ------- | --------------------- | ------------------------------------ |
| name        | string        | Yes       | -       | Portfolio name        | "My Tech Portfolio"                  |
| description | string        | No        | null    | Portfolio description | "Tech stocks"                        |
| assets      | array[object] | Yes       | -       | List of assets        | [{"symbol": "AAPL", "quantity": 10}] |

---

#### Get Portfolio

| Method | Path                               | Description           | Auth required |
| ------ | ---------------------------------- | --------------------- | ------------- |
| GET    | `/api/v1/portfolio/user/{user_id}` | Get user's portfolios | Yes           |

**Path Parameters:**

| Name    | Type    | Required? | Description | Example |
| ------- | ------- | --------- | ----------- | ------- |
| user_id | integer | Yes       | User ID     | 1       |

---

#### Update Portfolio

| Method | Path                               | Description      | Auth required |
| ------ | ---------------------------------- | ---------------- | ------------- |
| PUT    | `/api/v1/portfolio/{portfolio_id}` | Update portfolio | Yes           |

**Path Parameters:**

| Name         | Type    | Required? | Description  | Example |
| ------------ | ------- | --------- | ------------ | ------- |
| portfolio_id | integer | Yes       | Portfolio ID | 1       |

---

#### Delete Portfolio

| Method | Path                               | Description      | Auth required |
| ------ | ---------------------------------- | ---------------- | ------------- |
| DELETE | `/api/v1/portfolio/{portfolio_id}` | Delete portfolio | Yes           |

---

#### Get Blockchain Portfolio

| Method | Path                                       | Description                   | Auth required |
| ------ | ------------------------------------------ | ----------------------------- | ------------- |
| GET    | `/api/v1/portfolio/address/{user_address}` | Get portfolio from blockchain | Yes           |

**Path Parameters:**

| Name         | Type   | Required? | Description    | Example       |
| ------------ | ------ | --------- | -------------- | ------------- |
| user_address | string | Yes       | Wallet address | 0x742d35Cc... |

---

### Monitoring Endpoints

#### Get Performance Metrics

| Method | Path                             | Description                    | Auth required |
| ------ | -------------------------------- | ------------------------------ | ------------- |
| GET    | `/api/v1/monitoring/performance` | Get system performance metrics | Yes (Admin)   |

---

#### Get Endpoint Statistics

| Method | Path                           | Description                    | Auth required |
| ------ | ------------------------------ | ------------------------------ | ------------- |
| GET    | `/api/v1/monitoring/endpoints` | Get endpoint performance stats | Yes (Admin)   |

---

#### Optimize Portfolio

| Method | Path                          | Description                   | Auth required |
| ------ | ----------------------------- | ----------------------------- | ------------- |
| POST   | `/api/v1/monitoring/optimize` | Optimize portfolio allocation | Yes           |

**Request Body:**

| Name            | Type          | Required? | Default           | Description              | Example                   |
| --------------- | ------------- | --------- | ----------------- | ------------------------ | ------------------------- |
| assets          | array[string] | Yes       | -                 | Asset symbols            | ["AAPL", "MSFT", "GOOGL"] |
| current_weights | array[float]  | No        | null              | Current allocations      | [0.33, 0.33, 0.34]        |
| objective       | string        | No        | "maximize_sharpe" | Optimization objective   | "maximize_sharpe"         |
| constraints     | object        | No        | {}                | Optimization constraints | {"max_weight": 0.4}       |

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/monitoring/optimize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "assets": ["AAPL", "MSFT", "GOOGL"],
    "objective": "maximize_sharpe",
    "constraints": {
      "max_weight": 0.5,
      "min_weight": 0.1
    }
  }'
```

**Example Response:**

```json
{
    "status": "success",
    "data": {
        "optimal_weights": {
            "AAPL": 0.35,
            "MSFT": 0.4,
            "GOOGL": 0.25
        },
        "expected_return": 0.15,
        "expected_volatility": 0.2,
        "sharpe_ratio": 1.65
    }
}
```

---

## Health Check

#### Health Check Endpoint

| Method | Path      | Description             | Auth required |
| ------ | --------- | ----------------------- | ------------- |
| GET    | `/health` | Check API health status | No            |

**Example Request:**

```bash
curl http://localhost:5000/health
```

**Example Response:**

```json
{
    "status": "ok",
    "version": "1.0.0",
    "database": true,
    "cache": true,
    "timestamp": "2025-01-01T00:00:00Z"
}
```

## API Documentation (Swagger)

Interactive API documentation is available at:

```
http://localhost:5000/apidocs
```

## Code Examples

### Python Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:5000/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
token = response.json()["data"]["access_token"]

# Calculate VaR
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/risk/var",
    json={"returns": [-0.02, 0.01, -0.015, 0.03], "confidence": 0.95},
    headers=headers
)
var_result = response.json()
print(f"VaR: {var_result['data']['var']}")
```

### JavaScript Example

```javascript
const BASE_URL = 'http://localhost:5000/api/v1';

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password',
    }),
});
const {
    data: { access_token },
} = await loginResponse.json();

// Calculate VaR
const varResponse = await fetch(`${BASE_URL}/risk/var`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify({
        returns: [-0.02, 0.01, -0.015, 0.03],
        confidence: 0.95,
    }),
});
const varResult = await varResponse.json();
console.log(`VaR: ${varResult.data.var}`);
```

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (never in localStorage for sensitive apps)
3. **Refresh tokens before expiry** (default: 1 hour for access tokens)
4. **Handle rate limiting gracefully** with exponential backoff
5. **Validate input data** before sending requests
6. **Use appropriate error handling**
7. **Log API interactions** for debugging
