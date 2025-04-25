# Installation Guide

## Prerequisites

Before installing the RiskOptimizer platform, ensure you have the following prerequisites:

- **Operating System**: Linux, macOS, or Windows 10+
- **Docker**: Version 20.10.0 or higher
- **Docker Compose**: Version 2.0.0 or higher
- **Git**: Version 2.30.0 or higher
- **Node.js**: Version 16.0.0 or higher
- **Python**: Version 3.8.0 or higher
- **Kubernetes**: Version 1.20.0 or higher (for production deployment)
- **Terraform**: Version 1.0.0 or higher (for infrastructure provisioning)
- **Ansible**: Version 2.10.0 or higher (for configuration management)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/abrar2030/RiskOptimizer.git
cd RiskOptimizer
```

### 2. Environment Configuration

Copy the example environment file and configure it with your settings:

```bash
cp .env.example .env
```

Edit the `.env` file to set up your local development environment variables:

```
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=riskoptimizer
DB_USER=postgres
DB_PASSWORD=your_password

# Blockchain Configuration
BLOCKCHAIN_PROVIDER=http://localhost:8545
CONTRACT_ADDRESS=0x...

# API Keys
MARKET_DATA_API_KEY=your_api_key
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd code/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python manage.py init_db

# Start the backend server
python app.py
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd code/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

### 5. Blockchain Setup

```bash
# Navigate to blockchain directory
cd code/blockchain

# Install Truffle globally if not installed
npm install -g truffle

# Install dependencies
npm install

# Start local blockchain (Ganache)
npx ganache-cli

# In a new terminal, deploy contracts
truffle migrate --network development
```

### 6. AI Models Setup

```bash
# Navigate to AI models directory
cd code/ai_models

# Install dependencies
pip install -r requirements.txt

# Run model training (optional)
python training_scripts/train_optimization_model.py
```

## Docker Deployment

For a containerized setup, use Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps
```

## Production Deployment

### Kubernetes Deployment

1. **Configure Kubernetes**:

```bash
# Navigate to infrastructure/kubernetes directory
cd infrastructure/kubernetes

# Apply configuration for desired environment
kubectl apply -k environments/prod
```

### Terraform Infrastructure

1. **Initialize Terraform**:

```bash
# Navigate to infrastructure/terraform directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Apply configuration for desired environment
terraform apply -var-file=environments/prod/terraform.tfvars
```

### Ansible Configuration

1. **Run Ansible Playbooks**:

```bash
# Navigate to infrastructure/ansible directory
cd infrastructure/ansible

# Run playbook
ansible-playbook -i inventory/hosts.yml playbooks/main.yml
```

## Verification

After installation, verify that all components are running correctly:

1. **Backend API**: Access `http://localhost:5000/api/health` to check API status
2. **Frontend**: Access `http://localhost:3000` to view the application
3. **Blockchain**: Check contract deployment status with `truffle networks`
4. **Database**: Connect to the database and verify tables are created

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify database credentials in `.env` file
   - Ensure database service is running

2. **Blockchain Connection Issues**:
   - Check if local blockchain node is running
   - Verify contract addresses in configuration

3. **Frontend Build Failures**:
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

4. **Backend API Errors**:
   - Check logs for detailed error messages: `tail -f logs/api.log`
   - Verify environment variables are set correctly

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the [Troubleshooting Guide](troubleshooting.md) for more detailed solutions
2. Submit an issue on the GitHub repository
3. Contact the development team at support@riskoptimizer.com
