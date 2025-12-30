# Advanced Features Examples

Advanced usage patterns and features.

## Example 1: Portfolio Optimization

Optimize portfolio allocation using Modern Portfolio Theory.

```python
from riskoptimizer.services.ai_optimization import PortfolioOptimizer
import numpy as np

# Initialize optimizer
optimizer = PortfolioOptimizer()

# Asset returns (simulated or historical)
returns = {
    'AAPL': np.random.normal(0.12, 0.15, 252),
    'MSFT': np.random.normal(0.10, 0.12, 252),
    'GOOGL': np.random.normal(0.14, 0.18, 252),
    'AMZN': np.random.normal(0.16, 0.20, 252)
}

# Optimize for maximum Sharpe ratio
result = optimizer.optimize(
    returns=returns,
    objective='maximize_sharpe',
    constraints={
        'max_weight': 0.4,  # No asset > 40%
        'min_weight': 0.1   # No asset < 10%
    }
)

print("Optimal Allocation:")
for asset, weight in result['weights'].items():
    print(f"  {asset}: {weight*100:.2f}%")

print(f"\nExpected Return: {result['expected_return']:.4f}")
print(f"Expected Volatility: {result['expected_volatility']:.4f}")
print(f"Sharpe Ratio: {result['sharpe_ratio']:.4f}")
```

## Example 2: Monte Carlo Simulation

Run Monte Carlo simulations for risk assessment.

```python
from code.risk_models.risk_analysis import monte_carlo_var
import pandas as pd

# Load returns data
returns = pd.DataFrame({
    'AAPL': [-0.02, 0.01, -0.015, 0.03, -0.01],
    'MSFT': [0.015, -0.005, 0.02, -0.008, 0.012],
    'GOOGL': [0.01, 0.02, -0.01, 0.015, -0.005]
})

# Run Monte Carlo simulation (10,000 paths)
mc_var = monte_carlo_var(
    returns=returns,
    confidence_level=0.95,
    horizon=5,  # 5-day horizon
    n_simulations=10000
)

print("Monte Carlo VaR (95%, 5-day):")
print(mc_var)
```

## Example 3: GARCH Volatility Forecasting

Forecast volatility using GARCH models.

```python
from code.risk_models.risk_analysis import garch_volatility_forecast, load_data

# Load historical data
tickers = ['AAPL', 'MSFT']
returns = load_data(tickers)

# Forecast volatility for next 5 days
vol_forecast = garch_volatility_forecast(returns, horizon=5)

print("GARCH Volatility Forecast (annualized):")
print(vol_forecast)
```

## Example 4: Stress Testing

Simulate extreme market scenarios.

```python
from code.risk_models.risk_analysis import stress_test, load_data

# Load portfolio returns
returns = load_data(['AAPL', 'MSFT', 'GOOGL'])

# Stress test with 4x standard deviation shock
stress_results = stress_test(returns, scenario_multiplier=4.0)

print("Stress Test Results (4x Std Dev Shock):")
print(stress_results)
```

## Example 5: Blockchain Portfolio Tracking

Store and retrieve portfolio from blockchain.

```python
from code.blockchain.web3_integration import Web3Integration

# Initialize Web3 connection
w3 = Web3Integration(
    provider_url="http://localhost:8545",
    contract_address="0xYourContractAddress"
)

# Update portfolio on blockchain
assets = ['AAPL', 'MSFT', 'GOOGL']
allocations = [3500, 3500, 3000]  # Basis points (35%, 35%, 30%)

try:
    tx_hash = w3.update_portfolio(assets, allocations)
    print(f"Transaction hash: {tx_hash}")

    # Wait for confirmation
    receipt = w3.wait_for_transaction(tx_hash)
    print(f"Transaction confirmed in block {receipt['blockNumber']}")

except Exception as e:
    print(f"Error: {e}")

# Retrieve portfolio from blockchain
user_address = "0xYourWalletAddress"
portfolio = w3.get_portfolio(user_address)
print(f"On-chain portfolio: {portfolio}")
```

## Example 6: Efficient Frontier Calculation

Calculate the efficient frontier for portfolio optimization.

```python
import requests

# API call to calculate efficient frontier
response = requests.post(
    "http://localhost:5000/api/v1/risk/efficient-frontier",
    json={
        "returns": {
            "AAPL": [0.01, 0.02, -0.01, 0.015, 0.025],
            "MSFT": [0.015, 0.01, 0.02, -0.005, 0.018],
            "GOOGL": [0.02, -0.01, 0.015, 0.012, -0.008]
        },
        "num_portfolios": 100
    },
    headers={"Authorization": f"Bearer {TOKEN}"}
)

frontier = response.json()['data']

# Plot results (requires matplotlib)
import matplotlib.pyplot as plt

returns = [p['return'] for p in frontier['portfolios']]
risks = [p['risk'] for p in frontier['portfolios']]

plt.figure(figsize=(10, 6))
plt.scatter(risks, returns, c=returns, cmap='viridis')
plt.xlabel('Risk (Volatility)')
plt.ylabel('Expected Return')
plt.title('Efficient Frontier')
plt.colorbar(label='Return')
plt.show()
```

## Example 7: Extreme Value Theory

Model tail risks using Extreme Value Theory.

```python
from code.risk_models.extreme_value_theory import fit_gev, calculate_tail_var

# Sample returns (focus on losses)
returns = [-0.05, -0.03, -0.08, -0.02, -0.01, -0.06, -0.04, -0.07]

# Fit Generalized Extreme Value (GEV) distribution
params = fit_gev(returns)
print(f"GEV Parameters: {params}")

# Calculate tail VaR (99.9%)
tail_var = calculate_tail_var(returns, confidence=0.999)
print(f"Tail VaR (99.9%): {tail_var:.4f}")
```

## Example 8: Async Task Execution

Use Celery for long-running calculations.

```python
from riskoptimizer.tasks.maintenance_tasks import calculate_portfolio_metrics

# Submit task to Celery
task = calculate_portfolio_metrics.delay(
    portfolio_id=1,
    metrics=['var', 'cvar', 'sharpe', 'max_drawdown']
)

print(f"Task ID: {task.id}")

# Check task status
status = task.status
print(f"Status: {status}")

# Get result when ready
if task.ready():
    result = task.get()
    print(f"Metrics: {result}")
```

See [AI_OPTIMIZATION.md](AI_OPTIMIZATION.md) for AI/ML examples.
