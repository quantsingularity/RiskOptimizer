import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'riskoptimizer')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# Blockchain configuration
BLOCKCHAIN_PROVIDER = os.getenv('BLOCKCHAIN_PROVIDER', 'http://localhost:8545')
PORTFOLIO_TRACKER_ADDRESS = os.getenv('PORTFOLIO_TRACKER_ADDRESS', '0x0000000000000000000000000000000000000000')
RISK_MANAGEMENT_ADDRESS = os.getenv('RISK_MANAGEMENT_ADDRESS', '0x0000000000000000000000000000000000000000')

# API configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

# Model paths
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai_models', 'optimization_model.pkl'))
