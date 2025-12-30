# AI and Machine Learning Examples

Examples of AI-powered features in RiskOptimizer.

## Example 1: Train Custom Optimization Model

Train a neural network for portfolio optimization.

```bash
# Train optimization model with custom dataset
./scripts/model_training.sh \
  -m optimization \
  -d data/market_data.csv \
  -e 200 \
  -p '{"learning_rate": 0.001, "batch_size": 32, "hidden_layers": [64, 32]}'

# Output:
# Training optimization model...
# Epoch 1/200: loss=0.0523
# ...
# Epoch 200/200: loss=0.0012
# Model saved to: code/ai_models/trained_models/optimization_model_20250115.h5
# Evaluation metrics:
#   MAE: 0.0015
#   RMSE: 0.0023
#   R²: 0.94
```

## Example 2: AI-Powered Portfolio Optimization

Use trained AI models for portfolio allocation.

```python
from riskoptimizer.services.ai_optimization import PortfolioOptimizer
import numpy as np

# Load AI optimizer
optimizer = PortfolioOptimizer(
    model_path='code/ai_models/trained_models/optimization_model.h5'
)

# Historical returns
returns_data = {
    'AAPL': np.array([0.02, -0.01, 0.015, 0.025, -0.008]),
    'MSFT': np.array([0.015, 0.01, -0.005, 0.018, 0.012]),
    'GOOGL': np.array([0.01, 0.02, -0.01, -0.005, 0.015]),
    'AMZN': np.array([0.025, -0.015, 0.02, 0.01, -0.012])
}

# Optimize using AI
optimal_weights = optimizer.ai_optimize(
    returns=returns_data,
    risk_tolerance=0.5,  # Medium risk
    time_horizon=252  # 1 year
)

print("AI-Optimized Portfolio:")
for asset, weight in optimal_weights.items():
    print(f"  {asset}: {weight*100:.2f}%")
```

## Example 3: Market Prediction with LSTM

Predict market trends using LSTM neural networks.

```python
from code.risk_models.ml_risk_models import LSTMPredictor
import numpy as np

# Initialize predictor
predictor = LSTMPredictor(
    input_dim=5,  # 5 features
    sequence_length=60  # 60 days lookback
)

# Historical data (price, volume, etc.)
historical_data = np.random.rand(252, 5)  # 1 year of data

# Train model
predictor.fit(historical_data, epochs=100)

# Predict next 5 days
predictions = predictor.predict(steps=5)

print("Market Predictions (next 5 days):")
print(predictions)
```

## Example 4: Anomaly Detection

Detect unusual market patterns using machine learning.

```python
from code/risk_models.ml_risk_models import AnomalyDetector

# Initialize detector with Isolation Forest
detector = AnomalyDetector(method='isolation_forest')

# Historical returns
returns = np.array([
    0.01, 0.02, -0.01, 0.015, 0.018,
    -0.12,  # Anomaly: unusual large loss
    0.01, 0.02, -0.008, 0.012
])

# Detect anomalies
anomalies = detector.detect(returns)

print("Detected Anomalies:")
for idx, is_anomaly in enumerate(anomalies):
    if is_anomaly:
        print(f"  Day {idx}: {returns[idx]:.4f}")
```

## Example 5: Risk Prediction

Predict future risk levels using ML models.

```python
from code/risk_models/ml_risk_models import RiskPredictor

# Initialize predictor
predictor = RiskPredictor(model_type='gru')  # GRU neural network

# Historical volatility and returns
historical_features = {
    'returns': [0.01, -0.02, 0.015, -0.008, 0.025],
    'volatility': [0.15, 0.18, 0.16, 0.20, 0.17],
    'volume': [1000000, 1200000, 950000, 1100000, 1050000]
}

# Train predictor
predictor.fit(historical_features, epochs=150)

# Predict risk for next period
risk_forecast = predictor.predict_risk(horizon=5)

print(f"Predicted Risk (next 5 days): {risk_forecast:.4f}")
```

## Example 6: Reinforcement Learning for Trading

Use reinforcement learning for adaptive strategies.

```python
from code/ai_models.rl_agent import PortfolioAgent
import gym

# Create trading environment
env = gym.make('PortfolioTrading-v0')

# Initialize RL agent
agent = PortfolioAgent(
    state_dim=env.observation_space.shape[0],
    action_dim=env.action_space.shape[0],
    algorithm='PPO'  # Proximal Policy Optimization
)

# Train agent
episodes = 1000
for episode in range(episodes):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        action = agent.select_action(state)
        next_state, reward, done, info = env.step(action)
        agent.store_transition(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward

    agent.update()

    if episode % 100 == 0:
        print(f"Episode {episode}: Reward = {total_reward:.2f}")

# Use trained agent
optimal_action = agent.select_action(current_state, deterministic=True)
print(f"Recommended Action: {optimal_action}")
```

## Example 7: Feature Engineering for ML

Create features for machine learning models.

```python
import pandas as pd
import numpy as np

def engineer_features(prices_df):
    """Create ML features from price data."""
    features = pd.DataFrame(index=prices_df.index)

    # Returns
    features['returns'] = prices_df.pct_change()

    # Rolling statistics
    features['rolling_mean_20'] = prices_df.rolling(20).mean()
    features['rolling_std_20'] = prices_df.rolling(20).std()

    # Technical indicators
    features['rsi'] = calculate_rsi(prices_df, period=14)
    features['macd'] = calculate_macd(prices_df)

    # Volatility
    features['volatility'] = features['returns'].rolling(20).std()

    # Momentum
    features['momentum_10'] = prices_df.pct_change(10)

    return features.dropna()

# Use engineered features
prices = pd.read_csv('data/AAPL_historical.csv', index_col=0)['Close']
features = engineer_features(prices)

print("Engineered Features:")
print(features.head())
```

## Example 8: Hyperparameter Tuning

Optimize model hyperparameters.

```python
from sklearn.model_selection import GridSearchCV
from code.risk_models.ml_risk_models import RiskPredictor

# Define hyperparameter grid
param_grid = {
    'hidden_units': [32, 64, 128],
    'learning_rate': [0.001, 0.0001],
    'dropout_rate': [0.2, 0.3, 0.5],
    'batch_size': [16, 32, 64]
}

# Initialize model
model = RiskPredictor()

# Perform grid search
grid_search = GridSearchCV(
    model,
    param_grid,
    cv=5,  # 5-fold cross-validation
    scoring='neg_mean_squared_error',
    n_jobs=-1
)

# Fit with data
X_train, y_train = prepare_data()  # Your data preparation
grid_search.fit(X_train, y_train)

print("Best Hyperparameters:")
print(grid_search.best_params_)
print(f"Best Score: {-grid_search.best_score_:.4f}")
```

## Training Best Practices

1. **Data Split:** 70% train, 15% validation, 15% test
2. **Normalization:** Scale features to [0, 1] or standardize
3. **Cross-validation:** Use k-fold for robust evaluation
4. **Early stopping:** Prevent overfitting
5. **Model checkpointing:** Save best models during training
6. **Hyperparameter tuning:** Use grid search or Bayesian optimization
7. **Ensemble methods:** Combine multiple models for better predictions

See [BASIC_USAGE.md](BASIC_USAGE.md) for simpler examples.
