#!/bin/bash
# deploy.sh
# Comprehensive deployment automation script for RiskOptimizer
# This script handles deployment to various environments (dev, staging, prod)

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
ENVIRONMENT="dev"
COMPONENT="all"
SKIP_TESTS=false
SKIP_BUILD=false
VERBOSE=false

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Deploy RiskOptimizer components to specified environment"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV      Target environment (dev, staging, prod)"
    echo "  -c, --component COMPONENT  Deploy specific component"
    echo "                             (all, backend, frontend, ai_models, blockchain)"
    echo "  --skip-tests               Skip running tests before deployment"
    echo "  --skip-build               Skip building/compiling before deployment"
    echo "  -v, --verbose              Show verbose output"
    echo "  -h, --help                 Show this help message"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -c|--component)
            COMPONENT="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
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

# Validate environment argument
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    log "ERROR" "Invalid environment: $ENVIRONMENT"
    print_usage
    exit 1
fi

# Validate component argument
if [[ ! "$COMPONENT" =~ ^(all|backend|frontend|ai_models|blockchain)$ ]]; then
    log "ERROR" "Invalid component: $COMPONENT"
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

# Function to run tests before deployment
run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log "INFO" "Skipping tests as requested"
        return 0
    fi
    
    log "INFO" "Running tests before deployment..."
    
    # Run tests for the specified component
    "$SCRIPT_DIR/run_tests.sh" -c "$COMPONENT" -q
    
    log "SUCCESS" "Tests passed successfully"
}

# Function to load environment-specific configuration
load_env_config() {
    log "INFO" "Loading configuration for $ENVIRONMENT environment..."
    
    # Create config directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/config"
    
    # Check if environment config file exists
    ENV_CONFIG_FILE="$PROJECT_ROOT/config/$ENVIRONMENT.env"
    if [ ! -f "$ENV_CONFIG_FILE" ]; then
        log "WARNING" "Environment config file not found: $ENV_CONFIG_FILE"
        log "INFO" "Creating default config file for $ENVIRONMENT environment..."
        
        # Create default config file based on environment
        case $ENVIRONMENT in
            "dev")
                cat > "$ENV_CONFIG_FILE" << EOF
# RiskOptimizer Development Environment Configuration
API_URL=http://localhost:5000
WEB_URL=http://localhost:3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=riskoptimizer_dev
DB_USER=postgres
DB_PASSWORD=postgres
BLOCKCHAIN_NETWORK=development
LOG_LEVEL=debug
EOF
                ;;
            "staging")
                cat > "$ENV_CONFIG_FILE" << EOF
# RiskOptimizer Staging Environment Configuration
API_URL=https://api-staging.riskoptimizer.example.com
WEB_URL=https://staging.riskoptimizer.example.com
DB_HOST=staging-db.riskoptimizer.example.com
DB_PORT=5432
DB_NAME=riskoptimizer_staging
DB_USER=riskoptimizer_app
DB_PASSWORD=change_me_in_production
BLOCKCHAIN_NETWORK=testnet
LOG_LEVEL=info
EOF
                ;;
            "prod")
                cat > "$ENV_CONFIG_FILE" << EOF
# RiskOptimizer Production Environment Configuration
API_URL=https://api.riskoptimizer.example.com
WEB_URL=https://riskoptimizer.example.com
DB_HOST=prod-db.riskoptimizer.example.com
DB_PORT=5432
DB_NAME=riskoptimizer_prod
DB_USER=riskoptimizer_app
DB_PASSWORD=change_me_in_production
BLOCKCHAIN_NETWORK=mainnet
LOG_LEVEL=warn
EOF
                ;;
        esac
        
        log "SUCCESS" "Created default config file: $ENV_CONFIG_FILE"
    fi
    
    # Load environment variables from config file
    set -a
    source "$ENV_CONFIG_FILE"
    set +a
    
    log "SUCCESS" "Loaded configuration for $ENVIRONMENT environment"
}

# Function to deploy backend
deploy_backend() {
    log "INFO" "Deploying backend to $ENVIRONMENT environment..."
    
    cd "$PROJECT_ROOT/code/backend"
    
    # Build backend if needed
    if [ "$SKIP_BUILD" = false ]; then
        log "INFO" "Building backend..."
        
        # Install dependencies
        pip install -r requirements.txt
        
        log "SUCCESS" "Backend build completed"
    fi
    
    # Create deployment directory
    DEPLOY_DIR="$PROJECT_ROOT/deploy/$ENVIRONMENT/backend"
    mkdir -p "$DEPLOY_DIR"
    
    # Copy backend files to deployment directory
    log "INFO" "Copying backend files to deployment directory..."
    rsync -av --exclude "__pycache__" --exclude "*.pyc" --exclude "*.pyo" --exclude "*.pyd" \
        --exclude ".pytest_cache" --exclude "tests" \
        . "$DEPLOY_DIR/"
    
    # Create environment-specific config
    log "INFO" "Creating environment-specific configuration..."
    cat > "$DEPLOY_DIR/config.py" << EOF
# RiskOptimizer Backend Configuration for $ENVIRONMENT environment
# Generated by deploy.sh on $(date)

import os

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = int(os.environ.get("PORT", 5000))

# Database Configuration
DB_HOST = "${DB_HOST}"
DB_PORT = ${DB_PORT}
DB_NAME = "${DB_NAME}"
DB_USER = "${DB_USER}"
DB_PASSWORD = "${DB_PASSWORD}"

# Blockchain Configuration
BLOCKCHAIN_NETWORK = "${BLOCKCHAIN_NETWORK}"

# Logging Configuration
LOG_LEVEL = "${LOG_LEVEL}"
EOF
    
    # Deploy based on environment
    case $ENVIRONMENT in
        "dev")
            log "INFO" "Starting backend server for development..."
            # For dev, we just start the server locally
            python "$DEPLOY_DIR/app.py" &
            log "SUCCESS" "Backend deployed to development environment"
            log "INFO" "Backend API available at: http://localhost:5000"
            ;;
        "staging"|"prod")
            log "INFO" "Deploying backend to $ENVIRONMENT server..."
            
            # Create deployment package
            DEPLOY_PACKAGE="$PROJECT_ROOT/deploy/backend-$ENVIRONMENT-$(date +%Y%m%d%H%M%S).tar.gz"
            tar -czf "$DEPLOY_PACKAGE" -C "$DEPLOY_DIR" .
            
            log "SUCCESS" "Backend deployment package created: $DEPLOY_PACKAGE"
            log "INFO" "To complete deployment to $ENVIRONMENT server:"
            log "INFO" "1. Transfer the package to the server"
            log "INFO" "2. Extract the package to the deployment directory"
            log "INFO" "3. Restart the backend service"
            ;;
    esac
    
    log "SUCCESS" "Backend deployment completed"
}

# Function to deploy frontend
deploy_frontend() {
    log "INFO" "Deploying frontend to $ENVIRONMENT environment..."
    
    cd "$PROJECT_ROOT/code/web-frontend"
    
    # Build frontend if needed
    if [ "$SKIP_BUILD" = false ]; then
        log "INFO" "Building frontend..."
        
        # Install dependencies
        npm install
        
        # Create environment-specific .env file
        cat > ".env.$ENVIRONMENT" << EOF
# RiskOptimizer Frontend Configuration for $ENVIRONMENT environment
# Generated by deploy.sh on $(date)

REACT_APP_API_URL=${API_URL}
REACT_APP_ENVIRONMENT=${ENVIRONMENT}
REACT_APP_BLOCKCHAIN_NETWORK=${BLOCKCHAIN_NETWORK}
EOF
        
        # Build the frontend
        if [ "$ENVIRONMENT" = "dev" ]; then
            # For dev, we use the development build
            npm run build:dev
        else
            # For staging and prod, we use the production build
            REACT_APP_API_URL="$API_URL" \
            REACT_APP_ENVIRONMENT="$ENVIRONMENT" \
            REACT_APP_BLOCKCHAIN_NETWORK="$BLOCKCHAIN_NETWORK" \
            npm run build
        fi
        
        log "SUCCESS" "Frontend build completed"
    fi
    
    # Create deployment directory
    DEPLOY_DIR="$PROJECT_ROOT/deploy/$ENVIRONMENT/frontend"
    mkdir -p "$DEPLOY_DIR"
    
    # Copy frontend build to deployment directory
    log "INFO" "Copying frontend build to deployment directory..."
    if [ -d "build" ]; then
        rsync -av build/ "$DEPLOY_DIR/"
    else
        log "ERROR" "Frontend build directory not found"
        exit 1
    fi
    
    # Deploy based on environment
    case $ENVIRONMENT in
        "dev")
            log "INFO" "Starting frontend server for development..."
            # For dev, we start the development server
            npm start &
            log "SUCCESS" "Frontend deployed to development environment"
            log "INFO" "Frontend available at: http://localhost:3000"
            ;;
        "staging"|"prod")
            log "INFO" "Deploying frontend to $ENVIRONMENT server..."
            
            # Create deployment package
            DEPLOY_PACKAGE="$PROJECT_ROOT/deploy/frontend-$ENVIRONMENT-$(date +%Y%m%d%H%M%S).tar.gz"
            tar -czf "$DEPLOY_PACKAGE" -C "$DEPLOY_DIR" .
            
            log "SUCCESS" "Frontend deployment package created: $DEPLOY_PACKAGE"
            log "INFO" "To complete deployment to $ENVIRONMENT server:"
            log "INFO" "1. Transfer the package to the server"
            log "INFO" "2. Extract the package to the web server's document root"
            log "INFO" "3. Configure the web server if needed"
            ;;
    esac
    
    log "SUCCESS" "Frontend deployment completed"
}

# Function to deploy AI models
deploy_ai_models() {
    log "INFO" "Deploying AI models to $ENVIRONMENT environment..."
    
    cd "$PROJECT_ROOT/code/ai_models"
    
    # Build/train models if needed
    if [ "$SKIP_BUILD" = false ]; then
        log "INFO" "Building/training AI models..."
        
        # Install dependencies
        pip install -r requirements.txt 2>/dev/null || log "WARNING" "AI model requirements file not found, skipping"
        
        # Run model training script if it exists
        if [ -f "train_models.py" ]; then
            python train_models.py
        else
            log "WARNING" "Model training script not found, skipping"
        fi
        
        log "SUCCESS" "AI models build/training completed"
    fi
    
    # Create deployment directory
    DEPLOY_DIR="$PROJECT_ROOT/deploy/$ENVIRONMENT/ai_models"
    mkdir -p "$DEPLOY_DIR"
    
    # Copy AI model files to deployment directory
    log "INFO" "Copying AI model files to deployment directory..."
    rsync -av --exclude "__pycache__" --exclude "*.pyc" --exclude "*.pyo" --exclude "*.pyd" \
        --exclude ".pytest_cache" --exclude "tests" --exclude "training_data" \
        . "$DEPLOY_DIR/"
    
    # Deploy based on environment
    case $ENVIRONMENT in
        "dev")
            log "SUCCESS" "AI models deployed to development environment"
            ;;
        "staging"|"prod")
            log "INFO" "Deploying AI models to $ENVIRONMENT server..."
            
            # Create deployment package
            DEPLOY_PACKAGE="$PROJECT_ROOT/deploy/ai_models-$ENVIRONMENT-$(date +%Y%m%d%H%M%S).tar.gz"
            tar -czf "$DEPLOY_PACKAGE" -C "$DEPLOY_DIR" .
            
            log "SUCCESS" "AI models deployment package created: $DEPLOY_PACKAGE"
            log "INFO" "To complete deployment to $ENVIRONMENT server:"
            log "INFO" "1. Transfer the package to the server"
            log "INFO" "2. Extract the package to the deployment directory"
            log "INFO" "3. Restart the AI model service if applicable"
            ;;
    esac
    
    log "SUCCESS" "AI models deployment completed"
}

# Function to deploy blockchain contracts
deploy_blockchain() {
    log "INFO" "Deploying blockchain contracts to $ENVIRONMENT environment..."
    
    cd "$PROJECT_ROOT/code/blockchain"
    
    # Build/compile contracts if needed
    if [ "$SKIP_BUILD" = false ]; then
        log "INFO" "Building/compiling blockchain contracts..."
        
        # Install dependencies
        npm install
        
        # Compile contracts
        npx hardhat compile
        
        log "SUCCESS" "Blockchain contracts compilation completed"
    fi
    
    # Create deployment directory
    DEPLOY_DIR="$PROJECT_ROOT/deploy/$ENVIRONMENT/blockchain"
    mkdir -p "$DEPLOY_DIR"
    
    # Copy blockchain files to deployment directory
    log "INFO" "Copying blockchain files to deployment directory..."
    rsync -av --exclude "node_modules" --exclude "cache" \
        . "$DEPLOY_DIR/"
    
    # Create environment-specific deployment config
    log "INFO" "Creating environment-specific deployment configuration..."
    cat > "$DEPLOY_DIR/hardhat.config.$ENVIRONMENT.js" << EOF
// RiskOptimizer Blockchain Deployment Configuration for $ENVIRONMENT environment
// Generated by deploy.sh on $(date)

require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-ethers");
require("@nomiclabs/hardhat-etherscan");

module.exports = {
  solidity: "0.8.4",
  networks: {
    ${BLOCKCHAIN_NETWORK}: {
      url: process.env.BLOCKCHAIN_PROVIDER_URL || "http://localhost:8545",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    }
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY
  }
};
EOF
    
    # Deploy based on environment
    case $ENVIRONMENT in
        "dev")
            log "INFO" "Deploying contracts to local development network..."
            # Start local blockchain if not running
            if ! nc -z localhost 8545 2>/dev/null; then
                log "INFO" "Starting local blockchain network..."
                npx hardhat node > /dev/null 2>&1 &
                sleep 5
            fi
            
            # Deploy contracts to local network
            npx hardhat run --network localhost scripts/deploy.js
            
            log "SUCCESS" "Blockchain contracts deployed to development environment"
            ;;
        "staging"|"prod")
            log "INFO" "Preparing for blockchain deployment to $ENVIRONMENT network..."
            
            # Create deployment script
            cat > "$DEPLOY_DIR/deploy-$ENVIRONMENT.sh" << EOF
#!/bin/bash
# RiskOptimizer Blockchain Deployment Script for $ENVIRONMENT environment
# Generated by deploy.sh on $(date)

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    source ".env.$ENVIRONMENT"
fi

# Deploy contracts
npx hardhat run --network ${BLOCKCHAIN_NETWORK} scripts/deploy.js --config hardhat.config.$ENVIRONMENT.js

# Verify contracts on Etherscan (if applicable)
if [ -n "\$ETHERSCAN_API_KEY" ]; then
    npx hardhat verify --network ${BLOCKCHAIN_NETWORK} <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
fi
EOF
            chmod +x "$DEPLOY_DIR/deploy-$ENVIRONMENT.sh"
            
            log "SUCCESS" "Blockchain deployment script created: $DEPLOY_DIR/deploy-$ENVIRONMENT.sh"
            log "INFO" "To complete deployment to $ENVIRONMENT network:"
            log "INFO" "1. Set up the required environment variables (BLOCKCHAIN_PROVIDER_URL, PRIVATE_KEY, etc.)"
            log "INFO" "2. Run the deployment script: ./deploy-$ENVIRONMENT.sh"
            ;;
    esac
    
    log "SUCCESS" "Blockchain deployment preparation completed"
}

# Main execution
log "INFO" "Starting RiskOptimizer deployment to $ENVIRONMENT environment..."

# Create deployment directory
mkdir -p "$PROJECT_ROOT/deploy/$ENVIRONMENT"

# Load environment-specific configuration
load_env_config

# Run tests before deployment
run_tests

# Activate virtual environment for Python components
activate_venv

# Deploy components based on selection
if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "backend" ]; then
    deploy_backend
fi

if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "frontend" ]; then
    deploy_frontend
fi

if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "ai_models" ]; then
    deploy_ai_models
fi

if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "blockchain" ]; then
    deploy_blockchain
fi

# Deactivate virtual environment
deactivate

log "SUCCESS" "RiskOptimizer deployment to $ENVIRONMENT environment completed!"
exit 0
