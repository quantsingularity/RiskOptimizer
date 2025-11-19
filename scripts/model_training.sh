#!/bin/bash
# model_training.sh
# Comprehensive AI model training and evaluation script for RiskOptimizer
# This script automates the training, evaluation, and deployment of AI models

# Color definitions for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Log function for consistent output
log() {
    local level=$1
    local message=$2
    local color=$NC

    case $level in
        "INFO") color=$BLUE ;;
        "SUCCESS") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac

    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message${NC}"
}

# Error handling function
handle_error() {
    log "ERROR" "An error occurred on line $1"
    exit 1
}

# Set up error handling
trap 'handle_error $LINENO' ERR

# Enable strict mode
set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse command line arguments
MODEL_TYPE="all"
DATASET="default"
EPOCHS=100
HYPERPARAMS=""
EVALUATE_ONLY=false
SAVE_METRICS=true
VERBOSE=false

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Train and evaluate AI models for RiskOptimizer"
    echo ""
    echo "Options:"
    echo "  -m, --model MODEL_TYPE     Model type to train (all, optimization, risk, prediction)"
    echo "  -d, --dataset DATASET      Dataset to use for training (default, custom, path/to/data)"
    echo "  -e, --epochs EPOCHS        Number of training epochs (default: 100)"
    echo "  -p, --hyperparams PARAMS   Hyperparameters as JSON string"
    echo "  --evaluate-only            Skip training, only evaluate existing models"
    echo "  --no-metrics               Don't save metrics and evaluation results"
    echo "  -v, --verbose              Show verbose output"
    echo "  -h, --help                 Show this help message"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            MODEL_TYPE="$2"
            shift 2
            ;;
        -d|--dataset)
            DATASET="$2"
            shift 2
            ;;
        -e|--epochs)
            EPOCHS="$2"
            shift 2
            ;;
        -p|--hyperparams)
            HYPERPARAMS="$2"
            shift 2
            ;;
        --evaluate-only)
            EVALUATE_ONLY=true
            shift
            ;;
        --no-metrics)
            SAVE_METRICS=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Validate model type argument
if [[ ! "$MODEL_TYPE" =~ ^(all|optimization|risk|prediction)$ ]]; then
    log "ERROR" "Invalid model type: $MODEL_TYPE"
    print_usage
    exit 1
fi

# Function to activate virtual environment
activate_venv() {
    if [ -d "$PROJECT_ROOT/venv" ]; then
        source "$PROJECT_ROOT/venv/bin/activate"
        log "INFO" "Activated virtual environment"
    else
        log "WARNING" "Virtual environment not found at $PROJECT_ROOT/venv"
        log "INFO" "Creating virtual environment..."
        python3 -m venv "$PROJECT_ROOT/venv"
        source "$PROJECT_ROOT/venv/bin/activate"
        log "SUCCESS" "Created and activated virtual environment"
    fi
}

# Function to install required packages
install_requirements() {
    log "INFO" "Installing required packages..."

    # Install common ML packages
    pip install numpy pandas scikit-learn tensorflow matplotlib seaborn joblib > /dev/null

    # Install model-specific packages
    case $MODEL_TYPE in
        "all"|"optimization")
            pip install cvxpy pyportfolioopt > /dev/null
            ;;
        "all"|"risk")
            pip install arch statsmodels > /dev/null
            ;;
        "all"|"prediction")
            pip install keras prophet > /dev/null
            ;;
    esac

    log "SUCCESS" "Required packages installed"
}

# Function to prepare dataset
prepare_dataset() {
    log "INFO" "Preparing dataset for training..."

    # Create data directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/code/ai_models/data"

    # Handle different dataset options
    if [ "$DATASET" = "default" ]; then
        log "INFO" "Using default dataset"

        # Check if default dataset exists
        if [ ! -f "$PROJECT_ROOT/code/ai_models/data/default_dataset.csv" ]; then
            log "INFO" "Default dataset not found, downloading..."

            # Create Python script to download and prepare default dataset
            cat > "$PROJECT_ROOT/code/ai_models/data/download_default_data.py" << 'EOF'
#!/usr/bin/env python3
"""
Download and prepare default financial dataset for RiskOptimizer
"""
import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# Define tickers for S&P 500 components (using a subset for example)
tickers = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'JPM', 'V', 'PG', 'UNH',
           'HD', 'BAC', 'XOM', 'NVDA', 'DIS', 'ADBE', 'CRM', 'NFLX', 'CMCSA', 'PFE']

# Calculate date ranges
end_date = datetime.now()
start_date = end_date - timedelta(days=365*5)  # 5 years of data

print(f"Downloading data for {len(tickers)} stocks from {start_date.date()} to {end_date.date()}...")

# Download historical data
data = yf.download(tickers, start=start_date, end=end_date)

# Process the data
prices = data['Adj Close']
returns = prices.pct_change().dropna()

# Calculate additional features
volatility = returns.rolling(window=21).std() * np.sqrt(252)  # Annualized volatility
momentum = prices.pct_change(periods=63).dropna()  # 3-month momentum
volume = data['Volume']
volume_change = volume.pct_change().dropna()

# Create a multi-level DataFrame with all features
features = pd.concat([
    prices.add_suffix('_price'),
    returns.add_suffix('_return'),
    volatility.add_suffix('_volatility'),
    momentum.add_suffix('_momentum'),
    volume.add_suffix('_volume'),
    volume_change.add_suffix('_volume_change')
], axis=1).dropna()

# Save the dataset
output_dir = os.path.dirname(os.path.abspath(__file__))
features.to_csv(os.path.join(output_dir, 'default_dataset.csv'))

# Create train/test split
train_size = int(len(features) * 0.8)
train_data = features.iloc[:train_size]
test_data = features.iloc[train_size:]

train_data.to_csv(os.path.join(output_dir, 'train_dataset.csv'))
test_data.to_csv(os.path.join(output_dir, 'test_dataset.csv'))

print(f"Dataset created with {len(features)} rows and {features.shape[1]} features")
print(f"Training set: {len(train_data)} rows")
print(f"Testing set: {len(test_data)} rows")
print("Files saved to:", output_dir)
EOF

            # Install yfinance package
            pip install yfinance > /dev/null

            # Run the download script
            python "$PROJECT_ROOT/code/ai_models/data/download_default_data.py"

            log "SUCCESS" "Default dataset downloaded and prepared"
        else
            log "INFO" "Default dataset already exists"
        fi

        # Set dataset paths
        TRAIN_DATASET="$PROJECT_ROOT/code/ai_models/data/train_dataset.csv"
        TEST_DATASET="$PROJECT_ROOT/code/ai_models/data/test_dataset.csv"

    elif [ "$DATASET" = "custom" ]; then
        log "INFO" "Using custom dataset from data directory"

        # Check if custom dataset exists
        if [ ! -f "$PROJECT_ROOT/code/ai_models/data/custom_dataset.csv" ]; then
            log "ERROR" "Custom dataset not found at $PROJECT_ROOT/code/ai_models/data/custom_dataset.csv"
            exit 1
        fi

        # Set dataset paths
        TRAIN_DATASET="$PROJECT_ROOT/code/ai_models/data/custom_dataset.csv"
        TEST_DATASET="$PROJECT_ROOT/code/ai_models/data/custom_dataset.csv"

    else
        # Assume DATASET is a path
        log "INFO" "Using dataset from specified path: $DATASET"

        # Check if dataset exists
        if [ ! -f "$DATASET" ]; then
            log "ERROR" "Dataset not found at $DATASET"
            exit 1
        fi

        # Set dataset paths
        TRAIN_DATASET="$DATASET"
        TEST_DATASET="$DATASET"
    fi

    log "SUCCESS" "Dataset prepared for training"
    return 0
}

# Function to train optimization model
train_optimization_model() {
    log "INFO" "Training portfolio optimization model..."

    # Create model directory
    mkdir -p "$PROJECT_ROOT/code/ai_models/models/optimization"

    # Create Python script for training
    cat > "$PROJECT_ROOT/code/ai_models/train_optimization_model.py" << 'EOF'
#!/usr/bin/env python3
"""
Train portfolio optimization model for RiskOptimizer
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Parse command line arguments
import argparse
parser = argparse.ArgumentParser(description='Train portfolio optimization model')
parser.add_argument('--train_data', type=str, required=True, help='Path to training data')
parser.add_argument('--test_data', type=str, required=True, help='Path to test data')
parser.add_argument('--epochs', type=int, default=100, help='Number of iterations')
parser.add_argument('--hyperparams', type=str, default='{}', help='Hyperparameters as JSON string')
parser.add_argument('--output_dir', type=str, required=True, help='Output directory for model and metrics')
parser.add_argument('--verbose', action='store_true', help='Verbose output')
args = parser.parse_args()

# Load hyperparameters
try:
    hyperparams = json.loads(args.hyperparams)
except json.JSONDecodeError:
    print("Error: Invalid JSON format for hyperparameters")
    sys.exit(1)

# Set default hyperparameters
default_hyperparams = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 2,
    'min_samples_leaf': 1,
    'random_state': 42
}

# Update with user-provided hyperparameters
for key, value in hyperparams.items():
    default_hyperparams[key] = value

if args.verbose:
    print(f"Using hyperparameters: {default_hyperparams}")

# Load data
print(f"Loading data from {args.train_data} and {args.test_data}")
train_data = pd.read_csv(args.train_data, index_col=0)
test_data = pd.read_csv(args.test_data, index_col=0)

# Extract features and targets
# For optimization model, we'll predict returns based on other features
return_cols = [col for col in train_data.columns if col.endswith('_return')]
feature_cols = [col for col in train_data.columns if not col.endswith('_return')]

X_train = train_data[feature_cols]
y_train = train_data[return_cols]

X_test = test_data[feature_cols]
y_test = test_data[return_cols]

# Preprocess data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
print(f"Training model with {args.epochs} iterations...")
model = RandomForestRegressor(**default_hyperparams, n_estimators=args.epochs)
model.fit(X_train_scaled, y_train)

# Evaluate model
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model evaluation:")
print(f"Mean Squared Error: {mse:.6f}")
print(f"R² Score: {r2:.6f}")

# Save model and scaler
os.makedirs(args.output_dir, exist_ok=True)
joblib.dump(model, os.path.join(args.output_dir, 'optimization_model.pkl'))
joblib.dump(scaler, os.path.join(args.output_dir, 'optimization_scaler.pkl'))

# Save feature importance plot
plt.figure(figsize=(12, 8))
feature_importance = pd.DataFrame(
    {'feature': X_train.columns, 'importance': model.feature_importances_}
).sort_values('importance', ascending=False)

sns.barplot(x='importance', y='feature', data=feature_importance.head(20))
plt.title('Feature Importance for Return Prediction')
plt.tight_layout()
plt.savefig(os.path.join(args.output_dir, 'feature_importance.png'))

# Save metrics
metrics = {
    'mse': float(mse),
    'r2': float(r2),
    'hyperparameters': default_hyperparams,
    'feature_importance': {
        feature: float(importance)
        for feature, importance in zip(X_train.columns, model.feature_importances_)
    }
}

with open(os.path.join(args.output_dir, 'metrics.json'), 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"Model and metrics saved to {args.output_dir}")
EOF

    # Run training script
    python "$PROJECT_ROOT/code/ai_models/train_optimization_model.py" \
        --train_data "$TRAIN_DATASET" \
        --test_data "$TEST_DATASET" \
        --epochs "$EPOCHS" \
        --hyperparams "$HYPERPARAMS" \
        --output_dir "$PROJECT_ROOT/code/ai_models/models/optimization" \
        $([ "$VERBOSE" = true ] && echo "--verbose")

    log "SUCCESS" "Portfolio optimization model trained and saved"
}

# Function to train risk model
train_risk_model() {
    log "INFO" "Training risk assessment model..."

    # Create model directory
    mkdir -p "$PROJECT_ROOT/code/ai_models/models/risk"

    # Create Python script for training
    cat > "$PROJECT_ROOT/code/ai_models/train_risk_model.py" << 'EOF'
#!/usr/bin/env python3
"""
Train risk assessment model for RiskOptimizer
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Parse command line arguments
import argparse
parser = argparse.ArgumentParser(description='Train risk assessment model')
parser.add_argument('--train_data', type=str, required=True, help='Path to training data')
parser.add_argument('--test_data', type=str, required=True, help='Path to test data')
parser.add_argument('--epochs', type=int, default=100, help='Number of iterations')
parser.add_argument('--hyperparams', type=str, default='{}', help='Hyperparameters as JSON string')
parser.add_argument('--output_dir', type=str, required=True, help='Output directory for model and metrics')
parser.add_argument('--verbose', action='store_true', help='Verbose output')
args = parser.parse_args()

# Load hyperparameters
try:
    hyperparams = json.loads(args.hyperparams)
except json.JSONDecodeError:
    print("Error: Invalid JSON format for hyperparameters")
    sys.exit(1)

# Set default hyperparameters
default_hyperparams = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 3,
    'min_samples_split': 2,
    'min_samples_leaf': 1,
    'random_state': 42
}

# Update with user-provided hyperparameters
for key, value in hyperparams.items():
    default_hyperparams[key] = value

if args.verbose:
    print(f"Using hyperparameters: {default_hyperparams}")

# Load data
print(f"Loading data from {args.train_data} and {args.test_data}")
train_data = pd.read_csv(args.train_data, index_col=0)
test_data = pd.read_csv(args.test_data, index_col=0)

# Extract features and targets
# For risk model, we'll predict volatility based on other features
volatility_cols = [col for col in train_data.columns if col.endswith('_volatility')]
feature_cols = [col for col in train_data.columns if not col.endswith('_volatility')]

X_train = train_data[feature_cols]
y_train = train_data[volatility_cols]

X_test = test_data[feature_cols]
y_test = test_data[volatility_cols]

# Preprocess data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
print(f"Training model with {args.epochs} iterations...")
model = GradientBoostingRegressor(**default_hyperparams, n_estimators=args.epochs)
model.fit(X_train_scaled, y_train)

# Evaluate model
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model evaluation:")
print(f"Mean Squared Error: {mse:.6f}")
print(f"R² Score: {r2:.6f}")

# Save model and scaler
os.makedirs(args.output_dir, exist_ok=True)
joblib.dump(model, os.path.join(args.output_dir, 'risk_model.pkl'))
joblib.dump(scaler, os.path.join(args.output_dir, 'risk_scaler.pkl'))

# Save feature importance plot
plt.figure(figsize=(12, 8))
feature_importance = pd.DataFrame(
    {'feature': X_train.columns, 'importance': model.feature_importances_}
).sort_values('importance', ascending=False)

sns.barplot(x='importance', y='feature', data=feature_importance.head(20))
plt.title('Feature Importance for Volatility Prediction')
plt.tight_layout()
plt.savefig(os.path.join(args.output_dir, 'feature_importance.png'))

# Save metrics
metrics = {
    'mse': float(mse),
    'r2': float(r2),
    'hyperparameters': default_hyperparams,
    'feature_importance': {
        feature: float(importance)
        for feature, importance in zip(X_train.columns, model.feature_importances_)
    }
}

with open(os.path.join(args.output_dir, 'metrics.json'), 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"Model and metrics saved to {args.output_dir}")
EOF

    # Run training script
    python "$PROJECT_ROOT/code/ai_models/train_risk_model.py" \
        --train_data "$TRAIN_DATASET" \
        --test_data "$TEST_DATASET" \
        --epochs "$EPOCHS" \
        --hyperparams "$HYPERPARAMS" \
        --output_dir "$PROJECT_ROOT/code/ai_models/models/risk" \
        $([ "$VERBOSE" = true ] && echo "--verbose")

    log "SUCCESS" "Risk assessment model trained and saved"
}

# Function to train prediction model
train_prediction_model() {
    log "INFO" "Training market prediction model..."

    # Create model directory
    mkdir -p "$PROJECT_ROOT/code/ai_models/models/prediction"

    # Create Python script for training
    cat > "$PROJECT_ROOT/code/ai_models/train_prediction_model.py" << 'EOF'
#!/usr/bin/env python3
"""
Train market prediction model for RiskOptimizer
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
import matplotlib.pyplot as plt

# Parse command line arguments
import argparse
parser = argparse.ArgumentParser(description='Train market prediction model')
parser.add_argument('--train_data', type=str, required=True, help='Path to training data')
parser.add_argument('--test_data', type=str, required=True, help='Path to test data')
parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
parser.add_argument('--hyperparams', type=str, default='{}', help='Hyperparameters as JSON string')
parser.add_argument('--output_dir', type=str, required=True, help='Output directory for model and metrics')
parser.add_argument('--verbose', action='store_true', help='Verbose output')
args = parser.parse_args()

# Load hyperparameters
try:
    hyperparams = json.loads(args.hyperparams)
except json.JSONDecodeError:
    print("Error: Invalid JSON format for hyperparameters")
    sys.exit(1)

# Set default hyperparameters
default_hyperparams = {
    'lstm_units': 50,
    'dropout_rate': 0.2,
    'learning_rate': 0.001,
    'batch_size': 32,
    'sequence_length': 10
}

# Update with user-provided hyperparameters
for key, value in hyperparams.items():
    default_hyperparams[key] = value

if args.verbose:
    print(f"Using hyperparameters: {default_hyperparams}")

# Load data
print(f"Loading data from {args.train_data} and {args.test_data}")
train_data = pd.read_csv(args.train_data, index_col=0)
test_data = pd.read_csv(args.test_data, index_col=0)

# Extract price columns for time series prediction
price_cols = [col for col in train_data.columns if col.endswith('_price')]
train_prices = train_data[price_cols]
test_prices = test_data[price_cols]

# Preprocess data
scaler = StandardScaler()
train_scaled = scaler.fit_transform(train_prices)
test_scaled = scaler.transform(test_prices)

# Create sequences for LSTM
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

seq_length = default_hyperparams['sequence_length']
X_train, y_train = create_sequences(train_scaled, seq_length)
X_test, y_test = create_sequences(test_scaled, seq_length)

# Build LSTM model
model = Sequential([
    LSTM(units=default_hyperparams['lstm_units'], return_sequences=True,
         input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(default_hyperparams['dropout_rate']),
    LSTM(units=default_hyperparams['lstm_units']),
    Dropout(default_hyperparams['dropout_rate']),
    Dense(y_train.shape[1])
])

# Compile model
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=default_hyperparams['learning_rate']),
    loss='mean_squared_error'
)

# Train model
print(f"Training model for {args.epochs} epochs...")
history = model.fit(
    X_train, y_train,
    epochs=args.epochs,
    batch_size=default_hyperparams['batch_size'],
    validation_data=(X_test, y_test),
    verbose=1 if args.verbose else 0
)

# Evaluate model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test.reshape(-1), y_pred.reshape(-1))

print(f"Model evaluation:")
print(f"Mean Squared Error: {mse:.6f}")
print(f"R² Score: {r2:.6f}")

# Save model and scaler
os.makedirs(args.output_dir, exist_ok=True)
model.save(os.path.join(args.output_dir, 'prediction_model'))
joblib.dump(scaler, os.path.join(args.output_dir, 'prediction_scaler.pkl'))
joblib.dump(seq_length, os.path.join(args.output_dir, 'sequence_length.pkl'))

# Save training history plot
plt.figure(figsize=(12, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss During Training')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.savefig(os.path.join(args.output_dir, 'training_history.png'))

# Save prediction vs actual plot
plt.figure(figsize=(12, 6))
# Plot for the first asset as an example
plt.plot(y_test[:, 0], label='Actual')
plt.plot(y_pred[:, 0], label='Predicted')
plt.title('Prediction vs Actual (First Asset)')
plt.xlabel('Time Step')
plt.ylabel('Scaled Price')
plt.legend()
plt.savefig(os.path.join(args.output_dir, 'prediction_vs_actual.png'))

# Save metrics
metrics = {
    'mse': float(mse),
    'r2': float(r2),
    'hyperparameters': default_hyperparams,
    'training_history': {
        'loss': [float(x) for x in history.history['loss']],
        'val_loss': [float(x) for x in history.history['val_loss']]
    }
}

with open(os.path.join(args.output_dir, 'metrics.json'), 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"Model and metrics saved to {args.output_dir}")
EOF

    # Run training script
    python "$PROJECT_ROOT/code/ai_models/train_prediction_model.py" \
        --train_data "$TRAIN_DATASET" \
        --test_data "$TEST_DATASET" \
        --epochs "$EPOCHS" \
        --hyperparams "$HYPERPARAMS" \
        --output_dir "$PROJECT_ROOT/code/ai_models/models/prediction" \
        $([ "$VERBOSE" = true ] && echo "--verbose")

    log "SUCCESS" "Market prediction model trained and saved"
}

# Function to evaluate models
evaluate_models() {
    log "INFO" "Evaluating trained models..."

    # Create evaluation directory
    mkdir -p "$PROJECT_ROOT/code/ai_models/evaluation"

    # Create Python script for evaluation
    cat > "$PROJECT_ROOT/code/ai_models/evaluate_models.py" << 'EOF'
#!/usr/bin/env python3
"""
Evaluate trained models for RiskOptimizer
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf

# Parse command line arguments
import argparse
parser = argparse.ArgumentParser(description='Evaluate trained models')
parser.add_argument('--test_data', type=str, required=True, help='Path to test data')
parser.add_argument('--models_dir', type=str, required=True, help='Directory containing trained models')
parser.add_argument('--output_dir', type=str, required=True, help='Output directory for evaluation results')
parser.add_argument('--verbose', action='store_true', help='Verbose output')
args = parser.parse_args()

# Load test data
print(f"Loading test data from {args.test_data}")
test_data = pd.read_csv(args.test_data, index_col=0)

# Create output directory
os.makedirs(args.output_dir, exist_ok=True)

# Function to evaluate optimization model
def evaluate_optimization_model():
    model_dir = os.path.join(args.models_dir, 'optimization')
    if not os.path.exists(model_dir):
        print(f"Optimization model directory not found: {model_dir}")
        return None

    print("Evaluating optimization model...")

    # Load model and scaler
    model_path = os.path.join(model_dir, 'optimization_model.pkl')
    scaler_path = os.path.join(model_dir, 'optimization_scaler.pkl')

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print("Model or scaler file not found")
        return None

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # Extract features and targets
    return_cols = [col for col in test_data.columns if col.endswith('_return')]
    feature_cols = [col for col in test_data.columns if not col.endswith('_return')]

    X_test = test_data[feature_cols]
    y_test = test_data[return_cols]

    # Preprocess data
    X_test_scaled = scaler.transform(X_test)

    # Make predictions
    y_pred = model.predict(X_test_scaled)

    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Optimization Model Metrics:")
    print(f"Mean Squared Error: {mse:.6f}")
    print(f"Mean Absolute Error: {mae:.6f}")
    print(f"R² Score: {r2:.6f}")

    # Create evaluation plots
    plt.figure(figsize=(12, 8))

    # Plot actual vs predicted for a sample asset
    sample_asset = return_cols[0]
    plt.scatter(y_test[sample_asset], y_pred[:, 0], alpha=0.5)
    plt.plot([y_test[sample_asset].min(), y_test[sample_asset].max()],
             [y_test[sample_asset].min(), y_test[sample_asset].max()], 'k--')
    plt.xlabel('Actual Returns')
    plt.ylabel('Predicted Returns')
    plt.title(f'Actual vs Predicted Returns for {sample_asset}')
    plt.savefig(os.path.join(args.output_dir, 'optimization_actual_vs_predicted.png'))

    # Save metrics
    metrics = {
        'mse': float(mse),
        'mae': float(mae),
        'r2': float(r2),
        'sample_predictions': {
            'actual': y_test.iloc[:5].to_dict(),
            'predicted': {col: y_pred[:5, i].tolist() for i, col in enumerate(y_test.columns)}
        }
    }

    with open(os.path.join(args.output_dir, 'optimization_evaluation.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics

# Function to evaluate risk model
def evaluate_risk_model():
    model_dir = os.path.join(args.models_dir, 'risk')
    if not os.path.exists(model_dir):
        print(f"Risk model directory not found: {model_dir}")
        return None

    print("Evaluating risk model...")

    # Load model and scaler
    model_path = os.path.join(model_dir, 'risk_model.pkl')
    scaler_path = os.path.join(model_dir, 'risk_scaler.pkl')

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print("Model or scaler file not found")
        return None

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # Extract features and targets
    volatility_cols = [col for col in test_data.columns if col.endswith('_volatility')]
    feature_cols = [col for col in test_data.columns if not col.endswith('_volatility')]

    X_test = test_data[feature_cols]
    y_test = test_data[volatility_cols]

    # Preprocess data
    X_test_scaled = scaler.transform(X_test)

    # Make predictions
    y_pred = model.predict(X_test_scaled)

    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Risk Model Metrics:")
    print(f"Mean Squared Error: {mse:.6f}")
    print(f"Mean Absolute Error: {mae:.6f}")
    print(f"R² Score: {r2:.6f}")

    # Create evaluation plots
    plt.figure(figsize=(12, 8))

    # Plot actual vs predicted for a sample asset
    sample_asset = volatility_cols[0]
    plt.scatter(y_test[sample_asset], y_pred[:, 0], alpha=0.5)
    plt.plot([y_test[sample_asset].min(), y_test[sample_asset].max()],
             [y_test[sample_asset].min(), y_test[sample_asset].max()], 'k--')
    plt.xlabel('Actual Volatility')
    plt.ylabel('Predicted Volatility')
    plt.title(f'Actual vs Predicted Volatility for {sample_asset}')
    plt.savefig(os.path.join(args.output_dir, 'risk_actual_vs_predicted.png'))

    # Save metrics
    metrics = {
        'mse': float(mse),
        'mae': float(mae),
        'r2': float(r2),
        'sample_predictions': {
            'actual': y_test.iloc[:5].to_dict(),
            'predicted': {col: y_pred[:5, i].tolist() for i, col in enumerate(y_test.columns)}
        }
    }

    with open(os.path.join(args.output_dir, 'risk_evaluation.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics

# Function to evaluate prediction model
def evaluate_prediction_model():
    model_dir = os.path.join(args.models_dir, 'prediction')
    if not os.path.exists(model_dir):
        print(f"Prediction model directory not found: {model_dir}")
        return None

    print("Evaluating prediction model...")

    # Load model and scaler
    model_path = os.path.join(model_dir, 'prediction_model')
    scaler_path = os.path.join(model_dir, 'prediction_scaler.pkl')
    seq_length_path = os.path.join(model_dir, 'sequence_length.pkl')

    if not os.path.exists(model_path) or not os.path.exists(scaler_path) or not os.path.exists(seq_length_path):
        print("Model, scaler, or sequence length file not found")
        return None

    model = tf.keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)
    seq_length = joblib.load(seq_length_path)

    # Extract price columns for time series prediction
    price_cols = [col for col in test_data.columns if col.endswith('_price')]
    test_prices = test_data[price_cols]

    # Preprocess data
    test_scaled = scaler.transform(test_prices)

    # Create sequences for LSTM
    def create_sequences(data, seq_length):
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)

    X_test, y_test = create_sequences(test_scaled, seq_length)

    # Make predictions
    y_pred = model.predict(X_test)

    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test.reshape(-1), y_pred.reshape(-1))
    r2 = r2_score(y_test.reshape(-1), y_pred.reshape(-1))

    print(f"Prediction Model Metrics:")
    print(f"Mean Squared Error: {mse:.6f}")
    print(f"Mean Absolute Error: {mae:.6f}")
    print(f"R² Score: {r2:.6f}")

    # Create evaluation plots
    plt.figure(figsize=(12, 8))

    # Plot actual vs predicted time series for a sample asset
    plt.figure(figsize=(12, 6))
    plt.plot(y_test[:, 0], label='Actual')
    plt.plot(y_pred[:, 0], label='Predicted')
    plt.title(f'Actual vs Predicted Prices for {price_cols[0]}')
    plt.xlabel('Time Step')
    plt.ylabel('Scaled Price')
    plt.legend()
    plt.savefig(os.path.join(args.output_dir, 'prediction_time_series.png'))

    # Save metrics
    metrics = {
        'mse': float(mse),
        'mae': float(mae),
        'r2': float(r2),
        'sample_predictions': {
            'actual': y_test[:5, 0].tolist(),
            'predicted': y_pred[:5, 0].tolist()
        }
    }

    with open(os.path.join(args.output_dir, 'prediction_evaluation.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics

# Evaluate all models
results = {}

optimization_metrics = evaluate_optimization_model()
if optimization_metrics:
    results['optimization'] = optimization_metrics

risk_metrics = evaluate_risk_model()
if risk_metrics:
    results['risk'] = risk_metrics

prediction_metrics = evaluate_prediction_model()
if prediction_metrics:
    results['prediction'] = prediction_metrics

# Generate combined evaluation report
if results:
    # Create HTML report
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RiskOptimizer Model Evaluation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .metric-good {{ color: green; }}
            .metric-medium {{ color: orange; }}
            .metric-poor {{ color: red; }}
            .model-section {{ margin-bottom: 30px; }}
            img {{ max-width: 100%; height: auto; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>RiskOptimizer Model Evaluation Report</h1>
        <p>Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """

    if 'optimization' in results:
        html_report += f"""
        <div class="model-section">
            <h2>Portfolio Optimization Model</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Mean Squared Error</td>
                    <td>{results['optimization']['mse']:.6f}</td>
                </tr>
                <tr>
                    <td>Mean Absolute Error</td>
                    <td>{results['optimization']['mae']:.6f}</td>
                </tr>
                <tr>
                    <td>R² Score</td>
                    <td class="{'metric-good' if results['optimization']['r2'] > 0.7 else 'metric-medium' if results['optimization']['r2'] > 0.5 else 'metric-poor'}">
                        {results['optimization']['r2']:.6f}
                    </td>
                </tr>
            </table>
            <h3>Actual vs Predicted Plot</h3>
            <img src="optimization_actual_vs_predicted.png" alt="Optimization Model: Actual vs Predicted">
        </div>
        """

    if 'risk' in results:
        html_report += f"""
        <div class="model-section">
            <h2>Risk Assessment Model</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Mean Squared Error</td>
                    <td>{results['risk']['mse']:.6f}</td>
                </tr>
                <tr>
                    <td>Mean Absolute Error</td>
                    <td>{results['risk']['mae']:.6f}</td>
                </tr>
                <tr>
                    <td>R² Score</td>
                    <td class="{'metric-good' if results['risk']['r2'] > 0.7 else 'metric-medium' if results['risk']['r2'] > 0.5 else 'metric-poor'}">
                        {results['risk']['r2']:.6f}
                    </td>
                </tr>
            </table>
            <h3>Actual vs Predicted Plot</h3>
            <img src="risk_actual_vs_predicted.png" alt="Risk Model: Actual vs Predicted">
        </div>
        """

    if 'prediction' in results:
        html_report += f"""
        <div class="model-section">
            <h2>Market Prediction Model</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Mean Squared Error</td>
                    <td>{results['prediction']['mse']:.6f}</td>
                </tr>
                <tr>
                    <td>Mean Absolute Error</td>
                    <td>{results['prediction']['mae']:.6f}</td>
                </tr>
                <tr>
                    <td>R² Score</td>
                    <td class="{'metric-good' if results['prediction']['r2'] > 0.7 else 'metric-medium' if results['prediction']['r2'] > 0.5 else 'metric-poor'}">
                        {results['prediction']['r2']:.6f}
                    </td>
                </tr>
            </table>
            <h3>Time Series Prediction Plot</h3>
            <img src="prediction_time_series.png" alt="Prediction Model: Time Series">
        </div>
        """

    html_report += """
    </body>
    </html>
    """

    # Save HTML report
    with open(os.path.join(args.output_dir, 'evaluation_report.html'), 'w') as f:
        f.write(html_report)

    # Save combined metrics
    with open(os.path.join(args.output_dir, 'all_models_evaluation.json'), 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Evaluation report saved to {os.path.join(args.output_dir, 'evaluation_report.html')}")
else:
    print("No models were evaluated successfully")

print("Evaluation complete")
EOF

    # Run evaluation script
    python "$PROJECT_ROOT/code/ai_models/evaluate_models.py" \
        --test_data "$TEST_DATASET" \
        --models_dir "$PROJECT_ROOT/code/ai_models/models" \
        --output_dir "$PROJECT_ROOT/code/ai_models/evaluation" \
        $([ "$VERBOSE" = true ] && echo "--verbose")

    log "SUCCESS" "Models evaluated and reports generated"
}

# Main execution
log "INFO" "Starting RiskOptimizer AI model training and evaluation..."

# Activate virtual environment
activate_venv

# Install required packages
install_requirements

# Prepare dataset
prepare_dataset

# Train or evaluate models based on selection
if [ "$EVALUATE_ONLY" = false ]; then
    # Train models based on model type selection
    if [ "$MODEL_TYPE" = "all" ] || [ "$MODEL_TYPE" = "optimization" ]; then
        train_optimization_model
    fi

    if [ "$MODEL_TYPE" = "all" ] || [ "$MODEL_TYPE" = "risk" ]; then
        train_risk_model
    fi

    if [ "$MODEL_TYPE" = "all" ] || [ "$MODEL_TYPE" = "prediction" ]; then
        train_prediction_model
    fi
fi

# Evaluate models
if [ "$SAVE_METRICS" = true ]; then
    evaluate_models
fi

# Deactivate virtual environment
deactivate

log "SUCCESS" "RiskOptimizer AI model training and evaluation completed!"
exit 0
