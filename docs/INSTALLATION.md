# Installation Guide

Complete installation instructions for RiskOptimizer across different platforms and environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Docker Installation](#docker-installation)
- [Development Setup](#development-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing RiskOptimizer, ensure you have the following installed:

### Required Software

| Software   | Minimum Version | Purpose             | Installation Check    |
| ---------- | --------------- | ------------------- | --------------------- |
| Python     | 3.8+            | Backend runtime     | `python --version`    |
| Node.js    | 14+             | Frontend build      | `node --version`      |
| npm        | 6+              | Package manager     | `npm --version`       |
| Git        | 2.0+            | Version control     | `git --version`       |
| PostgreSQL | 12+             | Database (optional) | `psql --version`      |
| Redis      | 5+              | Caching (optional)  | `redis-cli --version` |

### System Requirements

| Resource | Minimum             | Recommended              | Notes                              |
| -------- | ------------------- | ------------------------ | ---------------------------------- |
| RAM      | 4GB                 | 8GB+                     | More for AI model training         |
| CPU      | 2 cores             | 4+ cores                 | Multi-core for parallel processing |
| Storage  | 10GB                | 20GB+                    | Includes data and models           |
| OS       | Linux/macOS/Windows | Ubuntu 20.04+, macOS 11+ | Windows requires WSL2              |

## Installation Methods

### Method 1: Quick Setup Script (Recommended)

The automated setup script handles all dependencies and configuration:

```bash
# Clone the repository
git clone https://github.com/quantsingularity/RiskOptimizer.git
cd RiskOptimizer

# Run the setup script
./scripts/setup_environment.sh

# This script will:
# - Check system dependencies
# - Create Python virtual environment
# - Install backend dependencies
# - Install frontend dependencies
# - Set up environment configuration
# - Initialize the database (optional)
```

### Method 2: Manual Installation

For more control over the installation process:

#### Step 1: Clone Repository

```bash
git clone https://github.com/quantsingularity/RiskOptimizer.git
cd RiskOptimizer
```

#### Step 2: Backend Setup

```bash
cd code/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

#### Step 3: Frontend Setup

```bash
# Navigate to web frontend
cd ../../web-frontend

# Install dependencies
npm install

# Build for production (optional)
npm run build
```

#### Step 4: Blockchain Setup (Optional)

```bash
cd ../code/blockchain

# Install Hardhat dependencies
npm install

# Compile smart contracts
npx hardhat compile
```

### Method 3: Docker Installation

Use Docker for containerized deployment:

```bash
# Clone repository
git clone https://github.com/quantsingularity/RiskOptimizer.git
cd RiskOptimizer

# Start all services
docker-compose up -d

# This starts:
# - Backend API (port 5000)
# - Frontend (port 3000)
# - PostgreSQL (port 5432)
# - Redis (port 6379)
# - Celery worker
```

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

| OS / Platform | Recommended Install Command                                                                                | Notes                             |
| ------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------- |
| Ubuntu 20.04+ | `sudo apt-get update && sudo apt-get install -y python3.9 python3-pip nodejs npm postgresql redis-server`  | Install system dependencies first |
| Ubuntu 22.04+ | `sudo apt-get update && sudo apt-get install -y python3.10 python3-pip nodejs npm postgresql redis-server` | Python 3.10 recommended           |

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nodejs npm postgresql postgresql-contrib redis-server git

# Start services
sudo systemctl start postgresql redis-server
sudo systemctl enable postgresql redis-server

# Create database (optional)
sudo -u postgres createdb riskoptimizer
sudo -u postgres createuser -s $USER

# Continue with Method 1 or 2 above
```

### macOS

| OS / Platform             | Recommended Install Command                      | Notes                        |
| ------------------------- | ------------------------------------------------ | ---------------------------- |
| macOS 11+ (Intel)         | `brew install python@3.10 node postgresql redis` | Use Homebrew package manager |
| macOS 11+ (Apple Silicon) | `brew install python@3.10 node postgresql redis` | Native ARM support           |

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 node postgresql redis

# Start services
brew services start postgresql
brew services start redis

# Continue with Method 1 or 2 above
```

### Windows

| OS / Platform           | Recommended Install Command                   | Notes                                        |
| ----------------------- | --------------------------------------------- | -------------------------------------------- |
| Windows 10/11 with WSL2 | Install WSL2, then follow Ubuntu instructions | Recommended approach                         |
| Windows 10/11 native    | Download installers from official websites    | PostgreSQL, Python, Node.js, Git for Windows |

**Option A: WSL2 (Recommended)**

```bash
# Install WSL2
wsl --install

# Follow Ubuntu instructions inside WSL2
```

**Option B: Native Windows**

1. Install Python 3.8+ from [python.org](https://python.org)
2. Install Node.js 14+ from [nodejs.org](https://nodejs.org)
3. Install Git for Windows from [git-scm.com](https://git-scm.com)
4. Install PostgreSQL from [postgresql.org](https://postgresql.org) (optional)
5. Install Redis from [redis.io](https://redis.io) or use WSL (optional)
6. Continue with Method 2 (Manual Installation)

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Copy template
cp .env.example .env

# Edit with your configuration
# Required variables:
# - SECRET_KEY
# - JWT_SECRET_KEY
# - DATABASE_URL (if using PostgreSQL)
# - REDIS_URL (if using Redis)
```

Example `.env` file:

```env
# Application
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Database (optional - uses SQLite by default)
DB_USE_SQLITE=true
SQLITE_DB_PATH=riskoptimizer.db
# For PostgreSQL:
# DB_USE_SQLITE=false
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=riskoptimizer
# DB_USER=postgres
# DB_PASSWORD=postgres

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Blockchain (optional)
BLOCKCHAIN_PROVIDER_URL=http://localhost:8545
PORTFOLIO_TRACKER_ADDRESS=
RISK_MANAGEMENT_ADDRESS=

# API
API_HOST=0.0.0.0
API_PORT=5000
CORS_ORIGINS=http://localhost:3000

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Verification

Verify your installation:

```bash
# Check backend
cd code/backend
python -c "import flask, pandas, numpy; print('Backend dependencies OK')"

# Check if app starts
python app.py &
sleep 3
curl http://localhost:5000/health
# Expected: {"status": "ok", ...}
kill %1

# Check frontend
cd ../../web-frontend
npm run build
# Should complete without errors

# Run tests
cd ../code/backend
pytest
# Expected: All tests pass
```

## Post-Installation Steps

### 1. Initialize Database

```bash
cd code/backend
python -c "from riskoptimizer.infrastructure.database.session import init_db; init_db()"
```

### 2. Load Sample Data

```bash
# Sample historical data is in data/ directory
ls -lh data/
# You should see:
# - AAPL_historical.csv
# - MSFT_historical.csv
# - BTC_USD_historical.csv
# etc.
```

### 3. Start Services

```bash
# Use the convenience script
./scripts/run_riskoptimizer.sh

# Or start manually:
# Terminal 1: Backend
cd code/backend && python app.py

# Terminal 2: Frontend
cd web-frontend && npm start

# Terminal 3: Celery (optional)
cd code/backend && celery -A riskoptimizer.tasks.celery_app worker --loglevel=info
```

### 4. Access the Application

- **Web Interface:** http://localhost:3000
- **API Documentation:** http://localhost:5000/apidocs
- **Health Check:** http://localhost:5000/health

## Docker Installation Details

### Prerequisites for Docker

- Docker Engine 20.10+
- Docker Compose 1.29+

### Docker Setup

```bash
# Clone repository
git clone https://github.com/quantsingularity/RiskOptimizer.git
cd RiskOptimizer

# Review docker-compose.yml
cat docker-compose.yml

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Docker Services

| Service       | Port | Description         |
| ------------- | ---- | ------------------- |
| backend       | 5000 | Flask API server    |
| frontend      | 3000 | React web app       |
| postgres      | 5432 | PostgreSQL database |
| redis         | 6379 | Redis cache         |
| celery-worker | -    | Async task worker   |

## Development Setup

For active development:

```bash
# Run setup script with development options
./scripts/setup_dev_environment.sh

# This additionally:
# - Installs pre-commit hooks
# - Sets up linting tools
# - Configures IDE settings
# - Installs development dependencies
```

## Troubleshooting

### Common Issues

**Issue: `ModuleNotFoundError: No module named 'riskoptimizer'`**

Solution:

```bash
cd code/backend
pip install -e .
```

**Issue: Database connection failed**

Solution:

```bash
# Use SQLite instead
export DB_USE_SQLITE=true
export SQLITE_DB_PATH=riskoptimizer.db
```

**Issue: Redis connection failed**

Solution:

```bash
# Redis is optional - application will work without it (no caching)
# Or start Redis:
redis-server
```

**Issue: Port already in use**

Solution:

```bash
# Change port in .env file
API_PORT=5001  # Instead of 5000
```

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Next Steps

After successful installation:

1. Read [USAGE.md](USAGE.md) for usage instructions
2. Check [CONFIGURATION.md](CONFIGURATION.md) for advanced configuration
3. Explore [examples/](examples/) for code examples
4. Review [API.md](API.md) for API documentation

## Uninstallation

To remove RiskOptimizer:

```bash
# Stop services
docker-compose down -v  # If using Docker

# Remove virtual environment
rm -rf code/backend/venv

# Remove node modules
rm -rf web-frontend/node_modules
rm -rf mobile-frontend/node_modules
rm -rf code/blockchain/node_modules

# Remove database (optional)
sudo -u postgres dropdb riskoptimizer

# Remove project directory
cd ..
rm -rf RiskOptimizer
```
