# RiskOptimizer Automation Scripts

This package contains a set of comprehensive automation scripts designed to streamline development, testing, deployment, and maintenance of the RiskOptimizer platform.

## Overview

These scripts automate various aspects of the RiskOptimizer development workflow, including:

- Development environment setup
- Comprehensive testing across all components
- Code quality checks and enforcement
- Deployment to different environments
- AI model training and evaluation

## Scripts Included

### 1. `setup_dev_environment.sh`

Sets up the complete development environment for RiskOptimizer.

**Features:**
- Detects and installs required dependencies
- Creates and configures Python virtual environment
- Installs backend, frontend, and blockchain dependencies
- Sets up git hooks for pre-commit checks
- Creates default environment configuration

**Usage:**
```bash
./setup_dev_environment.sh
```

### 2. `run_tests.sh`

Runs tests across all components of the RiskOptimizer platform.

**Features:**
- Supports testing specific components or all components
- Generates test coverage reports
- Supports parallel test execution
- Provides quick test mode for faster feedback
- Creates comprehensive test reports

**Usage:**
```bash
# Run all tests
./run_tests.sh

# Run tests for a specific component
./run_tests.sh -c backend

# Run tests with coverage reports
./run_tests.sh --coverage

# Run tests in parallel
./run_tests.sh -p

# Run quick tests only
./run_tests.sh -q
```

### 3. `code_quality.sh`

Performs code quality checks and formatting across all components.

**Features:**
- Lints Python code with flake8
- Formats Python code with black and isort
- Lints JavaScript/TypeScript with ESLint
- Formats JavaScript/TypeScript with Prettier
- Lints Solidity code with Solhint
- Generates code quality reports
- Can automatically fix common issues

**Usage:**
```bash
# Check code quality for all components
./code_quality.sh

# Check code quality for a specific component
./code_quality.sh -c frontend

# Automatically fix issues when possible
./code_quality.sh -f

# Check only staged files in git
./code_quality.sh -s
```

### 4. `deploy.sh`

Deploys RiskOptimizer components to different environments.

**Features:**
- Supports development, staging, and production environments
- Can deploy specific components or all components
- Runs tests before deployment
- Creates environment-specific configurations
- Generates deployment packages for remote servers

**Usage:**
```bash
# Deploy all components to development environment
./deploy.sh -e dev

# Deploy specific component to staging environment
./deploy.sh -e staging -c backend

# Skip tests before deployment
./deploy.sh -e prod --skip-tests
```

### 5. `model_training.sh`

Automates AI model training, evaluation, and deployment.

**Features:**
- Trains different types of models (optimization, risk, prediction)
- Supports custom datasets and hyperparameters
- Evaluates model performance with various metrics
- Generates visualizations and reports
- Supports model deployment

**Usage:**
```bash
# Train all models with default settings
./model_training.sh

# Train a specific model type
./model_training.sh -m optimization

# Train with custom dataset
./model_training.sh -d /path/to/custom/dataset.csv

# Specify number of training epochs
./model_training.sh -e 200

# Provide custom hyperparameters
./model_training.sh -p '{"learning_rate": 0.001, "batch_size": 64}'

# Only evaluate existing models without training
./model_training.sh --evaluate-only
```

## Requirements

- Bash shell (Linux, macOS, or Windows with WSL)
- Python 3.8+
- Node.js 14+
- Git

## Installation

1. Extract the zip file to your RiskOptimizer project root directory
2. Make the scripts executable:
   ```bash
   chmod +x scripts/*.sh
   ```
3. Run the setup script to configure the environment:
   ```bash
   ./scripts/setup_dev_environment.sh
   ```

## Best Practices

- Run the code quality script before committing changes
- Use the test script regularly to ensure all components work correctly
- Set up continuous integration to run these scripts automatically
- Keep the scripts updated as the project evolves

## Troubleshooting

If you encounter any issues:

1. Check the logs in the `logs` directory
2. Ensure all dependencies are installed
3. Verify that the scripts have execute permissions
4. Make sure the scripts are run from the project root directory

## Extending the Scripts

These scripts are designed to be extensible. To add new functionality:

1. Follow the existing patterns and coding style
2. Add clear documentation for new features
3. Test thoroughly before deployment
4. Update this README with new usage instructions

## License

These scripts are provided under the same license as the RiskOptimizer project.
