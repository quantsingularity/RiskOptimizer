#!/bin/bash

# =====================================================
# RiskOptimizer Environment Setup Script
# =====================================================
# This script sets up the development environment for
# the RiskOptimizer project.
#
# It installs necessary system packages, sets up Python
# and Node.js environments, and installs dependencies
# for all project components.
#
# Tested on Ubuntu 22.04
# =====================================================

set -e # Exit immediately if a command exits with a non-zero status.

PROJECT_DIR="" # Assuming project is extracted here

# --- Helper Functions ---
echo_step() {
    echo ""
    echo "====================================================="
    echo "STEP: $1"
    echo "====================================================="
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "Error: $1 is not installed. Please install it first."
        exit 1
    fi
}

# --- Prerequisites Installation ---
echo_step "Updating package list and installing prerequisites"
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv nodejs npm postgresql-client build-essential

# Verify installations
check_command git
check_command python3
check_command pip3
check_command node
check_command npm

echo "Prerequisites installed successfully."

# --- Environment Variable Setup ---
echo_step "Setting up Environment Variables"
ENV_FILE="$PROJECT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    echo ".env file found. Please ensure it contains the necessary variables:"
    echo "  POSTGRES_URI"
    echo "  SOLANA_RPC (if using Solana)"
    echo "  ETHEREUM_RPC (if using Ethereum)"
    echo "  PORTFOLIO_TRACKER_ADDRESS (if using Ethereum)"
    echo "  ALPHA_VANTAGE_KEY"
    echo ""
    echo "Example format:"
    echo "POSTGRES_URI=\"postgresql://user:pass@localhost:5432/portfolio_optimizer\""
    echo "ETHEREUM_RPC=\"wss://mainnet.infura.io/ws/v3/YOUR_PROJECT_ID\""
    echo "PORTFOLIO_TRACKER_ADDRESS=\"0xYourContractAddress\""
    echo "ALPHA_VANTAGE_KEY=\"your_api_key_here\""
    echo ""
    echo "Please edit $ENV_FILE with your actual credentials and endpoints."
else
    echo "Warning: .env file not found at $ENV_FILE. Please create it based on the README or project requirements."
fi

# --- Backend Setup (Python) ---
echo_step "Setting up Backend Environment (Python)"
BACKEND_DIR="$PROJECT_DIR/code/backend"
PYTHON_VENV_DIR="$BACKEND_DIR/venv"

if [ ! -d "$PYTHON_VENV_DIR" ]; then
    echo "Creating Python virtual environment for backend..."
    python3 -m venv "$PYTHON_VENV_DIR"
else
    echo "Python virtual environment already exists."
fi

echo "Activating virtual environment and installing backend dependencies..."
source "$PYTHON_VENV_DIR/bin/activate"
pip install -r "$BACKEND_DIR/requirements.txt"
deactivate
echo "Backend dependencies installed."

# --- Web Frontend Setup (Node.js/Vite/React) ---
echo_step "Setting up Web Frontend Environment (Node.js)"
WEB_FRONTEND_DIR="$PROJECT_DIR/code/web-frontend"

echo "Installing web frontend dependencies using npm..."
cd "$WEB_FRONTEND_DIR"
npm install
cd "$PROJECT_DIR" # Return to project root
echo "Web frontend dependencies installed."

# --- Mobile Frontend Setup (Node.js/React Native) ---
echo_step "Setting up Mobile Frontend Environment (Node.js/React Native)"
MOBILE_FRONTEND_DIR="$PROJECT_DIR/mobile-frontend"

# Check Node version (>=18 required)
NODE_VERSION=$(node -v)
echo "Detected Node.js version: $NODE_VERSION"
if [[ "$(printf '%s\n' "v18" "$NODE_VERSION" | sort -V | head -n1)" != "v18" ]]; then
    echo "Warning: Mobile frontend requires Node.js version 18 or higher. Your version is $NODE_VERSION."
    echo "Please upgrade Node.js if you encounter issues."
fi

echo "Installing mobile frontend dependencies using npm..."
cd "$MOBILE_FRONTEND_DIR"
npm install
cd "$PROJECT_DIR" # Return to project root
echo "Mobile frontend dependencies installed."
echo "NOTE: React Native development requires additional setup (Android SDK, Xcode/iOS SDK, Watchman)."
echo "Please refer to the official React Native documentation for setting up your specific development environment: https://reactnative.dev/docs/environment-setup"

# --- Blockchain Setup (Truffle) ---
echo_step "Setting up Blockchain Environment (Truffle)"
BLOCKCHAIN_DIR="$PROJECT_DIR/code/blockchain"

echo "Installing Truffle globally using npm..."
sudo npm install -g truffle
check_command truffle
echo "Truffle installed successfully."
echo "You may need to install specific Solidity compilers or other dependencies depending on the contracts."
echo "Check $BLOCKCHAIN_DIR/truffle-config.js for details."

# --- Custom Scripts Setup ---
echo_step "Making Custom Scripts Executable"
chmod +x "$PROJECT_DIR/git-auto-commit.sh"
chmod +x "$PROJECT_DIR/lint-all.sh"
chmod +x "$PROJECT_DIR/run_riskoptimizer.sh"
echo "Custom scripts made executable."

# --- Optional Infrastructure Tools ---
echo_step "Optional Infrastructure Tools"
echo "The project includes configurations for Ansible, Kubernetes, and Terraform in the 'infrastructure' directory."
echo "If you plan to use these for deployment, you will need to install them separately."
echo " - Ansible: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html"
echo " - kubectl (for Kubernetes): https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/"
echo " - Terraform: https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli"

# --- Database Setup ---
echo_step "Database Setup (PostgreSQL)"
echo "The backend requires a PostgreSQL database."
echo "Ensure you have PostgreSQL server installed and running."
echo "You may need to create the database and user specified in your .env file (POSTGRES_URI)."
echo "Example (using psql):"
echo "  sudo -u postgres psql"
echo "  CREATE DATABASE portfolio_optimizer;"
echo "  CREATE USER user WITH PASSWORD 'pass';"
echo "  GRANT ALL PRIVILEGES ON DATABASE portfolio_optimizer TO user;"
echo "  \q"

# --- Completion ---
echo ""
echo "====================================================="
echo "RiskOptimizer Environment Setup Complete!"
echo "====================================================="
echo "Next Steps:"
echo "1. Verify and update '$PROJECT_DIR/.env' with your credentials."
echo "2. Set up your PostgreSQL database if not already done."
echo "3. For mobile development, complete React Native environment setup (SDKs, etc.)."
echo "4. Refer to '$PROJECT_DIR/README.md' for instructions on running the application components."
echo "   - Backend: Activate venv ('source $PYTHON_VENV_DIR/bin/activate') and run (e.g., 'flask run' or 'gunicorn ...')"
echo "   - Web Frontend: 'cd $WEB_FRONTEND_DIR && npm start'"
echo "   - Mobile Frontend: 'cd $MOBILE_FRONTEND_DIR && npm run android' or 'npm run ios'"

